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
from connections.charger.solArk_inverter import get_inverter_data
from automation import change_setpoint
from connections.charger.enphase_automation import charger_on
from connections.charger.enphase_automation import charger_off


realtime = datetime.now()
ev_charge = 0
pv_output = 0
cooler_indoor_temp = 0
ev_connected = True
total_power = 0
power_map = {}
cooler_dirty_periods = []
ev_clean_periods = []
ev_charging = True
coolth_timer = 0
econ_timer = 0
ev_percent = 0
ev_p5 = 0


############## input from UI ############
SETPOINT_DEFAULT = 55
SETPOINT_COOLTH = 53
SETPOINT_ECON = 57
CURRENT_SETPOINT = 55 
MAX_COOLTH_TIME_LIMIT = 40 # min 
MAX_ECON_TIME_LIMIT = 40
EV_PERCENT_DESIRED = 60

############## utility function ##############
def is_daytime(city="Detroit", country="USA"):
    location = LocationInfo(city, country)
    s = sun(location.observer, date=datetime.now().date())
    now = datetime.now().replace(tzinfo=None)
    sunrise = s['sunrise'].replace(tzinfo=None)
    sunset = s['sunset'].replace(tzinfo=None)
    return sunrise <= now <= sunset

############### data inputs ###############
def bring_in_inverter_data():
    global power_map
    power_map = get_inverter_data()

def get_pv():
    global pv_output
    pv = power_map["Solar W"]
    pv = int(pv.replace("W", ""))
    pv_output = pv 

def get_cooler_temp():
    global cooler_indoor_temp
    pass

def get_ev_connection():
    global ev_connected
    pass

def get_total_power():
    global coolEV_power
    consumption = power_map["Consumed W"]
    consumption = int(consumption.replace("W", ""))
    coolEV_power = consumption

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
def send_cooler_decision(setpoint):
    """Return true if setpoint changed, false otherwise."""
    return change_setpoint(setpoint)

def send_charging_decision(OnOFF:bool):
    if OnOFF:
        charger_on()
    else:
        charger_off()

############### decision rules ###############
def ems():
    global pv_output 
    global coolEV_power
    while True:
   
        # TODO: add ems rules here
        if pv_output > total_power: # daytime 
            if ev_charging:
                # adjust temperature setpoint  
                if CURRENT_SETPOINT != SETPOINT_COOLTH:
                    send_cooler_decision(SETPOINT_COOLTH)
                    CURRENT_SETPOINT = SETPOINT_COOLTH
                else:  # avoid coolth damage 
                    if cooler_indoor_temp <= SETPOINT_COOLTH + 2:
                        # start time 
                        if coolth_timer == 0:
                            # TODO: set a timer here 
                            pass
                        elif coolth_timer >= MAX_COOLTH_TIME_LIMIT:
                            send_cooler_decision(SETPOINT_DEFAULT)
            elif ev_charging == False and ev_connected == True:
                if pv_output > total_power + ev_p5:
                    send_charging_decision(True)

                    # star
                    if CURRENT_SETPOINT != SETPOINT_COOLTH:
                        send_cooler_decision(SETPOINT_COOLTH)
                        CURRENT_SETPOINT = SETPOINT_COOLTH
                    else:  # avoid coolth damage 
                        if cooler_indoor_temp <= SETPOINT_COOLTH + 2:
                            # start time 
                            if coolth_timer == 0:
                                # TODO: set a timer here 
                                pass
                            elif coolth_timer >= MAX_COOLTH_TIME_LIMIT:
                                send_cooler_decision(SETPOINT_DEFAULT)
                else:
                    # star 
                    if CURRENT_SETPOINT != SETPOINT_COOLTH:
                        send_cooler_decision(SETPOINT_COOLTH)
                        CURRENT_SETPOINT = SETPOINT_COOLTH
                    else:  # avoid coolth damage 
                        if cooler_indoor_temp <= SETPOINT_COOLTH + 2:
                            # start time 
                            if coolth_timer == 0:
                                # TODO: set a timer here 
                                pass
                            elif coolth_timer >= MAX_COOLTH_TIME_LIMIT:
                                send_cooler_decision(SETPOINT_DEFAULT)


        else: # daytime && night 
            if realtime in cooler_dirty_periods:
                # TODO do some coolth? 
                send_cooler_decision(SETPOINT_DEFAULT)
            else:
                if CURRENT_SETPOINT != SETPOINT_ECON:
                    send_cooler_decision(SETPOINT_ECON)
                    CURRENT_SETPOINT = SETPOINT_ECON
                else: # avoid econ damage
                    if cooler_indoor_temp >= SETPOINT_ECON - 2:
                        # start time counting 
                        if econ_timer == 0:
                            # TODO: set a timer here
                            pass
                        elif econ_timer >= MAX_ECON_TIME_LIMIT:
                            send_cooler_decision(SETPOINT_DEFAULT)



        if realtime in ev_clean_periods:
            if ev_connected:
                send_charging_decision(True)
        else:
            if ev_connected:
                send_charging_decision(False)

            


        # if is_daytime() == False: # nighttime: charge during clean periods
            
        #     if ev_connected:
        #         if realtime in clean_periods:
        #             # send command: ev charge on 
        #             send_charging_decision(True)
        #         else:
        #             # send command: ev charge off
        #             send_charging_decision(False)
            
        #     if realtime in clean_periods:
        #         # send command: cooler temp default
        #         send_cooler_decision(SETPOINT_DEFAULT)
        #     else:
        #         # send command: cooler temp eco
        #         send_cooler_decision(SETPOINT_ECO)

        # if is_daytime() == True: # daytime: lower temp setpoint when excess PV
        #     if pv_output >= coolEV_power:
        #         # send command: cooler temp coolth
        #         send_cooler_decision(SETPOINT_COOLTH)
        #     else:
        #         # send command: cooler temp default 
        #         send_cooler_decision(SETPOINT_DEFAULT)
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
    # main()
    send_cooler_decision(34)