from typing import List, Optional

class Interface():
    description:Optional[str]
    ismember:bool = False
    protocol:Optional[str] = ""
    channel_group:Optional[int]
    native_vlan:int = 1
    allowed_vlan:Optional[List[int]] = []

    def __init__(self, name:str):
        print(type(self))
        self.name = name

    def allowed_vlan_add(self, newvlans:List[int]):
        self.allowed_vlan = self.allowed_vlan + newvlans

class PortChannel(Interface):
    vpc:int = 0
    members = []

class Vpc(PortChannel):
    def __init__(self, name:str, vpcid:int):
        self.vpcid = vpcid
        print(type(self))
        super().__init__(name)