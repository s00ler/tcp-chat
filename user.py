import asyncio


class User:
    def __init__(self, name, reader, writer):
        self.name = name
        self.reader = reader
        self.writer = writer
        self.room = None

    def __str__(self):
        return self.name

    def __eq__(self, other: 'User obj' or str):
        if type(other) == type(self):
            return self.name == other.name
        elif type(other) == str:
            return self.name == other
        else:
            return False

    def join(self, room):
        if self.room is None:
            status = room.join(self)
            if status:
                self.room = room
                self.respond('You joined room {}.\n'.format(room))
            else:
                self.respond('Name {} is already taken in room {}.\n'.format(
                    self.name, room))
        else:
            self.respond('You are already in room {}.\n'.format(self.room))

    def leave(self):
        if self.room is not None:
            status = self.room.leave(self)
            if status:
                self.respond('You left room {}.\n'.format(self.room))
            else:
                self.respond('You are not in room {}.\n'.format(self.room))
            self.room = None
        else:
            self.respond('You are not in any room.\n')

    def respond(self, message):
        self.writer.write(message.encode())

    async def flush(self):
        await self.writer.drain()

    async def say(self):
        data = (await self.reader.readline()).decode().strip('\n')
        if data is None or data == '':
            return None
        else:
            return data
