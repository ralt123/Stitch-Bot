"""
ile used for the locally storing data
Importing example

from Local_Store import storageHandler
storageHandler.readUserDetailsDict(776428752281065494)
"""

import csv, os


class local_StorageM:
    """
    Class used for handling local storage
    """
    # Initialises class variables
    def __init__(self):
        self.csvFilePath = "UserDetails.csv"
        self.detailsStored = ["ID", "steam_id", "favourite_streamers", "favourite_games", "favourite_genres"]
        self.listDetails = ["favourite_streamers", "favourite_games", "favourite_genres"]
        self.setCSVPath()

    # Sets the absolute path for the csv file
    def setCSVPath(self):
        filePath = os.path.dirname(__file__)
        self.csvFilePath = os.path.join(filePath, self.csvFilePath)

    def readUserDetails(self, userID):
        """
        Retrieve the stored details regarding a specific user given their ID

        :param userID: str/int - discord ID of the user of interest
        :return: A ordered list containing the users details, following the order of "self.detailsStored"
        """
        # Opens csv containing user data
        with open(self.csvFilePath, "r") as csvFile:
            heldRows = list(csv.reader(csvFile))
        # Prepares important variables for a binary search
        amountOfRows = len(heldRows)
        lowerIndex = 0
        higherIndex = amountOfRows - 1
        userDetails = False
        # Search until the required details are found or all stored details have been searched
        while lowerIndex <= higherIndex:
            currentRowIndex = (higherIndex + lowerIndex)//2
            currentRowID = int(heldRows[currentRowIndex][0])
            # Required details was found
            if currentRowID == userID:
                userDetails = heldRows[currentRowIndex]
                break
            elif currentRowID > userID:
                higherIndex = currentRowIndex - 1
            elif currentRowID < userID:
                lowerIndex = currentRowIndex + 1
        # Returns false if the users data was not found
        if not userDetails:
            return False
        while len(userDetails) != len(self.detailsStored):
            userDetails.append("")
        for i in range(0, len(self.detailsStored)):
            if self.detailsStored[i] in self.listDetails:
                userDetails[i] = userDetails[i].split(",")

        # Returns the users details
        return userDetails

    def readUserDetailsDict(self, userID):
        """
        Retrieve the stored details regarding a specific user given their ID as a dictionary

        :param userID: str/int - discord ID of the user of interest
        :return: A dictionary containing the users details
        """
        # Retrieves the users details as a list or False if their details were not found
        userDetails = self.readUserDetails(userID)
        if not userDetails:
            return False
        # Creates a dictionary containing the users details
        dictDetails = {}
        for i in range(0, len(userDetails)):
            dictDetails[self.detailsStored[i]] = userDetails[i]
        return dictDetails

    # Do not access directly, I will write functions as to correctly format the parameter before passing
    def writeUserDetails(self, *userDetails):
        """
        Used to write a users details to a locally stored csv file

        Formatting when calling method
        storageHandler.writeUserDetails(userID, attributeName, attributeValue, attributeName, attributeValue)
        You can continuously add attribute names and their corresponding values if you follow the format

        :param userDetails: A list containing all arguments passed to the method of which is all the
        provided details regarding the user
        """
        # Ensures passed attribute names are valid
        for i in range(1, len(userDetails), 2):
            if not userDetails[i] in self.detailsStored:
                raise ValueError('Invalid parameters, please refer to method documentation')
        # Retrieves data held in the csv file
        with open(self.csvFilePath, "r") as csvFile:
            heldRows = list(csv.reader(csvFile))
        heldData = False
        # Checks if the users ID is already stored within the csv
        # Run if statement if data is held within the csv
        if len(heldRows) != 0:
            # Prepares important variables for a binary search
            amountOfRows = len(heldRows)
            lowerIndex = 0
            higherIndex = amountOfRows - 1
            userID = userDetails[0]
            # Search until the required details are found or all stored details have been searched
            while lowerIndex <= higherIndex:
                currentRowIndex = (higherIndex + lowerIndex) // 2
                currentRowID = int(heldRows[currentRowIndex][0])
                # Currently held user details were found
                if currentRowID == userID:
                    heldData = heldRows[currentRowIndex]
                    break
                elif currentRowID > userID:
                    higherIndex = currentRowIndex - 1
                elif currentRowID < userID:
                    lowerIndex = currentRowIndex + 1
        # If there was no data held in the csv
        else:
            currentRowIndex = 0

        # Run if the user was already in the list of user details
        if heldData:
            storeData = heldData
            # Ensures the data to be stored is of the expected length
            while len(storeData) != len(self.detailsStored):
                storeData.append("")
            # Sets the data to be stored
            for i in range(1, min(len(self.detailsStored), len(userDetails)), 2):
                # Checks if the attribute name is within the list of stored attributes
                if userDetails[i] in self.detailsStored:
                    # Checks if the attribute name indicates the attribute is to be stored as a list
                    if userDetails[i] in self.listDetails:
                        multipleValue = storeData[self.detailsStored.index(userDetails[i])].split(",")
                        # If the data to be added to the list attribute is already in the list, move that attribute
                        # to the end of the list to represent it's higher importance
                        if userDetails[i+1] in multipleValue:
                            multipleValue.remove(userDetails[i+1])
                            multipleValueString = ""
                            for value in multipleValue:
                                multipleValueString += value + ","
                            storeData[self.detailsStored.index(userDetails[i])] = multipleValueString + str(userDetails[i + 1])
                        # Limits the attributes list to 20 values
                        elif len(multipleValue) > 19:
                            multipleValue = ''.join(multipleValue[1:])
                            storeData[self.detailsStored.index(userDetails[i])] = multipleValue + "," + str(userDetails[i + 1])
                        # Add new value to the end of the list
                        else:
                            storeData[self.detailsStored.index(userDetails[i])] += "," + str(userDetails[i + 1])
                    # Replace the data held for the specific attribute
                    else:
                        storeData[self.detailsStored.index(userDetails[i])] = userDetails[i + 1]
                # Raises error if the attribute name is invalid
                else:
                    raise ValueError("Invalid attribute name - refer to documentation")
        # User had no details stored in the csv
        else:
            # Sets the data to be stored
            storeData = [userDetails[0]]
            for detailData in self.detailsStored[1:]:
                if detailData in userDetails:
                    dataIndex = userDetails.index(detailData) + 1
                    storeData.append(userDetails[dataIndex])
                else:
                    storeData.append("")

        # Writes all users details, including the newly added details, to a ordered csv
        with open(self.csvFilePath, "w", newline="") as csvFile:
            writer = csv.writer(csvFile)
            indexTracker = 0
            for currentRow in heldRows:
                # Users details are being updated
                if heldData and indexTracker == currentRowIndex:
                    storeList = [storeData]
                # Users details are added to csv but the users details were not previously stored
                elif indexTracker == currentRowIndex:
                    # Details to be stored is greater than the lowest details
                    if int(storeData[0]) > int(currentRow[0]):
                        storeList = [currentRow, storeData]
                    else:
                        storeList = [storeData, currentRow]
                else:
                    storeList = [currentRow]
                # Actually writes the data to the csv
                for storeRow in storeList:
                    writer.writerow(storeRow)
                indexTracker += 1
            # Allows writing to an empty csv file
            if not heldRows:
                writer = csv.writer(csvFile)
                writer.writerow(storeData)

storageHandler = local_StorageM()

