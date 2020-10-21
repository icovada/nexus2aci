import pandas as pd
from copy import deepcopy
import pickle
import csv
import urllib3

from cobra.mit.access import MoDirectory
from cobra.mit.session import LoginSession
from cobra.model.fv import Tenant, Ap, AEPg, BD, RsBd, RsPathAtt
from cobra.mit.request import ConfigRequest
from cobra.model.infra import AccBndlGrp, RsLacpPol, HPortS, RsAccBaseGrp


import acicreds
import defaults
import policymappings
import helpers.generic
import helpers.int


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

excel = pd.read_excel("excelout.xlsx")

with open("tempdata.bin", "rb") as data:
    networkdata = pickle.load(data)

with open("intnames.csv", "r") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        for interface in networkdata:
            try:
                if interface['name'] == row['name']:
                    if row['newname'] != "":
                        interface['newname'] = row['newname']
                    break
            except KeyError:
                pass

networkdata = [x for x in networkdata if "newname" in x]

tenant_list = excel.Tenant.unique().tolist()
# remove nan from list
clean_tenant_list = [x for x in tenant_list if str(x) != 'nan']

data = {}

fabric = []
alltenant = []

for tenant in clean_tenant_list:
    thistenant = excel.loc[excel['Tenant'] == tenant]
    app_list = thistenant.ANP.unique().tolist()
    clean_app_list = [x for x in app_list if str(x) != 'nan']
    allapp = []
    all_tenant_bd = []

    for app in clean_app_list:
        app_bd_list = []
        thisapp = thistenant.loc[thistenant['ANP'] == app]
        epg_list = thisapp.EPG.unique().tolist()
        clean_epg_list = [x for x in epg_list if str(x) != 'nan']
        all_app_epg = []

        for epg in clean_epg_list:
            thisepg = thisapp.loc[thisapp['EPG'] == epg]
            bd_list = thisepg.BD.unique().tolist()
            clean_bd_list = [x for x in bd_list if str(x) != 'nan']
            assert len(clean_bd_list) == 1

            for bd in clean_bd_list:
                thisbd = thisepg.loc[thisepg['BD'] == bd]
                thisrow = thisbd.iloc[0]
                vrf = thisrow['VRF-NEW']
                bddict = deepcopy(defaults.bd)
                vlanid = int(thisrow['Vlan ID'])

                bddict.update({'name': helpers.generic.safe_string(bd),
                               'vrf': vrf})

                if isinstance(thisrow['netmask'], str):
                    netmask = thisrow['netmask'].split('.')
                    # Validate subnet mask
                    for i in range(len(netmask)-1):
                        try:
                            assert netmask[i] >= netmask[i+1]
                        except AssertionError:
                            raise AssertionError(
                                f"Invalid subnet format {thisrow['netmask']}")

                    # Black magic from https://stackoverflow.com/questions/38085571/how-use-netaddr-to-convert-subnet-mask-to-cidr-in-python
                    cidr = sum(bin(int(x)).count('1') for x in netmask)
                    l3 = {'name': thisrow['ip_address'],
                          'mask': cidr,
                          'scope': 'public'}

                bddict['subnet'].append(l3)
                all_tenant_bd.append(bddict)

            epgdict = deepcopy(defaults.epg)
            epgdict.update({'name': helpers.generic.safe_string(epg),
                            'bd': bddict,
                            'old_vlan_tag': vlanid})
            all_app_epg.append(epgdict)

            epgdict = deepcopy(defaults.epg)
            epgdict.update({'name': helpers.generic.safe_string(epg),
                            'bd': clean_bd_list[0]})

        appdict = deepcopy(defaults.app)
        appdict.update({'name': helpers.generic.safe_string(app),
                        'epg': all_app_epg})
        allapp.append(appdict)

    vrf_list = thistenant['VRF-NEW'].unique().tolist()
    clean_vrf_list = [{'name': x} for x in vrf_list if str(x) != 'nan']

    tenantdict = deepcopy(defaults.tenant)
    tenantdict.update({'name': helpers.generic.safe_string(tenant),
                       'app': allapp,
                       'bd': all_tenant_bd,
                       'vrf': clean_vrf_list})
    alltenant.append(tenantdict)

# alltenant now contains:
# [{'app': [{'epg': [{'bd': {'name': 'ITO-APP_ENTERPRICE_A-GDC_BD',
#                           'subnet': [{'mask': 24,
#                                       'name': '172.22.90.254',
#                                       'scope': 'public'}],
#                           'vrf': 'VINTAGE-GDC_VRF'},
#                    'contract': [],
#                    'domain': [],
#                    'name': 'ITO-APP_ENTERPRICE_A-GDC_EPG',
#                    'old_vlan_tag': 93,
#                    'static_path': []},
#                   {'bd': {'name': 'ITO-APP_ENTERPRICE_B-GDC_BD',
#                           'subnet': [{'mask': 24,
#                                       'name': '172.22.91.254',
#                                       'scope': 'public'}],
#                           'vrf': 'VINTAGE-GDC_VRF'},
#                    'contract': [],
#                    'domain': [],
#                    'name': 'ITO-APP_ENTERPRICE_B-GDC_EPG',
#                    'old_vlan_tag': 94,
#                    'static_path': []}],
#           'name': 'VINTAGE-GDC_ANP'}],
#  'bd': [{'name': 'ITO-APP_ENTERPRICE_A-GDC_BD',
#          'subnet': [{'mask': 24, 'name': '172.22.90.254', 'scope': 'public'}],
#          'vrf': 'VINTAGE-GDC_VRF'},
#         {'name': 'ITO-APP_ENTERPRICE_B-GDC_BD',
#          'subnet': [{'mask': 24, 'name': '172.22.91.254', 'scope': 'public'}],
#          'vrf': 'VINTAGE-GDC_VRF'}],
#  'contract': [],
#  'description': '',
#  'name': 'Antani',
#  'protocol_policy': {},
#  'vrf': [{'name': 'VINTAGE-GDC_VRF'}]}]

for tenant in alltenant:
    for application in tenant['app']:
        for epg in application['epg']:
            for interface in networkdata:
                if "newname" not in interface:
                    # Do not lookup non-migrated interfaces
                    continue

                if "ismember" in interface:
                    continue
                try:
                    if epg['old_vlan_tag'] in interface['allowed_vlan']:
                        epg['static_path'].append({'interface': interface,
                                                   'tag': True})
                except KeyError:
                    pass

                try:
                    if epg['old_vlan_tag'] == interface['native_vlan']:
                        epg['static_path'].append({'interface': interface,
                                                   'tag': False})
                except KeyError:
                    pass

# alltenant now contains:
# [{'app': [{'epg': [{'bd': {'name': 'ITO-APP_ENTERPRICE_A-GDC_BD',
#                           'subnet': [{'mask': 24,
#                                       'name': '172.22.90.254',
#                                       'scope': 'public'}],
#                           'vrf': 'VINTAGE-GDC_VRF'},
#                    'contract': [],
#                    'domain': [],
#                    'name': 'ITO-APP_ENTERPRICE_A-GDC_EPG',
#                    'old_vlan_tag': 93,
#                    'static_path': [{'interface': {'description': 'SNSV00864_nic0_1',
#                                                   'name': 'H3-4/1/Ethernet114/1/5',
#                                                   'native_vlan': 93,
#                                                   'newname': '101/1/1'},
#                                     'tag': False}]},
#                   {'bd': {'name': 'ITO-APP_ENTERPRICE_B-GDC_BD',
#                           'subnet': [{'mask': 24,
#                                       'name': '172.22.91.254',
#                                       'scope': 'public'}],
#                           'vrf': 'VINTAGE-GDC_VRF'},
#                    'contract': [],
#                    'domain': [],
#                    'name': 'ITO-APP_ENTERPRICE_B-GDC_EPG',
#                    'old_vlan_tag': 94,
#                    'static_path': [{'interface': {'description': 'SNSV01048_nic0_1',
#                                                   'name': 'H3-4/1/Ethernet114/1/7',
#                                                   'native_vlan': 94,
#                                                   'newname': '101/1/3'},
#                                     'tag': False},
#                                    {'interface': {'description': 'SNSV01202_nic0_1',
#                                                   'name': 'H3-4/1/Ethernet114/1/9',
#                                                   'native_vlan': 94,
#                                                   'newname': '101/1/5'},
#                                     'tag': False},
#                                    {'interface': {'description': 'SNSV01255_nic0_1',
#                                                   'name': 'H3-4/1/Ethernet114/1/11',
#                                                   'native_vlan': 94,
#                                                   'newname': '101/1/7'},
#                                     'tag': False},
#                                    {'interface': {'description': 'SNSV01257_nic0_1',
#                                                   'name': 'H3-4/1/Ethernet114/1/12',
#                                                   'native_vlan': 94,
#                                                   'newname': '101/1/8'},
#                                     'tag': False},
#                                    {'interface': {'description': 'SNSV01261_nic0_1',
#                                                   'name': 'H3-4/1/Ethernet114/1/13',
#                                                   'native_vlan': 94,
#                                                   'newname': '101/1/9'},
#                                     'tag': False}]}],
#           'name': 'VINTAGE-GDC_ANP'}],
#  'bd': [{'name': 'ITO-APP_ENTERPRICE_A-GDC_BD',
#          'subnet': [{'mask': 24, 'name': '172.22.90.254', 'scope': 'public'}],
#          'vrf': 'VINTAGE-GDC_VRF'},
#         {'name': 'ITO-APP_ENTERPRICE_B-GDC_BD',
#          'subnet': [{'mask': 24, 'name': '172.22.91.254', 'scope': 'public'}],
#          'vrf': 'VINTAGE-GDC_VRF'}],
#  'contract': [],
#  'description': '',
#  'name': 'Antani',
#  'protocol_policy': {},
#  'vrf': [{'name': 'VINTAGE-GDC_VRF'}]}]

# Init ACI session
loginSession = LoginSession(acicreds.url, acicreds.username, acicreds.password)
moDir = MoDirectory(loginSession)
moDir.login()
uniMo = moDir.lookupByDn('uni')

tenantconfig = ConfigRequest()
for tenant in alltenant:
    fvTenant = Tenant(uniMo, tenant['name'])
    tenant["aciobject"] = fvTenant
    tenantconfig.addMo(fvTenant)

    for app in tenant['app']:
        fvApp = Ap(fvTenant, app['name'])
        app["aciobject"] = fvApp
        tenantconfig.addMo(fvApp)

        for epg in app['epg']:
            fvAEPg = AEPg(fvApp, epg['name'])
            epg["aciobject"] = fvAEPg
            tenantconfig.addMo(fvAEPg)

            fvBD = BD(fvTenant, epg['bd']['name'])
            epg['bd']['aciobject'] = fvBD
            tenantconfig.addMo(fvBD)

            bind = RsBd(fvAEPg, tnFvBDName=epg['bd']['name'])
            tenantconfig.addMo(bind)

moDir.commit(tenantconfig)


switch_profiles = helpers.generic.find_switch_profiles(moDir)

# Create port-channels and vpc
# add object in interface dict
bundleparent = moDir.lookupByDn('uni/infra/funcprof')
config = ConfigRequest()
for interface in networkdata:
    try:
        if interface["ismember"] == True:
            continue
    except KeyError:
        pass

    if "newname" not in interface:
        continue

    if any([x in interface['name'] for x in ["port-channel", "vpc"]]):
        # TODO: Check if it already exists
        bundle, lacp_pol = helpers.int.create_bundle_interface_polgrp(interface, bundleparent)
        config.addMo(bundle)
        config.addMo(lacp_pol)

        # Add members in policy group
        if "port-channel" in interface['name']:
            membernames = [x for x in interface['members']]
        else:
            membernames = []
            for intf in interface['members']:
                membernames = membernames + intf['members']

        int_selector_name = defaults.xlate_policy_group_bundle_int_selector_name(interface['newname'])
        for intf in membernames:
            if "newname" in intf:
                try:
                    path = intf['newname'].split("/")
                    assert len(path) == 3
                except KeyError:
                    continue
                except AssertionError:
                    raise AssertionError("Wrong interface name " + intf['newname'] + ", format 100/1/1")
                leaf = helpers.generic.leaf_str_to_tuple(path[0])
                int_selector_name = defaults.xlate_policy_group_bundle_int_selector_name(interface['newname'])
                try:
                    assert leaf in switch_profiles
                except AssertionError:
                    # TODO: Create leaf_profile and interface selector profile
                    raise AssertionError("No leaf profile for this interface")

                try:
                    interfaceselector = switch_profiles[leaf]['portselectors'][interface['newname']]
                except KeyError:
                    # Create port selector
                    interfaceselector = HPortS(switch_profiles[leaf]['leafintprofile'], int_selector_name, "range")
                    switch_profiles[leaf]['portselectors'][defaults.POLICY_GROUP_ACCESS] = interfaceselector
                    config.addMo(interfaceselector)

                    accbasegrp = RsAccBaseGrp(interfaceselector, tDn="uni/infra/funcprof/accbundle-" + interface['newname'])
                    config.addMo(interfaceselector)
                    config.addMo(accbasegrp)

                port_block = helpers.int.create_port_block(intf, interfaceselector)
                config.addMo(port_block)
        

    if "Ethernet" in interface['name']:
        try:
            path = interface['newname'].split("/")
            assert len(path) == 3
        except KeyError:
            continue
        except AssertionError:
            raise AssertionError("Wrong interface name " + interface['newname'] + ", format 100/1/1")

        leaf = helpers.generic.leaf_str_to_tuple(path[0])
        int_selector_name = defaults.xlate_policy_group_bundle_int_selector_name(defaults.POLICY_GROUP_ACCESS)
        try:
            assert leaf in switch_profiles
        except AssertionError:
            # TODO: Create leaf_profile and interface selector profile
            raise AssertionError("No leaf profile for this interface")
        
        try:
            interfaceselector = switch_profiles[leaf]['portselectors'][defaults.POLICY_GROUP_ACCESS]
        except KeyError:
            # Create port selector
            interfaceselector = HPortS(switch_profiles[leaf]['leafintprofile'], int_selector_name, "range")
            switch_profiles[leaf]['portselectors'][defaults.POLICY_GROUP_ACCESS] = interfaceselector
            config.addMo(interfaceselector)

            # Assign policy group to port selector
            accbasegrp = RsAccBaseGrp(interfaceselector, tDn="uni/infra/funcprof/accportgrp-" + defaults.POLICY_GROUP_ACCESS)
            config.addMo(interfaceselector)
            config.addMo(accbasegrp)


        port_block = helpers.int.create_port_block(interface, interfaceselector)
        config.addMo(port_block)

    # save leaf pair in interface definition
    interface['leaf'] = leaf

moDir.commit(config)


path_endpoints = helpers.generic.find_path_endpoints(moDir)
path_vpc = helpers.generic.find_path_vpc(moDir)
path_po = helpers.generic.find_path_po(moDir)
# Create static paths
config = ConfigRequest()
for tenant in alltenant:
    for app in tenant['app']:
        for epg in app['epg']:
            for path in epg['static_path']:
                interface = path['interface']
                if "newname" in interface:
                    if "port-channel" in interface['name']:
                        staticpath = RsPathAtt(epg['aciobject'], tDn=str(path_po[interface['newname']].dn))
                    elif "vpc" in interface['name']:
                        staticpath = RsPathAtt(epg['aciobject'], tDn=str(path_vpc[interface['newname']].dn))
                    elif "Ethernet" in interface['name']:
                        intpath = interface['newname'].split("/")                        
                        parentpath = str(path_endpoints[(int(intpath[0]),)].dn)
                        pathexp_path = f"/pathep-[eth{str(intpath[1])}/{str(intpath[2])}]"
                        staticpath = RsPathAtt(epg['aciobject'], tDn=parentpath+pathexp_path)
                    else:
                        raise KeyError("Unknown interface type")

                    if path['tag']:
                        staticpath.mode = "regular"
                    else:
                        staticpath.mode = "native"

                    staticpath.instrImedcy = "immediate"
                    staticpath.encap = "vlan-" + str(epg['old_vlan_tag'])
                    config.addMo(staticpath)

moDir.commit(config)