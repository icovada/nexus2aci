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

POLICY_GROUP_ACCESS = {"1000": "access_SRV_1G-auto_PolGrp",
                       "10G": "access_SRV_10G-auto_PolGrp"}

UNSAFE_CHARACTER_REPLACE = {"&": "_e_",
                            " ": "_"}

def xlate_policy_group_bundle_int_selector_name(polgroup):
    if "PolGrp" in polgroup:
        intselname = polgroup.replace("PolGrp", "IntSel")
    else:
        intselname = polgroup + "_IntSel"
    return intselname