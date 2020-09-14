from cobra.mit.request import DnQuery
import re
from defaults import UNSAFE_CHARACTER_REPLACE

def find_children(mo, moDir):
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



def find_switch_profiles(moDir):
    swprofiles = {}
    leafswprofiles = moDir.lookupByClass("infraNodeP")
    
    for leafprof in leafswprofiles:
        leaves = []
        leafselectors = moDir.lookupByClass("infraNodeBlk", 
                                            propFilter=f'wcard(infraNodeBlk.dn, "uni/infra/nprof-{leafprof.name}")')
        
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
                dn = find_children(selector, moDir)["infraRsAccBaseGrp"][0].tDn.replace("uni/infra/funcprof/","")
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


def safe_string(string):
    unsafe_find = re.compile(r"[^a-zA-Z0-9_.-]")
    for i in unsafe_find.findall(string):
        safe_char = UNSAFE_CHARACTER_REPLACE.get(i, "")
        string = string.replace(i, safe_char)

    return string

def leaf_str_to_tuple(leafs):
    if "," in leafs:
        leafarr = leafs.split(",")
        assert len(leafarr) == 2
        leaves = (int(leafarr[0]), int(leafarr[1]))
    else:
        leaves = (int(leafs),)
    
    return leaves