from objects import PortChannel, Vpc
import yaml
from libs import parse_nexus_pair_l2
from filelist import entiredc
import csv
import pickle
from helpers.generate_excel import generate_excel


parseddc = []

for k, v in entiredc.items():
    parseddc = parseddc + parse_nexus_pair_l2(v[0], v[1], k)

for interface in parseddc:
    try:
        interface.inherit()
    except AttributeError:
        pass


# Export interface names for renaming
allintdata = []
for i in parseddc:
    if type(i) == PortChannel:
        if i.ismember:
            continue
    thisint = {"newname": "",
               "name": str(i),
               "description": i.description if hasattr(i, "description") else ""}
    allintdata.append(thisint)


with open("intnames.csv", "w") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=[
                            "name", "description", "newname"])
    writer.writeheader()
    writer.writerows(allintdata)


with open("tempdata.bin", "wb") as tempdata:
    pickle.dump(parseddc, tempdata)

generate_excel()
