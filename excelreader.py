import pandas as pd
import numpy as np
import yaml
import math
from copy import deepcopy


default_tenant = {'name': '',
                  'description': '',
                  'app': [],
                  'bd': [],
                  'vrf': [],
                  'contract': [],
                  'protocol_policy': {}}

default_app = {'name': '',
               'epg': []}

default_epg = {'name': '',
               'bd': '',
               'contract': [],
               'static_path': [],
               'domain': []}

default_bd = {'name': '',
              'subnet': [],
              'vrf': ''}


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
    all_tenant_bd = []

    for app in clean_app_list:
        app_bd_list = []
        thisapp = thistenant.loc[thistenant['ANP'] == app]
        epg_list = thisapp.EPG.unique().tolist()
        clean_epg_list = [x for x in epg_list if str(x) != 'nan']
        all_app_epg = []

        for epg in clean_epg_list:
            thisepg = thisapp.loc[thisapp['EPG'] == epg]
            bd_list = thisepg.BD.unique().tolist()
            clean_bd_list = [x for x in bd_list if str(x) != 'nan']
            assert len(clean_bd_list) == 1

            for bd in clean_bd_list:
                thisbd = thisepg.loc[thisepg['BD'] == bd]
                thisrow = thisbd.iloc[0]
                vrf = thisrow['VRF-NEW']
                bddict = deepcopy(default_bd)
                bddict.update({'name': bd,
                               'vrf': vrf})
                all_tenant_bd.append(bddict)

            epgdict = deepcopy(default_epg)
            epgdict.update({'name': epg,
                            'bd': bddict['name']})
            all_app_epg.append(epgdict)

            epgdict = deepcopy(default_epg)
            epgdict.update({'name': epg,
                            'bd': clean_bd_list[0]})

        

        appdict = deepcopy(default_app)
        appdict.update({'name': app,
                        'epg': all_app_epg})
        allapp.append(appdict)

    vrf_list = thistenant['VRF-NEW'].unique().tolist()
    clean_vrf_list = [x for x in vrf_list if str(x) != 'nan']

    tenantdict = deepcopy(default_tenant)
    tenantdict.update({'name': tenant,
                       'app': allapp,
                       'bd': all_tenant_bd,
                       'vrf': clean_vrf_list})
    alltenant.append(tenantdict)

fabric = {'tenant': alltenant}

with open('fabric-cfg.yml', 'w') as f:
    f.write(yaml.dump(fabric))
