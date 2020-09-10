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
        intselectors = moDir.lookupByClass("infraRsAccPortP",
                                           propFilter=f'wcard(infraRsAccPortP.dn, "uni/infra/nprof-{leafprof.name}")')
        assert len(intselectors) == 1
        for selector in intselectors:
            realselector = moDir.lookupByDn(selector.tDn)

        swprofiles[tuple(leaves)] = {"leafselector": leafprof,
                                     "interfaceselector": realselector}

    return swprofiles


def safe_string(string):
    unsafe_find = re.compile(r"[^a-zA-Z0-9_.-]")
    for i in unsafe_find.findall(string):
        safe_char = UNSAFE_CHARACTER_REPLACE.get(i, "")
        string = string.replace(i, safe_char)

    return string