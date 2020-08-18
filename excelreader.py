import pandas as pd
import numpy as np
import yaml

excel = pd.read_excel("SNAM-Censimento-VLAN-GDC_v20200622.xlsx")

tenant_list = excel.TENANT.unique().tolist()

data = {}

fabric = []
alltenant = []

for tenant in tenant_list:
    thistenant = excel.loc[excel['TENANT'] == tenant]
    applist = thistenant.ANP.unique().tolist()
    allapp = []

    for app in applist:
        thisapp = thistenant.loc[thistenant['ANP'] == app]
        epglist = thisapp.EPG.unique().tolist()
        allepg = []

        for epg in epglist:
            thisepg = thisapp.loc[thisapp['EPG'] == epg]
            bdlist = thisepg.BD.unique().tolist()

            for bd in bdlist:
                thisbd = thisepg.loc[thisepg['BD'] == bd]
                thisrow = thisbd.iloc[0]
                vrf = thisrow['VRF.1']
                bddict = {'name': bd,
                          'vrf': vrf}

            epgdict = {'name': epg,
                       'bd': bddict}
            allepg.append(epgdict)

        appdict = {'name': app,
                   'epg': allepg}
        allapp.append(appdict)
    
    tenantdict = {'name': tenant,
                  'app': allapp,
                  'bd': thistenant.['BD'].unique().tolist(),
                  'vrf': thistenant.['VRF.1'].unique().tolist()}
    alltenant.append(tenantdict)

fabric = {'tenant': alltenant}

with open('fabric-cfg.yml', 'w') as f:
    f.write(yaml.dump(fabric))