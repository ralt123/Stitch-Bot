"""
Host requires port forwarding. I've already setup port forwarding on my own router so I can host.
"""
# Imports required modules
import socket, csv, hashlib, ast

# Variables to control the main loop and initial host start up
ongoingTransmission = True
initialBooting = False
# Continuously loops whilst hosting
while ongoingTransmission:
    # Uses try expression to capture known errors without ending the entire program whilst explaining to the user the
    # cause of error
    try:
        # Initial startup which sets the port used
        if not initialBooting:
            usedPort = int(input("Input port - "))
            port = usedPort
            initialBooting = True
        # Sets up connection with client
        client = socket.socket()
        client.bind(('', port))
        # Only one client permitted at a time
        client.listen(1)
        client, address = client.accept()
        # Variable used to loop with current client until completion or failure in communicating with the client
        successfulTransmission = False
        print("Connection from " + str(address))
        # Receives the clients request
        clientRequest = client.recv(1024).decode()
        # Send csv data to the user
        if clientRequest == "receive":
            # Retrieves data held in the csv file
            with open("UserDetails.csv", "r") as csvFile:
                heldCSVData = list(csv.reader(csvFile))
            # Raises error if the csv file contains no data
            if not heldCSVData:
                raise Exception("'UserDetails.csv is empty")
            heldCSVData = str(heldCSVData)
            attempts = 0
            # Produces a hash of the csv value, used to ensure data is not lost or modified during transmission
            hashedCSVData = hashlib.sha256(heldCSVData.encode('utf-8')).hexdigest()
            while not successfulTransmission:
                # Sends the csv data
                client.send(heldCSVData.encode())
                client.recv(1024)
                # Sends the hashed csv data
                client.send(hashedCSVData.encode())
                # Receives confirmation that the hashed version of the csv data received matches the sent hashed data
                confirmation = client.recv(1024).decode()
                # Transmission was successful so the connection ends
                if confirmation == "True":
                    successfulTransmission = True
                # Transmission failed 4 times so an exception is raised
                elif attempts == 3:
                    successfulTransmission = True
                    client.close()
                    raise Exception('Transmission failed 4 times, try again later')
                else:
                    attempts += 1
            client.close()
        # Receive a new csv from the user
        else:
            while not successfulTransmission:
                # Receives csv data sent by client
                csvData = client.recv(1024).decode()
                # Confirmation of received data
                client.send("True".encode())
                # Receives hashed csv data sent by client
                hashedCSVData = client.recv(1024).decode()
                # Produces the hash of the given data and compares it to the given hash.
                # If they match the transmission was a success, otherwise the transmission failed
                if hashlib.sha256(csvData.encode('utf-8')).hexdigest() == hashedCSVData:
                    hashSuccess = "True"
                else:
                    hashSuccess = "False"
                # Tells the sender if the transmission was a success or failure
                client.send(hashSuccess.encode())
                if hashSuccess == "True":
                    successfulTransmission = True
            client.close()
            # Converts the string, of which contains a list, into a list
            csvDataList = ast.literal_eval(csvData)
            # Writes the received data into a csv
            with open("UserDetails.csv", "w", newline="") as csvFile:
                writer = csv.writer(csvFile)
                for rowData in csvDataList:
                    writer.writerow(rowData)
        print("Complete\n")
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

