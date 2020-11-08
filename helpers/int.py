from objects import PortChannel, Vpc, Interface
from cobra.model.infra import AccBndlGrp, PortBlk, RsLacpPol
import policymappings


def create_bundle_interface_polgrp(interface, parent, *args, **kwargs):
    if type(interface) == PortChannel:
        lagT = "link"
    elif type(interface) == Vpc:
        lagT = "node"
    else:
        raise KeyError("This shouldn't happen")

    bundle = AccBndlGrp(parent, interface.get_newname(), lagT=lagT)

    if hasattr(interface, "protocol"):
        try:
            assert interface.protocol in policymappings.lacp_modes
            lacp = interface.protocol
        except AssertionError:
            # protocol value not in lacp_modes
            raise AssertionError("Unknown protocol value " + str(
                interface.protocol) + ", set it in policymappings.lacp_modes")
    else:
        # protocol not in interface
        lacp = "on"
    lacp = policymappings.lacp_modes.get(lacp)

    lacp_pol = RsLacpPol(bundle, tnLacpLagPolName=lacp)

    return bundle, lacp_pol


def create_port_block(interface, interfaceselector):

    leaf, card, port = interface.get_newname().split("/")
    block = PortBlk(interfaceselector,
                    f"ethernet_{port}",
                    descr=interface.description,
                    fromCard=int(card),
                    toCard=int(card),
                    fromPort=interface.port[0],
                    toPort=interface.port[-1])

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

    if len(allblocks) == 1:
        print("INVALID PORT BLOCK")
        return False
    elif len(allblocks) > 1:
        raise AssertionError(
            f"Port block {port_block.fromPort} to {port_block.toPort}, parent {str(port_block._BaseMo__parentDn)} overlaps with another block")
    else:
        print("OK PORT BLOCK")
        return True


def compare_port_block(port_block: PortBlk, switch_profiles: dict, fabric_allportblocks: list, leaf_tuple: tuple):
    """
    Compare a new port block object to one coming from the fabric

    Suggested to use only after getting True from check_port_block()

    Parameters:
    - port_block (PortBlk): PortBlk to check
    - switch_profiles (dict): Output of helpers.generic.find_switch_profiles()
    - fabric_allportblocks (list): List of all `infraPortBlk`
    - leaf_tuple (tuple): Tuple of leaves to check

    Returns:
    - valid (bool): Whether the port blocks are equal
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

    if len(allblocks) == 1:
        oneblock = allblocks[0]
        if (str(port_block._BaseMo__parentDn) == str(oneblock._BaseMo__parentDn)
                and str(port_block.fromPort) == str(oneblock.fromPort)
                and str(port_block.toPort) == str(oneblock.toPort)
                and str(port_block.fromCard) == str(oneblock.fromCard)
                and str(port_block.toCard) == str(oneblock.toCard)):

            return True
        else:
            return False
    else:
        raise AssertionError(
            f"Something went wrong. I found {len(allblocks)} port blocks")
