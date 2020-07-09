def allowed_vlan_to_list(vlanlist):
    split = vlanlist.split(",")
    outlist = ()
    for vlan in split:
        if "-" in vlan:
            begin, end = vlan.split("-")
            outlist = outlist + tuple(range(int(begin), int(end)))
        else:
            outlist = outlist + (int(vlan), )
    return outlist

if __name__ == "__main__":
    pass