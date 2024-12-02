import socket
from pymongo.mongo_client import MongoClient
from pymongo.server_ai import ServerApi

def start_tcp_server():
    myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Get the server IP address and port number
        user_server_ip = input("Please enter the server IP address: ")
        user_server_port = int(input("Please enter the server port number: "))

        myTCPSocket.bind(('0.0.0.0', user_server_port))

    except ValueError:
        print("Please enter a positive integer for the server port.")
        return

    except socket.error as err:
        print(f"Socket error: {err}")
        return

    # Listen for incoming connections
    myTCPSocket.listen(5)  # Allow up to 5 connections in queue
    print(f"Server now listening on {user_server_ip}:{user_server_port}")

    # Accept an incoming connection
    incomingSocket, incomingAddress = myTCPSocket.accept()
    print(f"Client connected! Connection from {incomingAddress}")

    maxBytes: int = 1024
    serverIsOn: bool = True

    try:
        # Infinite loop to handle multiple messages
        while serverIsOn:
            received_message = incomingSocket.recv(maxBytes).decode('utf-8').strip()
            print(f"Client's message: {received_message}")

            # Check for empty message or "exit" command to close server
            if received_message.lower() == 'exit' or received_message == '':
                print("Shutting down server on 'exit' command.")
                serverIsOn = False

            else:
                # Send back the received message in uppercase
                incomingSocket.send(bytearray(received_message.upper(), encoding='utf-8'))

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the connection when done
        incomingSocket.close()
        myTCPSocket.close()
        print("Connection now closed.")

if __name__ == "__main__":
    start_tcp_server()

