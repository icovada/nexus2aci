import pandas as pd
import numpy as np
import yaml
import math

excel = pd.read_excel("excelout.xlsx")

tenant_list = excel.Tenant.unique().tolist()
# remove nan from list
clean_tenant_list = [x for x in tenant_list if str(x) != 'nan']

data = {}

fabric = []
alltenant = []

for tenant in clean_tenant_list:
    thistenant = excel.loc[excel['Tenant'] == tenant]
    app_list = thistenant.ANP.unique().tolist()
    clean_app_list = [x for x in app_list if str(x) != 'nan']
    allapp = []

    for app in clean_app_list:
        thisapp = thistenant.loc[thistenant['ANP'] == app]
        epg_list = thisapp.EPG.unique().tolist()
        clean_epg_list = [x for x in epg_list if str(x) != 'nan']
        allepg = []

        for epg in clean_epg_list:
            thisepg = thisapp.loc[thisapp['EPG'] == epg]
            bd_list = thisepg.BD.unique().tolist()
            clean_bd_list = [x for x in bd_list if str(x) != 'nan']

            for bd in clean_bd_list:
                thisbd = thisepg.loc[thisepg['BD'] == bd]
                thisrow = thisbd.iloc[0]
                vrf = thisrow['VRF-NEW']
                bddict = {'name': bd,
                          'vrf': vrf}

            epgdict = {'name': epg,
                       'bd': bddict}
            allepg.append(epgdict)

        appdict = {'name': app,
                   'epg': allepg}
        allapp.append(appdict)

    bd_list = thistenant['BD'].unique().tolist()
    clean_bd_list = [x for x in bd_list if str(x) != 'nan']

    vrf_list = thistenant['VRF-NEW'].unique().tolist()
    clean_vrf_list = [x for x in vrf_list if str(x) != 'nan']

    tenantdict = {'name': tenant,
                  'app': allapp,
                  'bd': clean_bd_list,
                  'vrf': clean_vrf_list}
    alltenant.append(tenantdict)

fabric = {'tenant': alltenant}

with open('fabric-cfg.yml', 'w') as f:
    f.write(yaml.dump(fabric, default_flow_style=False))
