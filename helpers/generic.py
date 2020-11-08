import re

from cobra.mit.request import DnQuery

def find_children(mo, moDir):
    print("Get children of", mo.dn)
    dnQuery = DnQuery(mo.dn)
    dnQuery.queryTarget = "children"
    children =  moDir.query(dnQuery)
    childdict = {}
    for i in children:
        try:
            childdict[i.meta.moClassName].append(i)
        except KeyError:
            childdict[i.meta.moClassName] = []
            childdict[i.meta.moClassName].append(i)

    return childdict

def find_switch_profiles(moDir) -> dict:
    print("Get switch profiles")
    swprofiles = {}

    print("Get all leaf profiles")
    leafswprofiles = moDir.lookupByClass("infraNodeP")

    print("Get all Leaf Selectors")
    nodeblocks = moDir.lookupByClass("infraNodeBlk")

    for leafprof in leafswprofiles:
        print("Get leaf profile for", leafprof.dn)
        # Path is infraNodeP/infraLeafS/infraNodeBlk so we
        # have to associate blocks to sw profiles
        leaves = []
        leafselectors = [x for x in nodeblocks if str(leafprof.dn) in str(x.dn)]
        
        for selector in leafselectors:
            for i in range(int(selector.from_), int(selector.to_)+1):
                if i not in leaves:
                    leaves.append(i)

        # Find interface selector for normal interfaces
        # port channels are infraHPortS
        intprofile = moDir.lookupByClass("infraRsAccPortP",
                                         propFilter=f'wcard(infraRsAccPortP.dn, "uni/infra/nprof-{leafprof.name}")')
        assert len(intprofile) == 1
        leafintprofile = moDir.lookupByDn(intprofile[0].tDn)
        accportselector = find_children(leafintprofile, moDir).get("infraHPortS", [])
        
        # Find list of port selectors and relative Policy Groups
        # so we can add interfaces to existing groups
        portselectors = {}
        for selector in accportselector:
            try:
                dn = find_children(selector, moDir)["infraRsAccBaseGrp"][0].tDn.replace("uni/infra/funcprof/", "")
                dashposition = dn.find("-")
                accgrpname = dn[dashposition+1:]
                portselectors[accgrpname] = selector
            except KeyError:
                continue


        swprofiles[tuple(leaves)] = {"leafintprofile": leafintprofile,
                                 "portselectors": portselectors}

    # Sample return data:
    # {(101,): {"intprofile": <cobra.modelimpl.infra.AccPortP>,
    #           "portselectors": {'uni/infra/funcprof/accportgrp-1G': <cobra.modelimpl.infra.hports.HPortS object at 0x7f03d1a58fd0>, 
    #                             'uni/infra/funcprof/accportgrp-accessantani': <cobra.modelimpl.infra.hports.HPortS object at 0x7f03d19f33a0>, 
    #                             'uni/infra/funcprof/accbundle-porc-ciannel': <cobra.modelimpl.infra.hports.HPortS object at 0x7f03d1a14d60>}}}
    return swprofiles

def find_path_endpoints(moDir):
    path_endpoints = {}
    single_path = moDir.lookupByClass("fabricPathEpCont")

    for path in single_path:
        node = int(path.nodeId)
        path_endpoints[(node,)] = path

    double_path = moDir.lookupByClass("fabricProtPathEpCont")

    for path in double_path:
        node_a = int(path.nodeAId)
        node_b = int(path.nodeBId)
        path_endpoints[(node_a,node_b)] = path
    
    return path_endpoints

def find_path_vpc(moDir):
    vpcs = {}
    propfilter = 'and(not(wcard(fabricPathEp.dn,"__ui_")),and(eq(fabricPathEp.lagT,"node"),wcard(fabricPathEp.dn,"^topology/pod-[\d]*/protpaths-")))'
    vpc_paths = moDir.lookupByClass("fabricPathEp", propFilter=propfilter)

    for path in vpc_paths:
        vpcs[path.name] = path

    return vpcs


def find_path_po(moDir):
    pos = {}
    propfilter = 'and(not(wcard(fabricPathEp.dn,"__ui_")),eq(fabricPathEp.lagT,"link"))'
    po_paths = moDir.lookupByClass("fabricPathEp", propFilter=propfilter)

    for path in po_paths:
        pos[path.name] = path

    return pos

def safe_string(string):
    unsafe_find = re.compile(r"[^a-zA-Z0-9_.-]")
    if len(unsafe_find.findall(string)) > 0:
        raise SyntaxError("Invalid string "+string)

    return string

def leaf_str_to_tuple(leafs):
    if "," in leafs:
        leafarr = leafs.split(",")
        assert len(leafarr) == 2
        leaves = (int(leafarr[0]), int(leafarr[1]))
    else:
        leaves = (int(leafs),)

    return leaves
