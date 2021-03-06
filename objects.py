from typing import List, Optional, Tuple
import more_itertools as mit


class Interface():
    def __init__(self, name: str, **kwargs):
        self.name: str = name
        self.description: Optional[str] = None
        self.ismember: bool = False
        self.protocol: Optional[str] = None
        self.channel_group: Optional[int]
        # TODO: Change to Set
        self.allowed_vlan: List[int] = []
        self.native_vlan: Optional[int] = None
        self.cage: Optional[str]
        self.switch: Optional[int]
        self._newname: str = ""
        self.leaf: Tuple[int] = kwargs.get("leaf", None)
        self.card: int = kwargs.get("card", None)
        self.port: range = kwargs.get("port", None)
        self.is_superseeded: bool = False
        self.intstatus: str = ""
        self.speed: str = ""
        self.adapter: str = ""

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

    def set_newname(self, newname: str, **kwargs):
        leaf = kwargs.get("leaf", None)
        card = kwargs.get("card", None)
        port = kwargs.get("port", None)

        self._newname = newname

        if leaf is not None and card is not None and port is not None:
            self.leaf = leaf
            self.card = card
            self.port = port
        else:
            leaf, card, port = newname.split("/")

            self.leaf = (int(leaf),)

            self.card = int(card)

            if "-" in port:
                from_port, to_port = port.split("-")
                self.port = range(int(from_port), int(to_port)+1)
            else:
                self.port = range(int(port), int(port)+1)

    def get_newname(self):
        leaf = str(self.leaf[0])

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

                if self.native_vlan is None:
                    try:
                        self.native_vlan = member.native_vlan
                    except AttributeError:
                        pass
                else:
                    try:
                        self.native_vlan = member.native_vlan
                    except AttributeError:
                        pass
                    assert self.native_vlan == member.native_vlan

                if self.protocol is None:
                    try:
                        self.protocol = member.protocol
                    except AttributeError:
                        pass

                if self.description is None:
                    try:
                        self.description = member.description
                    except AttributeError:
                        pass

                member.ismember = True

                self.leaf = member.leaf

    def set_newname(self, newname: str, **kwargs):
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
                port_ranges.append(range(group[0], group[-1]+1))

        newmembers = []

        # Tag old interfaces as superseeded
        for member in self.members:
            member.is_superseeded = True

        for port_range in port_ranges:
            newint = Interface("generatedrange")
            newint.ismember = True
            newint.set_newname("generated", leaf=self.leaf,
                               card=1, port=port_range)
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
            raise ValueError(
                f"One of the members of {self.name} is not on the same leaf as others: {[str(x) for x in self.members]}")
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
                        aggport = Interface("generatedrange")
                        aggport.ismember = True
                        aggport.set_newname("generated", leaf=(
                            po1_leaf[0], po2_leaf[0]), card=1, port=po1_member.port)
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

        allinterfaces = allinterfaces + \
            self.members[0].members + self.members[1].members

        for interface in allinterfaces:
            interface.description = self._newname

        self.members = allinterfaces
