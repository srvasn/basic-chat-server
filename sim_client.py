import copy
import json
import random
import socket
import time
from threading import Timer

from constants import *

# Loading test user auth information from file
with open(TEST_USER_FILE) as sim_user_auth:
    TEST_CLIENT_AUTH = json.load(sim_user_auth)

# For the list to pop from the front
TEST_MESSAGES.reverse()


# Function that is passed on to threads that simulate clients
def test_chat(user_auth, messages):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', PORT))
    # Send username:password
    s.send(user_auth)
    data = s.recv(1024)
    username = user_auth.split(":")[0]
    if 'failed' not in data:
        print '%s logged in' % (username,)

    # The loop runs until we run out of messages
    while len(messages) > 0:
        # Selecting a target user that is not the current one
        target = get_target_user(username)
        s.send(target + ">" + messages.pop())
        print("%s sent a message to %s" % (username, target))

        data = s.recv(1024)
        time.sleep(1)
    # Close socket after all messages have been sent
    s.close()
    print '%s disconnected' % (username,)


def get_target_user(exclude):
    # Returns a user that is not exclude
    while True:
        user = random.choice(TEST_CLIENT_AUTH)['username']
        if user != exclude:
            return user
        else:
            continue


for user in TEST_CLIENT_AUTH:
    # Launching a new thread for every simulated client in the test file
    Timer(0.5, test_chat, args=["%s:%s" % (user["username"], user["password"]), copy.deepcopy(TEST_MESSAGES)]).start()
