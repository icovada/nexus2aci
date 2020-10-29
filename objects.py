from typing import List, Optional


class Interface():

    def __init__(self, name: str):
        self.name = name
        self.description: Optional[str]
        self.ismember: bool = False
        self.protocol: Optional[str]
        self.channel_group: Optional[int]
        self.native_vlan: int
        # TODO: Change to Set
        self.allowed_vlan:Optional[List[int]] = []
        self.cage:Optional[str]
        self.switch:Optional[int]

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
