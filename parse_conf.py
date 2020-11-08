import csv
import pickle
from objects import Interface, PortChannel, Vpc
from libs import parse_nexus_pair_l2
from filelist import entiredc
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
    # We don't care about members of other objects
    if i.ismember:
        continue
    elif type(i) == PortChannel and len(i.members) == 0:
        continue
    elif type(i) == Vpc and (len(i.members[0].members) + len(i.members[1].members) == 0):
        continue
    else:
        thisint = {"newname": "",
                   "vpc": "",
                   "portchannel": "",
                   "name": str(i),
                   "description": i.description if i.description is not None else ""}
        allintdata.append(thisint)

    if type(i) == PortChannel and not i.ismember:
        for member in i.members:
            thisint = {"newname": "",
                       "vpc": "",
                       "portchannel": str(i),
                       "name": str(member),
                       "description": member.description if member.description is not None else ""}
            allintdata.append(thisint)

    elif type(i) == Vpc:
        for pomember in i.members:
            for member in pomember.members:
                thisint = {"newname": "",
                           "vpc": str(i),
                           "portchannel": str(pomember),
                           "name": str(member),
                           "description": member.description if member.description is not None else ""}
                allintdata.append(thisint)
    


with open("intnames.csv", "w") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=[
        "name", "vpc", "portchannel", "description", "newname"])
    writer.writeheader()
    writer.writerows(allintdata)


with open("tempdata.bin", "wb") as tempdata:
    pickle.dump(parseddc, tempdata)

generate_excel()
