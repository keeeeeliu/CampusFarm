import subprocess
import time
from datetime import datetime
import csv
import os

def check_wifi_status_ifconfig():
    result = subprocess.run(['ifconfig'], capture_output=True, text=True)
    # print(result)
    if 'status: active' in result.stdout:
        # print("Wi-Fi is active.")
        return True 
        # return "active"
    else:
        # print("Wi-Fi is not connected or inactive.")
        return False 
        # return "inactive"

def monitor_wifi_status(interval=5, csv_filename='wifi_status.csv'):
    # Check if CSV file exists to determine if we need to write the header
    file_exists = os.path.isfile(csv_filename)
    try:
        with open(csv_filename, 'a', newline='') as csvfile:
            fieldnames = ['Timestamp', 'Wi-Fi Status']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            # Write header only if file does not exist
            if not file_exists:
                writer.writeheader()

            while True:
                status = check_wifi_status_ifconfig()
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # Write the status and timestamp to CSV
                writer.writerow({'Timestamp': timestamp, 'Wi-Fi Status': status})
                # Optionally print the status to the console
                # print(f"{timestamp} - {status}")
                time.sleep(interval)  # Wait for the specified interval before checking again
    except KeyboardInterrupt:
        print("Monitoring stopped.")
# monitor_wifi_status(5)

# print(check_wifi_status_ifconfig())