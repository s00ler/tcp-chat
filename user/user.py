"""Module with user class."""


class User:
    """Class to handle user actions on the chat server."""

    max_attempts = 3

    @classmethod
    async def ask_for_name(cls, reader, writer):
        """Ask user for his name. Check if it is correct. Accept or retry."""
        attempt = 0
        writer.write(
            'Enter your username (only alphabetic symbols allowed):\n'.encode())

        while cls.max_attempts > attempt:
            attempt += 1
            try:
                await writer.drain()
                data = await reader.readline()
            except Exception:
                return None

            if data is not None:
                data = data.decode().strip()
                if data.isalpha():
                    writer.write(
                        'Hello, {}! Use @help for help.\n'.format(data).encode())
                    return data
            writer.write(
                'Incorrect username. Try again. {} attemps left.\n'
                .format(cls.max_attempts - attempt).encode())

        writer.write('Failed to log in.\n'.encode())
        return None

    def __init__(self, name, reader, writer):
        """Create user.

        Args:
            name (str): user name.
            reader, write (stream objects): streams to read and write data.
        Init attributes:
            room (Room): room user currently in.
            connected (bool): user connection flag.
        """
        self.name = name
        self.reader = reader
        self.writer = writer
        self.room = None
        self.connected = True

    def __str__(self):
        """Str view is user name."""
        return self.name

    def __eq__(self, other: 'User obj' or str):
        """User obj can be compared to string and other User obj.

        Name attribute is compared really.
        """
        if type(other) == type(self):
            return self.name == other.name
        elif type(other) == str:
            return self.name == other
        else:
            return False

    def join(self, room):
        """Join room."""
        if self.room is None:
            status = room.join(self)
            if status:
                self.room = room
                self.send('You joined room {}.\n'.format(room))
            else:
                self.send('Name {} is already taken in room {}.\n'.format(
                    self.name, room))
        else:
            self.send('You are already in room {}.\n'.format(self.room))

    def leave(self):
        """Leave current room if in any."""
        if self.room is not None:
            status = self.room.leave(self)
            if status:
                self.send('You left room {}.\n'.format(self.room))
            else:
                self.send('You are not in room {}.\n'.format(self.room))
            self.room = None
        else:
            self.send('You are not in any room.\n')

    def broadcast(self, msg):
        if self.room is None:
            self.send('Message failed to send. Reason: no room joined.')
        else:
            self.room.broadcast(msg, self)

    def send(self, *args):
        """Send user a message."""
        for message in args:
            if not message.endswith('\n'):
                message += '\n'
                self.writer.write(message.encode())

    async def flush(self):
        """Flush user buffer."""
        await self.writer.drain()

    async def recieve(self):
        """Recieve data from user."""
        attempt = 0

        while self.max_attempts > attempt:
            attempt += 1
            data = await self.reader.readline()
            if data is not None:
                data = data.decode().strip()
                if data != '':
                    return data
            self.send('Incorrect input. {} attemps left.'.format(
                self.max_attempts - attempt))

        self.send('Kicked from server for bullshitting.')
        self.connected = False
        return None

    def disconnect(self):
        """Close user connection."""
        try:
            self.reader.feed_eof()
            self.writer.write_eof()
        except Exception:  # TODO If closed by client OSError raised, may be catch it exacltly?
            pass
