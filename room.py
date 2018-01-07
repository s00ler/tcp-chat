import datetime


class Room:
    def __init__(self, name: str):
        self.name = name
        self.users = []

    def __str__(self):
        return self.name

    def __eq__(self, other: 'Room obj' or str):
        if type(other) == type(self):
            return self.name == other.name
        elif type(other) == str:
            return self.name == other
        else:
            return False

    def join(self, user):
        if user not in self.users:
            status = True
            self.users.append(user)
            self.broadcast('{} joined room {}\n'.format(user, self.name), user)
        else:
            status = False
        return status

    def leave(self, user):
        if user in self.users:
            status = True
            self.users.remove(user)
            self.broadcast('{} left room {}\n'.format(user, self.name), user)
        else:
            status = False
        return status

    def broadcast(self, message: str, user):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        for client in self.users:
            client.respond('room: {}, user: {}, time: {}\nmessage: {}\n'.format(
                self.name, user, now, message))
