# Author: Rodolfo Rivera & Mohammad Asim Sheikh
# Date: 04/12/2024
# A Chat Application for Remote Message Exchange

import sys
import socket
import threading
import select

# Returns user IP address
def get_my_ip():
    try:
        hostname = socket.gethostname()
        myip = socket.gethostbyname(hostname)
        return myip
    except:
        print("Error finding IP address")

class Peer:
    # initiates lists and dictionaries and creates server
    def __init__(self, port):
        self.host = '0.0.0.0'
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.connections = {self.server_socket: ('server', self.port)}
        self.address_map = {}
        self.connection_counter = 1  # To assign IDs to connections for easier management

    # Starts listening for any incoming communication
    def listen_for_connections(self):
        print(f"Listening for connections on ({get_my_ip()},{self.port})")
        while True:
            # Records only readable sockets
            readable, _, _ = select.select(self.connections.keys(), [], [], 0)
            # Gets socket, IP address and port number
            for sock in readable:
                if sock == self.server_socket:
                    client_socket, addr = self.server_socket.accept()
                    self.connections[client_socket] = addr
                    self.address_map[addr] = self.connection_counter
                    print(f"Accepted connection from {addr}, ID: {self.connection_counter}")
                    self.connection_counter += 1
                else:
                    # If socket is not a server socket, it will check for a message
                    try:
                        data = sock.recv(1024)
                        if data:
                            sender_id = self.address_map[self.connections[sock]]
                            print(f"Message received from {self.connections[sock][0]}")
                            print(f"Sender's Port: {self.connections[sock][1]}")
                            print(f"Message: \"{data.decode().strip()}\"")
                        else:
                            self.close_connection(sock)
                    except ConnectionResetError:
                        self.close_connection(sock)

    # Will send a message to id that is specified
    def send_message_by_id(self, connection_id, message):
        # Check if the connection ID is valid and get the corresponding socket
        target_sock = None
        for sock, addr in self.connections.items():
            if sock != self.server_socket and self.address_map[addr] == connection_id:
                target_sock = sock
                break
        # After corresponding socket is located, message will be sent
        if target_sock:
            try:
                target_sock.sendall(message.encode('utf-8'))
                print(f"Message sent to connection ID {connection_id}")
            except socket.error as e:
                print(f"Failed to send message to connection ID {connection_id}: {e}")
                self.close_connection(target_sock)
        else:
            print("Invalid connection ID.")

    # Closes connection with specified sock
    def close_connection(self, sock):
        try:
            # Finds sock in both connections and adress_map dictionaries and deletes them
            if sock in self.connections:
                addr = self.connections.pop(sock, None)
                if addr and addr in self.address_map:
                    del self.address_map[addr]
                    print(f"closing connection with {addr}")
                sock.close()
            else:
                print("Connection not tracked")
        except socket.error as e:
            print(f"Error closing socket: {e}")
        except KeyError as e:
            print(f"Key error accessing address map: {e}")

    # Handles all commands that are entered in terminal
    def handle_commands(self):
        while True:
            # Splits the input to get information entered
            command = input("").strip().split()
            if not command:
                continue
            cmd = command[0]
            if cmd == "exit":
                for sock in list(self.connections.keys()):
                    if sock != self.server_socket:
                        self.close_connection(sock)
                self.server_socket.close()
                print("Server and all connections have been closed.")
                break
            elif cmd == "help":
                self.print_help()
            elif cmd == "myip":
                print(get_my_ip())
            elif cmd == "myport":
                print(self.port)
            elif cmd == "list":
                self.list_connections()
            elif cmd == "connect" and len(command) == 3:
                dest_ip, dest_port = command[1], int(command[2])
                self.connect_to_peer(dest_ip, dest_port)
            elif cmd == "terminate" and len(command) == 2:
                conn_id = int(command[1])
                self.terminate_connection_by_id(conn_id)
            elif cmd == "send" and len(command) >= 3:
                conn_id = int(command[1])
                message = ' '.join(command[2:])
                self.send_message_by_id(conn_id, message)
            else:
                print("Unknown command or incorrect usage.")

    # Lists all the connections currently active
    def list_connections(self):
        print("id: IP address  Port No.")
        for sock, addr in self.connections.items():
            if sock != self.server_socket:
                print(f"{self.address_map[addr]}: {addr}")
                
    # Connects host to peer through ip address and port and adds their information to dictionaries
    def connect_to_peer(self, host, port):
        try:
            new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_sock.connect((host, port))
            self.connections[new_sock] = (host, port)
            self.address_map[(host, port)] = self.connection_counter
            print(f"Connected to {host} on port {port}, ID: {self.connection_counter}")
            self.connection_counter += 1
        except socket.error as e:
            print(f"Failed to connect to {host} on port {port}: {e}")

    # Finds the socket that corresponds to the id given
    def terminate_connection_by_id(self, connection_id):
        for sock, addr in list(self.connections.items()):
            if addr in self.address_map and self.address_map[addr] == connection_id:
                self.close_connection(sock)
                
            
    # Prints help menu
    def print_help(self):
        text = """
myip                              Display IP address of this process
myport                            Display the port on which this process is listening for incoming connections
connect<destination><port no>     This command establishes a new TCP connection to the specified address and port
list                              Diplay a numbered list of all connections this process is part of
terminate <connection id.>        Terminate the connection with id provided
send <connection id.><message>    Send message to host with id provided (100 characters max.)
exit                              Close all connections and terminate this proccess\n
        """
        print(text)

# Runs the peer class and listens for connections on thread
def run_peer(port):
    peer = Peer(port)
    threading.Thread(target=peer.listen_for_connections, daemon=True).start()
    peer.handle_commands()

# Runs on file run, gets the port specified and runs peer class on port given
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python chat.py <port>")
        sys.exit(1)

    port = int(sys.argv[1])
    run_peer(port)



