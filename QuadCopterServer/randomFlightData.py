__author__ = 'Ohad'

lat_long_delta = 0.0005

delta = {'lat':         0.0005,
         'long':        0.0005,
         'height':      5,
         'orientation': 20,
         'battery':     1}

data = {'lat':          35.01574,
        'long':         32.77849,
        'height':       90,
        'orientation':  0,
        'battery':      100}


def get_data():
    import random
    for key in data:
        data[key] = random.uniform(data[key]-delta[key], data[key]+delta[key])
    return data
