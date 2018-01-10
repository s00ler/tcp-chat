"""Module with Room class."""
import datetime


class Room:
    """Class to handle chat room concept.

    Main method - broadcast, to send messages between room users.
    """

    def __init__(self, name: str, father):
        """Init with name and user who call @create command."""
        self.name = name
        self.users = []
        self.father = father

    def __str__(self):
        """String view is a room name."""
        return self.name

    def __eq__(self, other: 'Room obj' or str):
        """Room obj can be compared to string and other Room obj.

        Name attribute is compared really.
        """
        if type(other) == type(self):
            return self.name == other.name
        elif type(other) == str:
            return self.name == other
        else:
            return False

    def join(self, user):
        """User joins."""
        if user not in self.users:
            status = True
            self.users.append(user)
            self.broadcast('{} joined room {}\n'.format(user, self.name), user)
        else:
            status = False
        return status

    def leave(self, user):
        """User leaves."""
        if user in self.users:
            status = True
            self.users.remove(user)
            self.broadcast('{} left room {}\n'.format(user, self.name), user)
        else:
            status = False
        return status

    def broadcast(self, message: str, user):
        """Send message to all users in room except sender.

        Args:
            message (str): message to send.  # TODO make *args
            user (User): message sender.
        """
        now = datetime.datetime.now().strftime('%H:%M')
        for client in self.users:
            if client != user:
                client.send('{} > {} > @{}: {}'.format(
                    self.name, user, now, message))
