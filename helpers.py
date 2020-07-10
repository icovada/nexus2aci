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
    for vlan in vlans.ioscfg:
        vlan_id = int(vlan[0].split()[-1])
        if "name" in str(vlan):
            namelist = [x for x in vlan if " name " in x]
            assert len(namelist) == 1
            vlan_name_raw = namelist[0]
            vlan_name = vlan_name_raw.replace(" name ").strip()
            l2dict[vlan_id] = {}
        else: 
            l2dict[vlan_id] = {"name": vlan_name}

    return l2dict
