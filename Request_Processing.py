from Discord_chatbot.Process_Functions import *
from Discord_chatbot.Data_Control_Files.Reusable_Functions import alphanumericString
from nltk.stem import WordNetLemmatizer
import copy, json, os


filePath = os.path.dirname(__file__)
gameAliasesPath = os.path.join(filePath, "Discord_chatbot/Data_Control_Files/game_aliases.json")
with open(gameAliasesPath, "r") as jsonFile:
    steamAliases = json.load(jsonFile)["aliases"][0]
twitchAliasesPath = os.path.join(filePath, "Discord_chatbot/Data_Control_Files/twitch_aliases.json")
with open(twitchAliasesPath, "r") as jsonFile:
    twitchAliases = json.load(jsonFile)["aliases"][0]
lem = WordNetLemmatizer()

availableFunctions = [[["undefined"], unknownRequest, 0, [], 1000],
                      [["stream"], stream_details, 0, ["streamerID"], 400],
                      [["stream", "clip"], overallTopStreamerClips, 0, ["streamerID"], 630],
                      [["top", "streamers", "play"], gameCurrentTopStreamers, 0,["userID", "gameIdentifier"], 300],
                      [["compare", "vs"], generateCompareGraph, 0, ["diObjectID", "diObjectID", "referenceType"], 50],
                      [["graph"], generateSingleGraph, 0, ["ObjectID", "referenceType"], 60],
                      [["set", "preference", "set", "set"], setPreference, 0, ["userID", "preferenceID", "preferenceType"], 10],
                      [["delete", "remove"], deletePreference, 0, ["userID", "preferenceID", "preferenceType"], 9],
                      [["favourite", "stream"], userFavouriteStreamersStreaming, 0, ["userID"], 550],
                      [["game", "play"], checkUserPlayingGame, 0, ["steamID"], 490],
                      [["favourite", "game", "play"], currentPlayerCountFavouriteGames, 0, ["userID"], 510],
                      [["friends", "game", "play"], friendsPlaying, 0, ["userID"], 520],
                      [["friends", "with", "long", "when"], friendsSince, 0, ["userID", "friendID"], 800],
                      [["what", "command"], botCommands, 0, [], 345],
                      [["greet", "hi", "hello"], botGreeting, 0, [], 950],
                      [["info", "information", "yourself"], botInfo, 0, [], 970],
                      [["play"], game_details, 0, ["gameID"], 15],
                      [["stats", "csgo", "counter", "strike"], csgo_stats, 0, ["userID"], 74]]
linkingVerbs = ["be", "for", "with"]

def aliasesCheck(rawReference):
    if rawReference in steamAliases.keys():
        rawReference = steamAliases[rawReference]
    elif rawReference in twitchAliases.keys():
        rawReference = twitchAliases[rawReference]
    return rawReference

def requestProcessing(userRequest, userID):
    argumentList = []
    possibleFunctions = copy.deepcopy(availableFunctions)
    rawRequest = userRequest.split(" ")
    originalRequest = rawRequest[:]
    for i in range(0, len(rawRequest)):
        rawRequest[i] = alphanumericString(rawRequest[i])
        originalRequest[i] = rawRequest[i]
        rawRequest[i] = lem.lemmatize(rawRequest[i],'v')
    for i in range(1, len(possibleFunctions)):
        for expectedWord in possibleFunctions[i][0]:
            if lem.lemmatize(expectedWord,'v') in rawRequest:
                possibleFunctions[i][2] += 1

    largestIndexList = []
    largestIndex = 0
    largestValue = 0
    for i in range(1, len(possibleFunctions)):
        if possibleFunctions[i][2] > largestValue:
            largestValue = possibleFunctions[i][2]
            largestIndexList = [i]
        elif possibleFunctions[i][2] == largestValue:
            largestIndexList.append(i)

    if len(largestIndexList) > 1:
        newIndex = largestIndex
        highestPriority = possibleFunctions[largestIndex][4]
        for checkIndex in largestIndexList:
            if possibleFunctions[checkIndex][4] < highestPriority:
                highestPriority = possibleFunctions[checkIndex][4]
                newIndex = checkIndex
        largestIndex = newIndex
    else:
        if largestIndexList:
            largestIndex = largestIndexList[0]


    referenceType = ""
    if {"stream", "streamer", "streamers"} in set(rawRequest):
        referenceType = "twitch"
    else:
        referenceType = "steam"

    for loopCounter in range(len(possibleFunctions[largestIndex][3])):
        if not argumentList and "userID" in possibleFunctions[largestIndex][3]:
            argumentList.append(userID)
        elif {"preference", "set", "delete", "remove"} & set(rawRequest):
            if {"steam", "id"} & set(rawRequest) == {"steam", "id"}:
                steamIndex = rawRequest.index("steam")
                rawRequest[steamIndex] = "steamid"
                originalRequest[steamIndex] = "steamid"
                rawRequest.pop(steamIndex + 1)
                originalRequest.pop(steamIndex + 1)
            addPreference = True
            preferenceFirst = True
            indicatorTuple = ("set", "remove", "delete")
            connectTuple = ("a", "my", "from")
            dividerTuple = ("as", "to")
            for possibleIndicator in indicatorTuple:
                if possibleIndicator in rawRequest:
                    indicatorIndex = rawRequest.index(possibleIndicator)
                    if not possibleIndicator == "set":
                        addPreference = False
                    break

            for possibleConnect in connectTuple:
                if possibleConnect in rawRequest:
                    connectIndex = rawRequest.index(possibleConnect)
                    break

            dividerIndex = connectIndex
            for possibleDivider in dividerTuple:
                if possibleDivider in rawRequest:
                    dividerIndex = rawRequest.index(possibleDivider)
                    break

            if indicatorIndex + 1 in [connectIndex]:
                preferenceFirst = False
                indicatorIndex += 1
                connectIndex = dividerIndex
            referencedObject = ""
            for gameSectionIndex in range(indicatorIndex + 1, dividerIndex):
                referencedObject += f"{originalRequest[gameSectionIndex]} "

            argumentList.append(referencedObject[:-1])

            referencedObject = ""
            for gameSectionIndex in range(connectIndex + 1, len(rawRequest)):
                referencedObject += f"{originalRequest[gameSectionIndex]} "

            referencedObject = referencedObject[:-1]
            argumentList.append(referencedObject)

            if not preferenceFirst:
                argumentList[1], argumentList[2] = argumentList[2], argumentList[1]
            argumentList[2] = argumentList[2].replace(" ", "_")
            if argumentList[2] in ["favourite_streamer", "favourite_game", "blacklisted_streamer"]:
                argumentList[2] += "s"
            if argumentList[2] == "steamid":
                argumentList[2] = "steam_id"


            if addPreference:
                return setPreference(argumentList[0], argumentList[1], argumentList[2])
            else:
                argumentList[1] = argumentList[1].replace(" ", "")
                return deletePreference(argumentList[0], argumentList[1], argumentList[2])
        else:
            if "play" in rawRequest or ("for" in rawRequest and "and" not in rawRequest and "vs" not in rawRequest):
                indicatorTuple = ("play", "for")
                for possibleIndicator in indicatorTuple:
                    if possibleIndicator in rawRequest:
                        indicatorIndex = rawRequest.index(possibleIndicator)
                        break

                referencedGame = ""
                for gameSectionIndex in range(indicatorIndex+1, len(rawRequest)):
                    referencedGame += f"{originalRequest[gameSectionIndex]} "
                if referencedGame:
                    referencedGame = referencedGame[:-1]
                    referencedGame = aliasesCheck(referencedGame)
                    argumentList.append(referencedGame)
                    break
            elif "graph" in rawRequest or "compare" in rawRequest:
                indicatorIndex = ""
                connectIndex = ""
                indicatorTuple = ("for", "compare")
                connectTuple = ("and", "vs")
                for possibleIndicator in indicatorTuple:
                    if possibleIndicator in rawRequest:
                        indicatorIndex = rawRequest.index(possibleIndicator)

                for possibleConnect in connectTuple:
                    if possibleConnect in rawRequest:
                        indicatorIndex = rawRequest.index(possibleConnect)
                        break

                if str(indicatorIndex) and str(connectIndex):
                    referencedObject = ""
                    for gameSectionIndex in range(indicatorIndex + 1, connectIndex):
                        referencedObject += f"{originalRequest[gameSectionIndex]} "
                    referencedObject = referencedObject[:-1]
                    argumentList.append(referencedObject)

                    referencedObject = ""
                    for gameSectionIndex in range(connectIndex + 1, len(rawRequest)):
                        referencedObject += f"{originalRequest[gameSectionIndex]} "
                    referencedObject = referencedObject[:-1]
                    argumentList.append(referencedObject)

                    break
                else:
                    return unknownRequest()
            for verb in linkingVerbs:
                if verb in rawRequest:
                    linkingVerb = rawRequest.index(verb)
                    extractedArgument = originalRequest[linkingVerb + 1]
                    extractedArgument = aliasesCheck(extractedArgument)
                    argumentList.append(extractedArgument)

    if "referenceType" in possibleFunctions[largestIndex][3]:
        argumentList.append(referenceType)
    if not argumentList:
        return possibleFunctions[largestIndex][1]()
    elif len(argumentList) == 1:
        return possibleFunctions[largestIndex][1](argumentList[0])
    elif len(argumentList) == 2:
        return possibleFunctions[largestIndex][1](argumentList[0], argumentList[1])
    elif len(argumentList) == 3:
        return possibleFunctions[largestIndex][1](argumentList[0], argumentList[1], argumentList[2])
    else:
        raise Exception("Redundant arguments extracted from request")

def tryRequestProcessing(userRequest, userID):
    try:
        return requestProcessing(userRequest, userID)
    except Exception as errorMessage:
        print(errorMessage)
        return unknownRequest()

