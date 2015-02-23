from email import message_from_file

__author__ = 'Aviad Rom'
from flask import Flask, url_for, request, redirect
from messageQueue import MessageQueue, Message
from datetime import datetime
from threading import Thread
from logging import Logger
import json

app = Flask(__name__)
droneData = {'lastUpdate': datetime.utcnow(), 'stats': None}
messagesQueue = None
droneIp = None


def is_new_valid_ip(ip):
    #add more ip validation
    return ip and ip != droneIp


def destroy_queue(ip):
    global droneIp
    global messagesQueue
    if ip != droneIp or not messagesQueue:
        return
    messagesQueue.stop()
    messagesQueue = None
    droneIp = None


def create_queue(ip):
    global messagesQueue
    global droneIp
    droneIp = ip
    messagesQueue = MessageQueue(target=('http://' + ip + ':8080/receiveMessage'))
    messagesQueue.start()


def handle_hello(ip, message=None):
    if not is_new_valid_ip(ip):
        return
    destroy_queue(droneIp)
    create_queue(ip)


def handle_bye(ip, message=None):
    destroy_queue(ip)


def handle_heartbeat(ip, message):
    if ip != droneIp:
        print 'not mu drone'
    elif message.timeStamp < droneData['lastUpdate']:
        print 'old'
    else:
        droneData['lastUpdate'] = message.timeStamp
        droneData['stats'] = message.content['stats']
        print 'Drone data updated'


def log_message(message, ip):
    sent = message.timeStamp.strftime('%Y-%m-%d %H:%M:%S')
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    print 'Got: "' + message.kind + '" from: ' + ip
    print 'Message Sent: ' + sent + ', received: ' + now


messagesHandlers = {
    'hello': handle_hello,
    'bye':      handle_bye,
    'heartBeat': handle_heartbeat
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
    handle_hello(ip=request.args.get('ip', False))
    return 'ok'


@app.route('/receiveMessage', methods=['POST'])
def receive_message():
    message = Message(json.loads(request.data))
    log_message(message, request.remote_addr)
    if message.kind in messagesHandlers:
        messagesHandlers[message.kind](ip=request.remote_addr, message=message)
        return "ok"
    return "No handler found for message kind: " + message.kind


@app.route('/flightData', methods=['GET'])
def flight_data():
    return json.dumps(droneData['stats'])


serverThread = None


def start_server():
    global serverThread
    if serverThread:
        return "Server already running"
    serverThread = Thread(target=app.run,
                          kwargs={'port': 8080, 'host': '0.0.0.0', 'debug': False, 'threaded': True})
    serverThread.start()
    return "ok"


def connect(ip=None):
    if not serverThread:
        return "Server not running"
    handle_hello(ip)
    return "Hello sent"


def send_message(message_json):
    if not serverThread:
        return "Server not running"
    if not messagesQueue:
        return "Not connected"
    messagesQueue.enqueue(message_json)
    return "Message queued"


if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0',debug=True, threaded=True)


# @app.route('/droneData', methods=['POST'])
# def drone_request():
#     obj = request.get_json()
#     drone.update(obj)
#     #push object to "from_drone" queue
#     #return next mission (actual mission or NOP)