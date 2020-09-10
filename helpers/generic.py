from cobra.mit.request import DnQuery
import re
from defaults import UNSAFE_CHARACTER_REPLACE

def find_children(mo, moDir, filter=None):
    dnQuery = DnQuery(mo.dn)
    dnQuery.queryTarget = "children"
    children =  moDir.query(dnQuery)
    if filter is not None:
        return [x for x in children if x.meta.moClassName == filter]
    else:
        return children



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
        accportselector = find_children(leafintprofile, moDir, "infraHPortS")
        
        # Find list of port selectors and relative Policy Groups
        # so we can add interfaces to existing groups
        portselectors = {}
        for selector in accportselector:
            accaccgroup = find_children(selector, moDir, "infraRsAccBaseGrp")[0].tDn
            accportblock = find_children(selector, moDir, "infraPortBlk")
            portrange = []
            for block in accportblock:
                # Not going to bother with these
                assert block.fromCard == block.toCard

                for i in range(int(block.fromPort), int(block.toPort)+1):
                    if i not in portrange:
                        portrange.append(i)

            portselectors[accaccgroup] = selector


        swprofiles[tuple(leaves)] = {"leafselector": leafprof,
                                     "interfaceselector": portselectors}

    # Sample return data:
    # {(101,): {'leafselector': <cobra.modelimpl.infra.nodep.NodeP object at 0x7f03d19ff490>, 
    #           'interfaceselector': {'uni/infra/funcprof/accportgrp-1G': <cobra.modelimpl.infra.hports.HPortS object at 0x7f03d1a58fd0>, 
    #                                 'uni/infra/funcprof/accportgrp-accessantani': <cobra.modelimpl.infra.hports.HPortS object at 0x7f03d19f33a0>, 
    #                                 'uni/infra/funcprof/accbundle-porc-ciannel': <cobra.modelimpl.infra.hports.HPortS object at 0x7f03d1a14d60>}}}
    return swprofiles


def safe_string(string):
    unsafe_find = re.compile(r"[^a-zA-Z0-9_.-]")
    for i in unsafe_find.findall(string):
        safe_char = UNSAFE_CHARACTER_REPLACE.get(i, "")
        string = string.replace(i, safe_char)

    return string