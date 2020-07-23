import unittest

from helpers import allowed_vlan_to_list
from helpers import parse_vlan_l2
from helpers import parse_svi
from helpers import parse_physical_interface


class TestAllowedVlanToList(unittest.TestCase):

    def test_only_commas(self):
        test_data = "1,2,3,4,5"
        output = [1, 2, 3, 4, 5]
        assert allowed_vlan_to_list(test_data) == output

    def test_only_ranges(self):
        test_data = "1-5"
        output = [1, 2, 3, 4, 5]
        assert allowed_vlan_to_list(test_data) == output

    def test_comma_and_range(self):
        test_data = "1,2,3-5"
        output = [1, 2, 3, 4, 5]
        assert allowed_vlan_to_list(test_data) == output


class TestParseVlanL2(unittest.TestCase):
    from ciscoconfparse import CiscoConfParse

    def test_parse_vlan_l2(self):
        config = ["vlan 3",
                  "  name FRONT-END",
                  "vlan 4",
                  "  name EX_CED_SDM",
                  "vlan 6",
                  "  name Back-End-New",
                  "vlan 9",
                  "  name Front-End-NEW"]

        test_data = self.CiscoConfParse(config)

        output = {1: {},
                  3: {"name": "FRONT-END"},
                  4: {"name": "EX_CED_SDM"},
                  6: {"name": "Back-End-New"},
                  9: {"name": "Front-End-NEW"}}

        assert parse_vlan_l2(test_data) == output

    def test_parse_vlan_l2_no_name(self):
        config = ["vlan 3"]

        test_data = self.CiscoConfParse(config)

        output = {1: {},
                  3: {}}

        assert parse_vlan_l2(test_data) == output

    def test_parse_vlan_l2_name_in_name(self):
        config = ["vlan 3",
                  "  name name",
                  "vlan 4",
                  "  name anothername"]

        test_data = self.CiscoConfParse(config)

        output = {1: {},
                  3: {"name": "name"},
                  4: {"name": "anothername"}}

        assert parse_vlan_l2(test_data) == output


class TestParseSVI(unittest.TestCase):
    from ciscoconfparse import CiscoConfParse

    def test_parse_svi(self):
        config = ["vlan 3",
                  "  name FRONT-END",
                  "vlan 4",
                  "  name EX_CED_SDM",
                  "",
                  "interface Vlan3",
                  "  vrf member VRF-VINTAGE",
                  "  no ip redirects",
                  "  ip address 172.26.54.41/26",
                  "  hsrp version 2",
                  "  hsrp 3 ",
                  "    authentication md5 key-chain hsrp-vintage",
                  "    priority 150",
                  "    timers  5  15",
                  "    ip 172.26.54.62 ",
                  "  description SRG-FRONT-END_NEW_SYS-SAT-CMS-W2K",
                  "  no shutdown",
                  "",
                  "interface Vlan4",
                  "  vrf member VRF-VINTAGE",
                  "  no ip redirects",
                  "  ip address 172.22.178.110/22",
                  "  hsrp version 2",
                  "  hsrp 4 ",
                  "    authentication md5 key-chain hsrp-vintage",
                  "    priority 150",
                  "    timers  5  15",
                  "    ip 172.22.176.9 ",
                  "  description ***VLAN_CED_CAVASSI***",
                  "  no shutdown"]

        test_data = self.CiscoConfParse(config)

        output = {1: {},
                  3: {"name": "FRONT-END",
                      "vrf": "VRF-VINTAGE",
                      "l3": {"ip_address": "172.26.54.62",
                             "netmask": "255.255.255.192",
                             "shutdown": False},
                      "description": "SRG-FRONT-END_NEW_SYS-SAT-CMS-W2K",
                      },
                  4: {"name": "EX_CED_SDM",
                      "vrf": "VRF-VINTAGE",
                      "l3": {"ip_address": "172.22.176.9",
                             "netmask": "255.255.252.0",
                             "shutdown": False},
                      "description": "***VLAN_CED_CAVASSI***",
                      }}

        assert parse_svi(test_data) == output

    def test_parse_svi_no_hsrp(self):
        config = ["vlan 3",
                  "  name FRONT-END",
                  "",
                  "interface Vlan3",
                  "  vrf member VRF-VINTAGE",
                  "  no ip redirects",
                  "  ip address 172.26.54.41/26",
                  "  description SRG-FRONT-END_NEW_SYS-SAT-CMS-W2K",
                  "  no shutdown"]

        test_data = self.CiscoConfParse(config)

        output = {1: {},
                  3: {"name": "FRONT-END",
                      "vrf": "VRF-VINTAGE",
                      "l3": {"ip_address": "172.26.54.41",
                             "netmask": "255.255.255.192",
                             "shutdown": False},
                      "description": "SRG-FRONT-END_NEW_SYS-SAT-CMS-W2K",
                      }}
        assert parse_svi(test_data) == output

    def test_parse_svi_shutdown(self):
        config = ["vlan 3",
                  "  name FRONT-END",
                  "",
                  "interface Vlan3",
                  "  vrf member VRF-VINTAGE",
                  "  no ip redirects",
                  "  ip address 172.26.54.41/26",
                  "  description SRG-FRONT-END_NEW_SYS-SAT-CMS-W2K",
                  "  shutdown"]

        test_data = self.CiscoConfParse(config)

        output = {1: {},
                  3: {"name": "FRONT-END",
                      "vrf": "VRF-VINTAGE",
                      "l3": {"ip_address": "172.26.54.41",
                             "netmask": "255.255.255.192",
                             "shutdown": True},
                      "description": "SRG-FRONT-END_NEW_SYS-SAT-CMS-W2K",
                      }}
        assert parse_svi(test_data) == output

    def test_parse_svi_no_vrf(self):
        config = ["vlan 3",
                  "  name FRONT-END",
                  "",
                  "interface Vlan3",
                  "  no ip redirects",
                  "  ip address 172.26.54.41/26",
                  "  description SRG-FRONT-END_NEW_SYS-SAT-CMS-W2K",
                  "  no shutdown"]

        test_data = self.CiscoConfParse(config)

        output = {1: {},
                  3: {"name": "FRONT-END",
                      "vrf": "default",
                      "l3": {"ip_address": "172.26.54.41",
                             "netmask": "255.255.255.192",
                             "shutdown": False},
                      "description": "SRG-FRONT-END_NEW_SYS-SAT-CMS-W2K",
                      }}
        assert parse_svi(test_data) == output

    def test_parse_svi_no_ip(self):
        config = ["interface Vlan1",
                  "  no ip redirects",
                  "  no ipv6 redirects"]

        test_data = self.CiscoConfParse(config)

        output = {1: {"vrf": "default",
                      "l3": {"shutdown": False},
                      }}
        assert parse_svi(test_data) == output


class TestParsePhyInt(unittest.TestCase):
    from ciscoconfparse import CiscoConfParse

    def test_access_port(self):
        config = ["interface Ethernet100/1/8",
                  "  description SNSV01021_nic0_3",
                  "  switchport access vlan 300",
                  "  spanning-tree port type edge",
                  "  no shutdown"]

        test_data = self.CiscoConfParse(config)

        output = {100: {1: {8: {"description": "SNSV01021_nic0_3",
                                "native_vlan": 300
                                }}}}

        assert parse_physical_interface(test_data) == output

    def test_trunk_port(self):
        config = ["interface Ethernet100/1/8",
                  "  switchport mode trunk",
                  "  switchport trunk allowed vlan 300-302,303",
                  "  no shutdown"]

        test_data = self.CiscoConfParse(config)

        output = {100: {1: {8: {"allowed_vlan": [300, 301, 302, 303],
                                }}}}

        assert parse_physical_interface(test_data) == output

if __name__ == '__main__':
    unittest.main()
