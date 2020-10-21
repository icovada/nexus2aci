from cobra.model.infra import AccBndlGrp, PortBlk, RsLacpPol
from cobra.mit.request import ConfigRequest
import policymappings

def create_bundle_interface_polgrp(interface, parent, *args, **kwargs):
    if "port-channel" in interface['name']:
        lagT = "link"
    elif "vpc" in interface['name']:
        lagT = "node"
    else:
        raise KeyError("This shouldn't happen")

    bundle = AccBndlGrp(parent, interface['newname'], lagT=lagT)
    
    try:
        assert interface['protocol'] in policymappings.lacp_modes
        lacp = interface['protocol']
    except KeyError:
        # protocol not in interface
        lacp = "on"
    except AssertionError:
        # protocol value not in lacp_modes
        raise AssertionError("Unknown protocol value " + str(interface['protocol']) + ", set it in policymappings.lacp_modes")
    finally:
        lacp = policymappings.lacp_modes.get(lacp)

    lacp_pol = RsLacpPol(bundle, tnLacpLagPolName=lacp)

    return bundle, lacp_pol


def create_port_block(interface, portselector):
    path = interface['newname'].split("/")

    if "-" in path[2]:
        fromPort, toPort = path[2].split("-")
    else:
        fromPort = path[2]
        toPort = path[2]


    block = PortBlk(portselector, 
                    f"ethernet_{path[2]}",
                    descr=interface.get("description", ""), 
                    fromCard=int(path[1]),
                    toCard=int(path[1]),
                    fromPort=int(fromPort),
                    toPort=int(toPort))

    return block

def get_port_blocks(moDir, switch_profiles, leaf_tuple):
    """
    Find all port blocks inside all interface selectors in a leaf interface profile
    for a leaf, across all leaf profiles 
    
    Parameters:
    moDir (MoDirectory): MoDirectory(loginsession)
    switch_profiles (dict): Output of helpers.generic.find_switch_profiles()
    leafinterfaceprofile (str): Name of leaf interface profile

    Returns:
    allports (dict): Dict of cards containing a set of all ports inside it
                     {1: {1,2,3,4,5}}
    """

    # Find all leaf profiles in which our leaves might be
    leafprofileids = set()
    for leaf in leaf_tuple:
        newleaves = set(x for x in list(switch_profiles) if leaf in x)
        leafprofileids.update(newleaves)

    allports = {}
    for ids in leafprofileids:
        leafintprofile = str(switch_profiles[ids]['leafintprofile'].dn)

        blocks = moDir.lookupByClass('infraPortBlk', parentDn=leafintprofile)
        for block in blocks:
            port_range = range(int(block.fromPort), int(block.toPort)+1)
            card_range = range(int(block.fromCard), int(block.toCard)+1)

            for card in card_range:
                if card not in allports:
                    allports[card] = set()
                for port in port_range:
                    allports[card].add(port)
        
    return allports
