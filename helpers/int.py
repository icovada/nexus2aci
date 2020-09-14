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