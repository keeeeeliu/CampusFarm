#this is the file for the simulator
from dataclasses import dataclass
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

@dataclass



class PV:
    
    #later, model solar insolation change throughout year with sine wave
    #T_daylight = float #total daylight hours
    #max_power = float # 13.2 kW max power under ideal conditions, factoring pv efficiency

    def __init__(self, inv_eff, T_daylight, max_power, data):
        self.inv_eff = inv_eff
        self.T_daylight = T_daylight
        self.P_out = 0.0 #cummulative power
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

        #set the time step to start the simulation
    def simultator(self):
        #convert to time step of minutes
        t = np.floor(self.T_daylight * 60).astype(int)
        for i in range(t):
            self.update(i)
            print(f"Time: {i}, Instant Power: {round(self.get_current_power_output(),3)} kW")

    """"example:
    PV1 = PV(inv_eff=0.96, T_daylight=11.5, max_power=13.2, data=dataframe)
    PV1.simulator(t=800)
    """""
        
class EV:
    batt_charge: float
    batt_eff: float
    batt_capacity: float


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

# solar_array = PV()
transit = EV()
main_cooler = Cooler(min_temp = 45, max_temp = 50, Tg = 1, Ta = 70, Tk = 40)
basement_cooler = Cooler(min_temp = 34, max_temp = 38, Tg = 1, Ta = 70, Tk = 40)


# EV + EV CHARGER

# initialize variables 
transit.batt_eff = .9
transit.batt_charge = 100
transit.batt_capacity = 68 #kWh


# change these variables based on simulation !
p_in = 0 # power in (kW)
p_charge_out = 0 # power out to CF (kW)
p_drive_out = .05 # power out to driving (kW)
t_charge = 0 # time charging (min)
t_discharge = 0 # time discharging (min)
t_drive = 0 # time driving (min)

# power change eq
power_change = p_in*t_charge - p_charge_out*t_discharge - p_drive_out*t_drive

transit.batt_charge = transit.batt_charge + ((power_change/transit.batt_capacity)*100)
print("Battery State:", transit.batt_charge)


# PV ARRAY

# initialize variables
    #solar_array.pv_eff = 0.2
# solar_array.inv_eff = 0.96
#     #solar_array.I_max = 3.34 #avg in March in kWh/m^2
# solar_array.T_daylight = 11.5 #hours based on mid february
# solar_array.max_power = 13.2 #in kW, based on Utopian calculations (Joules per second)
#t = 0 # time in hours

#change these variables based on simulation !


# power change eq (PV)
# power_t = (max_power*sin(pi*t/T_daylight)+(13.2/2))*inv_eff
    #convert to time step of minutes, not hours
#PVpower_t = ((solar_array.inv_eff)*(solar_array.max_power)*np.sin(3.14159*t/(solar_array.T_daylight))+(solar_array.max_power)) #instant power at time t
# print("Solar Power",PVpower_t)
# power_cumulative = PVpower_t 
df = pd.read_csv('./PVdata.csv',usecols=['Minute','SolArk PV Power (DNI) kW'])
print(df.head())

PV1 = PV(inv_eff=0.96, T_daylight=24, max_power=13.2, data=df)
PV1.simultator()





# MAIN COOLER

#change these variables based on simulation !
alpha = 0.9
main_cooler.Tk = alpha*main_cooler.Tk + (1 - alpha)*(main_cooler.Ta - main_cooler.is_on*main_cooler.Tg)
# main_cooler.simulate()
print("Cooler Power", main_cooler.Tk)

# BASEMENT
basement_cooler.Tk = alpha*basement_cooler.Tk + (1 - alpha)*(basement_cooler.Ta - basement_cooler.is_on*basement_cooler.Tg)
print("Basement Power", basement_cooler.Tk)






