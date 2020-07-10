def allowed_vlan_to_list(vlanlist):
    split = vlanlist.split(",")
    outlist = ()
    for vlan in split:
        if "-" in vlan:
            begin, end = vlan.split("-")
            newvlans = tuple(range(int(begin), int(end)+1))
            outlist = outlist + newvlans
        else:
            outlist = outlist + (int(vlan), )
    return outlist

def parse_vlan_l2(conf):
    vlans = conf.find_objects(r"^vlan \d")
    l2dict = {}
    for vlan in vlans:
        vlancfg = vlan.ioscfg
        vlan_id = int(vlancfg[0].split()[-1])
        if "name" in str(vlancfg):
            namelist = [x for x in vlancfg if " name " in x]
            assert len(namelist) == 1
            vlan_name_raw = namelist[0]
            vlan_name = vlan_name_raw.replace(" name ", "").strip()
            l2dict[vlan_id] = {"name": vlan_name}
        else: 
            l2dict[vlan_id] = {}

    return l2dict
