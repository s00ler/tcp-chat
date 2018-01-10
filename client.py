from threading import Thread
import socket
import sys


class Connection:
    def __init__(self, host, port):
        self._socket = socket.socket()
        self._host = host
        self._port = port
        self.connected = False
        self.connect()

    def connect(self):
        if not self.connected:
            self.connected = True
            self._socket.connect((self._host, self._port))

    def read(self):
        try:
            data = self._socket.recv(6000)
        except Exception as e:
            print(e)
            self.connected = False
            return None

        if data is None or data == b'':
            self.connected = False
            return None
        else:
            return data.decode()

    def send(self, msg):
        if msg is not None:
            if msg != '\n':
                try:
                    self._socket.send(msg.encode())
                except Exception as e:
                    print(e)
                    self.connected = False


class Reader(Thread):
    def __init__(self, connection):
        Thread.__init__(self)
        self.connection = connection

    def run(self):
        while self.connection.connected:
            data = self.connection.read()
            if data is not None:
                print('Server > {}'.format(data))
        print('Disconnected from server.')


class Writer(Thread):
    def __init__(self, connection):
        Thread.__init__(self)
        self.connection = connection

    def run(self):
        while self.connection.connected:
            self.connection.send(sys.stdin.readline())


if __name__ == '__main__':
    connection = Connection(sys.argv[1], int(sys.argv[2]))
    writer = Writer(connection)
    reader = Reader(connection)
    writer.start()
    reader.start()

    reader.join()
    writer.join()
