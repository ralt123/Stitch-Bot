"""
File used for the twitch API
Importing example

from Twitch_API import twitchHandler
steamHandler.gamePlayerCount(730)
"""

# Imports required modules
import urllib.request, json, os
from Discord_chatbot.Data_Control_Files.Local_Store import storageHandler
from Encryption import encryptionAES128

class twitch_APIM:
    """
    Class used for handling the twitch API
    """

    # Initialises class variables
    def __init__(self):
        # Required private keys for accessing the twitch API
        self.__clientID = ""
        self.__auth = ""
        self.__setKeys()
    # Sets the crucial API keys

    def __setKeys(self):
        filePath = os.path.dirname(__file__)

        # setting decrypt key
        decrypt_key_path = os.path.join(filePath, "Encrypted_keys\Decrypt_key")
        with open(decrypt_key_path, 'r') as decrypt_key_file:
            decrypt_key = decrypt_key_file.read()
        encryption = encryptionAES128(decrypt_key)

        # Setting Auth key

        auth_key_path = os.path.join(filePath, "Encrypted_keys\Twitch_Authentication_key.txt")
        with open(auth_key_path, 'rb') as auth_key_file:
            encrypted_auth_key = auth_key_file.read()
        self.__auth = encryption.decrypt(encrypted_auth_key)

        # setting ClientID key

        client_key_path = os.path.join(filePath,"Encrypted_keys\Twitch_ClientID_key.txt")
        with open(client_key_path, 'rb') as client_key_file:
            encrypted_client_key = client_key_file.read()
        self.__clientID = encryption.decrypt(encrypted_client_key)

        # old open code before encryption update:
        """
        filePath = os.path.dirname(__file__)
        keyFile = os.path.join(filePath, 'Keys_DO_NOT_UPLOAD.txt')
        # Retrieves keys from the text file. Text file is used to simplicity and ease of editing for my peers.
        with open(keyFile, 'r') as keyFile:
            keyData = keyFile.read()
        keyData = keyData.replace(" ", "")
        keyDataList = keyData.split("\n")
        # Split beats .index
        for i in range(0, len(keyDataList)):
            keyDataValue = keyDataList[i].split("=")
            if keyDataValue[0] == "TwitchClientIDkey":
                self.__clientID = keyDataValue[1]
            elif keyDataValue[0] == "TwitchAuthenticationkey":
                self.__auth = keyDataValue[1]
        if self.__auth == "" or self.__clientID == "":
            raise Exception('Missing API key/s - Please check the Keys text file.')
        """

    def retrieveData(self, url):
        """
        Used to retrieve data from the given url

        :param url: String containing the url of the required data
        :return: The data retrieved from the given url as a dictionary
        """
        # Opens the required page with necessary data as headers
        request = urllib.request.Request(url, headers={"Authorization": "Bearer " + self.__auth,
                                                       'Client-ID': self.__clientID})
        # Use of try/except to inform the programmer if their API keys are invalid to resolve common errors
        try:
            page = urllib.request.urlopen(request)
        except urllib.error.HTTPError as errorMessage:
            raise Exception(f"HTTPError Likely causes - Possible API outage or incorrect API key/s\n{errorMessage}")
        # Retrieves the required data held in the page abd returns it
        pageData = json.loads(page.read().decode())
        return pageData

    def getStreamerID(self, steamerName):
        """
        Used to find the ID of a streamer given their channel name

        :param steamerName: String containing the name of the streamer in question
        :return: The ID of the streamer provided or False if their ID wasn't found
        """
        # Retrieves streamer data
        dataDict = self.retrieveData("https://api.twitch.tv/helix/users?login=" + str(steamerName))
        if len(dataDict["data"]) != 0:
            return dataDict["data"][0]["id"]
        else:
            return False

    def checkIfStreaming(self, streamerID):
        """
        Used to check if the streamer related to the provided streamer ID is currently streaming.

        :param streamerID: String containing the ID of the streamer in question
        :return: True if the streamer is currently streaming and False otherwise
        """
        # Retrieves stream data
        dataDict = self.retrieveData("https://api.twitch.tv/helix/streams?user_id=" + str(streamerID))
        if len(dataDict["data"]) != 0:
            return True
        else:
            return False

    def streamDetails(self, streamerID):
        """
        Used to retrieve information about an ongoing stream given the streamers ID and returns False if the streamer
        is not currently streaming

        :param streamerID: String containing the ID of the streamer in question
        :return: Dictionary containing data regarding the stream. Import keys for the dictionary are as follows:
        "viewer_count", "title", "language"
        """
        # Retrieves stream data
        dataDict = self.retrieveData("https://api.twitch.tv/helix/streams?user_id=" + str(streamerID))
        if len(dataDict["data"]) != 0:
            return dataDict["data"][0]
        else:
            return False

    def topStreamerClips(self, streamerID):
        """
        Used to retrieve the top 5 clips of a streamer given their ID.

        :param streamerID: str/int - ID of streamer
        :return: List/False - The list contains sublists of containg clip data.
        Sublist index 0 contains the clip URL whilst index 1 contains the clips name. As example is given below
        [[clipUrl, clipName], [clipURL, clipName], [clipURL, clipName], [clipURL, clipName], [clipURL, clipName]]

        Returns False if the streamer was not found or if the given streamer has no clips
        """
        # Retrieves the required data by using the twitch api
        topClipsData = self.retrieveData(
            "https://api.twitch.tv/helix/clips?first=5&broadcaster_id=" + str(streamerID))
        # topClipsData = self.retrieveData(url)
        # Returns False if the streamer was not found or if the given streamer has no clips
        if not topClipsData["data"]:
            return False
        clipList = []
        # cursorKey is required due to inconsistencies in the twitch API
        cursorKey = topClipsData["pagination"]["cursor"]
        # Repeats until the top 5 clips are retrieved, to fix the API inconsistency
        while len(clipList) != 5:
            # Only necessary data is appended to the list that is to be returned
            for clipData in topClipsData["data"]:
                clipList.append([clipData["url"], clipData["title"]])
            # In the event that less clip data is retrieved from the twitch API than expected, the remaining data that is required is retrieved
            if len(clipList) != 5:
                requiredClips = 5 - len(clipList)
                url = "https://api.twitch.tv/helix/clips?first=" + str(requiredClips) + "&after=" + str(
                    cursorKey) + "&broadcaster_id=" + str(streamerID)
                topClipsData = self.retrieveData(url)
                cursorKey = topClipsData["pagination"]["cursor"]
        return clipList

    # Method made by Jupiter
    def latestStreamerClips(self, streamerID):
        """
        Used to retrieve clips from a streamers latest stream

        :param streamerID: String containing the ID of the streamer in question
        :return the clips url
        """

        # Getting Two time variables in rfc3339 format
        # str - final_start is a rfc3339 timestamp for exactly 1 day ago
        # str - final_end is a rfc3339 timestamp for the time the variable was initiated
        # lots of string manipulation is needed to make the variables be in the correct format for the API
        # Example output: 2020-11-16T14:16:33Z
        from datetime import datetime, timedelta
        # started_at argument:
        time_minus_a_day = datetime.today() - timedelta(days=1)
        start_time = time_minus_a_day.isoformat()
        manip = start_time.split(':')
        manip2 = "{:.0f}".format(float(manip[2]))
        if float(manip2) < 10:
            manip2 = f'0{manip2}'
        manip2 = manip2.replace('.', ':')
        final_start = f'{manip[0]}:{manip[1]}:{manip2}Z'

        # ended_at argument
        time = datetime.today().isoformat()
        manip3 = time.split(':')
        manip4 = "{:.0f}".format(float(manip3[2]))
        if float(manip4) < 10:
            manip4 = f'0{manip4}'
        manip4 = manip4.replace('.', ':')
        final_end = f'{manip3[0]}:{manip3[1]}:{manip4}Z'

        clipsDict = self.retrieveData(
            f"https://api.twitch.tv/helix/clips?broadcaster_id={streamerID}&first=1&started_at={final_start}&ended_at={final_end}")
        if not clipsDict["data"]:
            return False
        else:
            clip = clipsDict['data'][0]
            clip = clip['url']
            return clip

    def getGameID(self, gameName):
        """
        Used to retrieve the twitch ID of a given game

        :param gameName: str - Name of the game in question
        :return: str/Boolean - ID of given name or False if the given game name was invalid
        """
        originalGameName = gameName
        # Replaces spaces in a format understood by the twitch API
        gameName = gameName.replace(" ", "%20")
        url = "https://api.twitch.tv/helix/games?name=" + gameName
        # Retrieves required data
        gameDetails = self.retrieveData(url)
        if not gameDetails["data"]:
            # Searches for the steam ID of the game (this is used because the "findGameID" method removes all
            # non-alphanumeric characters and sets the string to lowercase as to allow the desired game to be found
            # without concern for special symbols or capitalization)
            gameIdentifier = steamHandler.findGameID(originalGameName)
            # Steam ID of game could not be found, return False
            if not gameIdentifier:
                return False
            # Get the steam name of the game then search for the twitch game ID
            gameIdentifier = steamHandler.getGameName(gameIdentifier)
            # Removes special characters that aren't use by twitch but may be used in a title of a steam game
            refinedIdentifier = ""
            for character in gameIdentifier:
                if character in string.printable:
                    refinedIdentifier += character
            # Replaces spaces in a format understood by the twitch API
            refinedIdentifier = refinedIdentifier.replace(" ", "%20")
            url = "https://api.twitch.tv/helix/games?name=" + refinedIdentifier
            # Retrieves required data
            gameDetails = self.retrieveData(url)

            # Return False if the given game name was invalid
            if not gameDetails["data"]:
                return False
        # Return the ID of the given name
        return gameDetails["data"][0]["id"]

    def gameTopStreamers(self, userID, gameIdentifier):
        """
        Used to retrieve a list containing the top english streamers for a given game

        :param gameIdentifier: str/int - Name of game or ID of a game
        :param userID: int - Discord ID of user
        :return: list - A list containing sublists which contain basic stream information for the top 5 english
        streams playing the provided game. Sorted by most popular stream first then descending
        """
        originalGameIdentifier = gameIdentifier
        # Runs if the name of a game is given rather than a game ID
        if not str(gameIdentifier).isdigit():
            # Retrieves the ID of a given name
            gameIdentifier = self.getGameID(gameIdentifier)
            # twitch ID of game was not found
            if not gameIdentifier:
                return False
        url = f"https://api.twitch.tv/helix/streams?game_id={str(gameIdentifier)}&first=15&language=en"
        # Retrieves required information regarding top 5 english streams playing the given game
        gameStreamData = self.retrieveData(url)
        # Game ID is invalid or no english streamers are playing the given game
        if not gameStreamData["data"]:
            return False
        # Retrieves the names of streamers that have been blacklisted by the user
        hiddenStreamers = storageHandler.readUserDetails(userID)
        if hiddenStreamers:
            hiddenStreamers = hiddenStreamers[7]

        # Generates list to return
        streamDataList = []
        for streamData in gameStreamData["data"]:
            # Excludes blacklisted streamers
            if not (hiddenStreamers and streamData["user_name"].lower() in hiddenStreamers):
                dataList = [streamData["user_name"], streamData["title"], streamData["viewer_count"]]
                streamDataList.append(dataList)
        return streamDataList[:5]

    def favouriteStreamersStreaming(self, userID):
        """
        Returns the stream details for any favourited streamers of which are currently streaming

        :param userID: str/int - the user ID of the user
        :return: list - List containing sublists of which contain stream data for favourited currently streaming
        streamers. Returns False if either the user ID is invalid or if no favourited streamers are streaming
        """
        # Retrieves stored details for user
        favouriteStreamers = storageHandler.readUserDetails(userID)
        streamingFavourites = []
        if favouriteStreamers:
            # Extracts the list of favourited streamers
            favouriteStreamers = favouriteStreamers[2]
            # User has no favourited streamers
            if favouriteStreamers == [""]:
                return False
            # Produces the list of which is to be returned
            for streamer in favouriteStreamers:
                streamerStreamDetails = self.streamDetails(self.getStreamerID(streamer))
                if streamerStreamDetails:
                    streamingFavourites.append(streamerStreamDetails)
        # Returns if the list isn't empty
        if streamingFavourites:
            return streamingFavourites
        return False

    def getStreamerName(self, streamerID):
        """
        Retrieves the name of a streamer given their ID.
        Should only be used when the ID is known to be valid.

        :param streamerID: int - ID of streamer
        :return: str - Name of streamer
        returns False if the given ID does not relate to any streamer
        """
        # Retrieves data regarding the streaming
        streamerData = self.retrieveData(f"https://api.twitch.tv/helix/users?id={streamerID}")
        # Invalid streamer ID provided
        if not streamerData["data"]:
            return False
        # Extracts the name of the streamer
        streamerName = streamerData["data"][0]["login"]
        return streamerName

# Creates object
twitchHandler = twitch_APIM()
