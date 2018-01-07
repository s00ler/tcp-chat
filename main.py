import asyncio
from server import ChatServer
import sys

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    server = ChatServer('My first chat server',
                        sys.argv[1], int(sys.argv[2]), loop)
    try:
        loop.run_forever()
    finally:
        loop.close()
