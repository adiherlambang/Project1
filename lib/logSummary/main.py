import pandas as pd
import re
from datetime import datetime

# Define regex pattern to extract information from each log line
pattern = re.compile(r'(\w+) (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ \[(.*?)\] (.*)')

# Define function to filter log lines based on start time
def filter_logs_by_start_time(log_lines, start_time):
    filtered_logs = []
    for line in log_lines:
        match = pattern.match(line)
        if match:
            timestamp = datetime.strptime(match.group(2), '%Y-%m-%d %H:%M:%S')
            if timestamp >= start_time:
                filtered_logs.append(match.groups())
    return filtered_logs

def summary_log(start_time):
    # Open the log file
    with open('log/CaptureConfig.log', 'r') as file:
        lines = file.readlines()

    log_start_time = start_time
    date_str, time_str = log_start_time.split(' ')
    year, month, day = map(int, date_str.split('-'))
    hour, minute, second = map(int, time_str.split(':'))
    # Define start time for filtering
    start_time = datetime(year, month, day, hour, minute, second)

    # Filter log lines based on start time
    filtered_logs = filter_logs_by_start_time(lines, start_time)

    # Parse filtered log lines and extract relevant information
    parsed_data = []
    for line in filtered_logs:
        log_level, timestamp, location, message = line
        parsed_data.append({'Timestamp': timestamp, 'Level': log_level, 'Location': location, 'Message': message})

    # Create a DataFrame from the parsed data
    df = pd.DataFrame(parsed_data)

    error_df = df[df['Level'] == 'ERROR']
    
    datime_logsFile = start_time.strftime("%d-%m-%y_%H_%M_%S")
    logs_file = 'log_summary_'+datime_logsFile+'.xlsx'

    # Write summaries to Excel
    with pd.ExcelWriter('log/summary/'+logs_file) as writer:
        error_df.to_excel(writer, sheet_name='Log Summary')
        # error_summary.to_excel(writer, sheet_name='Error Summary')
        return logs_file
