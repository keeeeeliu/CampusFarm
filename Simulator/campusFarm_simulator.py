#this is the file for the simulator
from dataclasses import dataclass
import numpy as np

@dataclass

class PVArray:
    #I_max = float #max solar insolation in a day in kWh/m^2
    #later, model solar insolation change throughout year with sine wave
    T_daylight = float #total daylight hours
    #array_area = float #solar array area
    max_power = float # 13.2 kW max power under ideal conditions, factoring pv efficiency
    inv_eff = float #inverter efficiency
    #pv_eff = float #pv efficiency


class EV:
    batt_charge: float
    batt_capacity: float
    connected: bool 
    ev_range: int



class Cooler:
    def __init__(self, min_temp, max_temp, Tg, Ta, Tk):
        self.is_on = False # m
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.Tg = Tg # Temp gain
        self.Ta = Ta # Ambient temp
        self.Tk = Tk # current internal temp
        self.t = 0 # time
    
    def set_alpha(self,alpha):
        self.alpha = alpha
    
    def temp_cal(self):
        Tk = self.alpha*Tk + (1 - self.alpha)*(self.Ta - self.is_on*self.Tg)

    def set_temp(self):
        if self.Tk < self.min_temp:
            self.is_on = False
        elif self.Tk > self.max_temp:
            self.is_on = True
            
    
    def simulate(self,steps):
        for t in range(steps):
            self.set_temp()
            self.temp_cal(self)
            print(f"Time: {self.k}, Mini Split ON: {self.is_on}, Internal Temperature: {self.Tk}")
    min_temp: float
    max_temp: float
    k: int
    alpha: float

solar_array = PVArray()
transit = EV()
main_cooler = Cooler(min_temp = 45, max_temp = 50, Tg = 1, Ta = 70, Tk = 40)
basement_cooler = Cooler(min_temp = 34, max_temp = 38, Tg = 1, Ta = 70, Tk = 40)


# EV + EV CHARGER

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

        # green house gas equation
        ghg_saved = 10 # will need to be updated 

        print(f"Green House Gases Saved During Drive: {ghg_saved}\n")
        print(f"Energy drained from battery: {drained_energy}\n")

        # battery % update
        transit.batt_capacity = transit.batt_capacity - drained_percentage
        print("Reconnecting to charger ...\n")
        i = drive_end # fast forwards to the time of when the drive ends
    
print("The Day has ended")
print(f"The final state of charge is {transit.batt_charge}.\n")
print("Happy Farming!")

# PV ARRAY

# initialize variables
    #solar_array.pv_eff = 0.2
solar_array.inv_eff = 0.96
    #solar_array.I_max = 3.34 #avg in March in kWh/m^2
solar_array.T_daylight = 11.5 #hours based on mid february
solar_array.max_power = 13.2 #in kW, based on Utopian calculations (Joules per second)
t = 0 # time in hours

#change these variables based on simulation !


# power change eq (PV)
# power_t = (max_power*sin(pi*t/T_daylight)+(13.2/2))*inv_eff
    #convert to time step of minutes, not hours
PVpower_t = ((solar_array.inv_eff)*(solar_array.max_power)*np.sin(3.14159*t/(solar_array.T_daylight))+(solar_array.max_power/2)) #instant power at time t
print("Solar Power",PVpower_t)
# power_cumulative = PVpower_t 






# MAIN COOLER

#change these variables based on simulation !
alpha = 0.9
main_cooler.Tk = alpha*main_cooler.Tk + (1 - alpha)*(main_cooler.Ta - main_cooler.is_on*main_cooler.Tg)
main_cooler.simulate()
print("Cooler Power", main_cooler.Tk)

# BASEMENT
basement_cooler.Tk = alpha*basement_cooler.Tk + (1 - alpha)*(basement_cooler.Ta - basement_cooler.is_on*basement_cooler.Tg)
print("Basement Power", basement_cooler.Tk)






