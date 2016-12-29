# basic-chat-server

Basic TCP chat server using the Twisted asynchronous I/O framework.

**Features :-**

1. User registration and login (using a PLAIN TEXT password).
2. DB persistence for user information and messages (SQLite).
3. User > User and Broadcast messaging.
4. Convenient DB operations using a light weight SQLite helper.
5. Tracks last login/logout time and online status of a user.

**Usage :**

Setup :

1. Clone the repository
2. Set up a python virtual envrionment and activate it
(https://realpython.com/blog/python/python-virtual-environments-a-primer/)
3. Install dependencies using the following command

    `pip install -r requirements.txt`
    
4. Run the server using
    
    `python chatserver.py`

5. Connect clients by typing this on a terminal

    `telnet <address> <port>`
    
* _Default value for < port > is 1236._
 
* < address > can be localhost if connecting from the same machine.

**Simulating clients :** _(Because why not?)_

After starting the server, run sim_client.py to simulate a number of clients. Internally, client auth is read from a configuration file _(sim_users.json is the default)._

**Database :**

The server creates and uses a SQLite database _(default name is storage.db)_ for storing user information and messages.


by _srvasn@gmail.com_