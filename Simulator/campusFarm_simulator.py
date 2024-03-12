##this is the file for the simulator
from dataclasses import dataclass
from enum import Enum, auto
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
    charge_eff = int
    discharge_eff = int
    charger_output_pwr_max = int
    state: Enum
    next_state: Enum
    tot_energy_consumed: float
    charge_pwr_consumed: float
    ev_deliveries = [] # list to hold all the deliveries (tuple with the start (index0), end time (index1), drive_length(index2), drive_distance(index3))
    charging_ctr: int
    drive_drained_percentage: float
    drive_drained_energy: float

    

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
    
    def initialize_ev(self, batt_charge, batt_capacity, ev_range, connected, charge_eff, discharge_eff, charger_output_pwr_max):
       
        self.user_input = input("Will there be a delivery Today? Please enter 'yes' or 'no': \n")
        self.delivery_bool = self.str_to_bool(self.user_input)
        self.tot_energy_consumed = 0
        self.charging_ctr = 0
        self.drive_drained_percentage = 0
        self.drive_drained_energy = 0
        self.charging_ctr = 0

        # initialize variables 
        self.batt_charge = batt_charge # %
        self.batt_capacity = batt_capacity # kWh
        self.ev_range = ev_range # mi 
        self.connected = connected
        self.charge_eff = charge_eff
        self.discharge_eff = discharge_eff
        self.charger_output_pwr_max = charger_output_pwr_max # kW
        self.state = EVState.NOT_CHARGED
        self.next_state = EVState.NOT_CHARGED
        
        # will need to put this into a for loop in the future for multiple deliveries
        if(self.delivery_bool):
            drive_time = int(input("When is the delivery scheduled? Please enter a time in military time with no colon. Example: 1330 for 1:30 PM: \n"))
            drive_length = int(input("How long will the drive be in minutes? Please enter a whole number. \n"))
            drive_distance = float(input("How many miles will the drive be? Please enter a whole or decimal number. \n"))
            drive_start = self.military_time_to_minutes(drive_time)
            delivery_tuple = (drive_start, drive_start + drive_length, drive_length, drive_distance)
            self.ev_deliveries.append(delivery_tuple)
            print(f"A drive is scheduled for: {self.drive_time}.\nThe drive will be {self.drive_distance} miles long and will take {self.drive_length} minutes.\n")


        if(self.connected):
            print("The Ford Transit is connected to the charger\n")
            print(f"The current state of charge is {self.batt_charge}.\n")
    
    def update(self):
        # state changes
        if(self.state != self.next_state):
            print(f"EV Battery Percentage: {self.batt_charge}\n")
            if(self.state == EVState.CHARGED):
                print("Stopping EV charging ...")
                # energy consumed eq                                                             
                energy_consumed = self.charge_pwr_consumed*(self.charging_ctr/60)
                self.tot_energy_consumed += energy_consumed
                print(f"Total energy consumed from EV during charge: {energy_consumed} kWh\n")

                self.charge_pwr_consumed = 0
                self.charging_ctr = 0
                if(self.next_state == EVState.DRIVING):
                    print("Disconnecting from charger. Starting drive ...\n")
                    self.drive_drained_percentage = (self.drive_distance/self.ev_range)*100
                    self.drive_drained_energy = (self.drive_distance/self.ev_range)*self.batt_capacity
                    # battery % update
                    self.batt_capacity = self.batt_capacity - self.drive_drained_percentage
            
            elif(self.state == EVState.NOT_CHARGED):
                if(self.next_state == EVState.DRIVING):
                    print("Disconnecting from charger. Starting drive ...\n")
                    self.drive_drained_percentage = (self.drive_distance/self.ev_range)*100
                    self.drive_drained_energy = (self.drive_distance/self.ev_range)*self.batt_capacity
                    # battery % update
                    self.batt_capacity = self.batt_capacity - self.drive_drained_percentage
                elif(self.next_state == EVState.CHARGED):
                    print("Starting EV charging ...")
    
            elif(self.state == EVState.DRIVING):
                print("Produce delivered! The drive has ended. Reconnecting to charger ...\n")
                # greenhouse gas equation
                ghg_saved = 10 # will need to be updated 

                print(f"Greenhouse Gases Saved During Drive: {ghg_saved}\n")
                print(f"Energy drained from battery: {self.drive_drained_energy}\n")
                if(self.next_state == EVState.CHARGED):
                    print("Starting EV charging ...")
            
            self.state = self.next_state

        if(self.state == EVState.CHARGED):
            # batt charge eq 
            p_in = (self.charger_output_power_max*(1/60)*self.charge_eff)
            self.charge_pwr_consumed += p_in
            self.batt_charge = self.batt_charge + (p_in/self.batt_capacity)
            ++self.charging_ctr

            
        #should we change to CHARGING/IDLE? 
        elif(self.state == EVState.NOT_CHARGED):
            #idle discharge eq (losses 2% every month)
            self.batt_charge = self.batt_charge - (1/20160)  

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
main_cooler = Cooler(min_temp = 45, max_temp = 50, Ta = 70, Tk = 48)
basement_cooler = Cooler(min_temp = 34, max_temp = 38, Ta = 70, Tk = 48)
main_cooler = Cooler(min_temp = 45, max_temp = 50, Ta = 70, Tk = 48)
basement_cooler = Cooler(min_temp = 34, max_temp = 38, Ta = 70, Tk = 48)

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

class EVState(Enum):
    CHARGED = auto()
    NOT_CHARGED = auto()
    DRIVING = auto()


class PowerState(Enum):
    GRID_SUPPORT = auto()
    OFF_GRID = auto()

class tempState(Enum):
    COOLTH = auto()
    ECONOMIC = auto()

class CleanGrid(Enum):
    RELATIVE_CLEAN = auto()
    RELATIVE_DIRTY = auto()


# NELSON Q: These are the charging/not charging states? --> Answered
# Should we add states for GRID_SUPPORT, OFF_GRID, COOLTH, WARMING ?

if __name__ == "__main__":
    print("Starting Campus Farm EMS Simulation for 24 hrs ...")

if __name__ == "__main__":
    data = pd.read_csv('./PVdata.csv',usecols=['Minute','SolArk PV Power (DNI) kW'])
    #declare PV, EV, main_cooler, basement_cooler
    pv = PV(inv_eff=0.96, T_daylight=24, max_power=13.2, data=data) 
    ev = EV() #TODO 
    ev.initialize_ev(72,131,320,True,.9,.9,19.2)

    # main_cooler = Cooler(min_temp = 45, max_temp = 50, Ta = 70, Tk = 48)
    # basement_cooler = Cooler(min_temp = 34, max_temp = 38, Ta = 70, Tk = 48)
    main_cooler = Cooler(Ta=70, setpoint=48, power=3)
    base_cooler = Cooler(Ta=70, setpoint=45, power=3)
    clean_time = ([24, 200], [500,800]) # a list of relatively clean periods extracted from 72 hrs marginal emissions rate forecast
    for t in range(1440):
        pv.update(t) 
        ev.update(t) # should take ev state into account - Nelson to update params
        main_cooler.update(t) 
    ev_delivery_time = [drive_time,drive_time] #a list of delivery time in form of minutes
    for t in range(1440):
        pv.update(t) 
        ev.update(t) # should take ev state into account
        main_cooler.update(t)
        basement_cooler.update(t)

        #EMS_action
        if pv.P < main_cooler.power:
            # pv is not generating enough power
            # pv+grid to cooler
            #TODO
            # NELSON Q : is there only one set point is that why it is + 2? --> answered
            # pv is not genrating enough power
            # pv+grid to cooler
            #TODO
            if main_cooler.setpoint + 2 < main_cooler.max_temp:
                # a temp fluctuation will stay within ideal healthy zone
                # increase setpoint to reduce power consumption
                main_cooler.setpoint += 1

            # have you not added the ult_max < cur_max check?

            # check ev delivery schedule, when is the nearest delivery task
                # charge EV when necessary using grid power
            if ev.ev_delivery_time[0] - t < 120 and ev.ev_delivery_time[0] - t > 0:
            # check ev delivery schedule, when is the nearest delivery task
                # charge EV when necessary using grid power
            if ev_delivery_time[0] - t < 120 and ev_delivery_time[0] - t > 0:
                # delivery task soon
                if ev.batt_charge < 50:
                    # chraging is urgent
                    ev.next_state = EVState.CHARGED
                else:
                    # charging ev is not urgent
                    # wait for clean period - consecutive charging 
                    if t >= clean_time[0] and t <=clean_time[1]:
                        ev.next_state = EVState.CHARGED
            if ev.ev_delivery_time[0] - t < 0:
                # pop the past delivery task, so that the first element in the delivery task list is always the upcoming?
                ev.ev_delivery_time.pop(0)
            if ev_delivery_time[0] - t < 0:
                # pop the past delivery task, so that the first element in the delivery task list is always the upcoming?
                ev_delivery_time.pop(0)

        else:
        # pv is generating excessive power
        # charge ev using solar power if ev is not fully charged
            if ev.batt_charge < 100:
                ev.next_state = EVState.CHARGED
            else:
                # no need to charge ev, will coolth cooler with solar power
                if main_cooler.setpoint - 2 > main_cooler.min_temp:
                    # coolth will not be harmful
                    main_cooler.setpoint -= 1
    
    print("The Day has ended")
    print(f"The final state of charge is {ev.batt_charge}.\n")
    print("Happy Farming!")





