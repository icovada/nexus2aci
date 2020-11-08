import ciscoconfparse
import yaml
from libs import parse_svi, parse_vlan_l2
from filelist import entiredc
import pandas as pd


def generate_excel():
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

    parsedconfs = []
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

    parsedconfs = []
    for k, v in entiredc.items():
        for i in v:
            parsedconfs.append(ciscoconfparse.CiscoConfParse(i))

    l2dict = None
    for i in parsedconfs:
        l2dict = parse_vlan_l2(i, l2dict)

    l3dict = l2dict
    for i in parsedconfs:
        l3dict = parse_svi(i, l3dict)

    excelout = []
    for k, v in l3dict.items():
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


if __name__ == '__main__':
    generate_excel()
