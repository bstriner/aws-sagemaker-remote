
def get_field(data, field):
    if field:
        path = field.split('.')
        for p in path:
            if p not in data:
                raise ValueError("Field does not exist: [{}]".format(field))
            data = data[p]
    return data
