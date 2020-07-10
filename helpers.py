import re
import ipaddress


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
        for line in vlan.re_search_children("name"):
            vlan_name = re.search("name (.*)", line.text)
            l2dict[vlan_id] = {"name": vlan_name.groups()[0]}

    return l2dict


def parse_svi(conf):
    l2dict = parse_vlan_l2(conf)
    svis = conf.find_objects(r"^interface Vlan")
    svidict = l2dict
    for svi in svis:
        # Cut away "interface Vlan"
        svi_id = int(svi.re_match(r"interface Vlan(\d{1,4})$"))

        svidict[svi_id]["vrf"] = "default"
        for vrf in svi.re_search_children("vrf member"):
            vrf_name = vrf.re_match("vrf member (.*)")
            svidict[svi_id].update({"vrf": vrf_name})

        svidict[svi_id]["l3"] = {}
        for vrf in svi.re_search_children("ip address"):
            ip_text = vrf.re_match(r"ip address (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})")
            address = ipaddress.ip_interface(ip_text)
            ip = str(address.ip)
            netmask = str(address.netmask)
            svidict[svi_id].update({"l3": {"ip_address": ip, "netmask": netmask}})

        for hsrp in svi.re_search_children(r"hsrp \d"):
            for address in hsrp.re_search_children("ip"):
                hsrp_ip = address.re_match(r"ip (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
                svidict[svi_id]["l3"].update({"ip_address": hsrp_ip})

        svidict[svi_id]["l3"].update({"shutdown": False})
        for line in svi.re_search_children("shutdown"):
            if "no" not in line.text:
                svidict[svi_id]["l3"].update({"shutdown": True})

        for line in svi.re_search_children("description"):
            description = line.re_match(r"description (.*)$")
            svidict[svi_id].update({"description": description})

    return svidict