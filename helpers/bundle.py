from cobra.model.infra import AccBndlGrp, PortBlk
from cobra.mit.request import ConfigRequest

def create_bundle_interface(name, moDir, vpc=False, *args, **kwargs):
    parent = moDir.lookupByDn('uni/infra/funcprof')
    bundle = AccBndlGrp(parent, name, **kwargs)
    if vpc is True:
        bundle.lagT = "node"

    tenantconfig = ConfigRequest()
    tenantconfig.addMo(bundle)
    moDir.commit(tenantconfig)


def create_port_block(name, portselector, description, fromPort, toPort=None):
    if toPort is None:
        toPort = fromPort

    block = PortBlk(portselector, 
                    name,
                    descr=description, 
                    fromPort=fromPort,
                    toPort=toPort)

    return block