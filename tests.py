from helpers import allowed_vlan_to_list
import unittest


class Test_allowed_vlan_to_list(unittest.TestCase):
    
    def test_only_commas(self):
        test_data = "1,2,3,4,5"
        result = (1,2,3,4,5)
        
        returns = allowed_vlan_to_list(test_data)
        assert returns == result

    def test_only_ranges(self):
        test_data = "1-5"
        result = (1,2,3,4,5)

        returns = allowed_vlan_to_list(test_data)
        assert returns == result

    def test_comma_and_range(self):
        test_data = "1,2,3-5"
        result = (1,2,3,4,5)

        returns = allowed_vlan_to_list(test_data)
        assert returns == result
