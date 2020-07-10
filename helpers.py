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
    l2dict = {1: {}}
    for vlan in vlans:
        vlan_id = int(vlan.text.split()[-1])
        l2dict[vlan_id] = {}
        for vlan in vlan.re_search_children("name"):
            vlan_name = vlan.text.replace(" name ", "").strip()
            l2dict[vlan_id] = {"name": vlan_name}

    return l2dict
