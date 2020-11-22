from Discord_chatbot.Local_Store import storageHandler
from Discord_chatbot.Steam_API import steamHandler
from Discord_chatbot.Twitch_API import twitchHandler

def friendsSince(userID, friendID):
    """
    Generates a response to a user requesting the date of which them and a given user became friends on steam

    :param userID: int - discord ID of user of which made the request
    :param friendID: str/int - Either the vanity ID or steam ID of the user's friend
    :return: str - Response to the user's request
    """
    userID = storageHandler.readUserDetails(userID)
    if not userID:
        return "Please inform me of your steam vanity ID or ID so I can fulfil your request"
    userID = userID[1]
    if not str(friendID).isdigit():
        user2 = steamHandler.getUserSteamID(friendID)
    friendDate = steamHandler.getFriendDate(userID, friendID)
    if friendDate:
        responseString = f"You became friends at {friendDate[0]}/{friendDate[1]}/{friendDate[2]} {friendDate[3]}:{friendDate[4]}:{friendDate[5]}"
        return responseString
    return "Sorry, but you are either not friends with this user or this information is private"

def friendsPlaying(userID):
    """
    Generates a response to a user asking what games their friends are playing

    :param userID: int - discord ID of user of which made the request
    :return: str - Response to the user's request
    """
    userID = storageHandler.readUserDetails(userID)
    if not userID:
        return "Please inform me of your steam vanity URL or ID so I can fulfil your request"
    userID = userID[1]
    friendsList = steamHandler.friendsPlayingGame(userID)
    if not friendsList:
        return "None of your friends are playing a game or your friends are hidden"
    returnString = ""
    for friendInfo in friendsList:
        returnString += f"{friendInfo[0]} is playing {friendInfo[1]}, "
    return returnString[:-2]

def setSteamID(userID, steamID):
    """
    Fulfils and generates a response to a user requesting that their steam ID is recorded

    :param userID: int - discord ID of user of which made the request
    :param steamID: str/int - Either the vanity ID or steam ID of the user
    :return: str - Response to the user's request
    """
    if not str(steamID).isdigit():
        steamID = steamHandler.getUserSteamID(steamID)
        if not steamID:
            return "Invalid vanity URL provided"
    else:
        if not steamHandler.validateID(steamID):
            return "Invalid vanity URL/ID provided"
    storageHandler.writeUserDetails(userID, "steam_id", steamID)
    return "Steam ID set"

