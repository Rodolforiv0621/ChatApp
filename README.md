# Project Overview:
This project is a simple chat application designed for remote message exchange among peers, developed as part of the coursework for COMP429. The application allows multiple clients to connect to a server (or peer) to send and receive messages in real time. It is implemented in Python and utilizes TCP sockets to manage communication between peers.

# Installation and Run:
1. Clone this git repository
2. To start the server on a specific port #

  ` python3 chat.py <port> `
  or
  ` py chat.py <port> `

# List of Commands
+ help : Displays a list of available commands
+ myip : Displays Displays the IP Address of your process
+ myport : Displays the port this process is listening on
+ connect &lt;IP&gt; &lt;port&gt; : Connects to peer at IP:Port
+ list : Displays a list of all active connections
+ terminate &lt;id&gt; : Terminates a connection using ID (Example: 1 or 2)
+ send &lt;id&gt; &lt;message&gt; : Sends a message to a connection using ID
+ exit : Closes all active connections and terminates program

# Project Demo Video
Will add video link here tonight






