"""
File used for the twitch API
Importing example

from Twitch_API import twitchHandler
steamHandler.gamePlayerCount(730)
"""

# Imports required modules
import urllib.request, json, os
from datetime import datetime, timedelta, timezone


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
        print(manip3[2])
        manip4 = "{:.0f}".format(float(manip3[2]))
        if float(manip4) < 10:
            manip4 = f'0{manip4}'
        print(manip4)
        manip4 = manip4.replace('.', ':')
        final_end = f'{manip3[0]}:{manip3[1]}:{manip4}Z'
        print(final_end)

        clipsDict = self.retrieveData(f"https://api.twitch.tv/helix/clips?broadcaster_id={streamerID}&first=1&started_at={final_start}&ended_at={final_end}")
        clip = clipsDict['data'][0]
        clip = clip['url']
        return clip


twitchHandler = twitch_APIM()
