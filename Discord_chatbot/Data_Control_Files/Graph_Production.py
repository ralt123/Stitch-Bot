# importing the required module
import matplotlib.pyplot as plt
from Discord_chatbot.Data_Control_Files.Local_Store import storageHandler
from Discord_chatbot.Data_Control_Files.Steam_API import steamHandler
from Discord_chatbot.Data_Control_Files.Twitch_API import twitchHandler


def produceSingleGraph(ID, trackedType):
    """
    Produces a single graph for a game/streamer and saves it as "botGraph.png"

    :param ID: int - ID of tracked game/streamer
    :param trackedType: str - either "twitch" or "steam" to indicate the platform of which the ID originates from
    :return: Boolean - Indicates whether the graph was successfully created with the given arguments
    """
    # Adjusts font
    plt.rcParams.update({'font.size': 10})
    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams['axes.labelweight'] = 'bold'

    # Retrieves tracked data regarding provided ID
    storedData = storageHandler.retrieveTrackedData(ID, trackedType)
    # returns False if there was no tracked data held for the provided ID
    if not storedData:
        return False
    # Sets title and labels
    if trackedType == "steam":
        graphLabel = steamHandler.getGameName(ID)
        graphTitle = f"{graphLabel} Player Count"
        yAxisLabel = "Player Count"
    else:
        graphTitle = twitchHandler.getStreamerName(ID)
        graphLabel = graphTitle
        graphTitle[0] = graphTitle[0].upper() + graphTitle[1:]
        graphTitle += " Viewer Count"
        yAxisLabel = "View Count"

    # Separate lists for the actual values within the x axis and display values
    # This is done so dates on the same day but different years are correctly sorted
    displayXAxis = []
    actualXAxis = []
    yAxis = []
    # Sets starting date for trend line
    date = storageHandler._unixToUTC(storedData[1][0])[0:3]
    date = str(date)[1:-1].replace(", ", "/")
    firstDate = date

    # Calculates the date stored and appends to necessary lists
    for i in range(len(storedData[1])):
        date = storageHandler._unixToUTC(storedData[1][i])
        displayDate = str(date[0:2])[1:-1].replace(", ", "/")
        actualDate = str(date[0:3])[1:-1].replace(", ", "/")
        displayXAxis.append(displayDate)
        actualXAxis.append(actualDate)

    # Sets last date for trend line
    lastDate = actualDate
    # Sets total and y axis values
    total = 0
    for count in storedData[2]:
        yAxis.append(int(count))
        total += int(count)
    average = total/len(storedData[2])

    # Sets the graphs size
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)

    # Sets trend line axes
    xtrendLine = [firstDate, lastDate]
    ytrendLine = [storedData[2][0], average]

    # creates the graphs
    ax.yaxis.grid(color='gray', linestyle='dashed')
    ax.xaxis.grid(color='gray', linestyle='dashed')
    ax.plot(actualXAxis, yAxis, "o-",linewidth=2, label=graphLabel) # , color="deepskyblue"
    plt.legend(framealpha=0.3)
    ax.plot(xtrendLine, ytrendLine, "--")
    # Changes display of x axis
    plt.xticks(actualXAxis, displayXAxis)

    # sets name of axes
    plt.xlabel('Date')
    plt.ylabel(yAxisLabel)

    # sets title
    plt.title(graphTitle)

    # Saves the graph as "botGraph.png"
    plt.savefig('images/botGraph.png', bbox_inches='tight')
    return True


def produceComparisonGraph(ID1, ID2, trackedType):
    """
    Produces a graph for a comparison between 2 games/streamers and saves it as "botGraph.png"
    Compares days of which both IDs were tracked

    :param ID1: int - ID of first tracked game/streamer
    :param ID2: int - ID of second tracked game/streamer
    :param trackedType: str - either "twitch" or "steam" to indicate the platform of which the ID originates from
    :return: Boolean - Indicates whether the graph was successfully created with the given arguments
    """
    # Adjusts font
    plt.rcParams.update({'font.size': 10})
    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams['axes.labelweight'] = 'bold'
    # plt.style.use(['dark_background'])

    # Retrieves tracked data regarding provided IDs
    storedData1 = storageHandler.retrieveTrackedData(ID1, trackedType)
    storedData2 = storageHandler.retrieveTrackedData(ID2, trackedType)
    # returns False if there was no tracked data held for either provided ID
    if not (storedData1 or storedData2):
        return False

    # Sets title and labels
    if trackedType == "steam":
        graphLabel1 = steamHandler.getGameName(ID1)
        graphLabel2 = steamHandler.getGameName(ID2)
        graphTitle = f"{graphLabel1} vs {graphLabel2} Player Count"
        yAxisLabel = "Player Count"
    else:
        graphLabel1 = twitchHandler.getStreamerName(ID1)
        graphLabel2 = twitchHandler.getStreamerName(ID2)
        graphLabel1 = graphLabel1[0].upper() + graphLabel1[1:]
        graphLabel2 = graphLabel2[0].upper() + graphLabel2[1:]
        graphTitle = f"{graphLabel1} vs {graphLabel2} Viewer Count"
        graphTitle += " Viewer Count"
        yAxisLabel = "View Count"

    # Variables used to deduce matching dates in the tracked data for the two provided IDs
    currentIndex1 = 0
    currentIndex2 = 0
    haltIndex1 = False
    haltIndex2 = False

    # Separate lists for the actual values within the x axis and display values
    # This is done so dates on the same day but different years are correctly sorted
    indexList1 = []
    indexList2 = []

    # Finds matching dates for the two IDs and records the index of these matching dates
    while True:
        # All dates for one IDs details have been reviewed therefore end the loop
        if currentIndex1 >= len(storedData1[1]) or currentIndex2 >= len(storedData2[2]):
            break
        if not haltIndex1:
            dateData1 = int(storedData1[1][currentIndex1]) % 86400
            currentIndex1 += 1
        if not haltIndex2:
            dateData2 = int(storedData2[1][currentIndex2]) % 86400
            currentIndex2 += 1
        # dates are the same so their indexes are appended to a list
        if dateData1 == dateData2:
            indexList1.append(currentIndex1 - 1)
            indexList2.append(currentIndex2 - 1)
        # The index containing the larger date is made stationary
        elif dateData1 > dateData2:
            haltIndex1 = True
            haltIndex2 = False
        else:
            haltIndex1 = False
            haltIndex2 = True

    # Returns False if only 1 or less dates match
    if len(indexList2) < 2:
        return False

    # Prepares variables for graph production
    displayXAxis = []
    actualXAxis = []
    yAxis1 = []
    yAxis2 = []
    # Sets first date for trend lines
    date = storageHandler._unixToUTC(storedData1[1][indexList1[0]])[0:3]
    date = str(date)[1:-1].replace(", ", "/")
    firstDate = date

    # Appends dates to lists, a last containing the actual time in UTC and another list containing
    # displayable time in UTC
    for currentIndex in indexList1:
        date = storageHandler._unixToUTC(storedData1[1][currentIndex])
        displayDate = str(date[0:2])[1:-1].replace(", ", "/")
        actualDate = str(date[0:3])[1:-1].replace(", ", "/")
        displayXAxis.append(displayDate)
        actualXAxis.append(actualDate)

    # Sets last matching dare for us in trend lines
    lastDate = actualDate
    # Sets total and y axis values
    total1 = 0
    total2 = 0
    for validIndex1, validIndex2 in zip(indexList1, indexList2):
        yAxis1.append(int(storedData1[2][validIndex1]))
        yAxis2.append(int(storedData2[2][validIndex2]))
        total1 += int(storedData1[2][validIndex1])
        total2 += int(storedData2[2][validIndex2])
    average1 = total1/len(indexList1)
    average2 = total2/len(indexList2)

    # Sets the graphs size
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)

    # Sets trend line axes
    xtrendLine = [firstDate, lastDate]
    ytrendLine1 = [storedData1[2][indexList1[0]], average1]
    ytrendLine2 = [storedData2[2][indexList2[0]], average2]

    # creates the graphs
    ax.yaxis.grid(color='gray', linestyle='dashed')
    ax.plot(actualXAxis, yAxis1, "o-", linewidth=2, label=graphLabel1, color="blue")  # , color="deepskyblue"
    ax.plot(actualXAxis, yAxis2, "o-", linewidth=2, label=graphLabel2, color="darkred")  # , color="deepskyblue"
    ax.plot(xtrendLine, ytrendLine1, "--", color="deepskyblue")
    ax.plot(xtrendLine, ytrendLine2, "--", color="red")
    plt.legend(framealpha=0.3)
    plt.xticks(actualXAxis, displayXAxis)

    # Changes display of x axis
    plt.xlabel('Date')
    # sets name of axes
    plt.ylabel(yAxisLabel)

    # sets title
    plt.title(graphTitle)

    # Saves the graph as "botGraph.png"
    plt.savefig('images/botGraph.png', bbox_inches='tight')
    return True

