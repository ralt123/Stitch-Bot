from Discord_chatbot.Data_Control_Files.Local_Store import storageHandler
from Discord_chatbot.Data_Control_Files.Steam_API import steamHandler
from Discord_chatbot.Data_Control_Files.Twitch_API import twitchHandler
from Discord_chatbot.Data_Control_Files.Graph_Production import produceSingleGraph, produceComparisonGraph
from Discord_chatbot.Data_Control_Files.Reusable_Functions import alphanumericString
import random


def validationOfID(objectID, objectType):
    """
    Validates a given ID/name for the specified platform and returns either the steamID64 or twitch user ID depending
    on the platform of which the ID is used for.

    :param objectID: int/str - ID/Name of steam user, steam game or twitch user
    :param objectType: str - Indicates the meaning of the passed identification ('steam_user', 'steam_game' or 'twitch_user')
    :return: str/int - Error message or integer ID
    """
    # validation of the ID belonging stream user
    if objectType == "steam_user":
        # Provided steam ID is a vanity ID of which must be resolved to find an their steamID64
        if not str(objectID).isdigit():
            objectID = steamHandler.getUserSteamID(objectID)
            if not objectID:
                return "Invalid vanity ID provided"
        # Provided ID is either a vanity ID or a steamID64
        else:
            if not steamHandler.validateID(objectID):
                objectID = steamHandler.getUserSteamID(objectID)
                if not objectID:
                    return "Invalid vanity ID/steamID64 provided"
    # validation of the ID of a steam game
    elif objectType == "steam_game":
        # Provided ID is the name of a steam game
        if not str(objectID).isdigit():
            objectID = steamHandler.findGameID(objectID)
            if not objectID:
                return "Invalid game name provided"
        # Provided ID is the ID of a steam game
        else:
            if not steamHandler.getGameName(objectID):
                return "Invalid gameID provided"
    # validation of the the ID belonging to a twitch user
    elif objectType == "twitch_user":
        # Provided ID is the name of a streamer
        if not str(objectID).isdigit():
            objectID = twitchHandler.getStreamerID(objectID)
            if not objectID:
                return "Invalid twitch channel name provided"
        # Provided ID is the ID of a twitch streamer
        else:
            if not twitchHandler.getStreamerName(objectID):
                return "Invalid twitchID provided"
    # Validation is complete and the ID of a whatever was provided is returned
    return objectID

def numberFormatter(passedNumber):
    """
    Adds commas to a number to increase readability

    :param passedNumber: int - Number to be adjusted
    :return: str - passedNumber with commas every 1000th
    """
    refinedNumber = passedNumber
    # Adds commas to the player count to allow the reader to more easily distinguish its value
    if refinedNumber > 999:
        refinedNumber = str(refinedNumber)
        refinedNumberLen = len(refinedNumber)
        refinedNumber = refinedNumber[:refinedNumberLen - 3] + "," + refinedNumber[refinedNumberLen - 3:]
        if len(refinedNumber) > 7:
            refinedNumber = refinedNumber[0] + "," + refinedNumber[1:]
    return refinedNumber

# I considered using threading here as to relieve the API bottle neck but this would make the code prone to error
# due to the reading and writing of csv data. Safely implementing threading here will not be done due to time
# constraints
def updateTracked():
    """
    Used to update the held values for all tracked streams/games

    :return: Boolean - True when the function has finished
    """
    # Retrieves all the tracked games
    trackedGames = storageHandler.trackedGameList()
    trackedGameList = []
    # userTracking is a list of games a given single user is tracking
    for userTracking in trackedGames:
        # gameName is the name of a single tracked game
        for gameName in userTracking[1]:
            if gameName not in trackedGameList:
                # Updates held data for the tracked game
                trackedGameList.append(gameName)
                gameID = steamHandler.findGameID(gameName)
                gamePlayerCount = steamHandler.gamePlayerCount(gameID)
                storageHandler.storeTrackedData(gameID, gamePlayerCount, "steam")

    # Retrieves all the tracked streamers
    trackedStreamers = storageHandler.trackedStreamList()
    trackedStreamersList = []
    # userTracking is a list of streamers a given single user is tracking
    for userTracking in trackedStreamers:
        # streamerName is the name of a single tracked streamer
        for streamerName in userTracking[1]:
            if streamerName not in trackedStreamersList:
                # Updates held data for the tracked streamer
                trackedStreamersList.append(streamerName)
                streamerID = twitchHandler.getStreamerID(streamerName)
                streamInfo = twitchHandler.streamDetails(streamerID)
                # Streamer is currently streaming
                if streamInfo:
                    streamerViewerCount = streamInfo["viewer_count"]
                    storageHandler.storeTrackedData(streamerID, streamerViewerCount, "twitch")
    return True


def getTopGames(userID=False):
    # Required API went down for maintenance during creation. The function will not be complete in time.
    topGames = steamHandler.top10Games(userID)
    if not topGames:
        return ["This function is currently unavailable as the required API is currently down, please try again later."]
    return topGames


def currentGamePlayerCount(gameID):
    """
    Used to response a user requesting the player count of a specified game

    :param gameID: str/int - Name or ID of steam game
    :return: str - Response to user
    """
    # Validates the passed ID/name and returns the integer ID of the object passed or a string error message
    gameID = validationOfID(gameID, "steam_game")
    # Run when the validation was successful
    if str(gameID).isdigit():
        playerCount = steamHandler.gamePlayerCount(gameID)
        gameName = steamHandler.getGameName(gameID)
        playerCount = numberFormatter(playerCount)
        return [f"{gameName} currently has {playerCount} players"]
    return ["Sorry, but I don't recognize that game"]


def botInfo():
    """
    Used to return bot info in a discord suitable format

    :return: str - Bot's response
    """
    return [''':information_source:**Info** ```This is Stitch Bot, it is an interactive Discord Bot that helps gamers \
gain information about the games they love and the streamers they watch. 
    It can help you find the most popular game to play and tell you when your favourite streamer is Streaming. It can \
also help with your usual basic commands like Kick and Ban. Use !commands to see the full capabilities of Stitch Bot. ``` ''']


def botGreeting():
    """
    Returns a random greeting.

    :return: str - A random greeting
    """
    # List of possible greetings
    possibleGreeting = ["Hi! :smile:", "Pleasure to meet you. :tophat:", "Hello! :wave:", "Greetings :ok_hand:", "Hello, what can I help you with? :mag_right:"]
    # Generates a random index to determine the greeting returned
    randomIndex = random.randint(0, len(possibleGreeting)-1)
    return [possibleGreeting[randomIndex]]


def botCommands():
    """
    Used to suggest a command for use by the user.
    Doesn't include all commands, just ones that I thought were particularly interesting.

    :return: str - Suggestion of command to try
    """
    possibleIdeas = (
        "tracking a streamer to get notified when they stream", "producing a graph of your favourite tracked game or streamer",
        "producing a graph comparing your two favourite tracked games/streamers",
        "checking when you became friends with another user on steam", "checking the top streams for a specific game",
        "checking what games your friends are playing", "requesting the top clips for your favourite streamer")
    randomIndex = random.randint(0, len(possibleIdeas) - 1)
    botResponse = "I can do many things! Tell me your preferences and I'll keep them in mind whilst talking to you! Why don't you try " + possibleIdeas[randomIndex] + "?"
    return [botResponse]


def friendsSince(userID, friendID):
    """
    Generates a response to a user requesting the date of which them and a given user became friends on steam

    :param userID: int - discord ID of user of which made the request
    :param friendID: str/int - Either the vanity ID or steam ID of the user's friend
    :return: str - Response to the user's request
    """
    # Retrieves stored details for the user
    userID = storageHandler.readUserDetails(userID)
    # User's steam ID has not been recorded
    if not userID or not userID[1]:
        return ["Please inform me of your steam vanity ID or steamID64 so I can fulfil your request"]
    # Extracts the user's steam ID
    steamID = userID[1]
    # friend ID is the friends vanity ID of which must be used to retrieve their actual steam ID
    if not str(friendID).isdigit():
        friendID = steamHandler.getUserSteamID(friendID)
    # Retrieves a list containing the date of which the friendship was established
    friendDate = steamHandler.getFriendDate(steamID, friendID)
    # Creates and returns string response
    if friendDate:
        # Adds a "0" to the front of a single digit number
        for i in range(len(friendDate)):
            if len(str(friendDate[i])) < 2:
                friendDate[i] = "0" + str(friendDate[i])
        responseString = f"You became friends at {friendDate[0]}/{friendDate[1]}/{friendDate[2]} {friendDate[3]}:{friendDate[4]}:{friendDate[5]}"
        return [responseString]
    return ["Sorry, but you are either not friends with this user or this information is private"]


def friendsPlaying(userID):
    """
    Generates a response to a user asking what games their friends are playing

    :param userID: int - discord ID of user of which made the request
    :return: str - Response to the user's request
    """
    # Retrieves held data regarding the user
    userID = storageHandler.readUserDetails(userID)
    # User's steam ID is not held in local storage
    if not userID or not userID[1]:
        return ["Please inform me of your steam vanity ID or steamID64 so I can fulfil your request"]
    userID = userID[1]
    # Retrieves details regarding the user's friends of which are currently playing a game
    friendsList = steamHandler.friendsPlayingGame(userID)
    # No friends of the user are currently playing a game or their friends are hidden
    if not friendsList:
        return ["None of your friends are playing a game or your friends are hidden"]
    # Combines players playing the same game into the same list for processing
    listIndex = 0
    if len(friendsList) > 1:
        while listIndex < len(friendsList):
            if friendsList[listIndex-1][-1:] == friendsList[listIndex][-1:]:
                friendsList[listIndex-1].insert(1, friendsList[listIndex][0])
                friendsList.pop(listIndex)
            else:
                listIndex += 1
    # Produces the string response to be returned
    returnString = ""
    for friendInfo in friendsList:
        # Only one person playing a specific game
        if len(friendInfo) == 2:
            returnString += f"{friendInfo[0]} is playing {friendInfo[1]}, "
        # Two people playing a specific game
        elif len(friendInfo) == 3:
            returnString += f"{friendInfo[0]} and {friendInfo[1]} are playing {friendInfo[2]}, "
        # Three or more people playing a specific game
        else:
            # Used to make use of commas for clarity and compactness
            for i in range(0, len(friendInfo)-2):
                returnString += friendInfo[i] +", "
            returnString = f"{returnString[:-2]} and {friendInfo[i+1]} are playing {friendInfo[i+2]}, "
    return[ returnString[:-2]]


def setSteamID(userID, steamID):
    """
    Fulfils and generates a response to a user requesting that their steam ID is recorded

    :param userID: int - discord ID of user of which made the request
    :param steamID: str/int - Either the vanity ID or steamID64 of the user
    :return: str - Response to the user's request
    """
    # Retrieves and validations the provided steam ID
    validationResponse = validationOfID(steamID, "steam_user")
    # Provided ID was invalid, returns error message
    if not str(validationResponse).isdigit():
        return [validationResponse]
    # Writes new steam ID to local storage
    storageHandler.writeUserDetails(userID, "steam_id", validationResponse)
    return ["Steam ID set"]


def currentPlayerCountFavouriteGames(userID):
    """
    Generates a response to inform the user of the current player counts for their favourite games

    :param userID: int - Discord ID of user
    :return: str - Response to user's request
    """
    # Retrieves the required data
    gameList = steamHandler.playerCountFavouriteGames(userID)
    # User has no favourite games set
    if not gameList:
        return[ "You don't have any favourite games set yet!"]
    # Produces the string response
    returnString = ""
    for gameData in gameList:
        returnString += f"{gameData[0]} - {numberFormatter(gameData[1])}, "
    returnString = returnString[:-2]
    return [returnString]


def checkUserPlayingGame(steamID):
    """
    Generates a response to inform the user whether a provided steam player is currently playing a game

    :param steamID: str/int - Either the vanity ID or steamID64 with the steam player in question
    :return: str - Response to user's request
    """
    # Provided steam ID is a vanity ID of which must be resolved to find an their steamID64
    if not str(steamID).isdigit():
        steamID = steamHandler.getUserSteamID(steamID)
        if not steamID:
            return ["Invalid vanity ID provided"]
    # Provided ID is either a vanity ID or a steamID64
    else:
        if not steamHandler.validateID(steamID):
            steamID = steamHandler.getUserSteamID(steamID)
            if not steamID:
                return ["Invalid vanity ID/steamID64 provided"]
    # Attempts to retrieves the name of the game the user is playing
    userInfo = steamHandler.checkPlayingGame(steamID)
    # Steam player is not playing a game or their game activity is private
    if userInfo == "nothing/private":
        return ["The user is currently not playing a game or this information is private."]
    return ["they are playing" + str(userInfo)]


def userFavouriteStreamersStreaming(userID):
    """
    Generates a response to inform the user which of their favourite streamers are streaming

    :param userID: int - DiscordID of user
    :return: str - Response to user's request
    """
    # Retrieves necessary information - Contains the stream details of favourited streaming currently streaming
    streamerList = twitchHandler.favouriteStreamersStreaming(userID)
    # None of the user's favourite streamers are streaming
    if not streamerList:
        return ["None of your favourited streamers are currently streaming."]
    # Generates the string response
    returnString = ""
    for gameData in streamerList:
        returnString += f"`{gameData['user_name']}` is streaming {gameData['game_name']}, "
    returnString = returnString[:-2]
    return [returnString]

def deletePreference(userID, preferenceID, preferenceType):
    """
    Deletes the specified preference from local storage for the requesting user.

    :param userID: int - Discord ID of user
    :param preferenceID: str - ID for the data to be deleted
    :param preferenceType: str - Name of preference to be deleted
    :return: str - Error or success message response to the user
    """

    if preferenceType in storageHandler.detailsStored:
        storageHandler.deleteUserDetails(userID, preferenceType, preferenceID)
        return ["Specified preference removed."]
    return ["Unknown preference type :frowning:"]

def setPreference(userID, preferenceID, preferenceType):
    """
    Used to set a given user preference.

    :param userID: int - Discord ID of user
    :param preferenceID: str - ID for the data to be stored
    :param preferenceType: str - Name of preference to be set
    :return: str - Error or success message response to the user
    """
    # Validates the passed ID by calling the necessary function with the require arguments
    if preferenceType in ["favourite_games", "tracked_game"]:
        validationResponse = validationOfID(preferenceID, "steam_game")
    elif preferenceType in ["favourite_streamers", "tracked_streamer", "blacklisted_streamers"]:
        validationResponse = validationOfID(preferenceID, "twitch_user")
    elif preferenceType in ["steam_id"]:
        validationResponse = validationOfID(preferenceID, "steam_user")
    # Stores data of which cannot be validated (No API for all steam game genres available)
    elif preferenceType in ["favourite_genre"]:
        storageHandler.writeUserDetails(userID, preferenceType, preferenceID)
        return ["Preference set successfully!"]
    # Raise an error to inform a fellow programmer using the function of their invalid arguments passed
    else:
        raise Exception("You must pass a valid 'preferenceType', please refer to documentation")
    # Returns error message if the validation fails
    if not str(validationResponse).isdigit():
        return validationResponse
    # Retrieves the string name corresponding to the given ID
    if preferenceType in ["favourite_games", "tracked_game"]:
        preferenceData = steamHandler.getGameName(validationResponse)
    elif preferenceType in ["favourite_streamers", "tracked_streamer", "blacklisted_streamers"]:
        preferenceData = twitchHandler.getStreamerName(validationResponse)
    elif preferenceType in ["steam_id"]:
        storageHandler.writeUserDetails(userID, preferenceType, validationResponse)
        return ["Steam ID set"]
    # Converts the string to only contain lowercase alphanumeric character
    preferenceData = alphanumericString(preferenceData)
    # Writes the user preference to storage
    storageHandler.writeUserDetails(userID, preferenceType, preferenceData)
    return ["Preference set successfully!"]


def generateSingleGraph(objectID, trackedType):
    """
    Produces a single graph representing either the viewer/player count of a streamer/game over the past 21
    tracked days.

    :param objectID: int/str - ID/name of the object of which the graph is based on (Either ID/name of steam game or twitch streamer)
    :param trackedType: str - Type of object being displayed on the graph ("steam_game" or "twitch_user")
    :return: Boolean/str - True if the graph was created successfully, string error message otherwise
    """
    # Validates passed ID
    if trackedType == "steam":
        validationResponse = validationOfID(objectID, "steam_game")
    else:
        validationResponse = validationOfID(objectID, "twitch_user")
    # Validation failed and the error message from validation is returned
    if not str(validationResponse).isdigit():
        return [validationResponse]
    # Produces the desired graph
    graphSuccess = produceSingleGraph(validationResponse, trackedType)
    if graphSuccess:
        return ["Graph set"]
    return ["No tracked data is held for the given streamer/game."]


def generateCompareGraph(objectID1, objectID2, trackedType):
    """
    Produces a comparision graph comparing either the viewer/player count of 2 streamers/games over the past 21
    days in which both streamers/games have been tracked

    :param objectID1: int/str - ID/name of the first object in the comparison (Either ID/name of steam game or twitch streamer)
    :param objectID2: int/str - ID/name of the second object in comparison (Same type of ID/name as objectID1)
    :param trackedType: Type of objects being compared on the graph ("steam_game" or "twitch_user")
    :return: Boolean/str - True if the graph was created successfully, string error message otherwise
    """
    # Validates passed both passed IDs
    if trackedType == "steam":
        validationResponse1 = validationOfID(objectID1, "steam_game")
        validationResponse2 = validationOfID(objectID2, "steam_game")
    else:
        validationResponse1 = validationOfID(objectID1, "twitch_user")
        validationResponse2 = validationOfID(objectID2, "twitch_user")
    # Validation failed and the error message from validation is returned
    if not str(validationResponse1).isdigit():
        return validationResponse1
    elif not str(validationResponse2).isdigit():
        return validationResponse2
    # Produces the desired graph
    graphSuccess = produceComparisonGraph(validationResponse1, validationResponse2, trackedType)
    if graphSuccess:
        return ["Graph set"]
    return ["No tracked data is held for the given streamer/game."]


def gameCurrentTopStreamers(userID, gameIdentifier):
    """
    Generates a response to inform the user of the current top streamers playing a specified name.
    The response contains only english streamers and excludes streamers blacklisted by the user.

    :param userID: int - discord ID of user
    :param gameIdentifier: str - Twitch game ID or name
    :return: str - response to user
    """
    # Retrieves a list of the top 5 english non-blacklisted streamers playing the game specified
    streamList = twitchHandler.gameTopStreamers(userID, gameIdentifier)
    if not streamList:
        return ["Invalid category/game."]
    # Prepares and returns the string response
    returnString = ""
    for streamData in streamList:
        returnString += f"{streamData[0]} streaming `{streamData[1]}` with {numberFormatter(streamData[2])} viewers,\n\n"
    returnString = returnString[:-3]
    return [returnString]


def overallTopStreamerClips(streamerID):
    """
    Used to retrieve the top 5 all time clips for a specified streamer.

    :param streamerID: int/str - ID or name of twitch streamer
    :return: str - Response to request
    """
    # Retrieves the ID of the streamer if their name was provided
    if not str(streamerID).isdigit():
        streamerID = twitchHandler.getStreamerID(streamerID)
    # Retrieves the streamers top 5 clips
    topClips = twitchHandler.topStreamerClips(streamerID)
    if not topClips:
        return ["Invalid twitch streamer provided."]
    # Prepares and returns the string response
    returnString = "Top clips - "
    for clipData in topClips:
        returnString += f"{clipData[1]} at {clipData[0]}\n"
    returnString = returnString[:-1]
    return [returnString]


def currentStreamDetails(streamerID):
    """
    Responds to a request asking for details regarding a specific streamer

    :param streamerID: str/int - Name/ID of specific streamer
    :return: str - Response to the user's request
    """
    # Checks if the argument passed is the name of a streamer, opposed to their ID
    if not str(streamerID).isdigit():
        streamerID = twitchHandler.getStreamerID(streamerID)
    # Retrieves the required stream data
    streamData = twitchHandler.streamDetails(streamerID)
    if not streamData:
        return ["Provided streamer is not currently streaming."]
    streamData["viewer_count"] = numberFormatter(streamData["viewer_count"])
    return [f"{streamData['user_name']} is currently streaming {streamData['game_name']} with {streamData['viewer_count']} viewers."]

def unknownRequest():
    return ["Sorry, but I don't understand"]

def csgo_stats(userID):
    steam_id = storageHandler.readUserDetails(userID)[1]
    csgo_stats = steamHandler.getCSGOStats(steam_id)
    if not csgo_stats:
        desc = '**Couldn`t find stats**'
    else:
        if type(csgo_stats['total_time_played']) == bool:
            hours = 'unknown'
        else:
            hours = int(csgo_stats['total_time_played']) // 3600
        desc = (f'''':first_place:** - CSGO Stats**
                    - Total Kills: {csgo_stats['total_kills']}
                    - Total Headshots: {csgo_stats['total_kills_headshot']}
                    - Total Damage: {csgo_stats['total_damage_done']}
                    - Total Deaths: {csgo_stats['total_deaths']}
                    - Total Wins: {csgo_stats['total_wins']}
                    - Total PlayTime in Match {hours}hrs 
                    ''')
    return [desc]


def stream_details(streamers_name):
    streamers_id = validationOfID(streamers_name, "twitch_user")

    if not streamers_id:
        return ['Streamer not Found']

    stream_checker = twitchHandler.checkIfStreaming(streamers_id)
    if not stream_checker:
        desc = '''
    **:white_circle:{streamers_name.content}**
    **They are not live right now**:sob:'''

    else:
        details = twitchHandler.streamDetails(streamers_id)
        vod = twitchHandler.latestStreamerClips(streamers_id)
        if not vod:
            clip = ''
            vod = ''
        else:
            clip = '+ Popular clip from the stream:'

        def live_emoji():
            if details['type'] == 'live':
                return ':red_circle:'
            else:
                return ''

        live = live_emoji()

        desc = f'''**{live + details['user_name']}**
                    - {details['type']}
                    - Title: {details['title']}
                    - Viewers: {details['viewer_count']}
                    - Started at: {details['started_at']}
                    - Language: {details['language']}'''

    return [desc, clip]


def game_details(game_name):
    game_id = validationOfID(game_name, "steam_game")
    if not game_id:
        return ['Game not found']

    def game_price_calc(id):
        price_dict = steamHandler.getGamePrice(id)
        if price_dict['free']:
            normal_price = 0
            current_price = 0
            money_saved = 0
            sale = False
        elif price_dict['normal_price'] == '':
            normal_price = 0
            current_price = price_dict['current_price']
            money_saved = 0
            sale = False
        else:
            current_price = price_dict['current_price']
            normal_price = price_dict['normal_price']
            sale = True
            x = float(price_dict['normal_price'][1:])
            y = float(price_dict['current_price'][1:])
            z = price_dict['current_price'][:1]
            money_saved = f'{z}{x - y}'
        return normal_price, current_price, money_saved, sale

    normal_price, current_price, money_saved, sale = game_price_calc(game_id)

    if normal_price == 0 and current_price == 0 and money_saved == 0:
        game_cost = 'Free'
    elif sale:
        game_cost = f'Sale Price: {current_price}\n{money_saved} Off!'
    else:
        game_cost = f'Price: {current_price}'
    player_count = steamHandler.gamePlayerCount(game_id)
    game_desc = steamHandler.gameDescription(game_id)
    game_trailer = steamHandler.getGameTrailers(game_id)
    desc = f'''** - {game_name}**
                - {game_cost}
                - Player Count: {player_count}
                - Game Description:\n {game_desc}
                - Trailer:'''
    return [desc, game_trailer]
