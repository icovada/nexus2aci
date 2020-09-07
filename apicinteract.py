#%%
from cobra.mit.access import MoDirectory
from cobra.mit.session import LoginSession
from cobra.mit.request import DnQuery
from cobra.model.fv import Tenant, Ap, AEPg
from cobra.mit.request import ConfigRequest

apicUrl = "https://10.10.20.14"
loginSession = LoginSession(apicUrl, "admin", "C1sco12345")
moDir = MoDirectory(loginSession)
moDir.login()
uniMo = moDir.lookupByDn('uni')

#%%
# Check Tenant does not exist
allTenants = moDir.lookupByClass('fvTenant')
"ExampleTenant" not in [x.name for x in allTenants]

#%%
# Create new Tenant
config = ConfigRequest()
fvTenantMo = Tenant(uniMo, "ExampleTenant")
config.addMo(fvTenantMo)
moDir.commit(config)

# %%
# Check Tenant exists
allTenants = moDir.lookupByClass('fvTenant')
"ExampleTenant" in [x.name for x in allTenants]

#%%
# Create Application profile
config = ConfigRequest()
app = Ap(fvTenantMo, "Frontend")
config.addMo(app)
moDir.commit(config)

#%%
# Create EPG
config = ConfigRequest()
epg = AEPg(app, "EPG1")
config.addMo(epg)
moDir.commit(config)



# %%
# Delete Tenant
config = ConfigRequest()
tenant = moDir.lookupByDn("uni/tn-ExampleTenant")
tenant.delete()
config.addMo(tenant)
moDir.commit(config)

# %%
# Check Tenant exists
allTenants = moDir.lookupByClass('fvTenant')
"ExampleTenant" in [x.name for x in allTenants]

# %%
