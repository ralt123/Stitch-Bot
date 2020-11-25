"""
File used for the steam API
Importing example

from Steam_API import steamHandler
steamHandler.gamePlayerCount(730)
"""

import urllib.request, json, os
from Discord_chatbot.Data_Control_Files.Local_Store import storageHandler
from Encryption import encryptionAES128


class steam_APIM:
    """
    Class used for handling the steam API
    """
    # Initialises class variables
    def __init__(self):
        # Do not change this variable, input the keys in the text file
        self.__apiKey = ""
        self.gameList = "gameList.json"
        self.__setKeys()
        self.setGameListPath()

    # Sets the crucial API keys
    def __setKeys(self):
        filePath = os.path.dirname(__file__)

        # setting decrypt key
        decrypt_key_path = os.path.join(filePath, "Encrypted_keys\Decrypt_key")
        with open(decrypt_key_path, 'r') as decrypt_key_file:
            decrypt_key = decrypt_key_file.read()
        encryption = encryptionAES128(decrypt_key)

        steam_key_path = os.path.join(filePath, "Encrypted_keys\Steam_key.txt")
        with open(steam_key_path, 'rb') as steam_key_file:
            encrypted_steam_key = steam_key_file.read()
        self.__auth = encryption.decrypt(encrypted_steam_key)

        # old key import code:
        '''
        filePath = os.path.dirname(__file__)
        keyFile = os.path.join(filePath, 'Keys_DO_NOT_UPLOAD.txt')
        # Retrieves keys from the text file. Text file is used to simplicity and ease of editing for my peers.
        with open(keyFile, 'r') as keyFile:
            keyData = keyFile.read()
        keyData = keyData.replace(" ", "")
        keyDataList = keyData.split("\n")
        # decrypting keys:
        for i in range(0, len(keyDataList)):
            keyDataValue = keyDataList[i].split("=")
            if keyDataValue[0] == "Steamkey":
                self.__apiKey = keyDataValue[1]
        if self.__apiKey == "":
            raise ValueError('Missing API key/s - Please check the Keys text file.')
        '''

    # Sets the absolute path for the game list
    def setGameListPath(self):
        filePath = os.path.dirname(__file__)
        self.gameList = os.path.join(filePath, self.gameList)

    @staticmethod
    def retrieveData(url):
        """
        Used to retrieve data from the given url

        :param url: String containing the url of the required data
        :return: The data retrieved from the given url as a dictionary
        """
        # Opens the webpage for data retrieval, page is closed once the data is retrieved
        try:
            with urllib.request.urlopen(url) as openPage:
                data = json.loads(openPage.read().decode())
        except urllib.error.HTTPError as errorMessage:
            raise ValueError(
                f"HTTPError Possible causes - Possible API outage, invalid URL or incorrect API key/s\n{errorMessage}")
        return data

    # Merge sort method was made myself so it's efficiency may not be optimal but it shall suffice
    # As storing the game list is not for frequent use, I don't plan on continuing to optimise the sorting method.
    # Uses iteration over recursion as the large size of the gameList to be sorted would use a lot of space in recursion
    def _gameListMergeSort(self, unsortedGL):
        """
        Method used to sort the list of all steam games by name.

        :param unsortedGL: unsorted game list as a list containing dictionaries of which contain individual game data
        :return: List of all sorted steam games, ascending
        """
        startingSize = len(unsortedGL)

        # Converts names into their alphanumeric equivalent so they are easier for user to specify
        for i in range(0, len(unsortedGL)):
            unsortedGL[i]["name"] = self.stringForComparison(unsortedGL[i]["name"])

        # Sorts every pair to be in order
        for i in range(0, len(unsortedGL) - 1, 2):
            if unsortedGL[i + 1]["name"] < unsortedGL[i]["name"]:
                unsortedGL[i], unsortedGL[i + 1] = unsortedGL[i + 1], unsortedGL[i]

        # Combines every pair into a small list
        for i in range(0, len(unsortedGL) // 2, 1):
            unsortedGL[i:i + 2] = [[unsortedGL[i], unsortedGL[i + 1]]]

        # If there's an odd number of elements, the final element replaced with a list containing only itself
        if startingSize % 2 != 0:
            unsortedGL[-1:] = [unsortedGL[-1:]]

        # Sorts all the pairs into a single sorted list
        # Repeats until only a single list remains
        while len(unsortedGL) != 1:
            # Combines every pair of lists into a single sorted list until only a single sorted list remains
            for i in range(0, len(unsortedGL) // 2, 1):
                sortedList = []
                # Assigns pointers to mark out the two lists being combined
                leftPointer = 0
                leftMax = len(unsortedGL[i])
                rightPointer = 0
                rightMax = len(unsortedGL[i + 1])
                # Repeat until a pair of the two lists is a subset of the sorted list
                while rightPointer != rightMax and leftPointer != leftMax:
                    if unsortedGL[i][leftPointer]["name"] < unsortedGL[i + 1][rightPointer]["name"]:
                        sortedList.append(unsortedGL[i][leftPointer])
                        leftPointer += 1
                    else:
                        sortedList.append(unsortedGL[i + 1][rightPointer])
                        rightPointer += 1
                # Appends the remaining elements to the sorted list
                if leftPointer != leftMax:
                    while leftPointer != leftMax:
                        sortedList.append(unsortedGL[i][leftPointer])
                        leftPointer += 1
                elif rightPointer != rightMax:
                    while rightPointer != rightMax:
                        sortedList.append(unsortedGL[i + 1][rightPointer])
                        rightPointer += 1
                unsortedGL[i:i + 2] = [sortedList]
        # Returns the sorted list
        return unsortedGL[0]

    def storeGameList(self):
        """
        Locally stores a sorted list of all steams games as requesting the data from the API whenever the data is
        required would create a bottleneck due to lackluster transfer speeds
        """
        # Retrieves basic information regarding all steam games from a webpage
        url = "http://api.steampowered.com/ISteamApps/GetAppList/v0002/?format=json"
        with urllib.request.urlopen(url) as openPage:
            pageData = json.loads(openPage.read().decode())
        pageData = pageData["applist"]["apps"]
        # Sorts the game list by name using merge sort
        sortedGameList = self._gameListMergeSort(pageData)
        # Stores the data in a .json file
        with open(self.gameList, "w") as jsonFile:
            json.dump(sortedGameList, jsonFile)

    def findGameID(self, gameName):
        """
        Searches for the ID of a given game by searching through a .json file containing every steam game with their
        respective ID and game name.
        Once the game is found within the .json file, the games ID is returned.
        If the game isn't found, False is returned
        Uses a simple linear search due to the data being unordered - Likely be improved in future

        :param gameName: str - name of steam game
        :return: steamID of given game as a string or False if the ID was not found
        """
        # Retrieves the steam game list
        with open(self.gameList, "r") as jsonFile:
            gameListData = json.load(jsonFile)

        searchingForIDs = True
        gameIDs = []
        gameName = self.stringForComparison(gameName)
        # As some games have the same name, searching only concludes until all games of a given name are found
        while searchingForIDs:
            # Sets key variables such as the higher and lower index
            amountOfRows = len(gameListData)
            lowerIndex = 0
            higherIndex = amountOfRows - 1
            searchingForIDs = False
            # Repeats until the game is found within the list or until the entire list has been searched
            while lowerIndex <= higherIndex:
                currentGameIndex = (higherIndex + lowerIndex) // 2
                currentGameName = self.stringForComparison(gameListData[currentGameIndex]["name"])
                # Game has been found and the game's ID is returned
                if currentGameName == gameName:
                    gameIDs.append(gameListData[currentGameIndex]["appid"])
                    gameListData.pop(currentGameIndex)
                    searchingForIDs = True
                    break
                # Game to be found is above the current game
                elif currentGameName > gameName:
                    higherIndex = currentGameIndex - 1
                # Game to be found is below the current game
                elif currentGameName < gameName:
                    lowerIndex = currentGameIndex + 1
        # If multiple games have the same name, the game with the highest player count has it's ID returned
        highestIndex = 0
        # Returns the games ID if it was found, returns false otherwise
        if len(gameIDs) == 0:
            return False
        elif len(gameIDs) != 1:
            # Compares the popularity of each game to decide which to return
            highestCount = self.gamePlayerCount(gameIDs[0])
            for i in range(1, len(gameIDs)):
                currentCount = self.gamePlayerCount(gameIDs[i])
                if currentCount > highestCount:
                    highestCount = currentCount
                    highestIndex = i
        return gameIDs[highestIndex]

    # Not official steam API
    def top10Games(self, userID=False):
        """
        Uses a non-official steam API to retrieve the top 10 games in the past 2 weeks.
        Optionally, by providing a user ID these games will be of the user's favourite genre.

        :param userID: int - discord ID of user (optional)
        :return: list - A list containing True/False at the 0th index, True means that the list of game's returned are
        of the user's favourite genre. The 1st index contains a sublist of the top games in the past 2 weeks.
        """
        # userID was provided and so their favourite genre is utilized
        if userID:
            # Retrieves the user's favourite genre
            userDetails = storageHandler.readUserDetails(userID)
            # User was found within storage and posses a favourite genre
            if userDetails:
                # Formatting required for the API
                favouriteGenre = userDetails[4].replace(" ", "+")
                url = "https://steamspy.com/api.php?request=tag&tag=" + favouriteGenre
        # userID not passed or the user's favourite genre could not be found
        if not userID:
            url = "https://steamspy.com/api.php?request=top100in2weeks"
        # This API suffers outages thus a try statement is used to prevent an outage from ending the program
        try:
            # Retrieves the data regarding the top games
            topGamesData = self.retrieveData(url)
        except json.decoder.JSONDecodeError:
            return False
        topGames = []
        retrievedGames = 0
        # Extracts necessary data
        for dictKey in topGamesData.keys():
            topGames.append(topGamesData[dictKey]["name"])
            retrievedGames += 1
            if retrievedGames == 10:
                break
        # Returns the data, with the boolean at the 0th index indicating whether the user's favourite genre was utilized
        if userID:
            return [True, topGames]
        else:
            return [False, topGames]

    def gamePlayerCount(self, gameID):
        """
        Returns the current player count of a game given its steam gameID
        If the gameID is invalid then False is returned

        :param gameID: str or int - ID of the steam game
        :return: Player count of game specified by gameID as an integer or False if the gameID is invalid
        """
        # Defines the webpage that contains the required data
        url = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=" + str(gameID)
        # Opens the webpage for data retrieval, page is closed once the data is retrieved
        data = self.retrieveData(url)
        if not data:
            return False
        # Returns player count as a an integer
        return int(data["response"]["player_count"])

    def gameDescription(self, gameID):
        """
        Returns a short description of a game given it's steam gameID

        :param gameID: str or int - ID of the steam game
        :return: The short description for the given steam game, retrieved by using the steam API, as a string
        """
        # Defines the webpage that contains the required data
        url = "https://store.steampowered.com/api/appdetails?l=en&appids=" + str(gameID)
        # Opens the webpage for data retrieval, page is closed once the data is retrieved
        data = self.retrieveData(url)
        # Returns short description
        return data[str(gameID)]["data"]["short_description"]

    def getUserSteamID(self, userURL):
        """
        Used to find the steam ID of a user given their steam vanity ID string.
        The required section of the user's URL is the unique portion of which acts as an ID

        https://steamcommunity.com/id/vanityID/

        :param userURL: str or int - The unique vanity ID of the user's URL
        :return:
        """
        # Defines the webpage that contains the required data
        url = "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=" + self.__apiKey + \
              "&vanityurl=" + str(userURL)
        # Opens the webpage for data retrieval, page is closed once the data is retrieved
        data = self.retrieveData(url)
        if data["response"]["success"] == 1:
            return data["response"]["steamid"]
        else:
            # Check if the steamID retrival failed as their vanity URL is their steam ID
            url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key=" + self.__apiKey + \
                  "&steamids=" + str(userURL)
            data = self.retrieveData(url)
            if len(data["response"]["players"]) == 0:
                return False
            return userURL

    def getCSGOStats(self, userSteamID):
        """
        Retrieves the stats for a player given their steam id for the popular FPS Counter Strike Global Offensive.
        Counter Strike Global Offensive is being used due to it's popularity and available api.
        Returns false is the given ID is invalid or if the user's stats are private

        :param userSteamID: str/int - ID of the user of which stats are being retrieved
        :return: A dictionary containing the user's stats or False if the data could not be retrieved
        """
        # Defines the web page that contains the required data
        url = "http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid=730&key=" + \
              str(self.__apiKey) + "&steamid=" + str(userSteamID)

        # Retrieves data
        data = self.retrieveData(url)
        if not data:
            return False
        data = data["playerstats"]["stats"]
        # Creates the dictionary containing the user's stats
        statsDict = {}
        for i in range(0, len(data)):
            dataSection = data[i]
            statsDict[dataSection["name"]] = dataSection["value"]
        return statsDict

    def getGamePrice(self, gameID):
        """
        Used to retrieve the price of a game on steam given its steam game ID

        :param gameID: str/int - Game ID of the game in question
        :return: A dictionary containing price data regarding the given name
        """
        # Defines the webpage that contains the required data
        url = "https://store.steampowered.com/api/appdetails?appids=" + str(gameID)
        # Opens the webpage for data retrieval, page is closed once the data is retrieved
        data = self.retrieveData(url)
        # Generates the dictionary to be returned
        if "price_overview" in data[str(gameID)]["data"]:
            priceDict = {"normal_price": data[str(gameID)]["data"]["price_overview"]["initial_formatted"],
                         "current_price": data[str(gameID)]["data"]["price_overview"]["final_formatted"],
                         "free": False}
            # Checks if the game is on deal
            if priceDict["normal_price"]:
                priceDict["on_deal"] = "True"
            else:
                priceDict["on_deal"] = "False"
            return priceDict
        # Returns short description
        if data[str(gameID)]["data"]["is_free"]:
            return {"free": True}
        return False

    def checkPlayingGame(self, userID):
        """
        Used to return the name of the game a given user is currently playing.

        :param userID: str/int - Steam ID of user
        :return: str/boolean - Name of game the user is playing, False if the given ID was invalid
        and returns the string "nothing/private" if the user is not playing a game or has a private profile
        """
        # Retrieving required data regarding the user
        url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?steamids={str(userID)}&key={self.__apiKey}"
        userInfo = self.retrieveData(url)
        # Returns False if the given ID was invalid
        if len(userInfo["response"]["players"]) == 0:
            return False
        else:
            # Extracts user info
            userInfo = userInfo["response"]["players"][0]
        # If the user is playing a game the game's name is returned
        if "gameextrainfo" in userInfo:
            return userInfo["gameextrainfo"]
        else:
            return "nothing/private"

    @staticmethod
    def stringForComparison(rawString):
        """
        Used to alter a given string to only contain alphanumeric characters, lower case only.
        Used to allow non-exact searches in an algorithm to return the desired result

        :param rawString: str - String to be altered
        :return: str - rawString but altered to only contain alphanumeric lowercase characters
        """
        # Changes string to prepare for comparison, most commands used are self explanatory
        if rawString.isalnum():
            preparedString = rawString.lower()
        # Could check if the string is alphanumeric after removing a non-alphanumeric character but not necessary as
        # only short strings will be used
        else:
            preparedString = ""
            # Removes any non-alphanumeric characters
            for character in rawString:
                if character.isalnum():
                    preparedString += character
            preparedString = preparedString.lower()
        return preparedString

    # Tried using a new implementation of discord of which I haven't used before
    # Uses recursion and efficiency could be improved however as I plan on only using
    # this method for relatively small lists of data, to save time, it should suffice
    def _friendQuickSort(self, playingFriends):
        """
        Used to sort a list of sub lists containing a user and the game they are currently playing

        :param playingFriends: list - list of sub lists containing a user and the game they are currently playing
        :return: list - the given list but sorted by game
        """
        # Implementation of quicksort
        # Key variables
        pivot = self.stringForComparison(playingFriends[-1:][0][1])
        pivotData = playingFriends[-1:][0]
        toSort = playingFriends[:-1]
        marker1 = 0
        marker2 = len(toSort) - 1
        marker1Stopped = False
        marker2Stopped = False
        # Whilst the markers are not adjacent
        while marker1 < marker2 - 1:
            if not marker1Stopped:
                # Stops marker as an out of place element has been found
                if self.stringForComparison(toSort[marker1][1]) > pivot:
                    marker1Stopped = True
                # Moves maker as the element was in place
                else:
                    marker1 += 1
            # Marker1 has priority so this is only ran when marker1 has stopped
            if marker1Stopped and not marker2Stopped:
                # Stops marker as an out of place element has been found
                if toSort[marker2][1].lower() < pivot:
                    marker2Stopped = True
                # Moves maker as the element was in place
                else:
                    marker2 -= 1
            # Run when both markers have stopped as hey have both encountered an out of place element
            if marker1Stopped and marker2Stopped:
                # Swaps out of place elements and sets the markers as being mobile
                toSort[marker1], toSort[marker2] = toSort[marker2], toSort[marker1]
                marker1Stopped, marker2Stopped = False, False
                marker1 += 1
                if marker1 < marker2 - 1:
                    marker2 -= 1
        # Ensures the element at marker2 is sorted as the previous while loop may end with unsorted data due to
        # marker1 being given priority
        if self.stringForComparison(toSort[marker2][1]) < pivot:
            toSort[marker1], toSort[marker2] = toSort[marker2], toSort[marker1]
        # If the element at marker1 is larger than the pivot, the pivot is below that element
        if self.stringForComparison(toSort[marker1][1]) > pivot:
            toSort.append(pivot)
            toSort[marker1], toSort[len(toSort) - 1] = toSort[len(toSort) - 1], toSort[marker1]
            lowerSection = toSort[0:marker1]
            higherSection = toSort[marker1 + 1:]
        # If the element at marker2 is larger than the pivot, the pivot is below that element
        elif self.stringForComparison(toSort[marker2][1]) > pivot:
            toSort.append(pivot)
            toSort[marker2], toSort[len(toSort) - 1] = toSort[len(toSort) - 1], toSort[marker2]
            lowerSection = toSort[0:marker2]
            higherSection = toSort[marker2 + 1:]
        # If the element at marker2+1 is larger than the pivot, the pivot is below that element
        elif marker2 + 1 < len(toSort) and toSort[marker2 + 1][0] > pivot:
            toSort.append(pivot)
            toSort[marker2 + 1], toSort[len(toSort) - 1] = toSort[len(toSort) - 1], toSort[marker2 + 1]
            lowerSection = toSort[0:marker2 + 1]
            higherSection = toSort[marker2 + 2:]
        # The pivot is larger than all elements in the list
        else:
            lowerSection = toSort[:]
            higherSection = []
        # Recursive calls to sort each section
        if len(lowerSection) > 1:
            lowerSection = self._friendQuickSort(lowerSection)
        if len(higherSection) > 1:
            higherSection = self._friendQuickSort(higherSection)
        # Prepares the list in a suitable format for returning
        passResult = []
        for i in lowerSection:
            passResult.append(i)
        passResult.append(pivotData)
        for i in higherSection:
            passResult.append(i)
        return passResult

    def friendsPlayingGame(self, userID):
        """
        Used to retrieve a sorted list of a user's friends of which are currently playing a game
        and the name of the game the user is playing

        :param userID: str/int - Steam ID of the user
        :return: list/Boolean - sorted list of sub lists containing their friends name and the game their friend is
        playing or False if the user has no friends or if their friends list is private
        Example of returned list [[Andrew, Rocket League], [Jim, Counter Strike: Global Offensive]]
        """
        # Retrieves a list containing the user's friends
        allFriends = self.getFriends(userID)
        # Returns False if the user has no friends or if their friends list is priviate
        if not allFriends:
            return False
        url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?steamids="
        friendsList = []
        # Can only check what games at most 100 users are playing through the steam API
        for i in range(0, len(allFriends)):
            # URL must be modified to contain the ID of at most 100 friends of the user
            url += "," + allFriends[i]["steamid"]
            # API call has reached it's maximum length, perform the call and prepare another
            if (i + 1) % 100 == 0:
                allFriendData = self.retrieveData(url + "&key=" + self.__apiKey)
                friendsList.append(allFriendData["response"]["players"])
                url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?steamids="
        # Performs the last data retrieval regarding the user's friends from the steam API
        if not (i + 1) % 100 == 0:
            allFriendData = self.retrieveData(url + "&key=" + self.__apiKey)
            friendsList.append(allFriendData["response"]["players"])
        playingFriends = []
        listMarker = 0
        elementMarker = 0
        # Retrieves the names and game being played by all friends currently playing a game
        for i in range(0, len(allFriends)):
            friendData = friendsList[listMarker][elementMarker]
            if "gameextrainfo" in friendData:
                playingFriends.append([friendData["personaname"], friendData["gameextrainfo"]])
            elementMarker += 1
            if elementMarker % 100 == 0:
                elementMarker = 0
                listMarker += 1
        if not playingFriends:
            return False
        if len(playingFriends) == 1:
            return playingFriends
        # Calls another method to sort the list then returns the sorted list
        return self._friendQuickSort(playingFriends)

    def getFriends(self, userID):
        """
        Used to retrieve all the friends of a given user.
        The unix time of which is used in the dictionary can be converted to UTC in a separate method

        :param userID: str/int - ID of user
        :return: list - list containing dictionaries which contain the ID of the users friends, their relationship and
        the time they became friends in unix.
        Dictionary as {'steamid': 'friendsSteamID', 'relationship': 'friend', 'friend_since': unixTime}
        """
        # Retrieves the data regarding the user's friends
        url = f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={self.__apiKey}&steamid={str(userID)}&relationship=friend"
        userInfo = self.retrieveData(url)
        # Returns False if the user has no friends or if their friends list is private
        if not userInfo:
            return False
        return userInfo["friendslist"]["friends"]

    @staticmethod
    def _unixToUTC(unixTime):
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

    def getFriendDate(self, userID1, userID2):
        """
        Used to retrieve the date, as a list, of which two users became friends

        :param userID1: str/int - steamID of first user in friendship
        :param userID2: str/int - steamID of second user in friendship
        :return: list - UTC time when the friendship was established
        Return format - [day, month, year, hour, minute, second]
        """
        # Retrieve a list containing basic details of all friendships that the user corresponding to userID1 is
        # apart of
        allFriends = self.getFriends(userID1)
        # Run when the user corresponding to userID1 has a hidden friends list or if userID1 is invalid
        if not allFriends:
            # Swaps the variables values as only the user corresponding to the contents of "userID1"
            # must have a public friends list
            userID1, userID2 = userID2, userID1
            allFriends = self.getFriends(userID1)
            # Returns False in this selection if both given IDs are invalid or both user's have a private friends list
            if not allFriends:
                return False
        # Checks list of user friends for the userID2
        for friendInfo in allFriends:
            if str(friendInfo["steamid"]) == str(userID2):
                # Calls method to convert unix date to UTC
                return self._unixToUTC(friendInfo["friend_since"])
        # Returns False by the below return statement if the user's aren't friends
        return False

    def getFriendDateDict(self, userID1, userID2):
        """
        Used to retrieve the date, as a dictionary, of which two users became friends

        :param userID1: str/int - steamID of first user in friendship
        :param userID2: str/int - steamID of second user in friendship
        :return: dictionary - UTC time when the friendship was established
        Return format - {"day":day, "month":month, "year":year, "hour":hour, "minute":minute, "second":second}
        """
        # Retrieves the date, as a list, of which two users became friends
        timeList = self.getFriendDate(userID1, userID2)
        timeTypes = ["day", "month", "year", "hour", "minute", "second"]
        timeDict = {}
        # Creates the date dictionary by using the date list
        for i in range(0, len(timeTypes)):
            timeDict[timeTypes[i]] = timeList[i]
        return timeDict

    def getGameTrailers(self, gameID):
        """
        Returns the first trailer for a steam game

        :param gameID: ID of the steam game in question
        :return: str/False - Link to the game's trailer of which will display the embedded video within discord or False
        if an invalid gameID was given
        """
        url = "https://store.steampowered.com/api/appdetails/?appids=" + str(gameID)
        # Retrieve information regarding the given game
        gameData = self.retrieveData(url)[str(gameID)]
        # If the gameID is invalid then False is returned
        if not gameData["success"]:
            return False
        # Extracts and returns the trailer
        trailerData = gameData["data"]["movies"][0]["mp4"]["480"]
        return trailerData

    def getGameName(self, gameID):
        """
        Used to retrieve the exact steam name of a game given its ID

        :param gameID: str/int - steam ID of game
        :return: str/boolean - Exact name of game or False if the given ID was invalid
        """
        url = "https://store.steampowered.com/api/appdetails/?appids=" + str(gameID)
        # Retrieve information regarding the given game
        gameData = self.retrieveData(url)[str(gameID)]
        # If the gameID is invalid then False is returned
        if not gameData["success"]:
            return False
        # Extracts the name of the game
        gameName = gameData["data"]["name"]
        return gameName

    def playerCountFavouriteGames(self, userID):
        """
        Used to retrieve the exact name and player count of a given user's favourite games

        :param userID: str/int - discord ID of user
        :return: list - List containing sublists of which contain a favourited game's name and its player count
        or False if an invalid user ID was given
        """
        # Retrieves the stored details for the given user ID
        favouriteGames = storageHandler.readUserDetails(userID)
        if favouriteGames:
            # Extracts the list of games favourited by the user
            playerCountList = []
            favouriteGames = favouriteGames[3]
            # Return False if the user has no favourite games set
            if favouriteGames == [""]:
                return False
            # Creates list to be returned
            for game in favouriteGames:
                gameID = self.findGameID(game)
                if gameID:
                    gameDiData = [self.getGameName(gameID), self.gamePlayerCount(gameID)]
                    playerCountList.append(gameDiData)
            return playerCountList
        # Returns False if an invalid user ID was given
        return False

    def validateID(self, userID):
        """
        Validates a provided user's steamID

        :param userID: int - steamID of user
        :return: Boolean - Indicates the validity of the ID
        """
        # Retrieving required data regarding the user
        url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?steamids={str(userID)}&key={self.__apiKey}"
        userInfo = self.retrieveData(url)
        # Returns False if the given ID was invalid
        if len(userInfo["response"]["players"]) == 0:
            return False
        else:
            return True

# Creates object
steamHandler = steam_APIM()