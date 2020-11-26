def fromUnixToUTC(unixTime):
    """
    Used to convert unix time to UTC

    :param unixTime: int - time to be converted in unix
    :return: List containing the time in UTC
    Return format [day, month, year, hour, minute, second]
    """
    # unix is the seconds since 1/1/1970 00:00 and therefore the method must take into consideration leap days
    daysInMonths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    dayFromLeap = unixTime / 86400
    # when the first leap day occurs from the epoch in days - calculation is left expanded to explain
    firstLeap = (365 * 2) + 31 + 29
    # when the leap day repeats in days - calculation is left expanded to explain
    repeatLeap = (365 * 4) + 1
    leapDays = 0
    # Checks if a leap day must be considered
    if dayFromLeap >= firstLeap:
        dayFromLeap -= firstLeap
        leapDays += 1
        # Removes all leap days from prior years
        while dayFromLeap >= repeatLeap:
            dayFromLeap -= repeatLeap
            leapDays += 1
    # Checks if the year of the date is a leap year
    if dayFromLeap < 366 - (31 + 29):
        daysInMonths[1] = 29
        leapDays -= 1
    day = (unixTime / 86400) - leapDays
    # Run if year of date is leap year
    if daysInMonths[1] == 29:
        year = 1970 + (day - 1) / 365
        day = (day - 1) % 365
        # Adds removed day
        day += 1
    else:
        year = 1970 + day / 365
        day = day % 365
    month = 1
    # Calculates the month and day
    while day > daysInMonths[month - 1]:
        day -= daysInMonths[month - 1]
        month += 1
    # As epoch is from 1st of jan not 0 of jan, add a day
    day += 1
    hour = (day % 1) * 24
    minute = (hour % 1) * 60
    second = round((minute % 1) * 60)
    timeList = [int(day), int(month), int(year), int(hour), int(minute), second]
    return timeList