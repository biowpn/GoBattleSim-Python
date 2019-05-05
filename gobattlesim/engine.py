
'''
A wrapper for native GoBattleSim engine (in C++).

It contains the following classes:

    Move
    Pokemon
    Party
    Player
    Strategy
    Battle
    
as well as some functions to set battle paremeters.

'''

from ctypes import *

import os
lib = CDLL(os.path.join(os.path.dirname(__file__), "GoBattleSim.dll"))





'''
Functions
'''

lib.GameMaster_set_num_types.argtypes = [c_int]
lib.GameMaster_set_num_types.restype = c_void_p
def set_num_types(num_types):
    '''
    Set the number of Pokemon Types.
    '''

    lib.GameMaster_set_num_types(num_types)


lib.GameMaster_set_effectiveness.argtypes = [c_int, c_int, c_double]
lib.GameMaster_set_effectiveness.restype = c_void_p
def set_effectiveness(type_i, type_j, multiplier):
    '''
    Set the effectiveness multiplier of type i attacking type j.
    '''

    lib.GameMaster_set_effectiveness(type_i, type_j, multiplier)


lib.GameMaster_set_type_boosted_weather.argtypes = [c_int, c_int]
lib.GameMaster_set_type_boosted_weather.restype = c_void_p
def set_type_boosted_weather(type_i, weather):
    '''
    Set the weather where type_i is boosted.
    '''

    lib.GameMaster_set_type_boosted_weather(type_i, weather)


lib.GameMaster_set_stage_multiplier.argtypes = [c_int, c_double]
lib.GameMaster_set_stage_multiplier.restype = c_void_p
def set_stage_multiplier(stage_i, multiplier):
    '''
    Set the stat multiplier for stage i.
    '''

    lib.GameMaster_set_stage_multiplier(stage_i, multiplier)


lib.GameMaster_set_parameter.argtypes = [c_char_p, c_double]
lib.GameMaster_set_parameter.restype = c_void_p
def set_parameter(name, value):
    '''
    Set a specific battle parameter.
    '''

    lib.GameMaster_set_parameter(name.encode('utf-8'), value)



'''
Classes
'''


class BattleOutcome(Structure):
    _fields_ = [("duration", c_int),
                ("win", c_bool),
                ("tdo", c_int),
                ("tdo_percent", c_double),
                ("num_deaths", c_int)]


atype_None = 0
atype_Wait = 1
atype_Fast = 2
atype_Charged = 3
atype_Dodge = 4

class Action(Structure):
    _fields_ = [("type", c_int),
                ("delay", c_int),
                ("value", c_int),
                ("time", c_int)]



class StrategyInput(Structure):
    _fields_ = [("time", c_int),
                ("subject", c_void_p),
                ("enemy", c_void_p),
                ("subject_action", Action),
                ("enemy_action", Action),
                ("random_number", c_int),
                ("battle_p", c_void_p),
                ("calc_damage", CFUNCTYPE(c_int, c_void_p, c_void_p, c_void_p, c_void_p))]


EventResponder = CFUNCTYPE(c_void_p, StrategyInput, POINTER(Action))



class Move:

    lib.Move_new.argtypes = [c_int, c_int, c_int, c_int, c_int]
    lib.Move_new.restype = c_void_p
    def __init__(self, poketype, power, energy, duration, dws):
        self.obj = lib.Move_new(poketype, power, energy, duration, dws)


    lib.Move_delete.argtypes = [c_void_p]
    lib.Move_delete.restype = c_void_p
    def __del__(self):
        lib.Move_delete(self.obj)




class Pokemon:

    lib.Pokemon_new.argtypes = [c_int, c_int, c_double, c_double, c_int]
    lib.Pokemon_new.restype = c_void_p
    def __init__(self, poketype1, poketype2, attack, defense, maxHP):
        self.obj = lib.Pokemon_new(poketype1, poketype2, attack, defense, maxHP)


    lib.Pokemon_delete.argtypes = [c_void_p]
    lib.Pokemon_delete.restype = c_void_p
    def __del__(self):
        lib.Pokemon_delete(self.obj)
    

    lib.Pokemon_add_fmove.argtypes = [c_void_p, c_void_p]
    lib.Pokemon_add_fmove.restype = c_void_p
    def add_fmove(self, move):
        lib.Pokemon_add_fmove(self.obj, move.obj)
        

    lib.Pokemon_add_cmove.argtypes = [c_void_p, c_void_p]
    lib.Pokemon_add_cmove.restype = c_void_p
    def add_cmove(self, move):
        lib.Pokemon_add_cmove(self.obj, move.obj)


    lib.Pokemon_set_immortal.argtypes = [c_void_p, c_bool]
    lib.Pokemon_set_immortal.restype = c_void_p
    def set_immortal(self, immortal):
        lib.Pokemon_set_immortal(self.obj, immortal)

        
    lib.Pokemon_set_strategy_flags.argtypes = [c_void_p, c_uint]
    lib.Pokemon_set_strategy_flags.restype = c_void_p
    def set_strategy_flags(self, flags):
        lib.Pokemon_set_strategy_flags(self.obj, flags)




class Party:

    lib.Party_new.argtypes = []
    lib.Party_new.restype = c_void_p
    def __init__(self):
        self.obj = lib.Party_new()


    lib.Party_delete.argtypes = [c_void_p]
    lib.Party_delete.restype = c_void_p
    def __del__(self):
        lib.Party_delete(self.obj)


    lib.Party_add_pokemon.argtypes = [c_void_p, c_void_p]
    lib.Party_add_pokemon.restype = c_void_p
    def add_pokemon(self, pokemon):
        lib.Party_add_pokemon(self.obj, pokemon.obj)


    lib.Party_set_revive_policy.argtypes = [c_void_p, c_int]
    lib.Party_set_revive_policy.restype = c_void_p
    def set_revive_policy(self, revive_policy):
        lib.Party_set_revive_policy(self.obj, revive_policy)



class Player:

    lib.Player_new.argtypes = []
    lib.Player_new.restype = c_void_p
    def __init__(self):
        self.obj = lib.Player_new()


    lib.Player_delete.argtypes = [c_void_p]
    lib.Player_delete.restype = c_void_p
    def __del__(self):
        lib.Player_delete(self.obj)


    lib.Player_add_party.argtypes = [c_void_p, c_void_p]
    lib.Player_add_party.restype = c_void_p
    def add_party(self, party):
        lib.Player_add_party(self.obj, party.obj)


    lib.Player_set_team.argtypes = [c_void_p, c_int]
    lib.Player_set_team.restype = c_void_p
    def set_team(self, team):
        lib.Player_set_team(self.obj, team)


    lib.Player_set_attack_multiplier.argtypes = [c_void_p, c_double]
    lib.Player_set_attack_multiplier.restype = c_void_p
    def set_attack_multiplier(self, multiplier):
        lib.Player_set_attack_multiplier(self.obj, multiplier)


    lib.Player_set_strategy.argtypes = [c_void_p, c_int]
    lib.Player_set_strategy.restype = c_void_p
    def set_strategy(self, strategy_index):
        lib.Player_set_strategy(self.obj, strategy_index)


    lib.Player_set_custom_strategy.argtypes = [c_void_p, c_void_p]
    lib.Player_set_custom_strategy.restype = c_void_p
    def set_custom_strategy(self, strategy):
        lib.Player_set_custom_strategy(self.obj, strategy.obj)



        
class Strategy:

    user_event_responders = []

    @staticmethod
    def wrap(event_responder):
        def event_responder_outer(t_si, t_action_p):
            atype, delay, value = event_responder(t_si)
            t_action_p[0].type = atype
            t_action_p[0].delay = delay
            t_action_p[0].value = value
        t_er = EventResponder(event_responder_outer)
        Strategy.user_event_responders.append(t_er)
        return t_er


    lib.Strategy_new.argtypes = []
    lib.Strategy_new.restype = c_void_p
    def __init__(self):
        self.obj = lib.Strategy_new()


    lib.Strategy_delete.argtypes = [c_void_p]
    lib.Strategy_delete.restype = c_void_p
    def __del__(self):
        lib.Strategy_delete(self.obj)


    lib.Strategy_set_on_free.argtypes = [c_void_p, c_void_p]
    lib.Strategy_set_on_free.restype = c_void_p
    def set_on_free(self, event_responder):
        lib.Strategy_set_on_free(self.obj, Strategy.wrap(event_responder))


    lib.Strategy_set_on_clear.argtypes = [c_void_p, c_void_p]
    lib.Strategy_set_on_clear.restype = c_void_p
    def set_on_clear(self, event_responder):
        lib.Strategy_set_on_clear(self.obj, Strategy.wrap(event_responder))


    lib.Strategy_set_on_attack.argtypes = [c_void_p, c_void_p]
    lib.Strategy_set_on_attack.restype = c_void_p
    def set_on_attack(self, event_responder):
        lib.Strategy_set_on_attack(self.obj, Strategy.wrap(event_responder))


    lib.Strategy_set_on_flash.argtypes = [c_void_p, c_void_p]
    lib.Strategy_set_on_flash.restype = c_void_p
    def set_on_flash(self, event_responder):
        lib.Strategy_set_on_flash(self.obj, Strategy.wrap(event_responder))





class Battle:

    lib.Battle_new.argtypes = []
    lib.Battle_new.restype = c_void_p
    def __init__(self):
        self.obj = lib.Battle_new()


    lib.Battle_delete.argtypes = [c_void_p]
    lib.Battle_delete.restype = c_void_p
    def __del__(self):
        lib.Battle_delete(self.obj)
        

    lib.Battle_add_player.argtypes = [c_void_p, c_void_p]
    lib.Battle_add_player.restype = c_void_p
    def add_player(self, player):
        lib.Battle_add_player(self.obj, player.obj)


    lib.Battle_set_time_limit.argtypes = [c_void_p, c_int]
    lib.Battle_set_time_limit.restype = c_void_p
    def set_time_limit(self, time_limit):
        lib.Battle_set_time_limit(self.obj, time_limit)


    lib.Battle_set_weather.argtypes = [c_void_p, c_int]
    lib.Battle_set_weather.restype = c_void_p
    def set_weather(self, weather):
        lib.Battle_set_weather(self.obj, weather)


    lib.Battle_set_random_seed.argtypes = [c_void_p, c_int]
    lib.Battle_set_random_seed.restype = c_void_p
    def set_random_seed(self, seed):
        lib.Battle_set_random_seed(self.obj, seed)


    lib.Battle_init.argtypes = [c_void_p]
    lib.Battle_init.restype = c_void_p
    def init(self):
        lib.Battle_init(self.obj)


    lib.Battle_start.argtypes = [c_void_p]
    lib.Battle_start.restype = c_void_p
    def start(self):
        lib.Battle_start(self.obj)


    lib.Battle_get_outcome.argtypes = [c_void_p, c_int, c_void_p]
    lib.Battle_get_outcome.restype = c_void_p
    def get_outcome(self, team):
        battle_outcome = BattleOutcome()
        lib.Battle_get_outcome(self.obj, team, pointer(battle_outcome))
        return battle_outcome
    



