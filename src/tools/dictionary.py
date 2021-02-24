import copy


def merge_dicts(target, source):
    if source is None:
        return
    if target is None:
        target = source
        return

    for k, v in source.items():
        if type(v) == list:
            if k not in target:
                target[k] = copy.deepcopy(v)
            else:
                target[k].extend(v)
        elif type(v) == dict:
            if k not in target:
                target[k] = copy.deepcopy(v)
            else:
                merge_dicts(target[k], v)
        elif type(v) == set:
            if k not in target:
                target[k] = v.copy()
            else:
                target[k].update(v.copy())
        else:
            target[k] = copy.copy(v)


def filter_keys(data, keys=[]):
    """
    Exclude keys from dictionary recursively.
    """
    # filter key
    for filter_key in keys:
        if filter_key in data:
            del data[filter_key]

    # filter sub dictionaries
    for _, value in data.items():
        if type(value) == dict:
            filter_keys(value, keys)
