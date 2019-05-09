
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
Global Constants
'''

BATTLE_PARAMETERS = [
    "max_energy",
    "min_stage",
    "max_stage",
    "dodge_duration",
    "dodge_window",
    "swap_duration",
    "switching_cooldown",
    "rejoin_duration",
    "item_menu_animation_time",
    "max_revive_time_per_pokemon",
    "same_type_attack_bonus_multiplier",
    "weather_attack_bonus_multiplier",
    "dodge_damage_reduction_percent",
    "energy_delta_per_health_lost",
]



STRATEGY_DEFENDER = 0
STRATEGY_ATTACKER_NO_DODGE = 1
STRATEGY_ATTACKER_DODGE_CHARGED = 2
STRATEGY_ATTACKER_DODGE_ALL = 3


atype_None = 0
atype_Wait = 1
atype_Fast = 2
atype_Charged = 3
atype_Dodge = 4


etype_None = 0
etype_Announce = 1
etype_Free = 2
etype_Fast = 3
etype_Charged = 4
etype_Dodge = 5
etype_Enter = 6


ETYPE_NAMES = dict([(globals()[k], k.split('_')[-1]) for k in globals() if k.startswith("etype_")])


'''
Functions
'''

lib.Global_set_random_seed.argtypes = [c_int]
lib.Global_set_random_seed.restype = c_void_p
def set_random_seed(seed):
    '''
    Set the random seed.
    '''

    lib.Global_set_random_seed(seed)


lib.get_damage.argtypes = [c_void_p, c_void_p, c_void_p, c_int]
lib.get_damage.restype = c_int
def calc_damage(attacker, move, defender, weather):
    '''
    Calculate the damage value of attacker using move against defender in some weather.
    '''

    return lib.get_damage(attacker._addr, move._addr, defender._addr, weather)


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
    Refer to BATTLE_PARAMETERS for all available parameters.
    '''

    lib.GameMaster_set_parameter(name.encode('utf-8'), value)



'''
Classes
'''

class TimelineEvent(Structure):
    _fields_ = [("type", c_int),
                ("time", c_int),
                ("player", c_int),
                ("value", c_int)]


class TimelineEventNode(Structure):
    _fields_ = [("next", c_void_p),
                ("item", TimelineEvent)]


class BattleOutcome(Structure):
    _fields_ = [("duration", c_int),
                ("win", c_bool),
                ("tdo", c_int),
                ("tdo_percent", c_double),
                ("num_deaths", c_int)]


class Action(Structure):
    _fields_ = [("type", c_int),
                ("delay", c_int),
                ("value", c_int),
                ("time", c_int)]


class _StrategyInput(Structure):
    _fields_ = [("time", c_int),
                ("subject", c_void_p),
                ("enemy", c_void_p),
                ("subject_action", Action),
                ("enemy_action", Action),
                ("random_number", c_int),
                ("weather", c_int)]


class StrategyInput:

    def __init__(self, _strat_input):
        self.time = _strat_input.time
        self.subject = Pokemon(_strat_input.subject)
        self.subject_action = _strat_input.subject_action
        self.enemy = Pokemon(_strat_input.enemy)
        self.enemy_action = _strat_input.enemy_action
        self.random_number = _strat_input.random_number
        self.weather = _strat_input.weather
            



EventResponder = CFUNCTYPE(c_void_p, _StrategyInput, POINTER(Action))





class Move:

    lib.Move_new.argtypes = [c_int, c_int, c_int, c_int, c_int]
    lib.Move_new.restype = c_void_p
    def __init__(self, _src=None, **kwargs):
        init_params = ["poketype", "power", "energy", "duration", "dws"]
        if _src is not None:
            if isinstance(_src, Move):
                self.__dict__["_addr"] = _src._addr
            else:
                self.__dict__["_addr"] = _src
            self.__dict__["_locked"] = True
        else:
            self.__dict__["_addr"] = lib.Move_new(
                kwargs.get("poketype", 0),
                kwargs.get("power", 0),
                kwargs.get("energy", 0),
                kwargs.get("duration", 0),
                kwargs.get("dws", 0))
            self.__dict__["_locked"] = False
            for name, value in kwargs.items():
                if name not in init_params:
                    self.__setattr__(name, value)


    lib.Move_delete.argtypes = [c_void_p]
    lib.Move_delete.restype = c_void_p
    def __del__(self):
        if not self._locked:
            lib.Move_delete(self._addr)


    lib.Move_has_attr.argtypes = [c_void_p, c_char_p]
    lib.Move_has_attr.restype = c_bool
    def __hasattr__(self, name):
        return lib.Move_has_attr(self._addr, name.encode('utf-8'))


    lib.Move_get_attr.argtypes = [c_void_p, c_char_p]
    lib.Move_get_attr.restype = c_int
    def __getattr__(self, name):
        return lib.Move_get_attr(self._addr, name.encode('utf-8'))


    lib.Move_set_attr.argtypes = [c_void_p, c_char_p, c_int]
    lib.Move_set_attr.restype = c_void_p
    def __setattr__(self, name, value):
        if self._locked:
            raise Exception("Cannot modify locked instance")
        lib.Move_set_attr(self._addr, name.encode('utf-8'), c_int(value))





class Pokemon:
        
    lib.Pokemon_new.argtypes = [c_int, c_int, c_double, c_double, c_int]
    lib.Pokemon_new.restype = c_void_p
    def __init__(self, _src=None, **kwargs):
        init_params = ["poketype1", "poketype2", "attack", "defense", "max_hp"]
        if _src is not None:
            if isinstance(_src, Pokemon):
                self.__dict__["_addr"] = _src._addr
            else:
                self.__dict__["_addr"] = _src
            self.__dict__["_locked"] = True
        else:
            self.__dict__["_addr"] = lib.Pokemon_new(
                kwargs.get("poketype1", -1),
                kwargs.get("poketype2", -1),
                kwargs.get("attack", 0),
                kwargs.get("defense", 0),
                kwargs.get("max_hp", 0))
            self.__dict__["_locked"] = False
            for name, value in kwargs.items():
                if name not in init_params:
                    self.__setattr__(name, value)


    lib.Pokemon_delete.argtypes = [c_void_p]
    lib.Pokemon_delete.restype = c_void_p
    def __del__(self):
        if not self._locked:
            lib.Pokemon_delete(self._addr)

    lib.Pokemon_get_fmove.argtypes = [c_void_p, c_int]
    lib.Pokemon_get_fmove.restype = c_void_p
    
    lib.Pokemon_add_fmove.argtypes = [c_void_p, c_void_p]
    lib.Pokemon_add_fmove.restype = c_void_p

    lib.Pokemon_add_cmove.argtypes = [c_void_p, c_void_p]
    lib.Pokemon_add_cmove.restype = c_void_p

    lib.Pokemon_get_cmove.argtypes = [c_void_p, c_int]
    lib.Pokemon_get_cmove.restype = c_void_p

    lib.Pokemon_erase_cmoves.argtypes = [c_void_p]
    lib.Pokemon_erase_cmoves.restype = c_void_p


    lib.Pokemon_has_attr.argtypes = [c_void_p, c_char_p]
    lib.Pokemon_has_attr.restype = c_bool
    def __hasattr__(self, name):
        return lib.Pokemon_has_attr(self._addr, name.encode('utf-8'))


    lib.Pokemon_get_attr.argtypes = [c_void_p, c_char_p]
    lib.Pokemon_get_attr.restype = c_double
    def __getattr__(self, name):
        if name == "fmove":
            return Move(lib.Pokemon_get_fmove(self._addr, 0))
        elif name == "cmove":
            return Move(lib.Pokemon_get_cmove(self._addr, -1))
        elif name == "cmoves":
            cmoves = []
            for i in range(round(self.cmoves_count)):
                cmoves.append(Move(lib.Pokemon_get_cmove(self._addr, i)))
            return cmoves
        else:
            return lib.Pokemon_get_attr(self._addr, name.encode('utf-8'))


    lib.Pokemon_set_attr.argtypes = [c_void_p, c_char_p, c_double]
    lib.Pokemon_set_attr.restype = c_void_p
    def __setattr__(self, name, value):
        if self._locked:
            raise Exception("Cannot modify locked instance")
        if name == "fmove":
            assert isinstance(value, Move)
            lib.Pokemon_add_fmove(self._addr, value._addr)
        elif name == "cmove":
            assert isinstance(value, Move)
            lib.Pokemon_erase_cmoves(self._addr)
            lib.Pokemon_add_cmove(self._addr, value._addr)
        elif name == "cmoves":
            lib.Pokemon_erase_cmoves(self._addr)
            for move in value:
                assert isinstance(move, Move)
                lib.Pokemon_add_cmove(self._addr, move._addr)
        else:
            lib.Pokemon_set_attr(self._addr, name.encode('utf-8'), c_double(value))





class Party:

    lib.Party_new.argtypes = []
    lib.Party_new.restype = c_void_p
    def __init__(self, _src=None, **kwargs):
        if _src is not None:
            if isinstance(_src, Party):
                self.__dict__["_addr"] = _src._addr
            else:
                self.__dict__["_addr"] = _src
            self.__dict__["_locked"] = True
        else:
            self.__dict__["_addr"] = lib.Party_new()
            self.__dict__["_locked"] = False
        for name, value in kwargs.items():
            self.__setattr__(name, value)


    lib.Party_delete.argtypes = [c_void_p]
    lib.Party_delete.restype = c_void_p
    def __del__(self):
        if not self._locked:
            lib.Party_delete(self._addr)


    lib.Party_get_pokemon.argtypes = [c_void_p, c_int]
    lib.Party_get_pokemon.restype = c_void_p

    lib.Party_add_pokemon.argtypes = [c_void_p, c_void_p]
    lib.Party_add_pokemon.restype = c_void_p

    lib.Party_erase_pokemon.argtypes = [c_void_p]
    lib.Party_erase_pokemon.restype = c_void_p
    
    
    def add(self, pokemon):
        '''
        Add a Pokemon to the party.
        '''
        
        if self._locked:
            raise Exception("Cannot modify locked instance")
        lib.Party_add_pokemon(self._addr, pokemon._addr)


    lib.Party_has_attr.argtypes = [c_void_p, c_char_p]
    lib.Party_has_attr.restype = c_bool
    def __hasattr__(self, name):
        return lib.Party_has_attr(self._addr, name.encode('utf-8'))


    lib.Party_get_attr.argtypes = [c_void_p, c_char_p]
    lib.Party_get_attr.restype = c_int    
    def __getattr__(self, name):
        if name == "pokemon":
            pokemon_list = []
            for i in range(round(self.pokemon_count)):
                pokemon_list.append(Pokemon(lib.Party_get_pokemon(self._addr, i)))
            return pokemon_list
        else:
            return lib.Party_get_attr(self._addr, name.encode('utf-8'))


    lib.Party_set_attr.argtypes = [c_void_p, c_char_p, c_int]
    lib.Party_set_attr.restype = c_void_p
    def __setattr__(self, name, value):
        if self._locked:
            raise Exception("Cannot modify locked instance")
        if name == "pokemon":
            lib.Party_erase_pokemon(self._addr)
            for pokemon in value:
                assert isinstance(pokemon, Pokemon)
                lib.Party_add_pokemon(self._addr, pokemon._addr)
        else:
            lib.Party_set_attr(self._addr, name.encode('utf-8'), value)




class Player:

    lib.Player_new.argtypes = []
    lib.Player_new.restype = c_void_p
    def __init__(self, _src=None, **kwargs):
        if _src is not None:
            if isinstance(_src, Player):
                self.__dict__["_addr"] = _src._addr
            else:
                self.__dict__["_addr"] = _src
            self.__dict__["_locked"] = True
        else:
            self.__dict__["_addr"] = lib.Player_new()
            self.__dict__["_locked"] = False
        self.__dict__["_attack_multiplier"] = 1
        for name, value in kwargs.items():
            self.__setattr__(name, value)


    lib.Player_delete.argtypes = [c_void_p]
    lib.Player_delete.restype = c_void_p
    def __del__(self):
        if not self._locked:
            lib.Player_delete(self._addr)


    lib.Player_get_party.argtypes = [c_void_p, c_int]
    lib.Player_get_party.restype = c_void_p

    lib.Player_add_party.argtypes = [c_void_p, c_void_p]
    lib.Player_add_party.restype = c_void_p

    lib.Player_erase_parties.argtypes = [c_void_p]
    lib.Player_erase_parties.restype = c_void_p

    
    def add(self, party):
        '''
        Add a party to the player.
        '''
        if self._locked:
            raise Exception("Cannot modify locked instance")
        lib.Player_add_party(self._addr, party._addr)



    lib.Player_has_attr.argtypes = [c_void_p, c_char_p]
    lib.Player_has_attr.restype = c_bool
    def __hasattr__(self, name):
        return lib.Player_has_attr(self._addr, name.encode('utf-8'))


    lib.Player_get_strategy.argtypes = [c_void_p]
    lib.Player_get_strategy.restype = c_void_p

    lib.Player_get_attr.argtypes = [c_void_p, c_char_p]
    lib.Player_get_attr.restype = c_int    
    def __getattr__(self, name):
        if name == "parties":
            party_list = []
            for i in range(round(self.parties_count)):
                party_list.append(Party(lib.Player_get_party(self._addr, i)))
            return party_list
        elif name == "attack_multiplier":
            return self._attack_multiplier
        elif name == "strategy":
            return Strategy(lib.Player_get_strategy(self._addr))
        else:
            return lib.Player_get_attr(self._addr, name.encode('utf-8'))


    lib.Player_set_attack_multiplier.argtypes = [c_void_p, c_double]
    lib.Player_set_attack_multiplier.restype = c_void_p

    lib.Player_set_strategy.argtypes = [c_void_p, c_int]
    lib.Player_set_strategy.restype = c_void_p

    lib.Player_set_custom_strategy.argtypes = [c_void_p, c_void_p]
    lib.Player_set_custom_strategy.restype = c_void_p
    
    lib.Player_set_attr.argtypes = [c_void_p, c_char_p, c_int]
    lib.Player_set_attr.restype = c_void_p
    def __setattr__(self, name, value):
        if self._locked:
            raise Exception("Cannot modify locked instance")
        if name == "parties":
            lib.Player_erase_parties(self._addr)
            for party in value:
                assert isinstance(party, Party)
                lib.Player_add_party(self._addr, party._addr)
        elif name == "attack_multiplier":
            self._attack_multiplier = value
            lib.Player_set_attack_multiplier(self._addr, c_double(value))
        elif name == "strategy":
            if isinstance(value, Strategy):
                lib.Player_set_custom_strategy(self._addr, value._addr)
            else:
                lib.Player_set_strategy(self._addr, value)
        else:
            lib.Player_set_attr(self._addr, name.encode('utf-8'), value)
    

        
class Strategy:

    user_event_responders = []

    @staticmethod
    def wrap(event_responder):
        def event_responder_outer(t_strat_input, t_action_p):
            action = event_responder(StrategyInput(t_strat_input))
            t_action_p[0].type = action.type
            t_action_p[0].delay = action.delay
            t_action_p[0].value = action.value
        t_er = EventResponder(event_responder_outer)
        Strategy.user_event_responders.append(t_er)
        return t_er


    lib.Strategy_new.argtypes = []
    lib.Strategy_new.restype = c_void_p
    def __init__(self, _src=None, **kwargs):
        if _src is not None:
            if isinstance(_src, Strategy):
                self.__dict__["_addr"] = _src._addr
            else:
                self.__dict__["_addr"] = _src
            self.__dict__["_locked"] = True
        else:
            self.__dict__["_addr"] = lib.Strategy_new()
            self.__dict__["_locked"] = False
        for name, value in kwargs.items():
            self.__setattr__(name, value)


    lib.Strategy_delete.argtypes = [c_void_p]
    lib.Strategy_delete.restype = c_void_p
    def __del__(self):
        if not self._locked:
            lib.Strategy_delete(self._addr)


    lib.Strategy_set_on_free.argtypes = [c_void_p, c_void_p]
    lib.Strategy_set_on_free.restype = c_void_p

    lib.Strategy_set_on_clear.argtypes = [c_void_p, c_void_p]
    lib.Strategy_set_on_clear.restype = c_void_p

    lib.Strategy_set_on_attack.argtypes = [c_void_p, c_void_p]
    lib.Strategy_set_on_attack.restype = c_void_p
    def __setattr__(self, name, value):
        if name == "on_free":
            lib.Strategy_set_on_free(self._addr, Strategy.wrap(value))
        elif name == "on_clear":
            lib.Strategy_set_on_clear(self._addr, Strategy.wrap(value))
        elif name == "on_attack":
            lib.Strategy_set_on_attack(self._addr, Strategy.wrap(value))
        else:
            raise AttributeError("Must be 'on_free' or 'on_clear' or 'on_attack'")
            




class Battle:

    lib.Battle_new.argtypes = []
    lib.Battle_new.restype = c_void_p
    def __init__(self, _src=None, **kwargs):
        if _src is not None:
            if isinstance(_src, Battle):
                self.__dict__["_addr"] = _src._addr
            else:
                self.__dict__["_addr"] = _src
            self.__dict__["_locked"] = True
        else:
            self.__dict__["_addr"] = lib.Battle_new()
            self.__dict__["_locked"] = False
        for name, value in kwargs.items():
            self.__setattr__(name, value)


    lib.Battle_delete.argtypes = [c_void_p]
    lib.Battle_delete.restype = c_void_p
    def __del__(self):
        lib.Battle_delete(self._addr)

        

    lib.Battle_get_player.argtypes = [c_void_p, c_int]
    lib.Battle_get_player.restype = c_void_p
    
    lib.Battle_add_player.argtypes = [c_void_p, c_void_p]
    lib.Battle_add_player.restype = c_void_p

    lib.Battle_erase_players.argtypes = [c_void_p]
    lib.Battle_erase_players.restype = c_void_p
    
    def add(self, player):
        '''
        Add a player to the battle.
        '''
        
        lib.Battle_add_player(self._addr, player._addr)
        

    lib.Battle_update_player.argtypes = [c_void_p, c_void_p]
    lib.Battle_update_player.restype = c_void_p
    lib.Battle_update_pokemon.argtypes = [c_void_p, c_void_p]
    lib.Battle_update_pokemon.restype = c_void_p
    def update(self, entity):
        '''
        Update a Player or Pokemon.
        '''

        if isinstance(entity, Player):
            lib.Battle_update_player(self._addr, entity._addr)
        elif isinstance(entity, Pokemon):
            lib.Battle_update_pokemon(self._addr, entity._addr)
        else:
            raise Exception("Unsupported type of entity")



    lib.Battle_init.argtypes = [c_void_p]
    lib.Battle_init.restype = c_void_p
    def init(self):
        '''
        Initialize the battle.
        '''
        
        lib.Battle_init(self._addr)


    lib.Battle_start.argtypes = [c_void_p]
    lib.Battle_start.restype = c_void_p
    def start(self):
        '''
        Start a new simulation.
        '''
        
        lib.Battle_start(self._addr)


    lib.Battle_get_outcome.argtypes = [c_void_p, c_int, c_void_p]
    lib.Battle_get_outcome.restype = c_void_p
    def get_outcome(self, team):
        '''
        Get the overall battle outcome of the team.
        '''
        
        battle_outcome = BattleOutcome()
        lib.Battle_get_outcome(self._addr, team, pointer(battle_outcome))
        return battle_outcome


    lib.Battle_get_log.argtypes = [c_void_p, c_void_p]
    lib.Battle_get_log.restype = c_void_p
    def get_log(self):
        '''
        Get the battle log. Note: enable logging, set has_log to True.
        '''

        tenode = TimelineEventNode()
        lib.Battle_get_log(self._addr, pointer(tenode))
        event_list = []
        while tenode.next is not None:
            tenode_ptr = cast(tenode.next, POINTER(TimelineEventNode))
            tenode = tenode_ptr[0]
            event_list.append(tenode.item)
        return event_list



    lib.Battle_has_attr.argtypes = [c_void_p, c_char_p]
    lib.Battle_has_attr.restype = c_bool
    def __hasattr__(self, name):
        return lib.Battle_has_attr(self._addr, name.encode('utf-8'))


    lib.Battle_get_attr.argtypes = [c_void_p, c_char_p]
    lib.Battle_get_attr.restype = c_int    
    def __getattr__(self, name):
        if name == "players":
            players_list = []
            for i in range(round(self.players_count)):
                players_list.append(Player(lib.Battle_get_player(self._addr, i)))
            return players_list
        elif name == "outcome":
            return self.get_outcome(1)
        elif name == "log":
            return self.get_log()
        else:
            return lib.Battle_get_attr(self._addr, name.encode('utf-8'))


    lib.Battle_set_attr.argtypes = [c_void_p, c_char_p, c_int]
    lib.Battle_set_attr.restype = c_void_p
    def __setattr__(self, name, value):
        if self._locked:
            raise Exception("Cannot modify locked instance")
        if name == "players":
            lib.Battle_erase_players(self._addr)
            for player in value:
                assert isinstance(player, Player)
                lib.Battle_add_player(self._addr, player._addr)
        else:
            lib.Battle_set_attr(self._addr, name.encode('utf-8'), value)



