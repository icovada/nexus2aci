import yaml
from libs import *

# parse configs for access and distribution switches
# you should theoretically add all switches in the DC

entiredc = {'agg': parse_nexus_pair_l2('AGGSNANGDC-1.nxos', 'AGGSNANGDC-1.nxos'),
            'aggp': parse_nexus_pair_l2('AGGSNANGDCP-1.nxos', 'AGGSNANGDCP-2.nxos'),
            'core': parse_nexus_pair_l2('CORESNANGDC-1.nxos', 'CORESNANGDC-2.nxos'),
            'core': parse_nexus_pair_l2('CORESNANGDC-1.nxos', 'CORESNANGDC-2.nxos'),
            'H1-2': parse_nexus_pair_l2('SWISNA-NGDC5K-H1.nxos', 'SWISNA-NGDC5K-H2.nxos'),
            'H3-4': parse_nexus_pair_l2('SWISNA-NGDC5K-H3.nxos', 'SWISNA-NGDC5K-H4.nxos'),
            'L1-2': parse_nexus_pair_l2('SWISNA-NGDC5K-L1.nxos', 'SWISNA-NGDC5K-L2.nxos'),
            'L3-4': parse_nexus_pair_l2('SWISNA-NGDC5K-L3.nxos', 'SWISNA-NGDC5K-L4.nxos'),
            'L5-6': parse_nexus_pair_l2('SWISNA-NGDC5K-L5.nxos', 'SWISNA-NGDC5K-L6.nxos'),
            }


flat = flatten_dict(entiredc)

with open('entiredc.yml', 'w') as f:
    f.write(yaml.dump(flat))


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
