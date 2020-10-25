from typing import List

class Interface():
    description:str = ""
    ismember:bool = False
    protocol:str = ""
    channel_group:int = 0
    native_vlan:int = 1
    allowed_vlan:List[int] = []

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