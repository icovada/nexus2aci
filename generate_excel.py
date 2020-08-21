import ciscoconfparse
import yaml
from helpers import parse_svi, parse_vlan_l2
import pandas as pd


# Define how to transform data from nexus into ACI object names
def epg(rowdict):
    if 'description' in rowdict:
        return rowdict['Vlan name'] + "-GDC_EPG"


def anp(rowdict):
    if 'vrf' in rowdict:
        step1 = rowdict['vrf'].replace("VRF-", "")
        step2 = step1 + "-GDC_ANP"
        return step2


def bd(rowdict):
    if 'description' in rowdict:
        return row['Vlan name'] + "-GDC_BD"


def vrf(rowdict):
    if 'vrf' in rowdict:
        step1 = rowdict['vrf'].replace("VRF-", "")
        step2 = step1 + "-GDC_VRF"
        return step2


def tenant(rowdict):
    pass


# parse configs for access and distribution switches
# you should theoretically add all switches in the DC
sw1 = ciscoconfparse.CiscoConfParse('SWISNA-NGDC5K-L1.log')
sw2 = ciscoconfparse.CiscoConfParse('SWISNA-NGDC5K-L2.log')
aggregation = ciscoconfparse.CiscoConfParse('AGGSNANGDC-1.txt')

# Combine info for VLANs for all switches.
# Just one switch could do, but why not showing off?
sw1_l2 = parse_vlan_l2(sw1)
sw2_l2 = parse_vlan_l2(sw2, sw1_l2)
l2dict = parse_vlan_l2(aggregation, sw2_l2)

# Combine info from all layer3 switches, passing in the vlan info from the previous step
sw1_l3 = parse_svi(sw1, l2dict)
sw2_l3 = parse_svi(sw2, sw1_l3)
agg_l3 = parse_svi(aggregation, sw1_l3)

excelout = []
for k, v in agg_l3.items():
    row = {}
    row['Vlan ID'] = k
    if 'name' in v:
        row['Vlan name'] = v['name']
    if 'l3' in v:
        row.update(v['l3'])
    if 'description' in v:
        row['description'] = v['description']

    row['EPG'] = epg(row)
    row['ANP'] = anp(row)
    row['BD'] = bd(row)
    row['VRF-NEW'] = vrf(row)
    row['Tenant'] = tenant(row)
    print(row)
    excelout.append(row)

dfexcel = pd.DataFrame(excelout, columns=["Vlan ID",
                                          "Vlan name",
                                          "description",
                                          "vrf",
                                          "ip_address",
                                          "netmask",
                                          "shutdown",
                                          "EPG",
                                          "ANP",
                                          "BD",
                                          "VRF-NEW",
                                          "Tenant"
                                          ])

dfexcel.sort_values(by=['Vlan ID'], inplace=True)
dfexcel.to_excel('excelout.xlsx')
