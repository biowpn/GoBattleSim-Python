
'''
A wrapper library for native GoBattleSim engine (in C++).

'''

from ctypes import *
import os
import platform

if platform.system() == "Windows":
    lib = CDLL(os.path.join(os.path.dirname(__file__), "libGoBattleSim.dll"))
else:
    lib = CDLL(os.path.join(os.path.dirname(__file__), "libGoBattleSim.so"))


'''
Global Constants
'''

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


ETYPE_NAMES = dict([(globals()[k], k.split('_')[-1])
                    for k in globals() if k.startswith("etype_")])


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


lib.Global_calc_damage.argtypes = [c_void_p, c_void_p, c_void_p, c_int]
lib.Global_calc_damage.restype = c_int


def calc_damage(attacker, move, defender, weather):
    '''
    [For PvE Battles] Calculate the damage value of attacker using move against defender in some weather.
    '''
    return lib.Global_calc_damage(attacker._addr, move._addr, defender._addr, weather)


lib.Global_calc_damage_pvp_fmove.argtypes = [c_void_p, c_void_p, c_void_p]
lib.Global_calc_damage_pvp_fmove.restype = c_int


def calc_damage_pvp_fmove(attacker, move, defender):
    '''
    [For PvP Battles] Calculate the damage value of attacker using move against defender.
    GameMaster::pvp_fast_attack_bonus_multiplier is taken into account.
    '''
    return lib.Global_calc_damage_pvp_fmove(attacker._addr, move._addr, defender._addr)


lib.Global_calc_damage_pvp_cmove.argtypes = [c_void_p, c_void_p, c_void_p]
lib.Global_calc_damage_pvp_cmove.restype = c_int


def calc_damage_pvp_cmove(attacker, move, defender, weather):
    '''
    [For PvP Battles] Calculate the damage value of attacker using move against defender.
    GameMaster::pvp_charged_attack_bonus_multiplier is taken into account.
    '''
    return lib.Global_calc_damage_pvp_cmove(attacker._addr, move._addr, defender._addr)


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


lib.GameMaster_set_stage_bounds.argtypes = [c_int, c_int]
lib.GameMaster_set_stage_bounds.restype = c_void_p
lib.GameMaster_set_stage_multiplier.argtypes = [c_int, c_double]
lib.GameMaster_set_stage_multiplier.restype = c_void_p


def set_stage_multipliers(multipliers, min_stage=None):
    '''
    Set the stat multipliers.
    '''
    if min_stage is None:
        min_stage = - (len(multipliers) // 2)
    max_stage = min_stage + len(multipliers) - 1
    lib.GameMaster_set_stage_bounds(min_stage, max_stage)
    for i in range(min_stage, max_stage + 1):
        lib.GameMaster_set_stage_multiplier(i, multipliers[i - min_stage])


lib.GameMaster_set_parameter.argtypes = [c_char_p, c_double]
lib.GameMaster_set_parameter.restype = c_void_p


def set_parameter(name, value):
    '''
    Set a specific battle parameter.
    Refer to BATTLE_PARAMETERS for all available parameters.
    '''
    lib.GameMaster_set_parameter(name.encode('utf-8'), value)


class Addressable:
    '''
    Base class for wrapper classes.
    An <Addressable> object contains an address to a C++ object.

    In initialization, the underlying C++ constructor will be called with positional arguments supplied.
    If positional arguments are less than what's required, 0 will be used to fill the gap.

    Simple shallow copy is supported. Deepcopy is not supported.

    A cast() class method is also provided, which accepts an address (an int)
    and returns an Addressable instance with the same address. Use with caution.
    '''

    @staticmethod
    def _constructor(*args):
        '''
        Derived class should override this method.
        This method should call the underlying C++ constructor,
        and return the address to the newly created instance.
        '''
        return None

    @staticmethod
    def _destructor(addr):
        '''
        Derived class should override this method.
        This method should call the underlying C++ destructor,
        given the address of the instance to be deconstructed.
        '''
        return

    def __init__(self, *args):
        self.__dict__["_locked"] = False
        self.__dict__["_addr"] = self._constructor(*args)
        self._addr = self._addr

    def __del__(self):
        locked = self.__dict__.get("_locked", False)
        addr = self.__dict__.get("_addr")
        if not locked and addr:
            self._destructor(addr)

    @classmethod
    def cast(cls, address):
        instance = object.__new__(cls)
        instance.__dict__["_addr"] = address
        instance.__dict__["_locked"] = True
        return instance

    def __copy__(self):
        return self.__class__.cast(self.__dict__["_addr"])

    def copy(self):
        return self.__copy__()


'''
    PvE Classes
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
        self.subject = Pokemon.cast(_strat_input.subject)
        self.subject_action = _strat_input.subject_action
        self.enemy = Pokemon.cast(_strat_input.enemy)
        self.enemy_action = _strat_input.enemy_action
        self.random_number = _strat_input.random_number
        self.weather = _strat_input.weather


EventResponder = CFUNCTYPE(c_void_p, _StrategyInput, POINTER(Action))


class MoveEffect(Structure):
    _fields_ = [("activation_chance", c_double),
                ("self_attack_stage_delta", c_int),
                ("self_defense_stage_delta", c_int),
                ("target_attack_stage_delta", c_int),
                ("target_defense_stage_delta", c_int)]


class Move(Addressable):

    lib.Move_new.argtypes = [c_int, c_int, c_int, c_int, c_int]
    lib.Move_new.restype = c_void_p
    @staticmethod
    def _constructor(*args):
        if len(args) < 5:
            args = list(args) + [0] * (5 - len(args))
        return lib.Move_new(*args)

    lib.Move_delete.argtypes = [c_void_p]
    lib.Move_delete.restype = c_void_p
    @staticmethod
    def _destructor(addr):
        return lib.Move_delete(addr)

    lib.Move_has_attr.argtypes = [c_void_p, c_char_p]
    lib.Move_has_attr.restype = c_bool

    def __hasattr__(self, name):
        return lib.Move_has_attr(self._addr, name.encode('utf-8'))

    lib.Move_get_effect.argtypes = [c_void_p, c_void_p]
    lib.Move_get_effect.restype = c_void_p
    lib.Move_get_attr.argtypes = [c_void_p, c_char_p]
    lib.Move_get_attr.restype = c_int

    def __getattr__(self, name):
        if name == "effect":
            effect = MoveEffect()
            lib.Move_get_effect(self._addr, pointer(effect))
            return effect
        else:
            return lib.Move_get_attr(self._addr, name.encode('utf-8'))

    lib.Move_set_effect.argtypes = [c_void_p, c_void_p]
    lib.Move_set_effect.restype = c_void_p
    lib.Move_set_attr.argtypes = [c_void_p, c_char_p, c_int]
    lib.Move_set_attr.restype = c_void_p

    def __setattr__(self, name, value):
        if self._locked:
            raise Exception("Cannot modify locked instance")
        if name == "effect":
            if isinstance(value, MoveEffect):
                lib.Move_set_effect(self._addr, pointer(value))
            elif isinstance(value, dict):
                effect = MoveEffect(**value)
                lib.Move_set_effect(self._addr, pointer(effect))
            else:
                raise TypeError(
                    "Expected MoveEffect/dict, got {}".format(type(value)))
        else:
            lib.Move_set_attr(self._addr, name.encode('utf-8'), value)


class Pokemon(Addressable):

    lib.Pokemon_new.argtypes = [c_int, c_int, c_double, c_double, c_int]
    lib.Pokemon_new.restype = c_void_p
    @staticmethod
    def _constructor(*args):
        return lib.Pokemon_new(*args)

    lib.Pokemon_delete.argtypes = [c_void_p]
    lib.Pokemon_delete.restype = c_void_p
    @staticmethod
    def _destructor(addr):
        return lib.Pokemon_delete(addr)

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
            return Move.cast(lib.Pokemon_get_fmove(self._addr, 0))
        elif name == "cmove":
            return Move.cast(lib.Pokemon_get_cmove(self._addr, -1))
        elif name == "cmoves":
            cmoves = []
            for i in range(round(self.cmoves_count)):
                cmoves.append(Move.cast(lib.Pokemon_get_cmove(self._addr, i)))
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
            lib.Pokemon_set_attr(
                self._addr, name.encode('utf-8'), c_double(value))


class Party(Addressable):

    lib.Party_new.argtypes = []
    lib.Party_new.restype = c_void_p
    @staticmethod
    def _constructor(*args):
        return lib.Party_new(*args)

    lib.Party_delete.argtypes = [c_void_p]
    lib.Party_delete.restype = c_void_p
    @staticmethod
    def _destructor(addr):
        lib.Party_delete(addr)

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
        assert isinstance(pokemon, Pokemon)
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
                pokemon_list.append(Pokemon.cast(
                    lib.Party_get_pokemon(self._addr, i)))
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


class Player(Addressable):

    lib.Player_new.argtypes = []
    lib.Player_new.restype = c_void_p
    @staticmethod
    def _constructor(*args):
        return lib.Player_new(*args)

    lib.Player_delete.argtypes = [c_void_p]
    lib.Player_delete.restype = c_void_p
    @staticmethod
    def _destructor(addr):
        lib.Player_delete(addr)

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
        assert isinstance(party, Party)
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
                party_list.append(Party.cast(
                    lib.Player_get_party(self._addr, i)))
            return party_list
        elif name == "attack_multiplier":
            return self.__dict__.get("attack_multiplier", 1)
        elif name == "clone_multiplier":
            return self.__dict__.get("clone_multiplier", 1)
        elif name == "strategy":
            return Strategy(lib.Player_get_strategy(self._addr))
        else:
            return lib.Player_get_attr(self._addr, name.encode('utf-8'))

    lib.Player_set_attack_multiplier.argtypes = [c_void_p, c_double]
    lib.Player_set_attack_multiplier.restype = c_void_p

    lib.Player_set_clone_multiplier.argtypes = [c_void_p, c_int]
    lib.Player_set_clone_multiplier.restype = c_void_p

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
            self.__dict__["attack_multiplier"] = value
            lib.Player_set_attack_multiplier(self._addr, c_double(value))
        elif name == "clone_multiplier":
            self.__dict__["clone_multiplier"] = value
            lib.Player_set_clone_multiplier(self._addr, c_int(value))
        elif name == "strategy":
            if isinstance(value, Strategy):
                lib.Player_set_custom_strategy(self._addr, value._addr)
            else:
                lib.Player_set_strategy(self._addr, value)
        else:
            lib.Player_set_attr(self._addr, name.encode('utf-8'), value)


class Strategy(Addressable):

    user_event_responders = []

    @staticmethod
    def wrap(event_responder):
        def event_responder_outer(t_strat_input, t_action_p):
            action = event_responder(StrategyInput(t_strat_input))
            t_action_p[0].type = action.type
            t_action_p[0].delay = action.delay
            t_action_p[0].value = action.value
        t_er = EventResponder(event_responder_outer)
        # Prevent garbage collection
        Strategy.user_event_responders.append(t_er)
        return t_er

    lib.Strategy_new.argtypes = []
    lib.Strategy_new.restype = c_void_p
    @staticmethod
    def _constructor(*args):
        return lib.Strategy_new(*args)

    lib.Strategy_delete.argtypes = [c_void_p]
    lib.Strategy_delete.restype = c_void_p
    @staticmethod
    def _destructor(addr):
        lib.Strategy_delete(addr)

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
            raise AttributeError(
                "Must be 'on_free' or 'on_clear' or 'on_attack'")


class Battle(Addressable):

    lib.Battle_new.argtypes = []
    lib.Battle_new.restype = c_void_p
    @staticmethod
    def _constructor(*args):
        return lib.Battle_new(*args)

    lib.Battle_delete.argtypes = [c_void_p]
    lib.Battle_delete.restype = c_void_p
    @staticmethod
    def _destructor(addr):
        lib.Battle_delete(addr)

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
        assert isinstance(player, Player)
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
            raise TypeError(
                "Expected Player/Pokemon, got {}".format(type(entity)))

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
        # TODO: Make the log human-readable
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
                players_list.append(Player.cast(
                    lib.Battle_get_player(self._addr, i)))
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


'''
    PvP Classes
'''


class SimplePvPBattleOutcome(Structure):
    _fields_ = [("tdo_percent", c_double * 2)]


class _PvPStrategyInput(Structure):
    _fields_ = [("subject", c_void_p),
                ("enemy", c_void_p),
                ("subject_hp", c_int),
                ("enemy_hp", c_int),
                ("subject_energy", c_int),
                ("enemy_energy", c_int),
                ("subject_shields", c_int),
                ("enemy_shields", c_int)]


class PvPStrategyInput:

    def __init__(self, _pvp_input):
        self.subject = Pokemon.cast(_pvp_input.subject)
        self.subject.__dict__["hp"] = _pvp_input.subject_hp
        self.subject.__dict__["energy"] = _pvp_input.subject_energy
        self.subject.__dict__["shields"] = _pvp_input.subject_shields
        self.enemy = Pokemon.cast(_pvp_input.enemy)
        self.enemy.__dict__["hp"] = _pvp_input.enemy_hp
        self.enemy.__dict__["energy"] = _pvp_input.enemy_energy
        self.enemy.__dict__["shields"] = _pvp_input.enemy_shields


PvPEventResponder = CFUNCTYPE(c_void_p, _PvPStrategyInput, POINTER(Action))


class PvPStrategy(Addressable):

    user_event_responders = []

    @staticmethod
    def wrap(event_responder):
        def event_responder_outer(t_strat_input, t_action_p):
            action = event_responder(PvPStrategyInput(t_strat_input))
            t_action_p[0].type = action.type
            t_action_p[0].delay = action.delay
            t_action_p[0].value = action.value
        t_er = PvPEventResponder(event_responder_outer)
        PvPStrategy.user_event_responders.append(t_er)
        return t_er

    lib.PvPStrategy_new.argtypes = []
    lib.PvPStrategy_new.restype = c_void_p
    @staticmethod
    def _constructor(*args):
        return lib.PvPStrategy_new(*args)

    lib.PvPStrategy_delete.argtypes = [c_void_p]
    lib.PvPStrategy_delete.restype = c_void_p
    @staticmethod
    def _destructor(addr):
        lib.PvPStrategy_delete(addr)

    lib.PvPStrategy_set_on_free.argtypes = [c_void_p, c_void_p]
    lib.PvPStrategy_set_on_free.restype = c_void_p

    lib.PvPStrategy_set_on_attack.argtypes = [c_void_p, c_void_p]
    lib.PvPStrategy_set_on_attack.restype = c_void_p

    # PvPBattle that supports on_switch not implemented
    lib.PvPStrategy_set_on_switch.argtypes = [c_void_p, c_void_p]
    lib.PvPStrategy_set_on_switch.restype = c_void_p

    def __setattr__(self, name, value):
        if name == "on_free":
            lib.PvPStrategy_set_on_free(self._addr, PvPStrategy.wrap(value))
        elif name == "on_attack":
            lib.PvPStrategy_set_on_attack(self._addr, PvPStrategy.wrap(value))
        elif name == "on_switch":
            lib.PvPStrategy_set_on_switch(self._addr, PvPStrategy.wrap(value))
        else:
            raise AttributeError(
                "Must be 'on_free' or 'on_attack' or 'on_switch'")


class PvPPokemon(Pokemon):

    lib.PvPPokemon_new.argtypes = [c_int, c_int, c_double, c_double, c_int]
    lib.PvPPokemon_new.restype = c_void_p
    @staticmethod
    def _constructor(*args):
        return lib.PvPPokemon_new(*args)

    lib.PvPPokemon_delete.argtypes = [c_void_p]
    lib.PvPPokemon_delete.restype = c_void_p
    @staticmethod
    def _destructor(addr):
        lib.PvPPokemon_delete(addr)

    lib.PvPPokemon_set_num_shields.argtypes = [c_void_p, c_int]
    lib.PvPPokemon_set_num_shields.restype = c_void_p

    def __setattr__(self, name, value):
        if name == "num_shields":
            lib.PvPPokemon_set_num_shields(self._addr, value)
        else:
            super().__setattr__(name, value)


class SimplePvPBattle(Addressable):

    lib.SimplePvPBattle_new.argtypes = [c_void_p, c_void_p]
    lib.SimplePvPBattle_new.restype = c_void_p
    @staticmethod
    def _constructor(*args):
        return lib.SimplePvPBattle_new(*args)

    lib.SimplePvPBattle_delete.argtypes = [c_void_p]
    lib.SimplePvPBattle_delete.restype = c_void_p
    @staticmethod
    def _destructor(addr):
        return lib.SimplePvPBattle_delete(addr)

    def __init__(self, pkm_0, pkm_1):
        assert isinstance(pkm_0, PvPPokemon)
        assert isinstance(pkm_1, PvPPokemon)
        super().__init__(pkm_0._addr, pkm_1._addr)

    lib.SimplePvPBattle_set_num_shields_max.argtypes = [c_void_p, c_int, c_int]
    lib.SimplePvPBattle_set_num_shields_max.restype = c_void_p

    def set_num_shields_max(self, num_shields_0, num_shields_1):
        '''
        Set the maximum number of shields allowed for both Pokemon.
        '''
        lib.SimplePvPBattle_set_num_shields_max(
            self._addr, num_shields_0, num_shields_1)

    lib.SimplePvPBattle_set_strategy.argtypes = [c_void_p, c_int, c_void_p]
    lib.SimplePvPBattle_set_strategy.restype = c_void_p

    def set_strategy(self, pkm_idx, strategy):
        '''
        Set custom strategy for Pokemon with index {pkm_idx}.
        '''
        assert isinstance(strategy, PvPStrategy)
        lib.SimplePvPBattle_set_strategy(
            self._addr, pkm_idx, pointer(strategy))

    lib.SimplePvPBattle_init.argtypes = [c_void_p]
    lib.SimplePvPBattle_init.restype = c_void_p

    def init(self):
        '''
        Initialize the battle.
        '''
        lib.SimplePvPBattle_init(self._addr)

    lib.SimplePvPBattle_start.argtypes = [c_void_p]
    lib.SimplePvPBattle_start.restype = c_void_p

    def start(self):
        '''
        Start a new simulation.
        '''
        lib.SimplePvPBattle_start(self._addr)

    lib.SimplePvPBattle_get_outcome.argtypes = [c_void_p, c_void_p]
    lib.SimplePvPBattle_get_outcome.restype = c_void_p

    def get_outcome(self):
        '''
        Get the simple pvp battle outcome.
        '''
        pvp_battle_outcome = SimplePvPBattleOutcome()
        lib.SimplePvPBattle_get_outcome(
            self._addr, pointer(pvp_battle_outcome))
        return pvp_battle_outcome

    def __getattr__(self, name):
        if name == "outcome":
            return self.get_outcome()


class BattleMatrix(Addressable):

    lib.BattleMatrix_new.argtypes = [c_void_p, c_int, c_void_p, c_int, c_bool]
    lib.BattleMatrix_new.restype = c_void_p
    @staticmethod
    def _constructor(*args):
        return lib.BattleMatrix_new(*args)

    lib.BattleMatrix_delete.argtypes = [c_void_p]
    lib.BattleMatrix_delete.restype = c_void_p
    @staticmethod
    def _destructor(addr):
        lib.BattleMatrix_delete(addr)

    def __init__(self, row_pkm, col_pkm, enum_shields=False):
        '''
        {row_pkm} and {col_pkm} are lists of PvPPokemon
        '''
        row_pkm_addrs = [pkm._addr for pkm in row_pkm]
        col_pkm_addrs = [pkm._addr for pkm in col_pkm]
        self.row_size = len(row_pkm_addrs)
        self.col_size = len(col_pkm_addrs)
        row_pkm_arr = (c_void_p * self.row_size)(*row_pkm_addrs)
        col_pkm_arr = (c_void_p * self.col_size)(*col_pkm_addrs)

        super().__init__(row_pkm_arr, self.row_size,
                         col_pkm_arr, self.col_size, enum_shields)

    lib.BattleMatrix_run.argtypes = [c_void_p]
    lib.BattleMatrix_run.restype = c_void_p

    def run(self):
        '''
        Run the battle matrix.
        '''
        lib.BattleMatrix_run(self._addr)
        return self

    lib.BattleMatrix_get.argtypes = [c_void_p, POINTER(POINTER(c_double))]
    lib.BattleMatrix_get.restype = c_void_p

    def get(self):
        '''
        Return the matrix, a 2D array of battle scores.
        '''
        STATIC_ROW = (self.col_size * c_double)
        DYNAMIC_ROW = POINTER(c_double)
        STATIC_MAT = (self.row_size * DYNAMIC_ROW)
        DYNAMIC_MAT = POINTER(DYNAMIC_ROW)

        c_matrix = cast(STATIC_MAT(
            *[cast(STATIC_ROW(), DYNAMIC_ROW) for _ in range(self.row_size)]), DYNAMIC_MAT)
        lib.BattleMatrix_get(self._addr, c_matrix)

        return [[c_matrix[r][c] for c in range(self.col_size)] for r in range(self.row_size)]
