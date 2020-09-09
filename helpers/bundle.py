from cobra.model.infra import AccBndlGrp
from cobra.mit.request import ConfigRequest

def create_bundle_interface(name, moDir, vpc=False, *args, **kwargs):
    parent = moDir.lookupByDn('uni/infra/funcprof')
    bundle = AccBndlGrp(parent, name, **kwargs)
    if vpc is True:
        bundle.lagT = "node"

    tenantconfig = ConfigRequest()
    tenantconfig.addMo(bundle)
    moDir.commit(tenantconfig)
