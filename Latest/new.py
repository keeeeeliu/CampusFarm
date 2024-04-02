from dataclasses import dataclass
from enum import Enum, auto
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import watttime_example as wt

class EVState(Enum):
    CHARGED = auto()
    NOT_CHARGED = auto()
    DRIVING = auto()
    # INIT = auto()


class PowerState(Enum):
    GRID_SUPPORT = auto()
    OFF_GRID = auto()
    COMBO = auto()
    INIT = auto()

class tempState(Enum):
    COOLTH = auto()
    ECONOMIC = auto()
    NORMAL = auto()

class CleanGrid(Enum):
    RELATIVE_CLEAN = auto()
    RELATIVE_DIRTY = auto()

class SafeState(Enum):
    SAFE = auto()
    DANGER = auto()

def min_to_real_time(t):
        hours, mins = divmod(t, 60)
        return f"{hours:02d}:{mins:02d}"

class PV:
    def __init__(self, inv_eff, T_daylight, max_power, data):
        self.inv_eff = inv_eff
        self.T_daylight = T_daylight
        self.P_out = 0.0 #cumulative power
        self.P = 0.0 #instant power 
        self.max_power = max_power
        self.data = data
        self.state = auto()
        
    def update(self, t):
        minute = np.floor((t / 5)).astype(int)
        #sin function simulation
        #self.P = (self.inv_eff)*(self.max_power/2)* (np.sin(np.pi * t/(self.T_daylight))+1)
        #real-world data simulation
        self.P = self.data.at[minute, 'Power'] 
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
            print(f"Time: {self.min_to_real_time(i)}, PV Power: {round(self.get_current_power_output(),3)}")

    """"example use:
    PV1 = PV(inv_eff=0.96, T_daylight=11.5, max_power=13.2, data=dataframe)
    PV1.simulator()
    """""

class Cooler:
    def __init__(self, Ta, setpoint, power):
        self.is_on = False # m
        self.min_temp = setpoint - 2
        self.max_temp = setpoint + 2
        self.p_consume = power # power consumed by the thermal cooling load kw/m
        self.Ta = Ta # Ambient temp
        self.Tk = 48 # current internal temp
        self.h = 0.016 # time
        self.COP = 2 #coefficient of performance
        self.Ri = 10 # thermal resistance of the thermal cooling load
        self.Ci = 0.2 # capacitance of the thermal cooling loadf
        self.state = tempState.NORMAL
        self.safestate = SafeState.SAFE
    
    def temp_cal(self):
        exponent = -self.h / (self.Ci * self.Ri)
        alpha = np.exp(exponent)
        Tg = self.Ri * self.p_consume * self.COP
        self.Tk = alpha*self.Tk + (1 - alpha)*(self.Ta - self.is_on*Tg)
        

    def set_temp(self):  
        if self.max_temp < self.Tk:
            self.is_on = True
        elif self.min_temp > self.Tk:
            self.is_on = False
        elif self.min_temp < self.Tk < self.max_temp:
            self.is_on = self.is_on
    
    def update(self):
        self.set_temp()
        self.temp_cal()

    def instant_power(self):
        if self.is_on:
            return self.p_consume
        else:
            return 0

    def change_setpoint(self, setpoint):
        self.max_temp = setpoint + 2
        self.min_temp = setpoint - 2

    def print_time(self, minute):
        hour = minute // 60
        minute_of_hour = minute % 60
        print(f"Current time (24-hour format): {hour:02d}:{minute_of_hour:02d}")

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
    

    

    def str_to_bool(self, input_str):
       # input_str.lower() in ("yes", "true", "t", "1")
        # if (input_str.lower() == "yes"):
            
        #     return True
        # elif (input_str.lower() == "no"):
        #     return False
        # return True
        if (input_str == 1):
            return 1
        elif (input_str == 0):
            return 0
    
    def military_time_to_minutes(self, military_time):
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
       
        self.user_input = input("Will there be a delivery Today? Please enter '1' for 'yes' or '0' for 'no': \n")
        # self.delivery_bool = self.str_to_bool(self.user_input)
        # self.delivery_bool = True
        self.delivery_bool = int(self.user_input)
        self.tot_energy_consumed = 0
        self.charge_pwr_consumed = 0
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
        #self.drive_distance = 250

        #print(self.state)
        
        # will need to put this into a for loop in the future for multiple deliveries
        print(type(self.delivery_bool))
        if(self.delivery_bool == True):
            drive_time = int(input("When is the delivery scheduled? Please enter a time in military time with no colon. Example: 1330 for 1:30 PM: \n"))
            drive_length = int(input("How long will the drive be in minutes? Please enter a whole number. \n"))
            drive_distance = float(input("How many miles will the drive be? Please enter a whole or decimal number. \n"))
            drive_start = self.military_time_to_minutes(drive_time)
            delivery_tuple = (drive_start, drive_start + drive_length, drive_length, drive_distance)
            self.ev_deliveries.append(delivery_tuple)
            print(f"A drive is scheduled for: {min_to_real_time(drive_start)}.\nThe drive will be {drive_distance} miles long and will take {drive_length} minutes.\n")

        if(self.connected):
            print("The Ford Lightning is connected to the charger\n")
            print(f"The current state of charge is {self.batt_charge}.\n")
    
    def update(self,t):
        # state changes
        if(self.state != self.next_state):
            #print(f"EV Battery Percentage: {self.batt_charge}\n")
            if(self.state == EVState.CHARGED):
                print("Time:", min_to_real_time(t), "Stopping EV charging ... Current Battery Level is", self.batt_charge)

                # energy consumed eq                                                             
                self.pv_energy_consumed = self.charge_pwr_consumed
                self.tot_energy_consumed += self.charge_pwr_consumed
                print(f"Total energy consumed from EV during charge: {self.tot_energy_consumed} kWh\n")

                self.charge_pwr_consumed = 0
                self.pv_energy_consumed = 0
                
                self.charging_ctr = 0
                if(self.next_state == EVState.DRIVING):
                    print("Disconnecting from charger. Starting drive ... Current Battery Percentage:", self.batt_charge,"\n")
                    self.drive_drained_percentage = (self.ev_deliveries[0][3]/self.ev_range)*100 / self.ev_deliveries[0][2]
                    self.drive_drained_energy = (self.ev_deliveries[0][3]/self.ev_range)*self.batt_capacity
                    self.batt_charge -= self.drive_drained_percentage
                    
            
            elif(self.state == EVState.NOT_CHARGED):
                if(self.next_state == EVState.DRIVING):
                    print("Time:",min_to_real_time(t),"Disconnecting from charger. Starting drive ...\n")
                    self.drive_drained_percentage = (self.ev_deliveries[0][3]/self.ev_range)*100 / self.ev_deliveries[0][2]
                    self.drive_drained_energy = (self.ev_deliveries[0][3]/self.ev_range)*self.batt_capacity
                    # battery % update
              
                    self.batt_charge -= self.drive_drained_percentage
                elif(self.next_state == EVState.CHARGED):
                    print("Time:", min_to_real_time(t), "Starting EV charging ... Current Battery Percentage:", self.batt_charge)
    
            elif(self.state == EVState.DRIVING):
                print("Time", min_to_real_time(t)," Produce delivered! The drive has ended. Reconnecting to charger ... Current Battery Percentage:", self.batt_charge,"\n")
                # greenhouse gas equation
                ghg_saved = 10 # will need to be updated 

                print(f"Greenhouse Gases Saved During Drive: {ghg_saved}\n")
                print(f"Energy drained from battery: {self.drive_drained_energy}\n")
                if(self.next_state == EVState.CHARGED):
                    print("Starting EV charging ... Current Battery Percentage:", self.batt_charge)
            
            self.state = self.next_state
        else:

            # state does not change 
            if(self.state == EVState.CHARGED):
                # batt charge eq 
                # charging until battery is full
                if (self.batt_charge < 99):
                    p_in = (self.charger_output_pwr_max*(1/60)*self.charge_eff)
                    # print("@@@@@", p_in)
                    # print("!!!!",self.charging_ctr)
                    e_consumed = self.charger_output_pwr_max / 60
                    # self.charge_pwr_consumed += p_in
                    self.charge_pwr_consumed += e_consumed
                    self.batt_charge +=  (p_in/self.batt_capacity) * 100
                    self.charging_ctr += 1
                else:
                    self.next_state = EVState.NOT_CHARGED
                
            #should we change to CHARGING/IDLE? 
            elif(self.state == EVState.NOT_CHARGED):
                #idle discharge eq (losses 2% every month)
                self.batt_charge = self.batt_charge - (1/20160)
            elif(self.state == EVState.DRIVING):
                self.drive_drained_percentage = self.ev_deliveries[0][3]/self.ev_range/self.ev_deliveries[0][2] * 100
                self.batt_charge -= self.drive_drained_percentage


if __name__ == "__main__":
    # integrate watt time data
    # token = wt.get_login_token()
    # data = wt.get_moer(token)
    # in ems, only returns a list of clean periods

    # data = pd.read_csv('./PVdata.csv',usecols=['Minute','SolArk PV Power (DNI) kW'])
    data = pd.read_csv('./Consistent_Sunlight_October.csv',usecols=['Minute','Power'])
    #declare PV, EV, main_cooler, basement_cooler
    pv = PV(inv_eff=0.96, T_daylight=24, max_power=13.2, data=data) 
    ev = EV() #TODO 
    ev.initialize_ev(20,131,320,True,.9,.9,19.2)

    power_type = PowerState.INIT
    
    main_cooler = Cooler(Ta=70, setpoint=48, power=3.67)
    base_cooler = Cooler(Ta=70, setpoint=45, power=3)
    cooler_load_value = main_cooler.p_consume
    # we extract clean time from 16:00 - 24:00 and 0:00 - 7:00 everyday, because we use ev during the day
    clean_time = wt.get_clean_periods() # a list of relatively clean periods extracted from 72 hrs marginal emissions rate forecast
    #ev_delivery_time = [355,700] #a list of delivery time in form of minutes
    power_consumed_by_cooler = 0
    # ulti_min, ulti_max = 34, 38 # danger zone set by the user
    # ideal_setpoint = 36 # ideal setpoint set by the user
    ulti_min = float(input("What is the minimum danger zone tempertaure? Pleaser enter:\n"))
    ulti_max = float(input("What is the maximum danger zone tempertaure? Pleaser enter:\n"))
    ideal_setpoint = float(input("What is an ideal temperature setpoint? Please enter:\n"))
    safe_min = float(input("What is an ideal temperature min? Please enter:\n")) # this is safe zone boundary
    safe_max = float(input("What is an ideal temperature max? Please enter:\n")) # this is safe zone boundary
    cooler_fluctuation_range = 2.0 # +/- 2 degrees of set point 
    ideal_min = safe_min + cooler_fluctuation_range # this is the boundary for set point
    ideal_max = safe_max - cooler_fluctuation_range # this is the boundary for set point, if current setpoint = ideal max, the cooler temp will always below safe max, even with temp fluctuation
    current_setpoint = ideal_setpoint
    coolth_tolerance_time = 60 # 1 hour 
    eco_tolerance_time = 60 # 1 hour
    eco_time_counter = 0 # should not exceed 1 hour per day
    coolth_time_counter = 0
   

    # GRAPH 
    time_axis = []
    temp_axis = []
    batt_axis = []
    pv_axis = []
    cooler_load = []
    current_temp = []
    healthy_max = []
    healthy_min = []
    current_temp_max = []
    current_temp_min = []
    danger_max = []
    danger_min = []


    # accumulated 
    energy_consumed_by_cooler = 0.0
    energy_generated_by_pv = 0.0

    energy_from_grid = 0.0
    pv_energy_consumed_by_ev = 0.0
    tot_pv_energy_consumed = 0.0
    
    grid_by_cooler = 0.0
    grid_by_ev = 0.0
    pv_by_ev = 0.0
    pv_by_cooler = 0.0

    for t in range(1440):
        
        pv.update(t)
        ev.update(t)
        # print(ev.state, ev.next_state)
        main_cooler.update()
        base_cooler.update()
        temp_axis.append(current_setpoint)
        batt_axis.append(ev.batt_charge)
        pv_axis.append(pv.get_current_power_output())
        time_axis.append(t)
        cooler_load.append(main_cooler.instant_power())
        current_temp.append(main_cooler.Tk)
        healthy_max.append(safe_max)
        healthy_min.append(safe_min)
        current_temp_max.append(current_setpoint+2)
        current_temp_min.append(current_setpoint-2)
        danger_max.append(ulti_max)
        danger_min.append(ulti_min)
        
        energy_consumed_by_cooler += main_cooler.instant_power()/60 # check
        energy_generated_by_pv += pv.get_current_power_output()/60 # check

        if (main_cooler.Tk > safe_max):
            eco_time_counter += 1
        
        if (main_cooler.Tk < safe_min):
            coolth_time_counter += 1

  

        if (pv.state != power_type):
            
            if (power_type == PowerState.COMBO):
                print("The system is using both PV power and Grid power Cooler Power Load is ", main_cooler.instant_power())
            elif (power_type == PowerState.OFF_GRID):
                print("The systm is using PV power only! Cooler Power Load is ", main_cooler.instant_power())
            elif (power_type == PowerState.GRID_SUPPORT):
                print("The system is using Grid power only! Cooler Power Load is ", main_cooler.instant_power())
            pv.state = power_type
            print(f"Time: {pv.min_to_real_time(t)}, PV Power: {round(pv.get_current_power_output(),3)} kW")

        if pv.P <= main_cooler.p_consume:
            if (pv.P > 0):
                power_type = PowerState.COMBO
            else:
                power_type = PowerState.GRID_SUPPORT

            # pv is not generating enough power
            # need to increase the set point 
            if power_type == PowerState.COMBO:
                ###grid + pv#### should we do coolth?? No, we will stay in normal mode
                # we go coolth with purely pv power
                if (current_setpoint >= ideal_min):
                    current_setpoint = ideal_setpoint                        
                    main_cooler.change_setpoint(current_setpoint)

                # energy consumption calculation
                if (main_cooler.instant_power()>0): 

                    energy_from_grid += np.abs(main_cooler.instant_power() - pv.P) / 60 #grid consumption
                    tot_pv_energy_consumed += pv.P / 60 #pv consumption
                    grid_by_cooler += np.abs(main_cooler.p_consume - pv.P) / 60 #grid consumption by cooler
                    pv_by_cooler += pv.P /60
                ev.next_state = EVState.NOT_CHARGED

            elif power_type == PowerState.GRID_SUPPORT: 
                # purely grid  ECO
                # energy calculation by cooler
                energy_from_grid += (main_cooler.instant_power()) / 60
                grid_by_cooler += main_cooler.instant_power() / 60

                #ECO
                if (eco_time_counter < eco_tolerance_time):
                    # go danger
                    if (current_setpoint < safe_max):
                        current_setpoint = safe_max
                        main_cooler.change_setpoint(current_setpoint)

                elif (eco_time_counter >= eco_tolerance_time):
                    # stay within safe zone
                    if (current_setpoint <= ideal_max):
                        current_setpoint = ideal_max
                    elif (current_setpoint == safe_max):
                        current_setpoint = ideal_max
                    main_cooler.change_setpoint(current_setpoint)
           
                
                # normally, we don't charge ev using grid power
                ev.next_state = EVState.NOT_CHARGED
                # we charge ev using grid only during clean period
                # we will charge ev every day, including days without delivery
                if clean_time:
                    if t >= clean_time[0][0] and t <= clean_time[0][1] and (t <= 420 or t >= 1020): # 0:00 - 7:00,  16:00 - 23:59
                        # during clean periods charge ev to keep a descent charge
                        # if battery charge if above 70, we don't charge using grid
                        if (ev.batt_charge < 70):
                            ev.next_state = EVState.CHARGED
                            #by ev
                            energy_from_grid += (ev.charger_output_pwr_max*(1/60)*ev.charge_eff)
                            grid_by_ev +=(ev.charger_output_pwr_max*(1/60)*ev.charge_eff)
                        
                    else:
                        # outside of clean periods
                        ev.next_state = EVState.NOT_CHARGED




            
        elif pv.P > main_cooler.p_consume and pv.P > 0:
            power_type = PowerState.OFF_GRID

            tot_pv_energy_consumed += main_cooler.instant_power()/ 60

            pv_by_cooler += main_cooler.instant_power()/ 60
            # pv is generating excess power
            # COOLTH
            if (coolth_time_counter < coolth_tolerance_time):
                if (current_setpoint > safe_min):
                    current_setpoint = safe_min
                    main_cooler.change_setpoint(current_setpoint)
            elif (coolth_time_counter >= coolth_tolerance_time):
                if (current_setpoint >= ideal_min):
                    current_setpoint = ideal_min
                elif (current_setpoint == safe_min):
                    current_setpoint = ideal_min
                main_cooler.change_setpoint(current_setpoint)


            # excessive pv may not be enough for ev charging, so ev may use grid power
            # therefore, rule is: if pv.P - main_cooler.p_consume  > 0, then ev use pv power
            if ev.batt_charge < 95:
                    # if excessive power, always charge ev
                
                if (pv.P - main_cooler.instant_power() > 0): 
                    ev.next_state = EVState.CHARGED   

                    tot_pv_energy_consumed += ev.charger_output_pwr_max*(1/60)*ev.charge_eff
                    pv_energy_consumed_by_ev += (ev.charger_output_pwr_max*(1/60)*ev.charge_eff)
                else:
                    ev.next_state = EVState.NOT_CHARGED
            else:
                ev.next_state = EVState.NOT_CHARGED
                

        # ev delivery task 
        if (len(ev.ev_deliveries) > 0):
            
            if ev.ev_deliveries[0][0] <= t and ev.ev_deliveries[0][1] >= t:
                    # pop the past delivery task, so that the first element in the delivery task list is always the upcoming?
                    ev.connected = False
                    ev.next_state = EVState.DRIVING
   
        #update clean periods and delivery schedule
        if clean_time:
            if t > clean_time[0][1]:
                clean_time.pop(0)
        if ev.ev_deliveries:
            if t > ev.ev_deliveries[0][1]:
                ev.ev_deliveries.pop(0)
                ev.connected = True
                ev.next_state = EVState.NOT_CHARGED
        
    pv_by_ev = pv_energy_consumed_by_ev
    # tot_pv_energy_consumed = pv_by_ev + pv_by_cooler
    print("Total energy consumed by Cooler", energy_consumed_by_cooler)
    print("Total energy generated by PV:", energy_generated_by_pv)
    print("Total energy consumed by EV:", ev.tot_energy_consumed)
    print("Total energy consumed from grid:", energy_from_grid)
    print("Total solar energy consumed:", tot_pv_energy_consumed)

    print("Time spent in ECONOMIC mode:", eco_time_counter)
    print("Time spent in COOLTH mode:", coolth_time_counter)

    
    
    print(pv_by_cooler)
    print(pv_by_ev)
    print(grid_by_cooler)
    print(grid_by_ev)


    plt.subplot(5,1,1)
    plt.plot(time_axis, temp_axis)  
    plt.xlabel('Time/min')  
    plt.ylabel('Temp Setpoint') 
    plt.title('Temperature Setpoint')  

    plt.subplot(5,1,2)
    plt.plot(time_axis, batt_axis) 
    plt.xlabel('Time/min')  
    plt.ylabel('Battery Charge Percentage') 
    plt.title('Battery Charge Percentage')

    plt.subplot(5,1,3)
    plt.plot(time_axis, pv_axis)  
    plt.xlabel('Time/min') 
    plt.ylabel('PV output')
    plt.title('PV output')  

    plt.subplot(5,1,4)
    plt.plot(time_axis, cooler_load)  
    plt.yticks(np.arange(0,2.1,0.5))
    plt.xlabel('Time/min')  
    plt.ylabel('cooler load') 
    plt.title('cooler load') 
    # plt.show()

    plt.subplot(5,1,5)
    plt.plot(time_axis, current_temp)  
    plt.plot(time_axis, healthy_max)
    plt.plot(time_axis,healthy_min)
    plt.plot(time_axis,current_temp_max)
    plt.plot(time_axis,current_temp_min)
    plt.plot(time_axis,danger_max)
    plt.plot(time_axis,danger_min)
    min_hour = min(time_axis) // 60
    max_hour = max(time_axis) // 60
    hour_ticks =  list(range(min_hour, max_hour + 1))
    hour_ticks_in_min = [h*60 for h in hour_ticks]
    plt.fill_between(time_axis, current_temp_max, current_temp_min, color = 'gray',alpha=0.5)
    plt.xticks(hour_ticks_in_min, [f"{int(h)}" for h in hour_ticks])
    plt.yticks(np.arange(ulti_min,ulti_max + 0.1, 2))

    # plt.xlabel('Time/hour1')  
    plt.ylabel('current cooler temperature') 
    plt.title('current cooler temprature') 
    plt.show()
    print("The Day has ended")
    print(f"The final state of charge is {ev.batt_charge}.\n")
    print("Happy Farming!")





            
                

            

    

                   