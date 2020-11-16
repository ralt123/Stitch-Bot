"""
Contains examples on importing and using the methods
"""

# Importing path will have to be modified depending on the location of the calling program
from Data_Control_Files.Twitch_API import twitchHandler
from Data_Control_Files.Steam_API import steamHandler

# Returns the ID of a streamer given their channel name
twitchHandler.getStreamerID("twitch")

# Returns True/False to indicate if a streamer is streaming, provided their ID
twitchHandler.checkIfStreaming("71092938")

# Returns the details regarding an ongoing stream, provided the streamer's ID
twitchHandler.streamDetails("71092938")

# Returns a list containing details regarding a streamers top 5 clips, provided the streamer's ID
twitchHandler.topStreamerClips("71092938")

# Updates the .json game list. Retrieving such a large quantity of data takes several seconds.
steamHandler.storeGameList()

# Returns the ID of a game provided the game's name
steamHandler.findGameID("Counter Strike: Global Offensive")

# Returns a game's player count given the game's ID
game_player_count = steamHandler.gamePlayerCount(730)

# Returns a short description of a game given the game's steam ID
steamHandler.gameDescription(730)

# Returns the ID of a user given their vanity ID
steamHandler.getUserSteamID("St4ck")

# Returns a dictionary of CSGO stats for a user given their steam ID
steamHandler.getCSGOStats(76561198023414915)

# Returns the price of a game given the game's ID
steamHandler.getGamePrice(730)

