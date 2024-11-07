import tkinter as tk
import threading
import time
from datetime import datetime
from tkinter import messagebox
import json
import subprocess
# import curret_watt_time as wt
import csv
from astral import LocationInfo
from astral.sun import sun 


realtime = datetime.now()
ev_charge = 0
pv_output = 0
cooler_indoor_temp = 0
ev_connected = True
coolEV_power = 0

# note: read data from json file

############## utility function ##############
def is_daytime(city="Detroit", country="USA"):
    location = LocationInfo(city, country)
    s = sun(location.observer, date=datetime.now().date())
    now = datetime.now().replace(tzinfo=None)
    sunrise = s['sunrise'].replace(tzinfo=None)
    sunset = s['sunset'].replace(tzinfo=None)
    return sunrise <= now <= sunset

############### data inputs ###############
def get_pv():
    global pv_output
    pass

def get_cooler_temp():
    global cooler_indoor_temp
    pass

def get_ev_connection():
    global ev_connected
    pass

def get_total_power():
    global coolEV_power
    pass

def get_charge():
    while True:
        global ev_charge
        try:
            with open('charge_data.json','r') as file:
                data = json.load(file)
                ev_charge = data['charge']
                print(ev_charge)
        except FileNotFoundError:
            ev_charge = 0.0
        
        time.sleep(2) # update EV charge every 5 mintues 


############### control commands ###############
def send_cooler_decision():
    pass

def send_charging_decision():
    pass

############### decision rules ###############
def ems():
    while True:
   
        # TODO: add ems rules here
        
        print(is_daytime())
        time.sleep(2) # run ems rules to make decisions every 5 mins 


############### multi-thread ###############
def main():

    # Start the ems script thread
    main_thread = threading.Thread(target=ems)
    main_thread.daemon = True  # Daemonize thread to exit when ems thread exits
    main_thread.start()

    # Start the real-time charge (walking steps) update thread
    charge_update_thread = threading.Thread(target=get_charge)
    charge_update_thread.daemon = True  # Daemon thread for step updates
    charge_update_thread.start()

    try:
        while True:
            print(f"Current ev_charge: {ev_charge}")
        
            time.sleep(10)  # Adjust this interval as needed to monitor `ev_charge`
    except KeyboardInterrupt:
        print("Program interrupted and stopped.")
    

if __name__ == "__main__":
    main()