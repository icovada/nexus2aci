def traverse_dict(dict, path):
    """gets a value in nested dictionaries across path"""
    if len(path) == 0:
        return dict
    else:
        return traverse(dict[path