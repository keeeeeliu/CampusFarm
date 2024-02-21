##this is the file for the simulator
from dataclasses import dataclass
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math

@dataclass

# Sam put instructions to activate venv in readme (. CF/bin/activate) or better link to how to create venv
# Sam is there a reason for three python versions in the venv?
# Sam might be better to put just the requirements in the github repo for the virtual env using pip freeze,
# Sam and then not have to save the whole venv. paths get hardcoded, so I'm not able to call the python envs
# Sam you have in here. See the pyvenv.cfg that it's adding Nelson's path, which I can see when I locally echo $PATH
# Sam https://stackoverflow.com/questions/6590688/is-it-bad-to-have-my-virtualenv-directory-inside-my-git-repository

# Sam might want to make a consistent interface for each of these classes (update(), simulate(), etc)

class PV:
    def __init__(self, inv_eff, T_daylight, max_power, data):
        self.inv_eff = inv_eff
        self.T_daylight = T_daylight
        self.P_out = 0.0 #cumulative power
        self.P = 0.0 #instant power 
        self.max_power = max_power
        self.data = data
    
    def update(self, t):
        minute = np.floor((t / 5)).astype(int)
        #sin function simulation
        #self.P = (self.inv_eff)*(self.max_power/2)* (np.sin(np.pi * t/(self.T_daylight))+1)
        #real-world data simulation
        self.P = self.data.at[minute, 'SolArk PV Power (DNI) kW']
        return self.P
        
    def get_current_power_output(self):
        return self.P
    
    def min_to_real_time(self,t):
        hours, mins = divmod(t, 60)
        return f"{hours:02d}:{mins:02d}"

    # Sam could add debug flags as part of the common interface for each element to set the output levels
    def simulate(self): # Sam should be called simulator? -Yes
        #convert to time step of minutes
        t = np.floor(self.T_daylight * 60).astype(int)
        for i in range(t):
            self.update(i)
            print(f"Time: {self.min_to_real_time(i)}, PV Power: {round(self.get_current_power_output(),3)} kW")

    """"example use:
    PV1 = PV(inv_eff=0.96, T_daylight=11.5, max_power=13.2, data=dataframe)
    PV1.simulator()
    """""
        
class EV:
    batt_charge: float
    batt_capacity: float
    connected: bool 
    ev_range: int



class Cooler:
    def __init__(self, min_temp, max_temp, Ta, Tk):
        self.is_on = False # m
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.p_consume = 3 # power consumed by the thermal cooling load kw/m
        self.Ta = Ta # Ambient temp
        self.Tk = Tk # current internal temp
        self.h = 0.01 # time
        self.COP = 4.5 #coefficient of performance
        self.Ri = 2 # thermal resistance of the thermal cooling load
        self.Ci = 0.05 # capacitance of the thermal cooling loadf
    
    def temp_cal(self):
        exponent = -self.h / (self.Ci * self.Ri)
        alpha = math.exp(exponent)
        # print(f"exponent: {exponent}")
        # print(f"alpha: {alpha}")
        Tg = self.Ri * self.p_consume * self.COP
        # print(f"alpha*self.Tk: {alpha*self.Tk}, (1 - alpha)*(self.Ta - self.is_on*Tg): {(1 - alpha)*(self.Ta - self.is_on*Tg)}")
        self.Tk = alpha*self.Tk + (1 - alpha)*(self.Ta - self.is_on*Tg)
        

    def set_temp(self):  
        if self.max_temp < self.Tk:
            self.is_on = True
        elif self.min_temp > self.Tk:
            self.is_on = False
        elif self.min_temp < self.Tk < self.max_temp:
            self.is_on = self.is_on

    def print_time(self, minute):
        hour = minute // 60
        minute_of_hour = minute % 60
        print(f"Current time (24-hour format): {hour:02d}:{minute_of_hour:02d}")
    # def simulate(self):
    #     steps = 10 # 1 step indicates one minute
    #     time = 1
    #     for t in range(steps):
    #         self.set_temp()
    #         self.temp_cal()
    #         ++time
    #         print(f"Time: {time}, Mini Split ON: {self.is_on}, Internal Temperature: {self.Tk}")

# solar_array = PV()
transit = EV()
main_cooler = Cooler(min_temp = 45, max_temp = 50, Ta = 70, Tk = 48)
basement_cooler = Cooler(min_temp = 34, max_temp = 38, Ta = 70, Tk = 48)


# EV + EV CHARGER

# Sam will probably want to functionize some of this main stuff

# initialize variables 
transit.batt_charge = 72 # %
transit.batt_capacity = 68 # kWh
transit.ev_range = 126 # mi 
transit.connected = True
charge_eff = .95
discharge_eff = .95
charger_output_power_max = 11.5 # kW

# for loop to simulate 1 day
print("Starting the EV Simulation for one day\n")
def str_to_bool(input_str):
    return input_str.lower() in ("yes", "true", "t", "1")

def military_time_to_minutes(military_time):
    # Check if the military time is a valid integer
    if not isinstance(military_time, int) or military_time < 0 or military_time > 2359:
        raise ValueError("Time must be an integer between 0 and 2359.\n")
    
    # Extract hours and minutes
    hours = military_time // 100  # Get first one or two digits as hours
    minutes = military_time % 100  # Get last two digits as minutes
    
    # Validate that the minutes are less than 60
    if minutes >= 60:
        raise ValueError("Invalid time provided. Minutes should be less than 60.\n")
    
    # Calculate the total number of minutes
    total_minutes = hours * 60 + minutes
    return total_minutes

user_input = input("Will there be a delivery Today? Please enter 'yes' or 'no': \n")
delivery_bool = str_to_bool(user_input)
drive_time = 0
drive_length = 0
drive_distance = 0
if(delivery_bool):
    drive_time = int(input("When is the delivery scheduled? Please enter a time in military time with no colon. Example: 1330 for 1:30 PM: \n"))
    drive_length = int(input("How long will the drive be in minutes? Please enter a whole number. \n"))
    drive_distance = float(input("How many miles will the drive be? Please enter a whole or decimal number. \n"))
    print(f"A drive is scheduled for: {drive_time}.\nThe drive will be {drive_distance} miles long and will take {drive_length} minutes.\n")

if(transit.connected):
    print("The Ford Transit is connected to the charger\n")
    print(f"The current state of charge is {transit.batt_charge}.\n")

charging = False
energy_consumed = 0
drive_start = military_time_to_minutes(drive_time)
drive_end = drive_start + drive_length
charging_ctr = 0

# for loop to model 24 hrs
for i in range(0, 1440):
    # battery is below 75%
    if(transit.batt_charge <= 75 and transit.connected):
        if(charging == False):
            print(f"Transit Battery Percentage: {transit.batt_charge}\n")
            print("Battery below 75%, starting charge ...\n")
            charging = True
        
        # batt charge eq 
        p_in = (charger_output_power_max*(1/60)*charge_eff)
        transit.batt_charge = transit.batt_charge + (p_in/transit.batt_capacity)

        ++charging_ctr # counting how many minutes spent charging 
        
    # battery is above  75%
    elif(transit.batt_charge > 75 and transit.connected):
        if(charging):
            print(f"Transit Battery Percentage: {transit.batt_charge}\n")
            print("Battery above 75%, stopping charge ...\n")

            # energy consumed eq                                                             
            energy_consumed = charger_output_power_max*(charging_ctr/60)*(1/charge_eff) 
            print(f"Total energy consumed from EV: {energy_consumed} kWh\n")

            charging = False
            charging_ctr = 0

        #idle discharge eq (losses 2% every month)
        transit.batt_charge = transit.batt_charge - (1/20160)   
        
    
    elif(delivery_bool and transit.connected and i == drive_start):
        print("Disconnecting from charger. Starting drive ...\n")
        
        # enter driving eq
        drained_percentage = (drive_distance/transit.ev_range)*100 #fix
        drained_energy = (drive_distance/transit.ev_range)*transit.batt_capacity

        print("Produce delivered! The drive has ended. Reconnecting to charger ...\n")

        # greenhouse gas equation
        ghg_saved = 10 # will need to be updated 

        print(f"Greenhouse Gases Saved During Drive: {ghg_saved}\n")
        print(f"Energy drained from battery: {drained_energy}\n")

        # battery % update
        transit.batt_capacity = transit.batt_capacity - drained_percentage
        print("Reconnecting to charger ...\n")
        i = drive_end # fast forwards to the time of when the drive ends
    
print("The Day has ended")
print(f"The final state of charge is {transit.batt_charge}.\n")
print("Happy Farming!")

# PV ARRAY simulation
df = pd.read_csv('./PVdata.csv',usecols=['Minute','SolArk PV Power (DNI) kW'])
PV1 = PV(inv_eff=0.96, T_daylight=24, max_power=13.2, data=df)
PV1.simulate() # Sam change function name here too

# MAIN COOLER

#change these variables based on simulation !
test_time = int(input("How long do you want to test for this time? Please enter a time in hours. \n"))
steps_c = test_time * 60 # test 2 hours for simulation
times_cooler = 1
print("\n")
print("Cooler information: ")
for i in range (steps_c):
    main_cooler.set_temp()
    main_cooler.temp_cal()
    main_cooler.print_time(i)
    print(f"Mini Split ON: {main_cooler.is_on}, Internal Temperature: {main_cooler.Tk}")
    times_cooler = times_cooler + 1

# BASEMENT
steps_b = test_time * 60 # test 2 hours for simulation
times_base = 1
print("\n")
print("Basement information: ")
for i in range (steps_b):
    basement_cooler.set_temp()
    basement_cooler.temp_cal()
    basement_cooler.print_time(i)
    print(f"Mini Split ON: {basement_cooler.is_on}, Internal Temperature: {basement_cooler.Tk}")
    times_base = times_base + 1






