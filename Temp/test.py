import datetime

def soc_to_datetime(soc):
    # Convert SOC (seconds since Jan 1, 1970) to a datetime object
    timestamp = datetime.datetime.utcfromtimestamp(soc)
    
    # Return the formatted date and time
    return timestamp

# Example SOC value (replace with your actual SOC value)
soc = 1680000000  # Replace this with your actual 32-bit SOC value

# Get the date and time
result = soc_to_datetime(soc)

# Print the result
print("Day, Date and Time:", result.strftime('%A, %B %d, %Y %H:%M:%S UTC'))
