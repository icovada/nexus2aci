import ciscoconfparse
import yaml
from helpers import *

# parse configs for access and distribution switches
# you should theoretically add all switches in the DC
sw1 = ciscoconfparse.CiscoConfParse('SWISNA-NGDC5K-L1.log')
sw2 = ciscoconfparse.CiscoConfParse('SWISNA-NGDC5K-L2.log')
aggregation = ciscoconfparse.CiscoConfParse('AGGSNANGDC-1.txt')

# Combine info for VLANs for all switches.
# Just one switch could do, but why not showing off?
sw1_l2 = parse_vlan_l2(sw1)
sw2_l2 = parse_vlan_l2(sw2, sw1_l2)
l2dict = parse_vlan_l2(aggregation, sw2_l2)

# Combine info from all layer3 switches, passing in the vlan info from the previous step
sw1_l3 = parse_svi(sw1, l2dict)
sw2_l3 = parse_svi(sw2, sw1_l3)
agg_l3 = parse_svi(aggregation, sw1_l3)


# Filter all switched interfaces from access switches
sw1_switched = sw1.find_objects(r"interface (port-channel|Ethernet).*")
sw2_switched = sw2.find_objects(r"interface (port-channel|Ethernet).*")

# This will hold information about all the switches in the DC, organised in pairs
# [{300: {}, 301: {}}, {302: {}, 303:{}}]
swpair = []
sw1_parsed = parse_switched_interface(sw1_switched, 1, l2dict)
sw2_parsed = parse_switched_interface(sw2_switched, 2, l2dict, sw1_parsed)


cage_config = match_vpc(sw2_parsed)




# # Check config matches on both sides. Raise exception if misaligned
# # Note: disregards descriptions and members
# for k, v in cage_config[1]['port-channel'].items():
#     if 'vpc' in v and 'vpc' in cage_config[2]['port-channel'][k]:
#         if v['vpc'] == cage_config[2]['port-channel'][k]['vpc']:
#             for k2, v2 in v.items():
#                 if not k2.endswith(('description', 'members')):
#                     try:
#                         assert v2 == cage_config[2]['port-channel'][k][k2]
#                     except AssertionError:
#                         print(f"Warning, vpc {v['vpc']} {k2} does not match on both switches")


swpair.append(sw2_parsed)

out = {'fabric': swpair,
       'network': agg_l3}

with open("out.yml", "w") as f:
    f.write(yaml.dump(cage_config))
