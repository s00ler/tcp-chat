import asyncio
from room import Room
from user import User


class ChatServer:

    commands = ['@list', '@join',
                '@leave', '@create',
                '@delete', '@help']

    def __init__(self, server_name, host, port, loop):
        self.server_name = server_name
        self.connections = {}
        self.rooms = {}
        self.server = loop.run_until_complete(
            asyncio.start_server(self.accept_connection, host, port, loop=loop))

    async def accept_connection(self, reader, writer):
        user = await self.new_user(reader, writer)
        if user is not None:
            print('User {} joined'.format(user))
            user.respond('Hello, {}.\nUse @help for help.\n'.format(user))
            await self.handle_user(user)
        await writer.drain()

    async def new_user(self, reader, writer):
        writer.write('Welcome to server. Enter your username:\n'.encode())
        await writer.drain()
        data = (await reader.readline()).decode()
        if not data:
            return None
        else:
            name = data.strip()
            return User(name, reader, writer)

    async def handle_user(self, user: User):
        while True:
            data = await user.say()
            print(data)
            if data is None:
                return None
            if data[0] == '@':
                self.process_command(data, user)
            else:
                try:
                    user.room.broadcast(data, user)
                except Exception as e:
                    print(e)
                    user.respond('Message failed to send.\n')
            await user.flush()

    def process_command(self, data, user):
        command = data.split()
        if command[0] in self.commands:
            if command[0] == '@list':
                user.respond(str(list(self.rooms.keys())))
            elif command[0] == '@help':
                user.respond('Available commands:\n'
                             '@list - view all rooms available.\n'
                             '@help - view this message.\n'
                             '@join room_name - join room.\n'
                             '@leave - leave current room.\n'
                             '@create room_name - create new room.\n'
                             '@delete room_name - delete existing room.\n')
            elif command[0] == '@join' and len(command) >= 2:
                user.join(self.rooms[command[1]])
            elif command[0] == '@leave':
                user.leave()
            elif command[0] == '@create' and len(command) >= 2:
                user.respond(self.add_room(command[1]))
            elif command[0] == '@delete' and len(command) >= 2:
                user.respond(self.delete_room(command[1]))
        else:
            user.respond('Command unknown. Use @help.\n')

    def add_room(self, name):
        if name not in self.rooms.keys():
            self.rooms[name] = Room(name)
            response = 'Room {} created.\n'.format(name)
        else:
            response = 'Room {} exists.\n'.format(name)
        return response

    def delete_room(self, name):
        if name in self.rooms.keys():
            for user in self.rooms[name].users:
                user.leave()
            self.rooms.remove(name)
            response = 'Room {} deleted.\n'.format(name)
        else:
            response = 'Room {} does not exist.\n'.format(name)
        return response
