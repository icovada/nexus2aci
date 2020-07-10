import unittest

from helpers import allowed_vlan_to_list
from helpers import parse_vlan_l2


class TestAllowedVlanToList(unittest.TestCase):

    def test_only_commas(self):
        test_data = "1,2,3,4,5"
        output = (1, 2, 3, 4, 5)
        assert allowed_vlan_to_list(test_data) == output

    def test_only_ranges(self):
        test_data = "1-5"
        output = (1, 2, 3, 4, 5)
        assert allowed_vlan_to_list(test_data) == output

    def test_comma_and_range(self):
        test_data = "1,2,3-5"
        output = (1, 2, 3, 4, 5)
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

        output = {3: {"name": "FRONT-END"},
                  4: {"name": "EX_CED_SDM"},
                  6: {"name": "Back_End-New"},
                  9: {"name": "Front-End-NEW"}}

        assert parse_vlan_l2(test_data) == output

    def test_parse_vlan_l2_no_name(self):
        config = ["vlan 3"]

        test_data = self.CiscoConfParse(config)

        output = {3: {}}

        assert parse_vlan_l2(test_data) == output


    def test_parse_vlan_l2_name_in_name(self):
        config = ["vlan 3",
                  "  name name",
                  "vlan 4",
                  "  name anothername"]

        test_data = self.CiscoConfParse(config)

        output = {3: {"name": "name"},
                  4: {"name": "anothername"}}

        assert parse_vlan_l2(test_data) == output


if __name__ == '__main__':
    unittest.main()
