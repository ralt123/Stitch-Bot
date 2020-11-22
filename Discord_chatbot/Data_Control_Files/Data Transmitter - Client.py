# Imports required modules
import socket, csv, hashlib, ast


sending = True
# Receives the user's input
while True:
    userPhrase = str(input("Send or receive data? - "))
    if "receive" in userPhrase.lower():
        sending = False
        break
    elif "send" in userPhrase.lower():
        break
    print("Invalid input\n")

# Variable to control the main loop
ongoingTransmission = True
while ongoingTransmission:
    try:
        # Controls loops to end transmission when appropriate
        successfulTransmission = False
        attempts = 0
        # Establishes connection with host
        currentHost = socket.socket()
        receiverIP = input("Receiver IP (in format 127.0.0.1) - ")
        usedPort = int(input("Input port - "))
        currentHost.connect((receiverIP, usedPort))
        # Sending a new csv to the host for storage
        if sending:
            # Informs the host of the clients intent
            currentHost.send("send".encode())
            # Retrieves data held in the csv file
            with open("UserDetails.csv", "r") as csvFile:
                heldCSVData = list(csv.reader(csvFile))
            # Raises error if the csv file contains no data
            if not heldCSVData:
                raise Exception("'UserDetails.csv' is empty")
            heldCSVData = str(heldCSVData)
            # Produces a hash of the csv value, used to ensure data is not lost or modified during transmission
            hashedCSVData = hashlib.sha256(heldCSVData.encode('utf-8')).hexdigest()
            while not successfulTransmission:
                # Sends the csv data
                currentHost.send(heldCSVData.encode())
                currentHost.recv(1024)
                # Sends the hashed csv data
                currentHost.send(hashedCSVData.encode())
                # Receives confirmation that the hashed version of the csv data received matches the sent hashed data
                confirmation = currentHost.recv(1024).decode()
                # Transmission was successful so the connection ends
                if confirmation == "True":
                    successfulTransmission = True
                # Transmission failed 4 times so an exception is raised
                elif attempts == 3:
                    successfulTransmission = True
                    currentHost.close()
                    raise Exception('Transmission failed 4 times, try again later')
                else:
                    attempts += 1
            currentHost.close()
        # Receiving a csv from the host for local storage
        else:
            # Informs the host of the clients intent
            currentHost.send("receive".encode())
            while not successfulTransmission:
                # Receives csv data sent by host
                csvData = currentHost.recv(1024).decode()
                # Confirmation of received data
                currentHost.send("True".encode())
                # Receives hashed csv data sent by host
                hashedCSVData = currentHost.recv(1024).decode()
                # Produces the hash of the given data and compares it to the given hash.
                # If they match the transmission was a success, otherwise the transmission failed
                if hashlib.sha256(csvData.encode('utf-8')).hexdigest() == hashedCSVData:
                    hashSuccess = "True"
                else:
                    hashSuccess = "False"
                # Tells the sender if the transmission was a success or failure
                currentHost.send(hashSuccess.encode())
                if hashSuccess == "True":
                    successfulTransmission = True
            currentHost.close()
            # Converts the string, of which contains a list, into a list
            csvDataList = ast.literal_eval(csvData)
            # Writes the received data into a csv
            with open("UserDetails.csv", "w", newline="") as csvFile:
                writer = csv.writer(csvFile)
                for rowData in csvDataList:
                    writer.writerow(rowData)
        ongoingTransmission = False
    # Used to capture and explain known causes of error
    # Error that occurs when an invalid port is given
    except OverflowError as errorMessage:
        print("Invalid port")
        print(f"{errorMessage}\n")
    # Error that occurs when the receiver is not running the program before the sender
    except ConnectionRefusedError:
        print("Given receiver must be running the program before the sender.\n")
    # Error that occurs when an invalid IP is given
    except socket.gaierror:
        print("Invalid IP given\n")
    # Error that occurs when the connection is interrupted
    except ConnectionResetError:
        print("Connection was interrupted\n")
    # Error that occurs when an the given port is not an integer
    except ValueError:
        print("Used port must be an integer\n")
    # Error that occurs when the sender doesn't have the require csv file
    except FileNotFoundError:
        print("'UserDetails.csv' not found\n")
    # Error that occurs when one user in the connection closes ends the connection, this is done when
    # transmission fails 4 times
    except ConnectionAbortedError:
        raise Exception('Transmission failed 4 times, try again later')


print("Complete")