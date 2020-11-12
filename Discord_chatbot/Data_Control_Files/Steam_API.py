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
    def __init__(self):
        # Steam API key not yet required thus it's False
        self.apiKey = False

    @staticmethod
    def storeGameList():
        """
        Locally stores the list of all steams games as requesting the data from the API whenver the data is
         required would create a bottleneck due to lackluster transfer speeds
        """
        # Retrieves basic information regarding all steam games from a webpage
        url = "http://api.steampowered.com/ISteamApps/GetAppList/v0002/?format=json"
        with urllib.request.urlopen(url) as openPage:
            pageData = json.loads(openPage.read().decode())
            # Generates a file path independent from the calling program
            filePath = os.path.dirname(__file__)
            gameListFilePath = os.path.join(filePath, "gameList.json")
            # Stores the data in a .json file
            with open(gameListFilePath, 'w') as f:
                json.dump(pageData, f)

    @staticmethod
    def findGameID(gameName):
        """
        Searches for the ID of a given game by searching through a .json file containing every steam game with their
        respective ID and game name.
        Once the game is found within the .json file, the games ID is returned.
        If the game isn't found, False is returned
        Uses a simple linear search due to the data being unordered - Likely be improved in future

        :param gameName: str - name of steam game
        :return: steamID of given game as a string or False if the ID was not found
        """
        gameID = False
        # Generates a file path independent from the calling program
        filePath = os.path.dirname(__file__)
        gameListFilePath = os.path.join(filePath, "gameList.json")
        # Searches json file for the data related to the game name provided
        with open(gameListFilePath,) as f:
            gameListData = json.load(f)
        for gameData in gameListData["applist"]["apps"]:
            if gameData["name"].lower() == gameName.lower():
                gameID = gameData["appid"]
                break
        return gameID

    # Returns the player count of a game given it's gameID (gameID data type is irrelevant)
    @staticmethod
    def gamePlayerCount(gameID):
        """
        Returns the current player count of a game given its steam gameID
        If the gameID is invalid then False is returned

        :param gameID: str or int
        :return: Player count of game specified by gameID as an integer or False if the gameID is invalid
        """
        # Defines the webpage that contains the required data
        url = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=" + str(gameID)
        # Opens the webpage for data retrieval, page is closed once the data is retrieved
        try:
            with urllib.request.urlopen(url) as openPage:
                data = json.loads(openPage.read().decode())
        except urllib.error.HTTPError:
            return False
        # Returns player count as a an integer
        # Example - "2305"
        return int(data["response"]["player_count"])


steamHandler = steam_APIM()
