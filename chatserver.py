import atexit

from twisted.internet import protocol, reactor
from twisted.python import log

from constants import *
from dboperations import DBOperations

db = DBOperations(DB_URL)
db.setup()


class Chat(protocol.Protocol):
    # Protocol class for the request
    def __init__(self, factory):
        self.factory = factory
        self.name = None
        self.state = STATE_AUTH

    def connectionMade(self):
        self.transport.write(
            'Enter \n1. username:password to login or register \nOR\n2. .quit to exit \n')
        self.transport.write('Input : ')

    def connectionLost(self, reason):
        self.display_greeting(EXIT)
        # Update user parameters
        db.update_logout(self.name)
        db.set_offline(self.name)

    def dataReceived(self, data):
        data = data.strip()

        if data == EXIT_COMMAND:
            self.transport.loseConnection()

        if self.state == STATE_AUTH:
            if ":" in data:
                # Message is a login request
                try:
                    username, password = data.split(":")
                except:
                    self.transport.write('Invalid input\nPlease retry :')
                if (username,) in db.return_all_users():
                    # Username present. Attempt to authenticate
                    self.auth_user(username, password)
                else:
                    # Username not present. Attempt to register user.
                    self.register_user(username, password)
            else:
                self.transport.write('Invalid input\nPlease retry :')
        else:
            # Attempt to send message
            self.process_message(data)

    def auth_user(self, username, password):
        # Authenticates user against a username and password
        if db.auth_user(username, password):
            self.update_user(username)
            self.display_greeting(LOGIN)
        else:
            self.transport.write('Authentication failed, please retry\nInput :')

    def update_user(self, username):
        # Update user parameters to reflect current state
        self.name = username
        self.factory.users[username] = self
        self.state = STATE_CHAT
        db.update_login(username)
        db.set_online(username)

    def display_greeting(self, type):
        """
        Displays generic greetings based on a type variable
        :param type: Type of scenario to display greeting for
        :return:
        """
        if type == SIGN_UP:
            self.transport.write("Registration successful. Welcome %s \n" % (self.name,))
            self.broadcast_message("%s has joined in \n" % (self.name,))
            log.msg("%s has joined in \n" % (self.name,))
            self.transport.write("%d other users are online\n " % (len(db.return_online_users()),))
            self.transport.write("Enter target_user>message to send a message\n")
        elif type == LOGIN:
            self.transport.write("Login successful. Welcome %s \n" % (self.name,))
            self.broadcast_message("%s has logged in \n" % (self.name,))
            log.msg("%s has logged in \n" % (self.name,))
            self.transport.write('%d other users are online\n ' % (len(db.return_online_users()),))
            self.transport.write("Enter target_user>message to send a message\n")
        elif type == EXIT:
            self.broadcast_message("%s has left the channel.\n" % (self.name,))
            log.msg("%s has left the channel. \n" % (self.name,))

    def register_user(self, name, password):
        """Register a user using a give username and password"""
        if (name,) not in db.return_all_users():
            db.add_user(name, password)
            self.update_user(name)
            self.display_greeting(SIGN_UP)
        else:
            # Name exists in database
            self.transport.write('Name already taken, login using username:password :')
            return

    def process_message(self, message):
        if '>' not in message:
            # Prompt again
            self.transport.write('Invalid format!!\nUse target>message')
            return
        else:
            target, content = message.split('>')

        self.factory.users[target].transport.write("%s : %s \n" % (self.name, content))
        db.add_message(self.name, target, content)

    def broadcast_message(self, message):
        """
        Sends out a message to all connected users
        :param message:
        :return:
        """
        for name, protocol in self.factory.users.iteritems():
            if protocol != self and protocol is not None:
                protocol.transport.write(message)


class ChatFactory(protocol.Factory):
    # Factory class that returns instances of the protocol
    def __init__(self):
        # Populating users from database
        self.users = dict.fromkeys(db.return_all_users())

    def buildProtocol(self, addr):
        return Chat(self)


def clean_up():
    """Pre exit formalities"""
    db.set_offline(username=False, all=True)


atexit.register(clean_up)

log.startLogging(open(LOG_FILE_URL, 'a'), )
reactor.listenTCP(PORT, ChatFactory())
reactor.run()
