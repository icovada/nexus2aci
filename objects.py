from typing import List, Optional
import more_itertools as mit

class Interface():
    def __init__(self, name: str, **kwargs):
        self.name: str = name
        self.description: Optional[str]
        self.ismember: bool = False
        self.protocol: Optional[str]
        self.channel_group: Optional[int]
        self.native_vlan: int
        # TODO: Change to Set
        self.allowed_vlan: List[int] = []
        self.cage: Optional[str]
        self.switch: Optional[int]
        self._newname: str = ""
        self.leaf = kwargs.get("leaf", None)
        self.card = kwargs.get("card", None)
        self.port = kwargs.get("port", None)
        self.is_superseeded = False

    def __str__(self) -> str:
        outname = self.name

        if hasattr(self, "switch"):
            outname = str(self.switch) + "/" + outname

        if hasattr(self, "cage"):
            outname = self.cage + "/" + outname

        return outname

    def allowed_vlan_add(self, newvlans: List[int]):
        self.allowed_vlan = self.allowed_vlan + newvlans

    def is_useful(self) -> bool:
        if len(self.__dict__) == 1:
            return False
        else:
            return True

    def set_newname(self, newname: str):
        self._newname = newname
        leaf, card, port = newname.split("/")

        if "," in leaf:
            leafa, leafb = leaf.split(",")
            self.leaf = (int(leafa), int(leafb))
        else:
            self.leaf = (int(leaf),)

        self.card = int(card)

        if "-" in port:
            from_port, to_port = port.split("-")
            self.port = range(int(from_port), int(to_port)+1)
        else:
            self.port = range(int(port), int(port)+1)

    def get_newname(self):
        if len(self.leaf) == 1:
            leaf = str(self.leaf[0])
        else:
            leaf = "(" + str(self.leaf[0]) + "," + str(self.leaf[1]) + ")"

        card = str(self.card)

        if len(self.port) == 1:
            port = str(self.port[0])
        else:
            port = str(self.port[0]) + "-" + str(self.port[-1])

        return leaf + "/" + card + "/" + port

    def has_newname(self):
        if self._newname == "":
            return False
        else:
            return True


class PortChannel(Interface):

    def __init__(self, name: str):
        self.vpc: Optional[int]
        self.po_id: int
        self.members: List[Interface]
        if type(self) == PortChannel:
            # Do not run if we are being subclassed
            self.po_id = int(name[12:])
        super().__init__(name)

    def is_useful(self) -> bool:
        # If has no members, it's useless
        if hasattr(self, "members"):
            if len(self.members) > 0:
                return True
            else:
                return False
        else:
            return False

    def inherit(self):
        for member in self.members:
            if member.has_newname():
                for vlan in member.allowed_vlan:
                    if vlan not in self.allowed_vlan:
                        self.allowed_vlan_add([vlan, ])
    
                if not hasattr(self, "native_vlan"):
                    self.native_vlan = member.native_vlan
                else:
                    assert self.native_vlan == member.native_vlan
    
                if not hasattr(self, "protocol"):
                    self.protocol = member.protocol
                else:
                    assert self.protocol == member.protocol
    
                if not hasattr(self, "description"):
                    self.description = member.description
    
                member.ismember = True
    
                self.leaf = member.leaf

    def set_newname(self, newname: str):
        self._newname = newname

    def get_newname(self):
        return self._newname

    def find_groups(self):
        po_allports = []
        for member in self.members:
            if member.has_newname():
                po_allports = po_allports + [x for x in member.port]

        # Black magic from https://stackoverflow.com/questions/2154249/identify-groups-of-continuous-numbers-in-a-list/47642650
        port_ranges: List[range] = []
        for group in mit.consecutive_groups(po_allports):
            group = list(group)
            if len(group) == 1:
                port_ranges.append(range(group[0], group[0]+1))
            else:
                port_ranges.append(range(group[0], group[-1]))

        newmembers = []

        # Tag old interfaces as superseeded
        for member in self.members:
            member.is_superseeded = True

        for port_range in port_ranges:
            newint = Interface("generatedrange", leaf=self.leaf, card=1, port=port_range)
            newint.ismember = True
            newint.set_newname("generated")
            newint.description = self._newname
            newmembers.append(newint)

        self.members = newmembers


    def check_members(self):
        leavesset = set()
        if self.is_useful():
            for member in self.members:
                if member.has_newname():
                    leavesset.add(member.leaf)

        if len(leavesset) == 0:
            return None
        if len(leavesset) > 1:
            raise ValueError(f"One of the members of {self.name} is not on the same leaf as others: {[str(x) for x in self.members]}")
        else:
            return leavesset.pop()



class Vpc(PortChannel):
    def __init__(self, vpcid: int):
        self.vpcid = vpcid
        self.members: List[PortChannel] = []
        name = "vpc" + str(vpcid)
        super().__init__(name)

    def __str__(self) -> str:
        outname = self.name

        if hasattr(self, "cage"):
            outname = self.cage + "/" + outname

        return outname

    def check_members(self):
        leavesset = set()
        if len(self.members) != 2:
            raise ValueError(f"{self.name} does not have exactly two members")
        for member in self.members:
            memberleaf = member.check_members()
            leavesset.add(memberleaf)

        if len(leavesset) != 2:
            raise ValueError(f"{self.name} does not span exactly two leaves")


    def find_groups(self):
        po1_leaf = self.members[0].leaf
        po2_leaf = self.members[1].leaf

        allinterfaces = []
        match_found = True
        # Cycle through all pairs of interfaces, remove them as found, continue until no pairs are left
        while match_found:
            for po1_member in [x for x in self.members[0].members]:
                for po2_member in [x for x in self.members[1].members]:
                    if po1_member.port == po2_member.port:
                        aggport = Interface("generatedrange", leaf=(po1_leaf, po2_leaf), card=1, port=po1_member.port)
                        aggport.ismember = True
                        aggport.set_newname("generated")
                        aggport.description = self._newname
                        allinterfaces.append(aggport)
                        match_found = True
                        po1_member.is_superseeded = True
                        po2_member.is_superseeded = True
                        self.members[0].members.remove(po1_member)
                        self.members[1].members.remove(po2_member)
                        # Only one possible pair per run
                        break
                    else:
                        match_found = False

                match_found = False
                break

        self.members[0].is_superseeded = True
        self.members[1].is_superseeded = True

        allinterfaces = allinterfaces + self.members[0].members + self.members[1].members

        self.members = allinterfaces

