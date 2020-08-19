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
sw1_switched = sw1.find_objects_w_child(r"interface ([A-Za-z\-]*)", "switchport")
sw2_switched = sw2.find_objects_w_child(r"interface ([A-Za-z\-]*)", "switchport")

# This will hold information about all the switches in the DC, organised in pairs
# [{300: {}, 301: {}}, {302: {}, 303:{}}]
swpair = []
allint = {'switch': {}, 'fex': {}}
sw1_parsed = parse_switched_interface(sw1_switched)
allint['switch'][300] = sw1_parsed['local']
allint['fex'].update(sw1_parsed['fex'])

sw2_parsed = parse_switched_interface(sw2_switched)
allint['switch'][301] = sw2_parsed['local']
allint['fex'].update(sw2_parsed['fex'])


swpair.append(allint)

with open("l3.yml","w") as f:
    f.write(yaml.dump(agg_l3))

with open("out.yml", "w") as f:
    f.write(yaml.dump(swpair))
