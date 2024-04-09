"""
Contains functions designed to show generallly how the accounting will work
structure of input parameters is made up and can be changed, but also can 
help form the interface with the simulator
"""
import math
import time

# constants
# CHARGER_OUTPUT_POWER = 20 # kW, made up value
CHARGER_LOSS_FACTOR = 0.8 # made up, probably needs to change based on ambient temp
PV_GENERATION = [12] * 1440

# types
energy = float # for clarity, could be changed to kWh or Wsec when we know what this type will be

# Class that holds all the necessary data on a minute-by-minute level
class EmsStat:
    def __init__(self, time : float, pv_production : energy, b_cool_load : energy, m_cool_load : energy,
                ev_charger_output : energy, grid_usage : energy):
        self.time = time
        self.b_cool_load = b_cool_load
        self.m_cool_load = m_cool_load
        self.ev_charger_output = ev_charger_output
        self.grid_usage = grid_usage
        self.total_load = self.b_cool_load + self.m_cool_load + (self.ev_charger_output * (1 / CHARGER_LOSS_FACTOR))

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
        return [self.time, self.b_cool_load, self.m_cool_load...]



# to be ran at ~3AM on the previous day's data
def calculate_co2_responsiblities(day_ems_stats_csv, previous_days_end_state):
    for minute in day_ems_stats_csv:
        # add in watttime data for the minute
        pass

    cooler_marginal_co2 = 0
    ev_marginal_co2 = 0
    

    for minute in day_ems_stats_csv:
        # go through and calculate stuff here

