"""
File used for the locally storing data
Importing example

from Local_Store import storageHandler
storageHandler.readUserDetailsDict(776428752281065494)
"""

import csv, os, time


class local_StorageM:
    """
    Class used for handling local storage
    """
    # Initialises class variables
    def __init__(self):
        self.userDetailsPath = "UserDetails.csv"
        self.trackedGameData = "TrackedGameData.csv"
        self.trackedStreamData = "TrackedStreamData.csv"
        self.detailsStored = ["ID", "steam_id", "favourite_streamers", "favourite_games", "favourite_genre", "tracked_game", "tracked_streamer", "blacklisted_streamers"]
        self.listDetails = ["favourite_streamers", "favourite_games", "blacklisted_streamers", "tracked_game", "tracked_streamer"]
        self.diDetailsStored = ["tracked_game", "tracked_streamer"]
        self.mentionedSubjectDictionary = {}
        self.setCSVPath()

    # Sets the absolute path for the csv file
    def setCSVPath(self):
        filePath = os.path.dirname(__file__)
        self.userDetailsPath = os.path.join(filePath, self.userDetailsPath)
        self.trackedGameData = os.path.join(filePath, self.trackedGameData)
        self.trackedStreamData = os.path.join(filePath, self.trackedStreamData)

    def trackedGameList(self):
        """
        Used to retrieve all the games of which are being tracked

        :return: list - List containing sublists of which contain a user's ID and the game they are tracking
        """
        # Opens csv containing user data
        with open(self.userDetailsPath, "r") as csvFile:
            heldRows = list(csv.reader(csvFile))
        # Sets the index corresponding to the index of the required data
        requiredDataIndex = self.detailsStored.index("tracked_game")
        trackedList = []
        # Produces the list to be returned
        for userData in heldRows:
            if len(userData) > requiredDataIndex:
                if userData[requiredDataIndex]:
                    trackedList.append([userData[0], userData[requiredDataIndex]])
        # Formats all games as a sublist
        for i in range(len(trackedList)):
            trackedList[i][1] = trackedList[i][1].split(",")
        return trackedList

    def trackedStreamList(self):
        """
        Used to retrieve all the streams of which are being tracked

        :return: list - List containing sublists of which contain a user's ID and the stream they are tracking
        """
        # Opens csv containing user data
        with open(self.userDetailsPath, "r") as csvFile:
            heldRows = list(csv.reader(csvFile))
        # Sets the index corresponding to the index of the required data
        requiredDataIndex = self.detailsStored.index("tracked_streamer")
        trackedList = []
        # Produces the list to be returned
        for userData in heldRows:
            if len(userData) > requiredDataIndex:
                if userData[requiredDataIndex]:
                    trackedList.append([userData[0], userData[requiredDataIndex]])
        # Formats all streamers as a sublist
        for i in range(len(trackedList)):
            trackedList[i][1] = trackedList[i][1].split(",")
        return trackedList

    def checkIfChecked(self, objectID, objectType):
        """
        Checks if a provided tracked object has already been updated for the current day

        :param objectID: int - ID of object
        :param objectType: str - Tracked object type, "steam" or "twitch"
        :return: Boolean - True if the object has been updated for the current day, False otherwise
        """
        # Gets the unix value corresponding to the current date
        currentTime = time.time() // 86400
        if objectType == "steam":
            # Retrieves the details stored regarding the provided object
            objectDetails = self.retrieveTrackedData(objectID, objectType)
            if objectDetails:
                # Compares current date to previously updated date
                if objectDetails[1][-1] // 86400 == currentTime:
                    return True
        elif objectType == "twitch":
            # Retrieves the details stored regarding the provided object
            objectDetails = self.retrieveTrackedData(objectID, objectType)
            if objectDetails:
                # Compares current date to previously updated date
                if objectDetails[1][-1] // 86400 == currentTime:
                    return True
        return False

    def readUserDetails(self, userID):
        """
        Retrieve the stored details regarding a specific user given their ID

        :param userID: str/int - discord ID of the user of interest
        :return: A ordered list containing the users details, following the order of "self.detailsStored"
        """
        # Opens csv containing user data
        with open(self.userDetailsPath, "r") as csvFile:
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

    def writeUserDetails(self, *userDetails):
        """
        Used to write a users details to a locally stored csv file

        Formatting when calling method
        storageHandler.writeUserDetails(userID, attributeName, attributeValue, attributeName, attributeValue)
        You can continuously add attribute names and their corresponding values if you follow the format

        :param userDetails: A tuple containing all arguments passed to the method of which is all the
        provided details regarding the user
        """
        userDetails = list(userDetails)
        # Finding current data held for user

        # Ensures passed attribute names are valid
        for i in range(1, len(userDetails), 2):
            if not userDetails[i] in self.detailsStored:
                raise ValueError('Invalid parameters, please refer to method documentation')
            elif isinstance(userDetails[i+1], str):
                userDetails[i+1] = userDetails[i+1].lower()
            if userDetails[i] == "favourite_streamers":
                userDetails[i+1] = userDetails[i+1].replace(" ", "_")
        # Retrieves data held in the csv file
        with open(self.userDetailsPath, "r") as csvFile:
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

        # Add new data to the user's details

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
                        # Limits the attributes list to 10 values
                        elif len(multipleValue) >= 10 or (userDetails[i] in self.diDetailsStored and len(multipleValue) == 2):
                            multipleValue = ''.join(multipleValue[1:])
                            storeData[self.detailsStored.index(userDetails[i])] = multipleValue + "," + str(userDetails[i + 1])
                        # Add new value to the end of the list
                        else:
                            # There is already data held in the multiple valued attribute
                            if storeData[self.detailsStored.index(userDetails[i])]:
                                storeData[self.detailsStored.index(userDetails[i])] += "," + str(userDetails[i + 1])
                            # The multiple valued attribute held no data
                            else:
                                storeData[self.detailsStored.index(userDetails[i])] += str(userDetails[i + 1])
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

        # Writing the modified details to the csv

        # Writes all users details, including the newly added details, to an ordered csv
        with open(self.userDetailsPath, "w", newline="") as csvFile:
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

    @staticmethod
    def unixToUTC(unixTime):
        """
        Used to convert unix time to UTC

        :param unixTime: int - time to be converted in unix
        :return: List containing the time in UTC
        Return format [day, month, year, hour, minute, second]
        """
        # unix is the seconds since 1/1/1970 00:00 and therefore the method must take into consideration leap days
        daysInMonths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        dayFromLeap = unixTime / 86400
        # when the first leap day occurs from the epoch in days - calculation is left expanded to explain
        firstLeap = (365 * 2) + 31 + 29
        # when the leap day repeats in days - calculation is left expanded to explain
        repeatLeap = (365 * 4) + 1
        leapDays = 0
        # Checks if a leap day must be considered
        if dayFromLeap >= firstLeap:
            dayFromLeap -= firstLeap
            leapDays += 1
            # Removes all leap days from prior years
            while dayFromLeap >= repeatLeap:
                dayFromLeap -= repeatLeap
                leapDays += 1
        # Checks if the year of the date is a leap year
        if dayFromLeap < 366 - (31 + 29):
            daysInMonths[1] = 29
            leapDays -= 1
        day = (unixTime / 86400) - leapDays
        # Run if year of date is leap year
        if daysInMonths[1] == 29:
            year = 1970 + (day - 1) / 365
            day = (day - 1) % 365
            # Adds removed day
            day += 1
        else:
            year = 1970 + day / 365
            day = day % 365
        month = 1
        # Calculates the month and day
        while day > daysInMonths[month - 1]:
            day -= daysInMonths[month - 1]
            month += 1
        # As epoch is from 1st of jan not 0 of jan, add a day
        day += 1
        hour = (day % 1) * 24
        minute = (hour % 1) * 60
        second = round((minute % 1) * 60)
        timeList = [int(day), int(month), int(year), int(hour), int(minute), second]
        return timeList

    def deleteUserDetails(self, *userDetails):
        """
        Used to delete a given detail regarding a user to allow for changing preferences

        Formatting when calling method - each specified value with the correct attribute name will be removed
        storageHandler.deleteUserDetails(userID, attributeName, attributeValue, attributeName, attributeValue)
        You can continuously add attribute names and their corresponding values if you follow the format

        :param userDetails: A tuple containing all arguments passed to the method of which is all the
        details to be deleted
        :return: Boolean - Returns False if the user was not found in local storage
        """
        # Casts the tuple containing passed arguments into a list
        userDetails = list(userDetails)

        # Ensures passed attribute names are valid
        for i in range(1, len(userDetails), 2):
            if not userDetails[i] in self.detailsStored:
                raise ValueError('Invalid parameters, please refer to method documentation')
            # Ensures all strings are lowercase
            elif isinstance(userDetails[i + 1], str):
                userDetails[i + 1] = userDetails[i + 1].lower()
            if userDetails[i] == "favourite_streamers":
                userDetails[i + 1] = userDetails[i + 1].replace(" ", "_")
        # Retrieves data held in the csv file
        with open(self.userDetailsPath, "r") as csvFile:
            heldRows = list(csv.reader(csvFile))
        heldData = False
        # Checks if the users ID is stored within the csv
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

        # Removes data from user details

        # Run if the user was found in the list of user details
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
                        # Deletes data in list
                        if userDetails[i+1] in multipleValue:
                            multipleValue.remove(userDetails[i+1])
                    # Delete the data held for the specific attribute
                    else:
                        storeData[self.detailsStored.index(userDetails[i])] = ""
                # Raises error if the attribute name is invalid
                else:
                    raise ValueError("Invalid attribute name - refer to documentation")
        # User had no details stored in the csv
        else:
            return False

        # Writing the modified details to the csv

        # Writes all users details, discarding the deleted details, to an ordered csv
        with open(self.userDetailsPath, "w", newline="") as csvFile:
            writer = csv.writer(csvFile)
            indexTracker = 0
            for currentRow in heldRows:
                # Users details are being updated
                if heldData and indexTracker == currentRowIndex:
                    storeList = [storeData]
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

    def storeTrackedData(self, ID, dataCount, trackedType):
        """
        Used to store details regarding a tracked game/streamer.

        :param ID: int - ID of streamer/game to be stored
        :param dataCount: int - current player count for games and current view count for streamers
        :param trackedType: str - either "twitch" or "steam" to indicate the platform of which the ID originates from
        """
        # Determines the csv to be used
        if trackedType == "twitch":
            storageFile = self.trackedStreamData
        elif trackedType == "steam":
            storageFile = self.trackedGameData
        else:
            raise Exception("Invalid arguments, refer to documentation")

        # Retrieves data held in the csv file
        with open(storageFile, "r") as csvFile:
            heldRows = list(csv.reader(csvFile))
        heldData = False
        ID = int(ID)
        dataCount = int(dataCount)
        # Checks if the  ID is already stored within the csv
        # Run if statement if data is held within the csv
        if len(heldRows) != 0:
            # Prepares important variables for a binary search
            amountOfRows = len(heldRows)
            lowerIndex = 0
            higherIndex = amountOfRows - 1
            # Search until the required details are found or all stored details have been searched
            while lowerIndex <= higherIndex:
                currentRowIndex = (higherIndex + lowerIndex) // 2
                currentRowID = int(heldRows[currentRowIndex][0])
                # Details for the given ID were found
                if currentRowID == ID:
                    heldData = heldRows[currentRowIndex]
                    break
                elif currentRowID > ID:
                    higherIndex = currentRowIndex - 1
                elif currentRowID < ID:
                    lowerIndex = currentRowIndex + 1
        # If there was no data held in the csv
        else:
            currentRowIndex = 0

        # Add new data to the user's details

        # Run if the ID was already in the list of user details
        if heldData:
            storeData = heldData
            currentDate = self.unixToUTC(time.time())[:3]
            # List containing recorded dates
            previousDates = storeData[1].split(",")
            # List containing records view/player count on a given date
            previousDataCounts = storeData[2].split(",")
            # Variable containing last stored date
            recordedDate = self.unixToUTC(int(previousDates[-1:][0]))[:3]
            # Checks if data for the current date was already stored
            if recordedDate == currentDate:
                # Adjusts previously stored data
                previousAverage = int(previousDataCounts[-1:][0])
                timesRecorded = int(storeData[3])
                newAverage = (previousAverage * timesRecorded + dataCount) / (timesRecorded + 1)
                previousDataCounts[len(previousDataCounts)-1] = int(newAverage)
                storeData[3] = timesRecorded + 1
            # Current date was not stored
            else:
                # Maximum amount of data for a single tracked game/streamer reached
                if len(previousDates) == 21:
                    # Removes oldest data
                    previousDates = previousDates[1:]
                    previousDataCounts = previousDataCounts[1:]
                # Adds new data for storage
                previousDates.append(int(time.time()))
                previousDataCounts.append(dataCount)
                storeData[3] = 1

            # Produces a string for storage of which corresponds to a list
            previousDatesString = ""
            for date in previousDates:
                previousDatesString += str(date) + ","
            previousDatesString = previousDatesString[:-1]

            # Produces another string for storage of which corresponds to a list
            previousCountsString = ""
            for playerCount in previousDataCounts:
                previousCountsString += str(playerCount) + ","
            previousCountsString = previousCountsString[:-1]

            storeData[1] = previousDatesString
            storeData[2] = previousCountsString
        # ID was not already stored
        else:
            # Simply add new ID with related data for storage
            storeData = [ID, int(time.time()), dataCount, 1]
        # Writing the modified details to the csv

        # Writes all tracked details of a given type, including the newly added details, to an ordered csv
        with open(storageFile, "w", newline="") as csvFile:
            writer = csv.writer(csvFile)
            indexTracker = 0
            for currentRow in heldRows:
                # ID details are being updated
                if heldData and indexTracker == currentRowIndex:
                    storeList = [storeData]
                # ID details are added to csv but the users details were not previously stored
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

    def retrieveTrackedData(self, ID, trackedType):
        """
        Used to retrieve tracked data for a specific game/streamer given their ID

        :param ID: int - ID of streamer/game
        :param trackedType: str - either "twitch" or "steam" to indicate the platform of which the ID originates from
        :return: list - list containing stored details regarding the given ID
        Returns False if no details regarding the ID are stored
        """
        # Determines the csv to be used
        if trackedType == "twitch":
            storageFile = self.trackedStreamData
        elif trackedType == "steam":
            storageFile = self.trackedGameData
        else:
            raise Exception("Invalid arguments, refer to documentation")

        # Retrieves data held in the csv file
        with open(storageFile, "r") as csvFile:
            heldRows = list(csv.reader(csvFile))
        heldData = False
        ID = int(ID)
        # Checks if the tracked ID is stored within the csv
        if len(heldRows) != 0:
            # Prepares important variables for a binary search
            amountOfRows = len(heldRows)
            lowerIndex = 0
            higherIndex = amountOfRows - 1
            # Search until the required details are found or all stored details have been searched
            while lowerIndex <= higherIndex:
                currentRowIndex = (higherIndex + lowerIndex) // 2
                currentRowID = int(heldRows[currentRowIndex][0])
                # Required ID data was found
                if currentRowID == ID:
                    heldData = heldRows[currentRowIndex]
                    break
                elif currentRowID > ID:
                    higherIndex = currentRowIndex - 1
                elif currentRowID < ID:
                    lowerIndex = currentRowIndex + 1
        # If there was no data held in the csv
        else:
            return False
        if not heldData:
            return False

        # Converts multiple value strings within the list into a list
        heldData[1] = heldData[1].split(",")
        heldData[2] = heldData[2].split(",")
        # Casting the values within the sublist into integers
        for i in range(0, len(heldData[1])):
            heldData[1][i] = int(heldData[1][i])
            heldData[2][i] = int(heldData[2][i])

        return heldData

    def automaticPreferences(self, userID, subjectName, mentionedSubject):
        """
        Used to allow automatic preference setting.
        If the same subject is mentioned 5 times, with each mentioning being less than an hour apart, that subject
        is set as a preference for that user.

        :param userID: int - Steam ID of user
        :param subjectName: str - Type of subject being mentioned
        :param mentionedSubject: str - Subject being mentioned
        :return: boolean - True if the subject was set as a preference, False otherwise
        """
        # Gets the current time
        currentTime = int(time.time())
        # Checks if the user has any previously mentioned subjects stored
        if userID in self.mentionedSubjectDictionary.keys():
            # Checks if the mentioned subject was previously mentioned
            if mentionedSubject in self.mentionedSubjectDictionary[userID].keys():
                # Subject was last mentioned within an hour
                if self.mentionedSubjectDictionary[userID][mentionedSubject + "Time"] + 3600 > currentTime:
                    self.mentionedSubjectDictionary[userID][mentionedSubject] += 1
                else:
                    self.mentionedSubjectDictionary[userID][mentionedSubject] = 1
                # Sets the time of which the subject was last mentioned
                self.mentionedSubjectDictionary[userID][mentionedSubject + "Time"] = currentTime
                # Subject was mentioned 5 times with less than an hour between each mentioning
                if self.mentionedSubjectDictionary[userID][mentionedSubject] == 5:
                    # Sets the mentioned subject as a preference
                    self.writeUserDetails(userID, subjectName, mentionedSubject)
                return True
        # Adds the mentioned subject to the mentionedSubjectDictionary with the mentioning time
        self.mentionedSubjectDictionary[userID] = {mentionedSubject: 1}
        self.mentionedSubjectDictionary[userID][mentionedSubject + "Time"] = currentTime
        return False


# Creates object
storageHandler = local_StorageM()

