"""
File used for the twitch API
Importing example

from Twitch_API import twitchHandler
steamHandler.gamePlayerCount(730)
"""

# Imports required modules
import urllib.request, json, os


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
            raise ValueError('Missing API key/s - Please check the Keys text file.')

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
        except urllib.error.HTTPError:
            raise ValueError("Incorrect API key/s - Please check the Keys text file.")
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
        :return: List or False - The list contains sublists of containg clip data.
        Sublist index 0 contains the clip URL whilst index 1 contains the clips name. As example is given below
        [[clipUrl, clipName], [clipURL, clipName], [clipURL, clipName], [clipURL, clipName], [clipURL, clipName]]

        Returns False if the streamer was not found or if the given streamer has no clips
        """
        # Retrieves the required data by using the twitch api
        topClipsData = self.retrieveData("https://api.twitch.tv/helix/clips?first=5&broadcaster_id=" + str(streamerID))
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


twitchHandler = twitch_APIM()
