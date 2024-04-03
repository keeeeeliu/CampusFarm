# contains functions designed to show generallly how the accounting will work
# structure of input parameters is made up and can be changed, but also can 
# help form the interface with the simulator
import math

CHARGER_OUTPUT_POWER = 20 # kW, made up value
CHARGER_LOSS_FACTOR = 0.8 # made up, probably needs to change based on ambient temp
PV_GENERATION = [12] * 1440

class PowerStat:
    def __init__(self, time, b_cool_load, m_cool_load, ev_charging):
        self.time = time
        self.b_cool_load = b_cool_load
        self.m_cool_load = m_cool_load
        self.ev_charging = ev_charging
        self.total_load = self.b_cool_consum + self.m_cool_consum + (int(ev_charging) * CHARGER_OUTPUT_POWER * (1 + CHARGER_LOSS_FACTOR))
        self.ev_load_frac = CHARGER_OUTPUT_POWER * CHARGER_LOSS_FACTOR / self.total_load


def func(power_stats):
    for power in power_stats:


