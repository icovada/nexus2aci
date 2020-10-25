from typing import List, Optional

class Interface():
    description:Optional[str]
    ismember:bool = False
    protocol:Optional[str] = ""
    channel_group:Optional[int]
    native_vlan:int = 1
    allowed_vlan:Optional[List[int]] = []

    def __init__(self, name:str):
        self.name = name

    def allowed_vlan_add(self, newvlans:List[int]):
        self.allowed_vlan = self.allowed_vlan + newvlans
    
    def is_useless(self) -> bool:
        if len(self.__dict__) == 1:
            return True
        else:
            return False

class PortChannel(Interface):
    vpc:Optional[int]
    po_id:int
    members:List[Interface]

    def __init__(self, name:str):
        print(type(self))
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

class Vpc(PortChannel):
    def __init__(self, vpcid:int):
        self.vpcid = vpcid
        name = "vpc" + str(vpcid)
        super().__init__(name)