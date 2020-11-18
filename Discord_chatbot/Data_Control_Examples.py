"""
Contains examples on importing and using the methods
"""

# Importing path will have to be modified depending on the location of the calling program
from Data_Control_Files.Twitch_API import twitchHandler
from Data_Control_Files.Steam_API import steamHandler


# Returns the ID of a streamer given their channel name
streamer_ID = twitchHandler.getStreamerID("twitch")

# Returns True/False to indicate if a streamer is streaming, provided their ID
is_streaming = twitchHandler.checkIfStreaming("71092938")

# Returns the details regarding an ongoing stream, provided the streamer's ID
stream_details = twitchHandler.streamDetails("71092938")

# Returns a list containing details regarding a streamers top 5 clips, provided the streamer's ID
top_clips_list = twitchHandler.topStreamerClips("71092938")

# Returns the twitch game ID of a given name
game_ID = twitchHandler.getGameID("rocket league")

# Returns top 5 english streams for a given game name or given game ID
top_streamers = twitchHandler.gameTopStreamers("rocket league")

# Updates the .json game list. Retrieving such a large quantity of data takes several seconds.
steamHandler.storeGameList()

# Returns the ID of a game provided the game's name
game_ID = steamHandler.findGameID("Counter Strike: Global Offensive")

# Returns a game's player count given the game's ID
game_player_count = steamHandler.gamePlayerCount(730)

# Returns a short description of a game given the game's steam ID
game_description = steamHandler.gameDescription(730)

# Returns the ID of a user given their vanity ID
user_ID = steamHandler.getUserSteamID("St4ck")

# Returns a dictionary of CSGO stats for a user given their steam ID
user_csgo_stats = steamHandler.getCSGOStats(76561198023414915)

# Returns the details about the price of a game given the game's ID as a dictionary
price_dictionary_info = steamHandler.getGamePrice(730)

# Returns the name of the game the user is playing
game_being_played = steamHandler.checkPlayingGame(76561198023414915)

# Returns list of sublists containing the friends name and game they are playing
playing_friends_info = steamHandler.friendsPlayingGame(76561198023414915)

# Returns list containing a dictionary containing basic information regarding the users friends
basic_friend_info = steamHandler.getFriends(76561198023414915)

# Returns the UTC date as a list that two user became friends
friends_since_list = steamHandler.getFriendDate(76561198023414915, 76561198264035001)

# Returns the UTC date as a dictionary that two user became friends
friends_since_dictionary = steamHandler.getFriendDateDict(76561198023414915, 76561198264035001)

# Returns URL of steam game trailer
game_trailer = steamHandler.getGameTrailers(730)

