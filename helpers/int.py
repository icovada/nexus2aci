from objects import PortChannel, Vpc, Interface
from cobra.model.infra import AccBndlGrp, PortBlk, RsLacpPol
from cobra.mit.request import ConfigRequest
import policymappings

def create_bundle_interface_polgrp(interface, parent, *args, **kwargs):
    if type(interface) == PortChannel:
        lagT = "link"
    elif type(interface) == Vpc:
        lagT = "node"
    else:
        raise KeyError("This shouldn't happen")

    bundle = AccBndlGrp(parent, interface.newname, lagT=lagT)

    if hasattr(interface, "protocol"):
        try:
            assert interface.protocol in policymappings.lacp_modes
            lacp = interface.protocol
        except AssertionError:
            # protocol value not in lacp_modes
            raise AssertionError("Unknown protocol value " + str(interface.protocol) + ", set it in policymappings.lacp_modes")
    else:
        # protocol not in interface
        lacp = "on"
    lacp = policymappings.lacp_modes.get(lacp)

    lacp_pol = RsLacpPol(bundle, tnLacpLagPolName=lacp)

    return bundle, lacp_pol


def create_port_block(interface, interfaceselector):
    path = interface.newname.split("/")

    if "-" in path[2]:
        fromPort, toPort = path[2].split("-")
    else:
        fromPort = path[2]
        toPort = path[2]

    block = PortBlk(interfaceselector,
                    f"ethernet_{path[2]}",
                    descr=interface.description, 
                    fromCard=int(path[1]),
                    toCard=int(path[1]),
                    fromPort=int(fromPort),
                    toPort=int(toPort))

    return block

def check_port_block(port_block: PortBlk, switch_profiles: dict, fabric_allportblocks: list, leaf_tuple: tuple):
    """
    Find all port blocks inside all interface selectors in a leaf interface profile
    for a leaf, across all leaf profiles, check input port block does not use
    any of the already defined ports
    
    Parameters:
    - port_block (PortBlk): PortBlk to check
    - switch_profiles (dict): Output of helpers.generic.find_switch_profiles()
    - fabric_allportblocks (list): List of all `infraPortBlk`
    - leaf_tuple (tuple): Tuple of leaves to check

    Returns:
    - valid (bool): Whether the port block is valid or not
    """

    # Find all leaf profiles in which our leaves might be
    print("Find all leaf profiles in which leaf", leaf_tuple, "could be")
    leafprofileids = set()
    for leaf in leaf_tuple:
        newleaves = set(x for x in list(switch_profiles) if leaf in x)
        leafprofileids.update(newleaves)

    allblocks = []
    for ids in leafprofileids:
        leafintprofile = str(switch_profiles[ids]['leafintprofile'].dn)

        print("Get port blocks in", leafintprofile)
        blocks = [x for x in fabric_allportblocks if leafintprofile in str(x.dn)
                                                  and int(x.fromPort) <= port_block.fromPort
                                                  and int(x.toPort) >= port_block.toPort
                                                  and int(x.fromCard) <= port_block.fromCard
                                                  and int(x.toCard) >= port_block.toCard]
        allblocks = allblocks + blocks

    if len(allblocks) > 0:
        print("INVALID PORT BLOCK")
        return False
    else:
        print("OK PORT BLOCK")
        return True
