"""
FINISH COMMENTING AND POLISHING LATER

File used for the locally storing data
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
        filePath = os.path.dirname(__file__)
        csvFileName = "UserDetails.csv"
        self.csvFilePath = os.path.join(filePath, csvFileName)
        self.detailsStored = ["ID", "steam_id", "favourite_streamers", "favourite_games", "favourite_genres"]
        self.listDetails = ["favourite_streamers", "favourite_games", "favourite_genres"]

    def readUserDetails(self, userID):
        """
        Retrieve the details about a specific user given their ID

        :param userID:
        :return:
        """
        rows = []
        with open(self.csvFilePath, "r") as csvFile:
            for row in csv.reader(csvFile):
                if row and row[0]:
                    rows.append(row)
        amountOfRows = len(rows)
        lowerIndex = 0
        higherIndex = amountOfRows - 1
        userDetails = False
        while lowerIndex <= higherIndex:
            currentRowIndex = (higherIndex+lowerIndex)//2
            currentRowID = int(rows[currentRowIndex][0])
            if currentRowID == userID:
                userDetails = rows[currentRowIndex]
                break
            elif currentRowID > userID:
                higherIndex = currentRowIndex - 1
            elif currentRowID < userID:
                lowerIndex = currentRowIndex + 1
        if not userDetails:
            return False
        while len(userDetails) != len(self.detailsStored):
            userDetails.append("")
        for i in range(0, len(self.detailsStored)):
            if self.detailsStored[i] in self.listDetails:
                userDetails[i] = userDetails[i].split(",")

        return userDetails


    def readUserDetailsDict(self, userID):
        userDetails = self.readUserDetails(userID)
        if not userDetails:
            return False
        dictDetails = {}
        for i in range(0, len(userDetails)):
            dictDetails[self.detailsStored[i]] = userDetails[i]
        return dictDetails


    # Do not access directly, I will write functions as to correctly format the parameter before passing
    def writeUserDetails(self, *userDetails):
        """
        Writes the user's details to a locally stored CSV file.

        # To be changed
        If the user's ID is found to be already within the CSV file, old data is overwritten
        Otherwise, a new row is created to hold the details at the correct position to maintain order.
        """
        rows = []
        # Ensures passed keys are valid
        for i in range(1, len(userDetails), 2):
            if not userDetails[i] in self.detailsStored:
                raise ValueError('Invalid parameters, please refer to method documentation')
        with open(self.csvFilePath, "r") as csvFile:
            for row in csv.reader(csvFile):
                if row and row[0]:
                    rows.append(row)
        heldData = False
        if len(rows) != 0:
            amountOfRows = len(rows)
            lowerIndex = 0
            higherIndex = amountOfRows - 1
            userID = userDetails[0]
            while lowerIndex <= higherIndex:
                currentRowIndex = (higherIndex + lowerIndex) // 2
                currentRowID = int(rows[currentRowIndex][0])
                belowRowID = int(rows[currentRowIndex-1][0])
                if currentRowID == userID:
                    heldData = rows[currentRowIndex]
                    break
                elif False and belowRowID == userID:
                    currentRowIndex -= 1
                    heldData = rows[belowRowID]
                    break
                elif False and higherIndex - lowerIndex < 2:
                    if higherIndex == 1:
                        currentRowIndex = 0
                        break
                    elif lowerIndex == amountOfRows - 2:
                        if int(rows[currentRowIndex+1][0]) <= userID:
                            currentRowIndex += 2
                        break
                elif currentRowID > userID > belowRowID:
                    break
                elif currentRowID > userID:
                    higherIndex = currentRowIndex - 1
                elif currentRowID < userID:
                    lowerIndex = currentRowIndex + 1
        else:
            currentRowIndex = 0

        if heldData:
            storeData = rows[currentRowIndex]
            while len(storeData) != len(self.detailsStored):
                storeData.append("")
            # for i in range(1, len(userDetails)):
            for i in range(1, min(len(self.detailsStored), len(userDetails)), 2):
                # For now we only overwrite held data
                if userDetails[i] in self.detailsStored:
                    if userDetails[i] in self.listDetails and userDetails[i] != "":
                        multipleValue = storeData[self.detailsStored.index(userDetails[i])].split(",")
                        if userDetails[i+1] in multipleValue:
                            multipleValue.remove(userDetails[i+1])
                            multipleValueString = ""
                            for value in multipleValue:
                                multipleValueString += value + ","
                            storeData[self.detailsStored.index(userDetails[i])] = multipleValueString + str(userDetails[i + 1])
                            # CHECK AGAIN
                        elif len(multipleValue) > 19:
                            multipleValue = ''.join(multipleValue[1:])
                            storeData[self.detailsStored.index(userDetails[i])] = multipleValue + "," + str(userDetails[i + 1])
                        else:
                            storeData[self.detailsStored.index(userDetails[i])] += "," + str(userDetails[i + 1])
                    else:
                        storeData[self.detailsStored.index(userDetails[i])] = userDetails[i + 1]
                else:
                    raise ValueError("Invalid attribute name - refer to documentation")
        else:
            # Add the ability to change a users ID such that they can transfer data across accounts
            storeData = [userDetails[0]]
            for detailData in self.detailsStored[1:]:
                if detailData in userDetails:
                    dataIndex = userDetails.index(detailData) + 1
                    storeData.append(userDetails[dataIndex])
                else:
                    storeData.append("")

        with open(self.csvFilePath, "w", newline="") as csvFile:
            writer = csv.writer(csvFile)
            indexTracker = 0
            for currentRow in rows:
                if heldData and indexTracker == currentRowIndex:
                    storeList = [storeData]
                elif indexTracker == currentRowIndex:
                    if int(storeData[0]) > int(currentRow[0]):
                        storeList = [currentRow, storeData]
                    else:
                        storeList = [storeData, currentRow]
                else:
                    storeList = [currentRow]
                for storeRow in storeList:
                    writer.writerow(storeRow)
                indexTracker += 1
            # Allows writing to an empty csv file
            if not rows:
                with open(self.csvFilePath, "w", newline="") as csvFile:
                    writer = csv.writer(csvFile)
                    writer.writerow(storeData)

storageHandler = local_StorageM()