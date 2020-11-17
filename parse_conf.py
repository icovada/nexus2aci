import csv
import pickle
from objects import Interface, PortChannel, Vpc
from libs import parse_nexus_pair_l2, parse_show_interface_status
from filelist import entiredc
from helpers.generate_excel import generate_excel


parseddc = []

for k, v in entiredc.items():
    parseddc = parseddc + parse_nexus_pair_l2(v['conf'][0], v['conf'][1], k)

for interface in parseddc:
    try:
        interface.inherit()
    except AttributeError:
        pass

for k, v in entiredc.items():
    if "intstatus" in v:
        parse_show_interface_status(parseddc, k, 1, v['intstatus'][0])
        parse_show_interface_status(parseddc, k, 2, v['intstatus'][1])
    

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
                   "description": i.description if i.description is not None else "",
                   "speed": i.speed,
                   "status": i.intstatus,
                   "adapter": i.adapter}
        allintdata.append(thisint)

    if type(i) == PortChannel and not i.ismember:
        for member in i.members:
            thisint = {"newname": "",
                       "vpc": "",
                       "portchannel": str(i),
                       "name": str(member),
                       "description": member.description if member.description is not None else "",
                       "speed": member.speed,
                       "status": member.intstatus,
                       "adapter": i.adapter}
            allintdata.append(thisint)

    elif type(i) == Vpc:
        for pomember in i.members:
            for member in pomember.members:
                thisint = {"newname": "",
                           "vpc": str(i),
                           "portchannel": str(pomember),
                           "name": str(member),
                           "description": member.description if member.description is not None else "",
                           "speed": member.speed,
                           "status": member.intstatus,
                           "adapter": i.adapter}
                allintdata.append(thisint)
    


with open("intnames.csv", "w") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=[
        "name", "vpc", "portchannel", "description", "status", "speed", "adapter", "newname"])
    writer.writeheader()
    writer.writerows(allintdata)


with open("tempdata.bin", "wb") as tempdata:
    pickle.dump(parseddc, tempdata)

generate_excel()
