from cobra.model.infra import AccBndlGrp, PortBlk, RsLacpPol
from cobra.mit.request import ConfigRequest
import policymappings

def create_bundle_interface(interface, parent, *args, **kwargs):
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


def create_port_block(name, portselector, description, fromPort, toPort=None):
    if toPort is None:
        toPort = fromPort

    block = PortBlk(portselector, 
                    name,
                    descr=description, 
                    fromPort=fromPort,
                    toPort=toPort)

    return block