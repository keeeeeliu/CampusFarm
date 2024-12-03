############## Imports ###############

import tkinter as tk
import time
from datetime import datetime
import json
import pytz
from datetime import datetime, timedelta
import math
#import webAPI
import requests
import subprocess

from astral import LocationInfo
from astral.sun import sun 
from connections.charger.solArk_inverter import get_inverter_data
from automation import change_setpoint, get_coolbot_temp, get_sensor_temp
from connections.charger.enphase_automation import charger_on, charger_off, plugged_in_and_charging
from connections.charger.get_charger_consumption import get_miles_added
from connections.ev_battery import check_battery
from WT_nonEMS import generate_clean_periods, save_clean_periods, save_nonEMS_charging_periods
from wifistatus import check_wifi_status_ifconfig
from genDirtyPeriods import generate_dirty_periods, save_dirty_periods
from WT_accounting import get_wt
from WT_data_optimization import get_48h_wt
from ems_UI import save_to_json, ui_main


############## Globals ###################
realtime = datetime.now()
ev_charge = 100
ev_miles_left = 0
pv_output = 0
cooler_indoor_temp = 33
ev_connected = True # EV charger plugged in? 
total_power = 0
power_map = {}
cooler_dirty_periods = []
ev_clean_periods = []
ev_nonEMS_charging_periods = []
ev_charging = False
coolth_timer = 0
econ_timer = 0
rules_timer = datetime.now()
charging_timer = datetime.now()
enphase_down = False
ev_p5 = 958.33
cooler_load = 0
time_interval = 5 # mins
ev_miles_travelled = 0 # 
grid_power = 0 ##### read from inverter ('Grid' in power map)
solar_power_used = 0 
driving = False
dirtytime_threshold = 3 # hours 
last_24_hour_run = datetime.now()
#### globals for outdoor temp
outdoor_temp = 0 # read from temp sensor
vent_open = False

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
ev_nonEMS_co2_list = []
ev_nonEMS_co2 = 0
cooler_ems_co2_list = []
cooler_ems_co2 = 0

baseline_con_emissions = 0
total_baseline_emissions = 0
ev_emission_reduction = 0 # relative to baseline 
pv_emission_reduction = 0
ems_emission_reduction = 0
total_emission_reduction = 0 # gonna be the sum(pv,ems,ev... reduction)
wifi_status = True 


############# constants #################
EV_CHARGING_RATE = 11.5 ## kW 
EV_CAPACITY = 131 ## kWh

############## Test Mode ################
EMS_EV = True
EMS_Cooler = True

############## input from UI ############
SETPOINT_DEFAULT = 41
SETPOINT_COOLTH = 35
SETPOINT_ECON = 48
CURRENT_SETPOINT = 32 
MAX_COOLTH_TIME_LIMIT = 40 # min 
MAX_ECON_TIME_LIMIT = 40
EV_PERCENT_DESIRED = 95
TMIN = 51
TMAX = 59
RULE_BASED_MODE = True
OPTIMIZATION_MODE = True

############## utility function ##############

# Load variables from JSON
def load_UI_data():
    save_to_json()
    global SETPOINT_DEFAULT, SETPOINT_COOLTH, SETPOINT_ECON, MAX_COOLTH_TIME_LIMIT, MAX_ECON_TIME_LIMIT, EV_PERCENT_DESIRED, TMIN, TMAX, RULE_BASED_MODE, OPTIMIZATION_MODE, CURRENT_SETPOINT
    with open("config.json", "r") as json_file:
        config = json.load(json_file)

    # Access variables
    SETPOINT_DEFAULT= config["current_temperature"]
    TMIN = config["tmin"]
    TMAX = config["tmax"]
    SETPOINT_COOLTH = config["coolth"]
    SETPOINT_ECON = config["econ"]
    MAX_COOLTH_TIME_LIMIT = config["tolerance_time"]
    MAX_ECON_TIME_LIMIT = config["tolerance_time"]
    EV_PERCENT_DESIRED = config["current_charge"]
    if config["current_mode"] == "Rule-Based":
        RULE_BASED_MODE = True
        OPTIMIZATION_MODE = False
    elif config["current_mode"] == "Optimization":
        RULE_BASED_MODE = False
        OPTIMIZATION_MODE = True


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

def load_nonEMS_charging_periods(filename="ev_nonEMS_charging_periods.json"):
    global ev_nonEMS_charging_periods
    with open(filename, "r") as file:
        periods = json.load(file)
    ev_nonEMS_charging_periods = periods

# Load dirty periods from JSON file
def load_dirty_periods(filename="cooler_dirty_periods.json"):
    global cooler_dirty_periods
    with open(filename, "r") as file:
        periods = json.load(file)
    cooler_dirty_periods = periods

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
    global total_power, power_map, cooler_dirty_periods
    global ev_charging, ev_charge, ev_p5, cooler_load, ev_miles_travelled, grid_power, solar_power_used, driving
    global enphase_down
    with open('output_1202.txt', 'a') as file:
        file.write(f"realtime: {realtime}\n")
        file.write(f"Current Setpoint: {CURRENT_SETPOINT}\n")
        file.write(f"Enphase website down? {enphase_down}\n")
        file.write(f"ev charging ? {ev_charging}\n")
        file.write(f"current temp in cooler: {cooler_indoor_temp}")
        file.write(f"ev_charge: {ev_charge}, ev_miles_left: {ev_miles_left}, pv_output: {pv_output}, cooler_indoor_temp: {cooler_indoor_temp}, ev_connected: {ev_connected}\n")
        file.write(f"total_power: {total_power}, power_map: {power_map}, cooler_dirty_periods: {cooler_dirty_periods}\n")
        file.write(f"ev_charging: {ev_charging}, driving: {driving}\n")
        file.write(f"ev_p5: {ev_p5}, cooler_load: {cooler_load}\n")
        file.write(f"ev_miles_travelled: {ev_miles_travelled}, grid_power: {grid_power}, solar_power_used: {solar_power_used}\n\n")

        

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
    old_power_map = power_map
    power_map = get_inverter_data()
    if not power_map:
        print("reattempt solark")
        power_map = get_inverter_data()
    if not power_map:
        print("reattempt solark 2")
        power_map = get_inverter_data()
    if not power_map:
        print("reattempt solark 3")
        power_map = get_inverter_data()
    if not power_map:
        print("reattempt solark 4")
        power_map = get_inverter_data()
    if not power_map:
        print("reattempt solark 5")
        power_map = get_inverter_data()
    if not power_map:
        power_map = old_power_map

def get_pv():
    global pv_output
    pv = power_map["Solar W"]
    pv = int(pv.replace("W", ""))
    pv_output = pv 

def update_realtime():
    global realtime
    realtime = datetime.now()

def get_cooler_temp():
    url="http://192.168.0.160:5000/temperature"
    global cooler_indoor_temp
    try:
        print("temp sensor worked!")
        response = requests.get(url)
        response.raise_for_status() 
        cooler_indoor_temp = float(response.text.strip())
        print(cooler_indoor_temp)
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"An error occurred with the temp sensor trying automation: {e}")
        cooler_indoor_temp = (get_coolbot_temp() + get_sensor_temp()) / 2

#### Get outdoor temp from temp sensor
def get_outdoor_temp():
    global outdoor_temp
    pass

#### Function to control the vent
def open_vent():
    global vent_open
    vent_open = True
    pass

def close_vent():
    global vent_open
    vent_open = False
    pass

def change_vent():
    global vent_open
    global cooler_indoor_temp
    global outdoor_temp, TMIN

    if outdoor_temp < cooler_indoor_temp and cooler_indoor_temp > TMIN and not vent_open:
        open_vent()
    else:
        if vent_open:
            close_vent()
    
    return vent_open

def get_is_ev_conn_and_charging():
    global ev_charging
    global ev_connected
    global enphase_down
    connection_dict = plugged_in_and_charging()
    enphase_down = False
    if len(connection_dict) != 2: #should be size two if it worked
        print("reattempt enphase")
        connection_dict = plugged_in_and_charging()
    if len(connection_dict) != 2:
        print("reattempt enphase 2")
        connection_dict = plugged_in_and_charging()
    if len(connection_dict) != 2:
        print("reattempt enphase 3")
        connection_dict = plugged_in_and_charging()
    if len(connection_dict) != 2:
        print("reattempt enphase 4")
        connection_dict = plugged_in_and_charging()
    if len(connection_dict) != 2:
        print("reattempt enphase 5")
        connection_dict = plugged_in_and_charging()
    if len(connection_dict) != 2:
        enphase_down = True
    
    if enphase_down == False:
        ev_connected = connection_dict['connected']
        ev_charging = connection_dict['charging']

def get_total_power():
    global total_power
    consumption = power_map["Consumed W"]
    consumption = int(consumption.replace("W", ""))
    total_power = consumption

def get_charge():
    global ev_charge
    global ev_miles_left

    old_ev_charge = ev_charge
    old_ev_miles_left = ev_miles_left

    ev_battery_dict = check_battery()
    if not ev_battery_dict:
       print("reattempt ford")
       ev_battery_dict = check_battery() 

    if not ev_battery_dict:
       print("reattempt ford 2")
       ev_battery_dict = check_battery() 
    
    if not ev_battery_dict:
       print("reattempt ford 3")
       ev_battery_dict = check_battery() 
    
    if not ev_battery_dict:
       print("reattempt ford 4")
       ev_battery_dict = check_battery() 

    if not ev_battery_dict:
       print("reattempt ford 5")
       ev_battery_dict = check_battery() 
    
    if not ev_battery_dict:
       print("setting to old battery values")
       ev_charge = old_ev_charge
       ev_miles_left = old_ev_miles_left
    else:
        ev_charge = int(ev_battery_dict['percentage'])
        ev_miles_left = int(ev_battery_dict['miles_left'])


def get_amount_of_clean_periods():
    global EV_CHARGING_RATE
    global EV_CAPACITY
    global ev_charge
    global EV_PERCENT_DESIRED
    global time_interval
    if EV_PERCENT_DESIRED - ev_charge <= 0:
        result = 0
    else:
        #result = (((EV_PERCENT_DESIRED - ev_charge)/100 * EV_CAPACITY) / EV_CHARGING_RATE) * 60 / time_interval
        charge_needed_percentage = EV_PERCENT_DESIRED - ev_charge
        charge_needed_kWh = (charge_needed_percentage / 100) * EV_CAPACITY
        charging_time_hours = charge_needed_kWh / EV_CHARGING_RATE
        result = (charging_time_hours * 60) / time_interval
    return math.ceil(result)

def get_amount_of_dirty_periods():
    global dirtytime_threshold
    return dirtytime_threshold * 12 

def get_ev_miles_travelled():
    global ev_miles_travelled
    ev_miles_travelled += get_miles_added()
    return ev_miles_travelled

def get_wifi_status():
    global wifi_status
    wifi_status = check_wifi_status_ifconfig()

############### control commands ###############
def send_cooler_decision(setpoint):
    return change_setpoint(setpoint)

def send_temp_to_automation():
    global cooler_indoor_temp
    return cooler_indoor_temp

def send_charging_decision(OnOFF:bool):
    if OnOFF:
        charger_on()
    else:
        charger_off()

def generate_new_clean_periods():
    get_charge()
    num_clean_periods = get_amount_of_clean_periods()
    print(num_clean_periods)
    generate_clean_periods(num_clean_periods)
    save_clean_periods()
    save_nonEMS_charging_periods()
    load_clean_periods()
    load_nonEMS_charging_periods()

def star_adjust_temp_setpoint_coolth():
    global CURRENT_SETPOINT
    global SETPOINT_COOLTH
    global MAX_COOLTH_TIME_LIMIT
    global cooler_indoor_temp
    global realtime
    global coolth_timer

    with open('output_1202.txt', 'a') as file:
        # adjust temperature setpoint  
        if CURRENT_SETPOINT != SETPOINT_COOLTH:
            send_cooler_decision(SETPOINT_COOLTH)
            file.write(f"Decision:\n")
            file.write(f"{realtime}: send_cooler_decision({SETPOINT_COOLTH}, CURRENT_SETPOINT != SETPOINT_COOLTH\n")
            functional_test_save()
            CURRENT_SETPOINT = SETPOINT_COOLTH
        else:  # avoid coolth damage 
            if cooler_indoor_temp <= SETPOINT_COOLTH + 2:
                # start time 
                if coolth_timer == 0:
                    coolth_timer = time.time()
                    file.write(f"EVENT:\n")
                    print("Coolth timer started!")
                    file.write(f"{realtime}: starting coolth timer \n")
                    functional_test_save()

                elif (time.time() - coolth_timer) >= MAX_COOLTH_TIME_LIMIT:
                    send_cooler_decision(SETPOINT_DEFAULT)
                    file.write(f"DECISION/EVENT:\n")
                    file.write(f"{realtime}: send_cooler_decision({SETPOINT_DEFAULT}, max coolth time limit hit!\n")
                    functional_test_save()
                    CURRENT_SETPOINT = SETPOINT_DEFAULT
                    coolth_timer = 0

            else:############### DELETE THIS BLOCK WHEN FOR FINAL CODE ONLY FOR DEBUGGING ###################
                file.write(f"Decision:\n")
                file.write(f"{realtime}: else coolth timer not >= MAX COOLTH TIME LIMIT, do nothing!\n")
                functional_test_save()


############### updater ###############
def update_inverter_data():
    global power_map
    global pv_output
    global grid_power
    bring_in_inverter_data()
    pv_output = int(power_map["Solar W"][:-1])
    grid_power = int(power_map["Grid W"][:-1])


############### decision rules ###############
def ems():
    global pv_output 
    global total_power
    global ev_charging
    global cooler_indoor_temp
    global realtime 
    global ev_connected 
    global ev_p5  
    global realtime
    global driving
    global cooler_indoor_temp
    global coolth_timer
    global econ_timer
    global EV_CHARGING_RATE
    global EV_CAPACITY
    global SETPOINT_DEFAULT
    global SETPOINT_COOLTH
    global SETPOINT_ECON
    global CURRENT_SETPOINT
    global TMAX
    global TMIN
    global rules_timer
    global charging_timer
   
    with open('output_1202.txt', 'a') as file:

        ############### Charging in clean periods section ###################

        realtime = datetime.now()
    
        ########## for nonEMS EV carbon accounting only ##########
        # if is_realtime_in_clean_periods(realtime, ev_nonEMS_co2_list):
        #     moer = get_wt("ruleBased", "moer")
        #     ev_nonEMS_co2_list.append(max(0,moer * ev_grid_load))
        #     ev_nonEMS_co2 = sum(ev_nonEMS_co2_list)
        #########################################################

        if is_realtime_in_clean_periods(realtime, ev_clean_periods):
            print(f"Current time {realtime.strftime('%H:%M')} is within a clean period.")
            if ev_connected:
                if ev_charging == False: 
                    send_charging_decision(True)
                    file.write(f"Decision:\n")
                    file.write(f"{realtime}: send_charging_decision(True)\n")
                    functional_test_save()
                else:
                    file.write(f"Decision:\n")
                    file.write(f"{realtime}: send_charging_decision(True), already charging, do nothing\n")
                    functional_test_save()

        else:
            print(f"Current time {realtime.strftime('%H:%M')} is NOT within a clean period.")
            if ev_connected:
                if driving == True:
                    # returned from a drive
                    # regen clean periods
                    driving = False
                    generate_new_clean_periods()
                    file.write(f"EVENT/Decision:\n")
                    file.write(f"{realtime}: back from drive, generate new clean charging schedule\n")
                    functional_test_save()
                if ev_charging:
                    send_charging_decision(False)
                    file.write(f"Decision:\n")
                    file.write(f"{realtime}: send_charging_decision(False) - not in clean period turning charging off)\n")
                    functional_test_save()
                else: 
                    file.write(f"Decision:\n")
                    file.write(f"{realtime}:not in clean period, not charging, do nothing\n")
                    functional_test_save()
            else:
                driving = True
                file.write(f"EVENT:\n")
                file.write(f"{realtime}: going on a drive)\n")
                functional_test_save()
        
        charging_timer = datetime.now()

    

        ############### Rules Section ######################
        if grid_power == 0 and (pv_output > total_power): # daytime 

            if cooler_indoor_temp < TMIN:
                if CURRENT_SETPOINT != SETPOINT_ECON:
                    send_cooler_decision(SETPOINT_ECON)
                    CURRENT_SETPOINT = SETPOINT_ECON
                    file.write(f"Decision:\n")
                    file.write(f"{realtime}: setting cooler decision to ECON - too cold inside the cooler!\n")
                    functional_test_save()
            else:
                star_adjust_temp_setpoint_coolth()
        
            if ev_charging == False:
                if ev_connected and ((pv_output*.0833) > ((total_power*.0833) + ev_p5)) and ev_charge != 100: # multiplying by 0.0833 to get energy for next 5 min
                    send_charging_decision(True)
                    file.write(f"Decision:\n")
                    file.write(f"{realtime}: send_charging_decision(True), excess PV including amount it takes to charge for 5 min\n")
                    functional_test_save()

        else: # daytime && night --- no excess PV
            if cooler_indoor_temp < TMIN:
                if CURRENT_SETPOINT != SETPOINT_ECON:
                    send_cooler_decision(SETPOINT_ECON)
                    CURRENT_SETPOINT = SETPOINT_ECON
                    file.write(f"Decision:\n")
                    file.write(f"{realtime}: setting cooler decision to ECON - too cold inside the cooler!\n")
                    functional_test_save()

            elif realtime not in cooler_dirty_periods and CURRENT_SETPOINT != SETPOINT_DEFAULT:
                # TODO do some coolth? 
                send_cooler_decision(SETPOINT_DEFAULT)
                file.write(f"Decision:\n")
                file.write(f"{realtime}: send_cooler_decision({SETPOINT_DEFAULT}, not in a cooler dirty period\n")
                functional_test_save()

                CURRENT_SETPOINT = SETPOINT_DEFAULT
            else:
                if CURRENT_SETPOINT != SETPOINT_ECON:
                    send_cooler_decision(SETPOINT_ECON)
                    file.write(f"Decision:\n")
                    file.write(f"{realtime}: send_cooler_decision({SETPOINT_ECON}, in a cooler dirty period\n")
                    functional_test_save()
                    CURRENT_SETPOINT = SETPOINT_ECON
                else: # avoid econ damage
                    if cooler_indoor_temp >= SETPOINT_ECON - 2:
                        # start time counting 
                        if econ_timer == 0:
                            econ_timer = time.time()
                            file.write(f"EVENT:\n")
                            print("Coolth timer started!")
                            file.write(f"{realtime}: starting econ timer \n")
                            functional_test_save()

                        elif (time.time() - econ_timer) >= MAX_ECON_TIME_LIMIT:
                            send_cooler_decision(SETPOINT_DEFAULT)
                            file.write(f"Decision/EVENT:\n")
                            file.write(f"{realtime}: stopping econ timer reached limit \n")
                            file.write(f"{realtime}: send_cooler_decision({SETPOINT_DEFAULT}\n")
                            functional_test_save()
                            CURRENT_SETPOINT = SETPOINT_DEFAULT
                            econ_timer = 0

                        else:############### DELETE THIS BLOCK WHEN FOR FINAL CODE ONLY FOR DEBUGGING ###################
                            file.write(f"{realtime}: econ_timer < max econ time limit, do nothing!\n")
                            functional_test_save()


                    else:############### DELETE THIS BLOCK WHEN FOR FINAL CODE ONLY FOR DEBUGGING ###################
                        file.write(f"{realtime}: else cooler_indoor temp not >= setpoint econ -2, do nothing!\n")
                        functional_test_save()


        # # ############## calculation ################
        # aoer = get_wt("ruleBased", "aoer")
        # moer = get_wt("ruleBased", "moer")
        # grid_co2_list.append(max(0,aoer * grid_power))
        # grid_co2 = sum(grid_co2_list)

        # # ############## EV reduction ###############
        # ev_total_load_fraction = ev_p5 / total_power ## total_power: PV used + grid power  (maybe 'Consume' in power map)
        # ev_grid_load = ev_total_load_fraction * grid_power 
        # ev_grid_co2_list.append(max(0,aoer * ev_grid_load))
        # ev_grid_co2 = sum(ev_grid_co2_list)

        # # ############## PV reduction ###############
        # solar_saving_list.append(max(0, aoer * solar_power_used))
        # solar_saving = sum(solar_saving_list)

        # # ############## rule-based EMS carbon accounting ##########
        # ev_ems_co2_list.append(max(0,moer * ev_grid_load))
        # ev_ems_co2 = sum(ev_ems_co2_list)

        # cooler_grid_load = (cooler_load / total_power) * grid_power
        # cooler_ems_co2_list.append(max(0, moer * cooler_grid_load))    
        # cooler_ems_co2 = sum(cooler_ems_co2_list)

        # connection = webAPI.model.get_db()
        # cur = connection.execute(
        #     "INSERT INTO data(totalCarbonEmission, solarCarbonEmission, evCarbonEmission, emsCarbonEmission, netInvertertoGrid, netSolartoInverter, netInvertertoComps) "
        #     "VALUES (?,?,?,?,?,?,?) ",
        #     (total_emission_reduction, solar_saving, ev_emission_reduction, ems_emission_reduction, grid_power, solar_power_used, total_power)
        # )
        # connection.commit()

        # cur2 = connection.execute(
        #     "INSERT INTO chart(baselineEmission, noEMSEmission, withEMSEmission) "
        #     "VALUES (?,?,?) ",
        #     (baseline_con_emissions, total_baseline_emissions, total_baseline_emissions  - total_emission_reduction)
        # )
        # connection.commit()

        rules_timer = datetime.now()


############### main ###############
def main():
    global ev_charge, pv_output, grid_power, ev_charging, cooler_indoor_temp, wifi_status, last_24_hour_run
    get_cooler_temp()
    generate_new_clean_periods()
    last_24_hour_run = datetime.now()
    ui_main()

    
    while True:
        try:
            # print(f"Current ev_charge: {ev_charge}")
            # print(f"Realtime: {datetime.now()}")
            get_wifi_status()
            
            if wifi_status:
                ########### this block: generate dirty periods sheet once per day
                if datetime.now() - last_24_hour_run >= timedelta(hours=24):
                    generate_dirty_periods(get_amount_of_clean_periods)
                    save_dirty_periods()
                    load_dirty_periods()
                    last_24_hour_run = datetime.now()  # Update the last run time
                ############
                update_realtime()
                get_is_ev_conn_and_charging()
                update_inverter_data()
                get_cooler_temp()
                ems()
                print(f"EV Charge: {ev_charge}%")
                print(f"PV Output: {pv_output}W")
                print(f"Grid Power: {grid_power}W")
                print(f"Wifi Connected: {wifi_status}")
                print(f"EV Charging Status: {ev_charging}")
                print(f"Cooler Indoor Temp: {cooler_indoor_temp}F")
                print(f"Current Setpoint: {CURRENT_SETPOINT}")
                time.sleep(300)
        except KeyboardInterrupt:
            print("Program interrupted and stopped.")
    

if __name__ == "__main__":
    main()
