"Define standard objects"
tenant = {'name': '',
          'description': '',
          'app': [],
          'bd': [],
          'vrf': [],
          'contract': [],
          'protocol_policy': {}}

app = {'name': '',
       'epg': []}

epg = {'name': '',
       'bd': '',
       'contract': [],
       'static_path': [],
       'domain': []}

bd = {'name': '',
      'subnet': [],
      'vrf': ''}



def INTERFACE_SELECTOR_ACCESS(name):
       return f"access_{name}_IntSel"

def INTERFACE_SELECTOR_BUNDLE(bundlemode, name):
       return f"{bundlemode}_GDC_{name}_IntSel"

def INTERFACE_SELECTOR_PROFILE(leaves):
       return f"Leaf-{'-'.join([str(x) for x in leaves])}_IntProf"

def LEAF_PROFILE(leaves):
       return f"Leaf-{'-'.join([str(x) for x in leaves])}_LeafProf"

def LEAF_SELECTOR(leaves):
       return f"Leaf-{'-'.join([str(x) for x in leaves])}_SwSel"

def POLICY_GROUP_BUNDLE(bundlemode, name):
       return f"{bundlemode}_GDC_{name}_PolGrp"
       
POLICY_GROUP_ACCESS = f"access_SRV_1G-auto_PolGrp"
UNSAFE_CHARACTER_REPLACE = {"&": "_e_",}