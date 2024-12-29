import datetime
import pandas as pd
import matplotlib.pyplot as plt
import uuid
import time
import re

def parse_column_detail(table_definition):
    
    column_names = table_definition
    column_names = column_names.split(',')
    column_names = [a.split(' ')[0] for a in column_names]
    column_names = [a.split('\n')[1] for a in column_names]
    
    return column_names

def generate_unique_identifier(client_address=None, client_port=None):
    timestamp = int(time.time() * 1000)  # Milliseconds since epoch
    unique_id = uuid.uuid4()  # Generate a UUID
    
    if client_address and client_port:
        identifier = f"{timestamp}-{client_address}:{client_port}-{unique_id}"
    else:
        identifier = f"{timestamp}-{unique_id}"
    
    return identifier

def soc_to_dateTime(soc):
    timestamp = datetime.datetime.utcfromtimestamp(soc)
    
    day = timestamp.strftime('%A')
    month = timestamp.strftime('%B')
    date = timestamp.strftime('%d')
    year = timestamp.strftime('%Y')
    time = timestamp.strftime('%H:%M:%S')

    return day, month, date, year, time

def plot_figure(file_path):
    df = pd.read_csv(file_path)
    df['Time'] = pd.to_datetime(df['Unnamed: 0'], errors='coerce')
    df.dropna(subset=['Time'], inplace=True)

    plt.figure(figsize=(12, 6))

    # Plot Frequency
    plt.subplot(2, 1, 1)
    plt.plot(df['Time'], df['Frequency'], color='blue', label='Frequency')
    plt.title('Frequency over Time')
    plt.xlabel('Time')
    plt.ylabel('Frequency (Hz)')
    plt.grid(True)
    plt.legend()

    # Plot ROCOF
    # plt.subplot(2, 1, 2)
    # plt.plot(df['Time'], df['ROCOF]'], color='red', label='ROCOF')
    # plt.title('Rate of Change of Frequency (ROCOF) over Time')
    # plt.xlabel('Time')
    # plt.ylabel('ROCOF')
    # plt.grid(True)
    # plt.legend()

    # Adjust layout and show the plots
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    pass