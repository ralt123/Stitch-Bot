"""
File used for the steam API
Importing example

from Steam_API import steamHandler
steamHandler.gamePlayerCount(730)
"""

import urllib.request, json, os


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
        keyFile = os.path.join(filePath, 'Keys_DO_NOT_UPLOAD.txt')
        # Retrieves keys from the text file. Text file is used to simplicity and ease of editing for my peers.
        with open(keyFile, 'r') as keyFile:
            keyData = keyFile.read()
        keyData = keyData.replace(" ", "")
        keyDataList = keyData.split("\n")
        for i in range(0, len(keyDataList)):
            keyDataValue = keyDataList[i].split("=")
            if keyDataValue[0] == "Steamkey":
                self.__apiKey = keyDataValue[1]
        if self.__apiKey == "":
            raise ValueError('Missing API key/s - Please check the Keys text file.')

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
        except urllib.error.HTTPError:
            return False
        return data

    # Merge sort method was made myself so it's efficiency may not be optimal but it shall suffice
    # As storing the game list is not for frequent use, I don't plan on continuing to optimise the sorting method.
    # Uses iteration over recursion as the large size of the gameList to be sorted would use a lot of space in recursion
    @staticmethod
    def gameListMergeSort(unsortedGL):
        """
        Method used to sort the list of all steam games by name.

        :param unsortedGL: unsorted game list as a list containing dictionaries of which contain individual game data
        :return: List of all sorted steam games, ascending
        """
        startingSize = len(unsortedGL)
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
                unsortedGL[i:i+2] = [sortedList]
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
        sortedGameList = self.gameListMergeSort(pageData)
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
                currentGameName = gameListData[currentGameIndex]["name"]
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
        # Returns player count as a an integer
        # Example - "2305"
        return int(data["response"]["player_count"])

    def gameDescription(self, gameID):
        """
        Returns a short description of a game given it's steam gameID

        :param gameID: str or int - ID of the steam game
        :return: The short description for the given steam game, retrieved by using the steam API, as a string
        """
        # Defines the webpage that contains the required data
        url = "https://store.steampowered.com/api/appdetails?appids=" + str(gameID)
        # Opens the webpage for data retrieval, page is closed once the data is retrieved
        data = self.retrieveData(url)
        # Returns short description
        return data[str(gameID)]["data"]["short_description"]

    def getUserSteamID(self, userURL):
        """
        Used to find the steam ID of a user given their steam URL string.
        The required section of the user's URL is the unique portion of which acts as an ID

        :param userURL: str or int - The unique URL of the user
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
        if "price_overview" in data[str(gameID)]["data"]:
            priceDict = {"normal_price": data[str(gameID)]["data"]["price_overview"]["initial_formatted"],
                         "current_price": data[str(gameID)]["data"]["price_overview"]["final_formatted"], "free": False}
            return priceDict
        # Returns short description
        if data[str(gameID)]["data"]["is_free"]:
            return {"free": True}
        return False


steamHandler = steam_APIM()
