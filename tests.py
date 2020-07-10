import unittest

from helpers import allowed_vlan_to_list


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

if __name__ == '__main__':
    unittest.main()