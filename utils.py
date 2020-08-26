def traverse_dict(dict, path):
    """gets a value in nested dictionaries across path"""
    if len(path) == 1:
        return dict[path[0]]
    else:
        return traverse_dict(dict[path[0]], path[1:])


def find_key(d, value):
    for k, v in d.items():
        if isinstance(v, dict):
            p = find_key(v, value)
            if p:
                return [k] + p
        elif v == value:
            return [k]


def flatten(fabric, newfabric={}, prefix=""):
    for k, v in fabric.items():
        if not isinstance(v, dict) or len(v) == 0:
            return "end"

        if prefix == "":
            thisprefix = str(k)
        else:
            thisprefix = prefix + "/" + str(k)

        deeper = flatten(v, newfabric, thisprefix)
        if deeper == "end":
            newfabric[thisprefix] = v

    return newfabric
