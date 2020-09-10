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


UNSAFE_CHARACTER_REPLACE = {"&": "_e_",}

INTERFACE_SELECTOR_ACCESS = f"access_{name}_IntSel"
INTERFACE_SELECTOR_BUNDLE = f"{bundlemode}_GDC_{name}_IntSel"
INTERFACE_SELECTOR_PROFILE = f"Leaf-{'-'.join([str(x) for x in leaves])_IntProf}"
LEAF_PROFILE = f"Leaf-{'-'.join([str(x) for x in leaves])_LeafProf}"
LEAF_SELECTOR = f"Leaf-{'-'.join([str(x) for x in leaves])_SwSel}"

POLICY_GROUP_BUNDLE = f"{bundlemode}_GDC_{name}_PolGrp"
POLICY_GROUP_ACCESS = f"access_SRV_1G-auto_PolGrp"