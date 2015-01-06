__author__ = 'Ohad'

from threading import Thread
from Queue import PriorityQueue
from datetime import datetime
import json
import urllib2

priority_dictionary = {
    'heartBeat': 3,
    'targetFound': 2,
    'Image': 1
}

last_sent = {
    'heartBeat': datetime.utcnow(),
    'targetFound': datetime.utcnow()
}


class BadParams(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Message():
    def __init__(self, kind, content):
        self.kind = kind
        if not kind in priority_dictionary:
            raise BadParams('"' + str(kind) + '" Is not a known message type')
        self.priority = priority_dictionary[kind]
        if not 'timeStamp' in content:
            raise BadParams('content has no timeStamp')
        try:
            self.timeStamp = datetime.strptime(content['timeStamp'], '%Y-%m-%d %H:%M:%S')
        except ValueError, e:
            print e
            raise BadParams('Bad timeStamp format')
        self.content = content

    def __cmp__(self, other):
        if self.priority > other.priority:
            return -1
        elif self.priority < other.priority:
            return 1
        elif self.timeStamp < other.timeStamp:
            return -1
        elif self.timeStamp > other.timeStamp:
            return 1
        return 0


class MessageQueue(Thread):
    __queue = PriorityQueue()
    # __target = 'http://127.0.0.1:8080/receiveMessage'
    __target = 'http://postcatcher.in/catchers/54abdf8c31b05e0200000924'

    def run(self):
        while True:
            message = self.__queue.get(block=True)
            if message.kind in last_sent and message.timeStamp < last_sent[message.kind] and message.priority != -1:
                message.priority = -1
                self.__queue.put_nowait(item=message)
                continue
            if not self._send_message(message):
                print 'failed to send'
                self.__queue.put_nowait(item=message)
            elif message.kind in last_sent:
                last_sent[message.kind] = max(message.timeStamp, last_sent[message.kind])

    def _send_message(self, message):
        request = urllib2.Request(self.__target)
        request.add_header('Content-Type', 'application/json')
        try:
            return urllib2.urlopen(url=request, data=json.dumps(message.content), timeout=10).code == 201
        except urllib2.URLError, e:
            print e
            return False

    def enqueue(self, content, kind):
        self.__queue.put_nowait(item=Message(kind=kind, content=content))

if __name__ == '__main__':
    q = MessageQueue()
    q.enqueue(kind='heartBeat', content={'timeStamp': '2014-12-22 20:30:37', 'b': '2'})
    q.enqueue(kind='heartBeat', content={'timeStamp': '2014-12-22 20:30:30', 'b': '1'})
    q.enqueue(kind='targetFound', content={'timeStamp': '2014-12-22 20:30:27', 'b': '4'})
    q.enqueue(kind='heartBeat', content={'timeStamp': '2014-12-22 20:30:40', 'b': '3'})
    q.start()