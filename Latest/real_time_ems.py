import tkinter as tk
import threading
import time
from datetime import datetime
from tkinter import messagebox
import json
import subprocess
import pytz
from datetime import datetime, timedelta
import math


# import curret_watt_time as wt
import csv
from astral import LocationInfo
from astral.sun import sun 
from connections.charger.solArk_inverter import get_inverter_data
from automation import change_setpoint, get_coolbot_temp, get_sensor_temp
from connections.charger.enphase_automation import charger_on, charger_off, plugged_in, check_charging
from connections.charger.get_charger_consumption import get_miles_added
from connections.ev_battery import check_battery
from WT_nonEMS import generate_clean_periods, save_clean_periods

realtime = datetime.now()
ev_charge = 0
ev_miles_left = 0
pv_output = 0
cooler_indoor_temp = 0
ev_connected = True # EV charger plugged in? 
total_power = 0
power_map = {}
ev_power = 0
cooler_dirty_periods = []
ev_clean_periods = []
ev_charging = True
coolth_timer = 0
econ_timer = 0
ev_p5 = 0.983
ev_percent = 51 # EV battery percentage
cooler_load = 0
time_interval = 2 # mins
ev_miles_travelled = 0 # 
grid_power = 0 ##### read from inverter ('Grid' in power map)
solar_power_used = 0 
driving = False

############# WattTime Data #############
aoer = [] # average operatinig emission rate
moer = [] # marginal operating emission rate

############ Carbon Accounting ##########
grid_co2_list = []
grid_co2 = 0 
ev_grid_co2_list = []
ev_grid_co2 = 0
solar_saving_list = []
solar_saving = 0
ev_ems_co2_list = []
ev_ems_co2 = 0
cooler_ems_co2_list = []
cooler_ems_co2 = 0

baseline_con_emissions = 0
total_baseline_emissions = 0
ev_emission_reduction = 0 # relative to baseline 
pv_emission_reduction = 0
ems_emission_reduction = 0
total_emission_reduction = 0 # gonna be the sum(pv,ems,ev... reduction)


############# constants #################
EV_CHARGING_RATE = 11.5 ## kW 
EV_CAPPACITY = 131 ## kWh

############## Test Mode ################
EMS_EV = True
EMS_Cooler = True

############## input from UI ############
SETPOINT_DEFAULT = 41
SETPOINT_COOLTH = 35
SETPOINT_ECON = 48
CURRENT_SETPOINT = 33 
MAX_COOLTH_TIME_LIMIT = 40 # min 
MAX_ECON_TIME_LIMIT = 40
EV_PERCENT_DESIRED = 80
TMIN = 51
TMAX = 59
RULE_BASED_MODE = True
OPTIMIZATION_MODE = True

############## utility function ##############
def is_daytime(city="Detroit", country="USA"):
    location = LocationInfo(city, country)
    s = sun(location.observer, date=datetime.now().date())
    now = datetime.now().replace(tzinfo=None)
    sunrise = s['sunrise'].replace(tzinfo=None)
    sunset = s['sunset'].replace(tzinfo=None)
    return sunrise <= now <= sunset

# Load clean periods from JSON file
def load_clean_periods(filename="ev_clean_periods.json"):
    global ev_clean_periods
    with open(filename, "r") as file:
        periods = json.load(file)
    ev_clean_periods = periods

# Function to check if current time is in clean periods
def is_realtime_in_clean_periods(realtime, clean_periods):
    adjusted_realtime = realtime - timedelta(hours=5)
    for start, end in clean_periods:
        # Parse start and end times from ISO 8601 format
        start_dt = datetime.fromisoformat(start).astimezone(pytz.UTC)
        end_dt = datetime.fromisoformat(end).astimezone(pytz.UTC)
        if start_dt <= adjusted_realtime.astimezone(pytz.UTC) < end_dt:
            return True
    return False

def functional_test_save():
    #save all variables to csv
    global realtime
    global ev_charge, ev_miles_left, pv_output, cooler_indoor_temp, ev_connected
    global total_power, power_map, ev_power, cooler_dirty_periods
    global ev_charging, ev_percent, ev_p5, cooler_load, ev_miles_travelled, grid_power, solar_power_used, driving
    with open('output_1121.txt', 'a') as file:
        file.write(f"realtime: {realtime}")
        file.write(f"ev_charge: {ev_charge}, ev_miles_left: {ev_miles_left}, pv_output: {pv_output}, cooler_indoor_temp: {cooler_indoor_temp}, ev_connected: {ev_connected}\n")
        file.write(f"total_power: {total_power}, power_map: {power_map}, ev_power: {ev_power}, cooler_dirty_periods: {cooler_dirty_periods}\n")
        file.write(f"ev_charging: {ev_charging}, driving: {driving}\n")
        file.write(f"ev_percent: {ev_percent}, ev_p5: {ev_p5}, cooler_load: {cooler_load}\n")
        file.write(f"ev_miles_travelled: {ev_miles_travelled}, grid_power: {grid_power}, solar_power_used: {solar_power_used}\n")

########### Carbon Accounting Getters #############
baseline_con_emissions = ev_miles_travelled * 1.590 # lbs CO2/mile

def get_total_baseline_emissions():
    global total_baseline_emissions
    global baseline_con_emissions
    global grid_co2
    total_baseline_emissions = baseline_con_emissions + grid_co2
    return total_baseline_emissions

def get_ev_emission_reduction():
    global ev_emission_reduction
    global baseline_con_emissions
    global ev_grid_co2
    ev_emission_reduction = baseline_con_emissions - ev_grid_co2
    return ev_emission_reduction

def get_pv_emission_reduction():
    global solar_saving
    return solar_saving  

def get_total_ems_ev_cooler_emissions():
    global ev_ems_co2, cooler_ems_co2
    return ev_ems_co2 + cooler_ems_co2

############### data inputs ###############
def bring_in_inverter_data():
    global power_map
    power_map = get_inverter_data()

def get_pv():
    global pv_output
    pv = power_map["Solar W"]
    pv = int(pv.replace("W", ""))
    pv_output = pv 

def update_realtime():
    global realtime
    realtime = datetime.now()

# def get_cooler_temp():
#     global cooler_indoor_temp
#     cooler_indoor_temp = (get_coolbot_temp() + get_sensor_temp()) / 2

def get_ev_connection():
    global ev_connected
    ev_connected = plugged_in()

def get_is_ev_charging():
    global ev_charging
    ev_charging = check_charging()

def get_total_power():
    global coolEV_power
    consumption = power_map["Consumed W"]
    consumption = int(consumption.replace("W", ""))
    coolEV_power = consumption

def get_charge():
    global ev_charge
    global ev_percent
    global ev_miles_left

    ev_battery_dict = check_battery()
    ev_charge = int(ev_battery_dict['percentage'])
    ev_percent = int(ev_charge)
    ev_miles_left = int(ev_battery_dict['miles_left'])


def get_amount_of_clean_periods():
    global EV_CHARGING_RATE
    global EV_CAPPACITY
    global ev_percent
    global EV_PERCENT_DESIRED
    global time_interval
    result = (((EV_PERCENT_DESIRED - ev_percent)/100 * EV_CAPPACITY) / EV_CHARGING_RATE) * 60 / time_interval
    return math.ceil(result)

def get_ev_miles_travelled():
    global ev_miles_travelled
    ev_miles_travelled += get_miles_added()
    return ev_miles_travelled


############### control commands ###############
def send_cooler_decision(setpoint):
    """Return true if setpoint changed, false otherwise."""
    return change_setpoint(setpoint)

def send_charging_decision(OnOFF:bool):
    if OnOFF:
        charger_on()
    else:
        charger_off()



############### updater ###############
def update_inverter_data():
    global power_map
    global pv_output
    global grid_power
    # while True:
    bring_in_inverter_data()
    pv_output = int(power_map["Solar W"][:-1])
    grid_power = int(power_map["Grid W"][:-1])

# def update_charge_data():
#     while True:
#         get_charge()
#         time.sleep(300)  # Update every 5 minutes

############### decision rules ###############
def ems():
    global pv_output 
    global coolEV_power
    global total_power
    global ev_charging
    global cooler_indoor_temp
    global realtime 
    global ev_connected 
    global ev_p5  
    global realtime
    global driving
    global cooler_indoor_temp
   
    with open('output_1121.txt', 'a') as file:
        if pv_output > total_power: # daytime 
            if ev_charging:
                # adjust temperature setpoint  
                if CURRENT_SETPOINT != SETPOINT_COOLTH:
                    cooler_indoor_temp = send_cooler_decision(SETPOINT_COOLTH)
                    file.write(f"{realtime}: send_cooler_decision({SETPOINT_COOLTH}\n")
                    functional_test_save()
                    CURRENT_SETPOINT = SETPOINT_COOLTH
                else:  # avoid coolth damage 
                    if cooler_indoor_temp <= SETPOINT_COOLTH + 2:
                        # start time 
                        if coolth_timer == 0:
                            # TODO: set a timer here 
                            pass
                        elif coolth_timer >= MAX_COOLTH_TIME_LIMIT:
                            cooler_indoor_temp = send_cooler_decision(SETPOINT_DEFAULT)
                            file.write(f"{realtime}: send_cooler_decision({SETPOINT_DEFAULT}\n")
                            functional_test_save()
            elif ev_charging == False and ev_connected == True:
                if pv_output > total_power + ev_p5:
                    cooler_indoor_temp = send_charging_decision(True)
                    file.write(f"{realtime}: send_charging_decision(True)\n")
                    functional_test_save()

                    # star
                    if CURRENT_SETPOINT != SETPOINT_COOLTH:
                        cooler_indoor_temp = send_cooler_decision(SETPOINT_COOLTH)
                        file.write(f"{realtime}: send_cooler_decision({SETPOINT_COOLTH}\n")
                        functional_test_save()
                        CURRENT_SETPOINT = SETPOINT_COOLTH
                    else:  # avoid coolth damage 
                        if cooler_indoor_temp <= SETPOINT_COOLTH + 2:
                            # start time 
                            if coolth_timer == 0:
                                # TODO: set a timer here 
                                pass
                            elif coolth_timer >= MAX_COOLTH_TIME_LIMIT:
                                cooler_indoor_temp = send_cooler_decision(SETPOINT_DEFAULT)
                                file.write(f"{realtime}: send_cooler_decision({SETPOINT_DEFAULT}\n")
                                functional_test_save()
                else:
                    # star 
                    if CURRENT_SETPOINT != SETPOINT_COOLTH:
                        cooler_indoor_temp = send_cooler_decision(SETPOINT_COOLTH)
                        file.write(f"{realtime}: send_cooler_decision({SETPOINT_COOLTH}\n")
                        functional_test_save()
                        CURRENT_SETPOINT = SETPOINT_COOLTH
                    else:  # avoid coolth damage 
                        if cooler_indoor_temp <= SETPOINT_COOLTH + 2:
                            # start time 
                            if coolth_timer == 0:
                                # TODO: set a timer here 
                                pass
                            elif coolth_timer >= MAX_COOLTH_TIME_LIMIT:
                                cooler_indoor_temp = send_cooler_decision(SETPOINT_DEFAULT)
                                file.write(f"{realtime}: send_cooler_decision({SETPOINT_DEFAULT}\n")
                                functional_test_save()

        else: # daytime && night 
            if realtime not in cooler_dirty_periods:
                # TODO do some coolth? 
                cooler_indoor_temp = send_cooler_decision(SETPOINT_DEFAULT)
                file.write(f"{realtime}: send_cooler_decision({SETPOINT_DEFAULT}\n")
                functional_test_save()
            else:
                if CURRENT_SETPOINT != SETPOINT_ECON:
                    cooler_indoor_temp = send_cooler_decision(SETPOINT_ECON)
                    CURRENT_SETPOINT = SETPOINT_ECON
                    file.write(f"{realtime}: send_cooler_decision({SETPOINT_ECON}\n")
                    functional_test_save()
                else: # avoid econ damage
                    if cooler_indoor_temp >= SETPOINT_ECON - 2:
                        # start time counting 
                        if econ_timer == 0:
                            # TODO: set a timer here
                            pass
                        elif econ_timer >= MAX_ECON_TIME_LIMIT:
                            cooler_indoor_temp = send_cooler_decision(SETPOINT_DEFAULT)
                            file.write(f"{realtime}: send_cooler_decision({SETPOINT_DEFAULT}\n")
                            functional_test_save()

        if EMS_EV:  # test EMS + EV 
            realtime = datetime.now()
            load_clean_periods()
            if is_realtime_in_clean_periods(realtime, ev_clean_periods):
                print(f"Current time {realtime.strftime('%H:%M')} is within a clean period.")
                if ev_connected:
                    if ev_charging == False: 
                        send_charging_decision(True)
                        file.write(f"{realtime}: send_charging_decision(True)\n")
                        functional_test_save()
                    else:
                        file.write(f"{realtime}: send_charging_decision(True), do nothing\n")
                        functional_test_save()

            else:
                print(f"Current time {realtime.strftime('%H:%M')} is NOT within a clean period.")
                if ev_connected:
                    if driving == True:
                        # returned from a drive
                        # regen clean periods
                        driving = False
                        num_clean_periods = get_amount_of_clean_periods()
                        print(num_clean_periods)
                        generate_clean_periods(num_clean_periods)
                        save_clean_periods()
                        file.write(f"{realtime}: back, generate new clean charging schedule\n")
                        functional_test_save()
                    if ev_charging:
                        send_charging_decision(False)
                        file.write(f"{realtime}: send_charging_decision(False))\n")
                        functional_test_save()
                    else: 
                        file.write(f"{realtime}: send_charging_decision(False), do nothing\n")
                        functional_test_save()
                else:
                    driving = True
                    file.write(f"{realtime}: going on a drive)\n")
                    functional_test_save()

        # ############## calculation ################
        # grid_co2_list.append(max(0,aoer * grid_power))
        # grid_co2 = sum(grid_co2_list)

        # ############## EV reduction ###############
        # ev_total_load_fraction = ev_p5 / total_power ## total_power: PV used + grid power  (maybe 'Consume' in power map)
        # ev_grid_load = ev_total_load_fraction * grid_power 
        # ev_grid_co2_list.append(max(0,aoer * ev_grid_load))
        # ev_grid_co2 = sum(ev_grid_co2_list)

        # ############## PV reduction ###############
        # solar_saving_list.append(max(0, aoer * solar_power_used))
        # solar_saving = sum(solar_saving_list)

        # ############## rule-based EMS carbon accounting ##########
        # ev_ems_co2_list.append(max(0,moer * ev_grid_load))
        # ev_ems_co2 = sum(ev_ems_co2_list)

        # cooler_grid_load = (cooler_load / total_power) * grid_power
        # cooler_ems_co2_list.append(max(0, moer * cooler_grid_load))    
        # cooler_ems_co2 = sum(cooler_ems_co2_list)

            # time.sleep(300) # run ems rules to make decisions every 5 mins 

############### multi-thread ###############
def main():
    global ev_percent, pv_output, grid_power, ev_charging, cooler_indoor_temp

    try:
        while True:
            # print(f"Current ev_charge: {ev_charge}")
            # print(f"Realtime: {datetime.now()}")
            get_ev_connection()
            get_charge()
            update_inverter_data()
            get_is_ev_charging()
            update_realtime()
            # get_cooler_temp()
            ems()
            print(f"EV Charge: {ev_percent}%")
            print(f"PV Output: {pv_output}W")
            print(f"Grid Power: {grid_power}W")
            print(f"EV Charging Status: {ev_charging}")
            print(f"Cooler Indoor Temp: {cooler_indoor_temp}F")
            # print(f"Current Setpoint: {CURRENT_SETPOINT}")
            time.sleep(60)  # Adjust this interval as needed to monitor `ev_charge`
    except KeyboardInterrupt:
        print("Program interrupted and stopped.")
    

if __name__ == "__main__":
    main()
    # print(get_amount_of_clean_periods())

    # print(ev_charging)

    ######## check cooler command functionality ########
    # send_cooler_decision(34)


    ######### check ev connection functionality ########
    # get_ev_connection()
    # print(ev_connected)
    # get_charge()
    # print(ev_charge)
    # print(ev_miles_left)

    ######### check clean periods extraction functionality ########
    # load_clean_periods()
    # if is_realtime_in_clean_periods(realtime,ev_clean_periods):
    #     print(f"Current time {realtime.strftime('%H:%M')} is within a clean period.")
    # else:
    #     print(f"Current time {realtime.strftime('%H:%M')} is NOT within a clean period.")

    ######### check inverter #########
    # bring_in_inverter_data()
    # print(power_map)

    
