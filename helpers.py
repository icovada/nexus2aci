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
    vlans = conf.find_objects(r"^vlan \d{1,4}$")
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

        if svi_id not in svidict:
            svidict[svi_id] = {}

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


def parse_physical_interface(conf):
    phy_int = conf.find_objects(r"^interface Ethernet\d")
    intdict = {}
    for eth in phy_int:
        eth_id = eth.text.strip().replace("interface Ethernet", "")
        eth_path = [int(x) for x in eth_id.split("/")]

        thisint = {}

        for line in eth.re_search_children("description"):
            description = line.re_match(r"description (.*)$")
            thisint.update({"description": description})

        for line in eth.re_search_children("switchport mode"):
            mode = line.re_match(r"switchport mode (\w*)$")

        for line in eth.re_search_children("switchport trunk allowed vlan"):
            allowed_vlan = line.re_match(
                r"switchport trunk allowed vlan (.*)$")
            allowed_vlan_list = allowed_vlan_to_list(allowed_vlan)
            thisint.update({"allowed_vlan": allowed_vlan_list})

        for line in eth.re_search_children("switchport trunk native vlan"):
            native_vlan = int(line.re_match(r"switchport trunk native vlan (.*)$"))
            thisint.update({"native_vlan": native_vlan})

        for line in eth.re_search_children("switchport access vlan"):
            native_vlan = int(line.re_match(r"switchport access vlan (.*)$"))
            thisint.update({"native_vlan": native_vlan})

        if "native_vlan" not in thisint:
            if mode == "access":
                thisint["native_vlan"] = 1

        for line in eth.re_search_children("channel-group"):
            channel_group = line.re_match(r"channel-group (\d*) mode")
            mode = line.re_match(r"mode (\w*)")
            thisint.update({"channel_group": channel_group,
                            "mode": mode})

        if len(eth_path) == 2:
            try:
                assert isinstance(intdict[eth_path[0]], dict)
            except (AssertionError, KeyError):
                intdict[eth_path[0]] = {}
            
            intdict[eth_path[0]].update({eth_path[1]: thisint})

        if len(eth_path) == 3:
            try:
                assert isinstance(intdict[eth_path[0]], dict)
            except (AssertionError, KeyError):
                intdict[eth_path[0]] = {}
            
            try:
                assert isinstance(intdict[eth_path[0]][eth_path[1]], dict)
            except (AssertionError, KeyError):
                intdict[eth_path[0]][eth_path[1]] = {}
            
            intdict[eth_path[0]][eth_path[1]].update({eth_path[2]: thisint})


    return intdict
