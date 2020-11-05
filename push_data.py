import pickle
import csv
from typing import Dict

import urllib3
import pandas as pd
from cobra.mit.access import MoDirectory
from cobra.mit.session import LoginSession
from cobra.model.fv import Tenant, Ap, AEPg, BD, RsBd, RsPathAtt, Ctx, RsCtx
from cobra.mit.request import ConfigRequest
from cobra.model.infra import HPortS, RsAccBaseGrp
from helpers.int import check_port_block, compare_port_block

from objects import Interface, PortChannel, Vpc
import acicreds
import defaults
import helpers.generic
import helpers.int

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("Reading excelout.xlsx")
excel = pd.read_excel("excelout.xlsx")

print("Reading tempdata.bin")
with open("tempdata.bin", "rb") as data:
    networkdata = pickle.load(data)

print("Reading intnames.csv")
with open("intnames.csv", "r") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        for interface in networkdata:
            try:
                if str(interface) == row['name']:
                    if row['newname'] != "":
                        interface.set_newname(row['newname'])
                    break
            except KeyError:
                pass

networkdata = [x for x in networkdata if x.has_newname()]

# Aggregate port channel interfaces
for x in [x for x in networkdata if type(x) == PortChannel]:
    x.check_members()
    x.find_groups()

for x in [x for x in networkdata if type(x) == Vpc]:
    x.check_members()
    x.find_groups()

# Add new interfaces of Po and Vpc to interface pool
for x in [x for x in networkdata if isinstance(x, PortChannel)]:
    networkdata = networkdata + x.members

# Shed interfaces that have been aggregated
networkdata = [x for x in networkdata if not x.is_superseeded]


tenant_list = excel.Tenant.unique().tolist()
# remove nan from list
clean_tenant_list = [helpers.generic.safe_string(x) for x in tenant_list if str(x) != 'nan']


# Init ACI session
print("Logging into ACI")
loginSession = LoginSession(acicreds.url, acicreds.username, acicreds.password)
moDir = MoDirectory(loginSession)
moDir.login()
uniMo = moDir.lookupByDn('uni')

data = {}

fabric = []
alltenant = []

# Get all tenants
print("Get list of all tenants")
fabric_alltenants = moDir.lookupByClass("fvTenant")
# Make a dict hashed by name for faster lookup
fabric_alltenantsdict = {x.name: x for x in fabric_alltenants}

print("Get list of all Application Profiles")
fabric_allaps = moDir.lookupByClass("fvAp")

print("Get list of all EPGs")
fabric_allepgs = moDir.lookupByClass("fvAEPg")

print("Get list of all BDs")
fabric_allbds = moDir.lookupByClass("fvBD")
fabric_bddict = {str(x.dn): x for x in fabric_allbds}

print("Get list of all EPG-BD relationships")
fabric_allfkepgbds = moDir.lookupByClass("fvRsBd")

print("Get list of all VRFs")
fabric_allvrfs = moDir.lookupByClass("fvCtx")
fabric_vrfdict = {str(x.dn): x for x in fabric_allvrfs}

print("Get list of all BD/VRF relationships")
fabric_allfkbdvrfs = moDir.lookupByClass("fvRsCtx")


# We will store the bd/VLAN id associations here
epg_tag_assoc: Dict[str, int] = {}

found = 0
added = 0

####################################################
# This section deals with Tenants, EPGs, BDs, VRFs #
####################################################

fabricconfig = ConfigRequest()
for tenant in clean_tenant_list:
    if tenant in fabric_alltenantsdict:
        tenantobj = fabric_alltenantsdict[tenant]
        print(f"Found Tenant: {tenantobj.name}")
        found = found + 1
    else:
        tenantobj = Tenant(uniMo, tenant)
        fabricconfig.addMo(tenantobj)
        print(f"CREATED Tenant: {tenantobj.name}")

    thistenant = excel.loc[excel['Tenant'] == tenant]
    app_list = thistenant.ANP.unique().tolist()
    clean_app_list = [helpers.generic.safe_string(x) for x in app_list if str(x) != 'nan']
    allapp = []
    all_tenant_bd = []

    # Find all Application Profiles belonging to this tenant
    fabric_tenantapps = [x for x in fabric_allaps if x._BaseMo__parentDnStr == tenantobj.dn]

    # Get dict of tenants keyed by name so we can search them
    fabric_tenantappdict = {x.name: x for x in fabric_tenantapps}

    # Get list of all VRFs in this tenant
    fabric_tenantvrfs = [x for x in fabric_allvrfs if x._BaseMo__parentDnStr == tenantobj.dn]
    fabric_tenantvrfnames = {x.name: x for x in fabric_tenantvrfs}
    fabric_tenantvrfdns = {str(x.dn): x for x in fabric_tenantvrfs}

    fabric_tenantbds = [x for x in fabric_allbds if x._BaseMo__parentDnStr == tenantobj.dn]
    fabric_tenantbdnames = {x.name: x for x in fabric_tenantbds}
    fabric_tenantbddns = {str(x.dn): x for x in fabric_tenantbds}

    for app in clean_app_list:
        if app in fabric_tenantappdict:
            appobject = fabric_tenantappdict[app]
            #print(f"Found Application profile: {appobject.name}")
            found = found + 1
        else:
            appobject = Ap(tenantobj, app)
            fabricconfig.addMo(appobject)
            print(f"CREATED Application profile: {appobject.name}")
            added = added + 1

        app_bd_list = []
        thisapp = thistenant.loc[thistenant['ANP'] == app]
        epg_list = thisapp.EPG.unique().tolist()
        clean_epg_list = [helpers.generic.safe_string(x) for x in epg_list if str(x) != 'nan']
        all_app_epg = []

        # Find all EPGs belonging to this Application Profile
        fabric_appepgs = [x for x in fabric_allepgs if x._BaseMo__parentDnStr == appobject.dn]

        # Get dict of EPGs by name so we can search them
        fabric_appepgdict = {x.name: x for x in fabric_appepgs}

        for epg in clean_epg_list:
            if epg in fabric_appepgdict:
                epgobject = fabric_appepgdict[epg]
                #print(f"Found EPG: {epgobject.name}")
                found = found + 1
            else:
                epgobject = AEPg(appobject, epg)
                fabricconfig.addMo(epgobject)
                print(f"CREATED EPG: {epgobject.name}")
                added = added + 1

            thisepg = thisapp.loc[thisapp['EPG'] == epg]
            bd_list = thisepg.BD.unique().tolist()
            clean_bd_list = [helpers.generic.safe_string(x) for x in bd_list if str(x) != 'nan']
            assert len(clean_bd_list) == 1

            # Find all BD inside this EPG
            fabric_epgfkepgbds = [x for x in fabric_allfkepgbds if x._BaseMo__parentDnStr == epgobject.dn]
            fabric_epgfkepgbdtnFvBDNames = {x.tnFvBDName: x for x in fabric_epgfkepgbds}
            fabric_epgfkepgbddns = {x.tDn: x for x in fabric_epgfkepgbds}

            for bd in clean_bd_list:
                # Need to check both that the BD exists and that is it linked to the EPG
                thisbd = thisepg.loc[thisepg['BD'] == bd]
                thisrow = thisbd.iloc[0]
                # Check if BD exists
                if bd in fabric_epgfkepgbdtnFvBDNames:
                    bdobject = fabric_tenantbdnames[bd]
                    #print(f"Found BD: {bdobject.name}")
                    found = found + 1
                else:
                    bdobject = BD(tenantobj, name=thisrow['BD'])
                    fabricconfig.addMo(bdobject)
                    print(f"CREATED BD: {bdobject.name}")
                    added = added + 1

                # Check link with EPG
                if str(bdobject.dn) in fabric_epgfkepgbddns:
                    fkepgbdobject = fabric_epgfkepgbddns[bdobject.dn]
                    #print(f"Found link between APP {appobject.name} and BD {bdobject.name}")
                    found = found + 1
                else:
                    fkepgbdobject = RsBd(epgobject, tnFvBDName=bdobject.name)
                    fabricconfig.addMo(fkepgbdobject)
                    print(f"CREATED link between APP {appobject.name} and BD {bdobject.name}")
                    added = added + 1

                # Check VRF exists
                vrf_name = thisrow['VRF-NEW']
                if vrf_name in fabric_tenantvrfnames:
                    vrfobject = fabric_tenantvrfnames[vrf_name]
                    #print(f"Found VRF: {vrfobject.name}")
                    found = found + 1
                else:
                    vrfobject = Ctx(tenantobj, name=vrf_name)
                    fabricconfig.addMo(vrfobject)
                    print(f"CREATED VRF: {vrfobject.name}")
                    added = added + 1

                # Check link with BD
                fabric_bdfkbdvrfs = [x for x in fabric_allfkbdvrfs if str(x.dn) == str(bdobject.dn) + "/rsctx"]
                fabric_bdfkbdvrftnFvCtxNames = {x.tnFvCtxName: x for x in fabric_bdfkbdvrfs}

                if str(vrfobject.name) in fabric_bdfkbdvrftnFvCtxNames:
                    fkvrfobject = fabric_bdfkbdvrftnFvCtxNames[vrfobject.name]
                    #print(f"Found link between BD {bdobject.name} and VRF {vrfobject.name}")
                    found = found + 1
                else:
                    fkvrfobject = RsCtx(bdobject, tnFvCtxName=vrfobject.name)
                    fabricconfig.addMo(fkvrfobject)
                    print(f"CREATED link between BD {bdobject.name} and VRF {vrfobject.name}")
                    added = added + 1

            epg_tag_assoc[epgobject.name] = int(thisrow['Vlan ID'])

                    # TODO: Add Subnets
                    # if isinstance(thisrow['netmask'], str):
                    #     netmask = thisrow['netmask'].split('.')
                    #     # Validate subnet mask
                    #     for i in range(len(netmask)-1):
                    #         try:
                    #             assert netmask[i] >= netmask[i+1]
                    #         except AssertionError:
                    #             raise AssertionError(
                    #                 f"Invalid subnet format {thisrow['netmask']}")

                    #     # Black magic from https://stackoverflow.com/questions/38085571/how-use-netaddr-to-convert-subnet-mask-to-cidr-in-python
                    #     cidr = sum(bin(int(x)).count('1') for x in netmask)
                    #     l3 = {'name': thisrow['ip_address'],
                    #           'mask': cidr,
                    #           'scope': 'public'}

print("")
print("")
print("     --------------")

if added > 0:
    print(f"Found {found} objects")
    print(f"About to create {added} objects")
    print("")
    input("Proceed? [Confirm]")
    moDir.login()
    moDir.commit(fabricconfig)
else:
    print("No objects will be modified, skipping confirmation")


##################################################
# This section deals with Fabric access policies #
##################################################

print("Get list of all EPGs")
fabric_allepgs = moDir.lookupByClass("fvAEPg")

print("Get list of all Port Blocks")
fabric_allportblocks = list(moDir.lookupByClass("infraPortBlk"))

switch_profiles: dict = helpers.generic.find_switch_profiles(moDir)
found = 0
added = 0

# Create port-channels and vpc
# add object in interface dict
bundleparent = moDir.lookupByDn('uni/infra/funcprof')
config = ConfigRequest()
for interface in networkdata:
    if interface.ismember:
        continue

    if not hasattr(interface, "newname"):
        continue

    # If is PortChannel or Vpc
    if type(interface) != Interface:
        # TODO: Check if it already exists
        bundle, lacp_pol = helpers.int.create_bundle_interface_polgrp(interface, bundleparent)
        config.addMo(bundle)
        config.addMo(lacp_pol)

        # Add members in policy group
        if type(interface) == PortChannel:
            members = interface.members
        else:
            members = []
            for intf in interface.members:
                members = members + intf.members

        for member in members:
            if member.has_newname():
                leaf = helpers.generic.leaf_str_to_tuple(interface.leaf)
                int_selector_name = defaults.xlate_policy_group_bundle_int_selector_name(interface.get_newname)
                try:
                    assert leaf in switch_profiles
                except AssertionError:
                    # TODO: Create leaf_profile and interface selector profile
                    raise AssertionError("No leaf profile for this interface")

                try:
                    interfaceselector = switch_profiles[leaf]['portselectors'][interface.get_newname]
                    print(f"Found Interface Selector {str(interfaceselector.dn)} for interface {interface.get_newname}")
                    found = found + 1
                except KeyError:
                    # Create port selector
                    interfaceselector = HPortS(switch_profiles[leaf]['leafintprofile'], int_selector_name, "range")
                    switch_profiles[leaf]['portselectors'][defaults.POLICY_GROUP_ACCESS] = interfaceselector
                    config.addMo(interfaceselector)

                    accbasegrp = RsAccBaseGrp(interfaceselector, tDn="uni/infra/funcprof/accbundle-" + interface.get_newname)
                    config.addMo(interfaceselector)
                    config.addMo(accbasegrp)
                    print(f"CREATED Interface selector {str(interfaceselector.dn)} for {interface.get_newname}")
                    added = added + 1

                port_block = helpers.int.create_port_block(member, interfaceselector)
                # If port block does not exist
                if check_port_block(port_block, switch_profiles, fabric_allportblocks, leaf):
                    config.addMo(port_block)
                    fabric_allportblocks.append(port_block)
                else:
                    # If it exists
                    if compare_port_block(port_block, switch_profiles, fabric_allportblocks, leaf):
                        # Do not add if equal
                        continue
                    else:
                        raise AssertionError(f"Cannot add port block for {member.name}, {member.get_newname}, as it overlaps with another")


    else:
        leaf = helpers.generic.leaf_str_to_tuple(interface.leaf)
        int_selector_name = defaults.xlate_policy_group_bundle_int_selector_name(defaults.POLICY_GROUP_ACCESS)
        try:
            assert leaf in switch_profiles
        except AssertionError:
            # TODO: Create leaf_profile and interface selector profile
            raise AssertionError("No leaf profile for this interface")

        try:
            interfaceselector = switch_profiles[leaf]['portselectors'][defaults.POLICY_GROUP_ACCESS]
            print(f"Found Interface Selector {str(interfaceselector.dn)} for interface {interface.get_newname}")
            found = found + 1
        except KeyError:
            # Create port selector
            interfaceselector = HPortS(switch_profiles[leaf]['leafintprofile'], int_selector_name, "range")
            switch_profiles[leaf]['portselectors'][defaults.POLICY_GROUP_ACCESS] = interfaceselector
            config.addMo(interfaceselector)


            # Assign policy group to port selector
            accbasegrp = RsAccBaseGrp(interfaceselector, tDn="uni/infra/funcprof/accportgrp-" + defaults.POLICY_GROUP_ACCESS)
            config.addMo(interfaceselector)
            config.addMo(accbasegrp)
            print(f"CREATED Interface selector {str(interfaceselector.dn)} for {interface.get_newname}")
            added = added + 1

        port_block = helpers.int.create_port_block(interface, interfaceselector)
        config.addMo(port_block)

    # save leaf pair in interface definition
    interface.leaf = leaf

print("")
print("")
print("     --------------")

if added > 0:
    print(f"Found {found} objects")
    print(f"About to create {added} objects")
    print("")
    input("Proceed? [Confirm]")
    moDir.login()
    moDir.commit(config)
else:
    print("No objects will be modified, skipping confirmation")


########################################
# This section deals with static paths #
########################################

found = 0
added = 0

path_endpoints = helpers.generic.find_path_endpoints(moDir)
path_vpc = helpers.generic.find_path_vpc(moDir)
path_po = helpers.generic.find_path_po(moDir)
# Create static paths
config = ConfigRequest()

print("Get list of static ports")
fabric_staticport = moDir.lookupByClass("fvRsPathAtt")
fabric_staticportdn = {x.dn: x for x in fabric_staticport}

print("Get list of all Port Blocks")
fabric_allportblocks = list(moDir.lookupByClass("infraPortBlk"))

for epg in fabric_allepgs:
    for interface in networkdata:
        if not interface.ismember and hasattr(interface, "newname"):
            try:
                if epg_tag_assoc[epg.name] in interface.allowed_vlan:
                    tag = True
                elif epg_tag_assoc[epg.name] == interface.native_vlan:
                    tag = False
                else:
                    continue
            except (AttributeError, KeyError):
                continue

            if type(interface) == PortChannel:
                staticpath = RsPathAtt(epg, tDn=str(path_po[interface.newname].dn))
            elif type(interface) == Vpc:
                staticpath = RsPathAtt(epg, tDn=str(path_vpc[interface.newname].dn))
            elif type(interface) == Interface:
                intpath = interface.newname.split("/")
                PARENTPATH = str(path_endpoints[(int(intpath[0]),)].dn)
                pathexp_path = f"/pathep-[eth{str(intpath[1])}/{str(intpath[2])}]"
                staticpath = RsPathAtt(epg, tDn=PARENTPATH + pathexp_path)
            else:
                raise KeyError("Unknown interface type")

            if staticpath.dn not in fabric_staticportdn:
                if tag:
                    staticpath.mode = "regular"
                else:
                    staticpath.mode = "native"

                staticpath.instrImedcy = "immediate"
                staticpath.encap = "vlan-" + str(epg_tag_assoc[epg.name])
                config.addMo(staticpath)
                added = added + 1
                print(f"Added Static Path {str(staticpath.dn)}")
            else:
                found = found + 1
                print(f"FOUND Static Path {str(staticpath.dn)}")

print("")
print("")
print("     --------------")

if added > 0:
    print(f"Found {found} objects")
    print(f"About to create {added} objects")
    print("")
    input("Proceed? [Confirm]")
    moDir.login()
    moDir.commit(config)
else:
    print("No objects will be modified, skipping confirmation")
