import ciscoconfparse
import yaml
from helpers import *

sw1 = ciscoconfparse.CiscoConfParse('SWISNA-NGDC5K-L1.log')
sw2 = ciscoconfparse.CiscoConfParse('SWISNA-NGDC5K-L2.log')
aggregation = ciscoconfparse.CiscoConfParse('AGGSNANGDC-1.txt')


sw1_switched = sw1.find_objects_w_child(r"interface ([A-Za-z\-]*)", "switchport")
sw2_switched = sw2.find_objects_w_child(r"interface ([A-Za-z\-]*)", "switchport")
aggsvi = parse_svi(aggregation)
sw1_parsed = parse_switched_interface(sw1_switched)

with open("l3.yml","w") as f:
    f.write(yaml.dump(aggsvi))

with open("out.yml", "w") as f:
    f.write(yaml.dump(sw1_parsed))
