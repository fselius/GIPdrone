__author__ = 'Aviad Rom'
from flask import Flask, url_for, request, jsonify, redirect

app = Flask(__name__)
#app.debug = True

mock_data = {'1': {'waypoint': 1, 'lat': 30.12345, 'lon': 32.234234, 'height': 30.3, 'orientation': 95},
             '2': {'waypoint': 2, 'lat': 30.12345, 'lon': 32.234234, 'height': 30.4, 'orientation': 100},
             '3': {'waypoint': 3, 'lat': 30.12345, 'lon': 32.234234, 'height': 30.5, 'orientation': 120}}

#mock_iterator = int(1)

@app.route("/")
def get_site():
    return redirect(url_for('static', filename='index.html'))


@app.route("/tiles/<tile_type>/<z>/<x>/<y>.jpg")
def get_tile(tile_type, x, y, z):
    import tileServer
    return tileServer.get_tile(tile_type, x, y, z)

@app.route('/flightData', methods=['GET', 'POST'])
def flight_data():
    method = request.method
    print(method)
    # data = request.form.get('foo', type=int)
    #print (foo)
    data = request.get_json()
    print(str(data))
    a = {'foo': 1234}
    #print(data)
    if method == 'POST':
        return str(a)
        #return 'got foo key' + str(data)
        #return 'processing flight data post request'
    elif method == 'GET':
        return jsonify(**get_flight_data())

    #@app.route('foo')
    #return render_template


def get_flight_data():
    data = mock_data.get('{0}'.format(get_random_mock_data()))
    return data

def get_random_mock_data():
    import random
    a = [1, 2, 3]
    return random.choice(a)


if __name__ == '__main__':
    app.run(port=80, host='0.0.0.0', threaded=True)



