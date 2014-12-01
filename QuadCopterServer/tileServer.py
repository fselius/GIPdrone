__author__ = 'Ohad'


import flask
import os


def create_path(tile_type, x, y, z):
    path = os.path.join('MapCache', tile_type, z, x)
    if not os.path.exists(path):
        os.makedirs(path)
    return '{0}/{1}.jpg'.format(path, y)


def load_to_cache(tile_type, x, y, z):
    file_path = create_path(tile_type, x, y, z)
    if os.path.exists(file_path):
        return
    print ('Tile ' + x + ', ' + y + ', ' + z + ' not found, fetching...')
    #old_url = '{0}/{1}/{2}/{3}/{4}.jpg'.format(settings.tileServer, tile_type, z, x, y)
    url = 'https://khms0.google.com/kh/v=162&src=app&expIds=201527&rlbl=1&x={1}&s=&y={2}&z={0}&s=G'.format(z, x, y)
    import urllib2
    try:
        response = urllib2.urlopen(url)
        if response.code == 200:
            with open(file_path, 'wb') as local_file:
                local_file.write(response.read())
    except Exception, e:
        print e


def get_tile(tile_type, x, y, z):
    load_to_cache(tile_type, x, y, z)
    try:
        return flask.send_file(create_path(tile_type, x, y, z), mimetype='image/jpg')
    except Exception, e:
        return "File not Found" + e