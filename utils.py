import datetime


def soc_to_dateTime(soc):
    timestamp = datetime.datetime.utcfromtimestamp(soc)
    
    day = timestamp.strftime('%A')
    month = timestamp.strftime('%B')
    date = timestamp.strftime('%d')
    year = timestamp.strftime('%Y')
    time = timestamp.strftime('%H:%M:%S')

    return day, month, date, year, time


if __name__ == "__main__":
    pass