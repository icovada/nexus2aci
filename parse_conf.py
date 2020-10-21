import yaml
from libs import *
from filelist import entiredc
import csv
import pickle
from helpers.generate_excel import generate_excel


parseddc = {}
for k, v in entiredc.items():
    parseddc[k] = parse_nexus_pair_l2(v[0], v[1])

flat = flatten_dict(parseddc)

consolidate_interfaces(flat, "port-channel")
consolidate_interfaces(flat, "vpc")

# Data at this point looks like this:

# {'description': 'VERSO_CORESNANGDC-1_E_2',
#  'ismember': True,
#  'members': [{'ismember': True, 'name': 'agg/1/Ethernet7/2'},
#              {'ismember': True, 'name': 'agg/1/Ethernet8/2'},
#              {'ismember': True, 'name': 'agg/1/Ethernet9/2'},
#              {'description': 'CORESNANGDC-2',
#               'ismember': True,
#               'name': 'agg/1/Ethernet10/2'}],
#  'name': 'agg/1/port-channel105',
#  'vpc': 105}

# Export interface names for renaming
allintdata = []
for i in flat:
    if "port-channel" in i['name']:
        if 'ismember' in i:
            continue
    thisint = {"newname": ""}
    thisint.update({"name": i.get("name", "")})
    thisint.update({"description": i.get("description", "")})

    allintdata.append(thisint)


with open("intnames.csv", "w") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=[
                            "name", "description", "newname"])
    writer.writeheader()
    writer.writerows(allintdata)


with open("tempdata.bin", "wb") as tempdata:
    pickle.dump(flat, tempdata)

generate_excel()
