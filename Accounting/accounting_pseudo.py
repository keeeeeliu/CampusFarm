"""
Contains functions designed to show generallly how the accounting will work
structure of input parameters is made up and can be changed, but also can 
help form the interface with the simulator
"""
import math
import time
import csv

# constants
# CHARGER_OUTPUT_POWER = 20 # kW, made up value
CHARGER_LOSS_FACTOR = 0.8 # made up, probably needs to change based on ambient temp
PV_GENERATION = [12] * 1440

# types
energy = float # for clarity, could be changed to kWh or Wsec when we know what this type will be

# Class that holds all the necessary data on a minute-by-minute level
class EmsStat:
    def __init__(self, time : float, pv_production : energy, b_cool_load : energy, m_cool_load : energy,
                ev_charger_output : energy, grid_usage : energy, isCharging : bool):
        self.time = time
        self.b_cool_load = b_cool_load
        self.m_cool_load = m_cool_load
        self.ev_charger_output = ev_charger_output
        self.grid_usage = grid_usage
        self.total_load = self.b_cool_load + self.m_cool_load + (self.ev_charger_output * (1 / CHARGER_LOSS_FACTOR))
        self.isCharging = isCharging

        self.has_watttime_data = False
        self.marginal_co2 = 0
        self.average_co2 = 0

        self.ev_load_frac = (self.ev_charger_output * (1 / CHARGER_LOSS_FACTOR)) / self.total_load
        self.ev_load_from_grid = self.ev_load_frac * self.grid_usage 
        
        self.both_cool_load_frac = (self.b_cool_load + self.m_cool_load) / self.total_load
        self.cool_load_from_grid = self.both_cool_load_frac * self.grid_usage

    # TODO add an overloaded init function that takes the values returned by get_data_for_csv()
    # and calculates everything else that is needed

    # return list to be put into csv rows for day's minute-by-minute data
    def get_data_for_csv(self):
        return [self.time, self.ev_load_from_grid, self.cool_load_from_grid, self.isCharging]


   # Writes a single row to a csv file every minute 
    def write_to_csv(self):
        f = open('path/to/csv_file', 'w')
        writer = csv.writer(f)
        writer.writerow(get_data_for_csv(self))
        


# to be ran at ~3AM on the previous day's data
# This will give us the marginal and average co2 emissions that come from the grid daily, as well as the amount of time 
# per day the EV is charging 
def calculate_co2_responsiblities(day_ems_stats_csv, previous_days_end_state):


    with open('EMS_Data.csv', mode = 'r') as oldfile:
    EmsReader = csv.reader(oldfile)

    with open('EMS_Wattime_Data.csv', mode = 'w') as newfile
        EmsWriter = csv.writer(newfile, delimiter="-")
    for row in EmsReader:
        # add in watttime data for the minute
        # TODO Access the wattime API and store both marginal and average CO2 data 
        # Get historical data for the day, and match time stamps to the time in the csv
        # Divide the wattime data by 60 million to turn pounds/MWh to pounds/(watt*minute)
        self.marginal_co2 = 0
        self.average_co2 = 0

        #copying the data from the original csv file without wattime data to a new one with the data
        EmsWriter.writerow(row + marginal_co2 + average_co2)
       
        pass

    cooler_marginal_co2 = 0
    cooler_average_co2 = 0
    ev_marginal_co2 = 0
    ev_average_co2 = 0
    chargeTime = 0
    
    with open('EMS_Wattime_Data.csv', mode = 'r') as currentFile
    reader = csv.reader(currentFile)
    
    for row in reader:
        E_Grid_EV = row[1]
        E_Grid_Cool = row[2]
        isCharging = row[3]
        Marginal_co2 = row[4]
        Average_co2 = row[5]
        cooler_marginal_co2 = cooler_marginal_co2 + E_Grid_Cool * Marginal_co2
        cooler_average_co2 = cooler_average_co2 + E_Grid_Cool * Average_co2
        ev_marginal_co2 = ev_marginal_co2 + E_Grid_EV * Marginal_co2
        ev_average_co2 = ev_average_co2 + E_Grid_EV * Average_co2
        if isCharging == true
            chargeTime ++

        # go through and calculate stuff here
        
        

