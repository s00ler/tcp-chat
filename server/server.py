"""Module with ChatServer class."""

import asyncio
from user import User
from room import Room


class ChatServer:
    """My pretty simple chat server."""

    commands = ['@rooms', '@create', '@delete', '@join', '@leave',
                '@help', '@disconnect']

    def __init__(self, server_name: str, host: str, port: int):
        """Initilise server.

        Args:
            server_name (str): name of the server.
            host (str): ip-address of the server.
            port (int): port number.
        """
        self._server_name = server_name
        self._rooms = {}
        self._loop = asyncio.get_event_loop()

        self._server = self._loop.run_until_complete(
            asyncio.start_server(self._accept_connection,
                                 host,
                                 port,
                                 loop=self._loop))

    def stop(self):
        """Stop server."""
        self._loop.stop()

    def run(self):
        """Start server."""
        self._loop.run_forever()

    async def _accept_connection(self, reader, writer):
        """Accepting and processing connetions."""
        user = await self._greet_user(reader, writer)
        if user is not None:
            await self._handle_user(user)
        else:
            try:
                print('Unknown disconnected.')
                reader.feed_eof()
                writer.write_eof()
            except Exception:
                pass
            return None

    async def _greet_user(self, reader, writer):
        """Greet user and ask him for name."""
        writer.write('Welcome to {}!\n'.format(self._server_name).encode())
        name = await User.ask_for_name(reader, writer)
        if name is not None:
            print('{} connected.'.format(name))
            return User(name, reader, writer)
        else:
            return None

    def _say_bye(self, user):
        """Make sure user left his room."""
        user.leave()
        print('{} disconnected.'.format(user))
        user.disconnect()
        del user

    async def _handle_user(self, user):
        """Handle user messages.

        If message starts with @ - it is a command. Parse and exexcute.
        Else - broadcast into room.
        """
        while user.connected:
            data = await user.recieve()
            print(user, data, sep=': ')  # may be logged instead

            if data is not None:
                if data[0] == '@':
                    self._process_command(data, user)
                else:
                    user.broadcast(data)
            await user.flush()
        self._say_bye(user)

    def _process_command(self, data, user):
        """Process commands."""
        command = data.split()
        if command[0] in self.commands:
            if command[0] == '@help':
                self._help(user)
            elif command[0] == '@rooms':
                user.send('Rooms: {}.'.format(list(self._rooms.keys())))
            elif command[0] == '@disconnect':
                user.connected = False
            elif command[0] == '@leave':
                user.leave()
            elif command[0] == '@create' and len(command) == 2:
                self._create_room(user, command[1])
            elif command[0] == '@delete' and len(command) == 2:
                self._delete_room(user, command[1])
            elif command[0] == '@join' and len(command) == 2:
                self._join_room(user, command[1])
            else:
                user.send('Command format unknown. Use @help.')
        else:
            user.send('Command unknown. Use @help.')

    def _help(self, user):
        """Send help message to user."""
        user.send('Available commands:',
                  '@help - view this message.',
                  '@rooms - view all rooms available.',
                  '@join room_name - join room.',
                  '@leave - leave current room.',
                  '@create room_name - create new room.',
                  '@delete room_name - delete existing room.',
                  '@disconnect - disconnect from server.')

    def _create_room(self, user, name):
        """Create new room."""
        if name not in self._rooms.keys():
            self._rooms[name] = Room(name, user)
            response = 'Room {} created.'.format(name)
        else:
            response = 'Room {} exists.'.format(name)
        user.send(response)

    def _join_room(self, user, name):
        """Join user to room."""
        room = self._rooms.get(name)
        if room is not None:
            user.join(room)
        else:
            user.send('Room {} does not exist.')

    def _delete_room(self, user, name):
        """Delete room if have permission."""
        room = self._rooms.get(name)
        if room is None:
            response = 'Room {} does not exist.'.format(name)
        elif room.father != user:
            response = 'You have no permission to delete room {}.'.format(name)
        else:
            for client in list(room.users):
                client.leave()
            del self._rooms[name]
            response = 'Room {} deleted.'.format(name)
        user.send(response)
