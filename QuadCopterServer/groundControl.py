__author__ = 'Aviad Rom'
from flask import Flask, url_for, request, jsonify, redirect
from Drone import Drone
from messageQueue import MessageQueue
import json

app = Flask(__name__)
drone = Drone()
messagesQueue = None
droneIp = None


def switch_queue(ip):
    global messagesQueue
    global droneIp
    #add more ip validation
    if not ip or ip == droneIp:
        return
    if messagesQueue:
        messagesQueue.stop()
    droneIp = ip
    messagesQueue = MessageQueue(target=('http://' + ip + ':8080/receiveMessage'))
    messagesQueue.start()


def handle_hello(message, ip):
    switch_queue(ip)
    print 'Got hello from: ' + ip


def handle_bye(message, ip):
    global messagesQueue
    global droneIp
    if ip == droneIp:
        messagesQueue.stop()
        messagesQueue = None
        droneIp = None
    print 'Got bye from: ' + ip

messagesHandlers = {
    'hello': handle_hello,
    'bye':      handle_bye
}

@app.route("/")
def get_site():
    return redirect(url_for('static', filename='index.html'))


@app.route('/tiles/<tile_type>/<z>/<x>/<y>.jpg')
def get_tile(tile_type, x, y, z):
    import tileServer
    return tileServer.get_tile(tile_type, x, y, z)


@app.route('/changeDrone', methods=['GET'])
def change_drone():
    switch_queue(request.args.get('ip', False))
    global messagesQueue
    global droneIp
    messagesQueue.stop()
    messagesQueue = None
    droneIp = None
    return 'ok'


@app.route('/receiveMessage', methods=['POST'])
def receive_message():
    message = json.loads(request.data)
    if message['kind'] in messagesHandlers:
        messagesHandlers[message['kind']](message, request.remote_addr)
    return "ok"


@app.route('/flightData', methods=['GET'])
def flight_data():
    import randomFlightData
    return json.dumps(randomFlightData.get_data())


@app.route('/droneData', methods=['POST'])
def drone_request():
    obj = request.get_json()
    drone.update(obj)
    #push object to "from_drone" queue
    #return next mission (actual mission or NOP)


if __name__ == '__main__':
    app.debug = True
    app.run(port=8080, host='0.0.0.0', threaded=True)

##############################################################

#app.debug = True

# mock_data = {'1': {'waypoint': 1, 'lat': 30.12345, 'lon': 32.234234, 'height': 30.3, 'orientation': 95},
#              '2': {'waypoint': 2, 'lat': 30.12345, 'lon': 32.234234, 'height': 30.4, 'orientation': 100},
#              '3': {'waypoint': 3, 'lat': 30.12345, 'lon': 32.234234, 'height': 30.5, 'orientation': 120}}


#
#FROM CLIENT {
#     'lat': 30.12345,
#     'lon': 32.234234,
#     'height': 30.3,
#     'orientation': 90,
#     'message': "",
#     'battery': 100
# }


#
#TO CLIENT {
#     'lat': 30.12345,
#     'lon': 32.234234,
#     'height': 30.3,
#     'orientation': 90,
#     'message': "",
#     'battery': 100
# }


#mock_iterator = int(1)

    # method = request.method
    # print(method)
    # data = ""
    # print request.data
    # print request.json
    # data = request.get_json()
    # print data["foo"]
    # # try:
    # #     data = request.get_json()
    # # except Exception, e:
    # #     print e
    # a = {'foo': 1234}
    # #print(data)
    # if method == 'POST':
    #     return str(a)
    #     #return 'got foo key' + str(data)
    #     #return 'processing flight data post request'
    # elif method == 'GET':
    #     return jsonify(**get_flight_data())
    #
    # #@app.route('foo')
    # #return render_template


# @app.route('/appData', methods=['GET', 'POST'])
# def client():
#
#



#
#FROM DRONE {
#     'lat': 30.12345,
#     'lon': 32.234234,
#     'elevation': 30.3,
#     'bearing': 90,
#     'battery': 100
#     'message': "",
#     'timestamp': now
# }


#
#TO DRONE {
#     'lat': 30.12345,
#     'lon': 32.234234,
#     'elevation': 30.3,
#     'orientation': 90,
#     'message': "",
#     'battery': 100
# }

# def get_flight_data():
#     data = mock_data.get('{0}'.format(get_random_mock_data()))
#     return data

# def get_random_mock_data():
#     import random
#     a = [1, 2, 3]
#     return random.choice(a)