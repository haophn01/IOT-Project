import socket

def start_tcp_client():
    myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    prompt1 = "1. What is the average moisture inside my kitchen fridge in the past three hours?"
    prompt2 = "2. What is the average water consumption per cycle in my smart dishwasher?"
    prompt3 = "3. Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?"

    try:
        maxBytesToReceive: int = 1024

        # Get the server IP address and port number
        user_server_ip = input("Please enter the server IP address: ")
        user_server_port = int(input("Please enter the server port number: "))

        # Try connecting to the server
        myTCPSocket.connect((user_server_ip, user_server_port))
        print(f"Successfully connected to server --> {user_server_ip}:{user_server_port}")

        clientIsOn: bool = True

        # Infinite loop until user wants to stop sending messages
        while clientIsOn:
            
            # Display the 3 prompts
            print(prompt1)
            print(prompt2)
            print(prompt3)

            # Obtain message from user
            user_message = input("Please enter 1, 2 or 3 to send (or type 'exit' to quit): ")

            # If the user types 'exit' or presses Enter with no message, break the loop
            if user_message.lower() == 'exit' or user_message == '':
                print("Exiting now...")
                clientIsOn = False
                break
            # If the user types anything other than 1, 2, or 3, proceed to the next iteration
            if user_message not in ['1', '2', '3', 'exit', '']:
                print("Please enter 1, 2, 3 or exit.")
                continue

            # Send the message to the server
            if user_message  in ['1', '2', '3', 'exit', '']:
                myTCPSocket.send(bytearray(user_message, encoding='utf-8'))

            # Receiving server's response (uppercased message)
            serverResponse = myTCPSocket.recv(maxBytesToReceive).decode('utf-8')

            # Print the server's response
            print(f"Server's reply: {serverResponse}")

    except ValueError:
        print("Please enter a valid port number.")
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the connection
        myTCPSocket.close()
        print("Connection now closed.")

if __name__ == "__main__":
    start_tcp_client()