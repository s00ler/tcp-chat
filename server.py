from server import ChatServer
import sys

if __name__ == '__main__':
    server = ChatServer('My first chat server',
                        sys.argv[1], int(sys.argv[2]))
    try:
        server.run()
    finally:
        server.stop()
