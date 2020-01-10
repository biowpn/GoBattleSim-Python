
'''
The interface module.

This module provides game master file parsing, setting game parameters,
and more convenient battle objects initialization (built on top of engine.py).

'''

import json
import re
import copy
import itertools

from .engine import GBS
from .GameMaster import GameMaster
from .PokeQuery import PokeQuery


'''
    Inferface Classes for engine.
'''


ROLE_PVE_ATTACKER = "ae"
ROLE_PVP_ATTACKER = "ap"
ROLE_GYM_DEFENDER = "gd"
ROLE_RAID_BOSS = "rb"


class Move:
    '''
    Interface Move class.
    Convinient for contructing gobattlesim.engine.Move objects.
    '''

    def __init__(self, *args, pvp=False, **kwargs):
        '''
        The named move paramters can be passed via keyword arguments,
        or via a str or dict as the first positional argument:

            Move("Counter"), Move({"name": "Counter"}), Move(name="Counter")

        give the same thing.
        '''
        game_master = GameMaster.CurrentInstance
        if len(args) > 0:
            if isinstance(args[0], str):
                kwargs["name"] = args[0]
                args = args[1:]
            elif isinstance(args[0], dict):
                kwargs.update(args[0])
                args = args[1:]
        if "name" in kwargs:
            if pvp:
                kwargs.update(game_master.search_pvp_move(kwargs["name"]))
            else:
                kwargs.update(game_master.search_pve_move(kwargs["name"]))
        self.pokeType = kwargs["pokeType"]
        self.power = kwargs["power"]
        self.energy = kwargs["energy"]
        self.duration = kwargs["duration"]
        self.dws = kwargs["dws"]
        if "effect" in kwargs:
            self.effect = kwargs["effect"]


class Pokemon:

    @staticmethod
    def calc_cp(bAtk, bDef, bStm, cpm, atkiv, defiv, stmiv):
        Atk = (bAtk + atkiv) * cpm
        Def = (bDef + defiv) * cpm
        Stm = (bStm + stmiv) * cpm
        return max(10, int(Atk * (Def * Stm)**0.5 / 10))

    @staticmethod
    def infer_level_and_IVs(bAtk, bDef, bStm, target_cp):
        CPMultipliers = GameMaster.CurrentInstance.CPMultipliers
        closest = None
        closest_cp = 0
        min_cpm_i = 0
        max_cpm_i = len(CPMultipliers) - 1
        while min_cpm_i < max_cpm_i:
            if Pokemon.calc_cp(bAtk, bDef, bStm, CPMultipliers[min_cpm_i], 15, 15, 15) >= target_cp:
                break
            min_cpm_i += 1
        while max_cpm_i > min_cpm_i:
            if Pokemon.calc_cp(bAtk, bDef, bStm, CPMultipliers[max_cpm_i], 0, 0, 0) <= target_cp:
                break
            max_cpm_i -= 1
        for cpm in CPMultipliers[min_cpm_i: max_cpm_i + 1]:
            for stmiv in range(16):
                for defiv in range(16):
                    for atkiv in range(16):
                        cp = Pokemon.calc_cp(
                            bAtk, bDef, bStm, cpm, atkiv, defiv, stmiv)
                        if cp == target_cp:
                            return (cpm, atkiv, defiv, stmiv)
                        elif closest_cp < cp and cp < target_cp:
                            closest_cp = cp
                            closest = (cpm, atkiv, defiv, stmiv)
        return closest

    def __init__(self, *args, **kwargs):
        '''
        All named parameters should be passed via keyword arguments, including:
            name, fmove, cmove, cmoves, level, atkiv, defiv, stmiv, cp, role, tier, immortal, strategy

        Some examples:
            Define an attacker:
                (name, fmove, cmove/cmoves, level, atkiv, defiv, stmiv)
            Define an attacker by cp (infer the stats):
                (name, fmove, cmove/cmoves, cp)
            Define a raid boss:
                (name, fmove, cmove, role=ROLE_RAID_BOSS, tier)
            Define a gym defender by cp (infer the stats, too):
                (name, fmove, cmove, cp, role=ROLE_GYM_DEFENDER)
        '''
        game_master = GameMaster.CurrentInstance
        if len(args) > 0:
            if isinstance(args[0], str):
                kwargs["name"] = args[0]
                args = args[1:]
            elif isinstance(args[0], dict):
                kwargs.update(args[0])
                args = args[1:]
        if "name" in kwargs:
            kwargs.update(game_master.search_pokemon(kwargs["name"]))

        role = kwargs.get("role", ROLE_PVE_ATTACKER)
        self.tier = None
        if role == ROLE_RAID_BOSS or "tier" in kwargs:
            self.tier = str(kwargs["tier"])
            tier_setting = game_master.search_raid_tier(self.tier)
            kwargs["attack"] = (kwargs["baseAtk"] + 15) * tier_setting["cpm"]
            kwargs["defense"] = (kwargs["baseDef"] + 15) * tier_setting["cpm"]
            kwargs["maxHP"] = tier_setting["maxHP"]
        elif len(args) < 5:
            if "cp" in kwargs:
                cp = kwargs["cp"]
                if not isinstance(cp, int):
                    raise TypeError("Expected int, got {}".format(type(cp)))
                cpm, atkiv, defiv, stmiv = Pokemon.infer_level_and_IVs(
                    kwargs["baseAtk"], kwargs["baseDef"], kwargs["baseStm"], cp)
            else:
                cpm = game_master.search_cpm(kwargs.get("level", 40))
                atkiv = int(kwargs.get("atkiv", 15))
                defiv = int(kwargs.get("defiv", 15))
                stmiv = int(kwargs.get("stmiv", 15))
            kwargs["attack"] = (kwargs["baseAtk"] + atkiv) * cpm
            kwargs["defense"] = (kwargs["baseDef"] + defiv) * cpm
            kwargs["maxHP"] = int((kwargs["baseStm"] + stmiv) * cpm)
            if role == ROLE_GYM_DEFENDER:
                kwargs["maxHP"] *= 2

        self.pokeType1 = kwargs["pokeType1"]
        self.pokeType2 = kwargs["pokeType2"]
        self.attack = kwargs["attack"]
        self.defense = kwargs["defense"]
        self.maxHP = kwargs["maxHP"]

        # Set up moves
        pvp = (role == ROLE_PVP_ATTACKER) or kwargs.get("pvp", False)
        if "fmove" in kwargs:
            self.fmove = Move(kwargs["fmove"], pvp=pvp,
                              game_master=game_master)
        raw_cmoves = []
        if "cmove" in kwargs:
            raw_cmoves = [kwargs["cmove"]]
            if "cmove2" in kwargs:
                raw_cmoves.append(kwargs["cmove2"])
        elif "cmoves" in kwargs:
            raw_cmoves = kwargs["cmoves"]
        cmoves = []
        for move in raw_cmoves:
            cmoves.append(Move(move, pvp=pvp))
        self.cmoves = cmoves

        # Set up other attributes
        self.immortal = kwargs.get("immortal", False)
        if "num_shields" in kwargs or "strategy2" in kwargs or "shield" in kwargs:
            self.num_shields = kwargs.get(
                "num_shields", kwargs.get("strategy2", kwargs.get("shield")))


class Party:

    def __init__(self, *args, **kwargs):
        '''
        All Party parameters should be passed via keyword arguments, which can include:
            pokemon, revive (revive)
        '''
        game_master = GameMaster.CurrentInstance

        if len(args) > 0:
            if isinstance(args[0], dict):
                kwargs.update(args[0])

        arg_pkm = kwargs["pokemon"]
        if isinstance(arg_pkm, list):
            kwargs["pokemon"] = [
                Pokemon(pkm) for pkm in arg_pkm]
        elif isinstance(arg_pkm, dict):
            kwargs["pokemon"] = [
                Pokemon(arg_pkm)]
        elif isinstance(arg_pkm, Pokemon):
            kwargs["pokemon"] = [arg_pkm]
        else:
            raise TypeError(
                "Expected list/dict/Pokemon, got {}".format(type(arg_pkm)))


class Player:
    '''
    Interface Player class.
    Convinient for contructing gobattlesim.engine.Player objects.
    '''

    def __init__(self, *args, **kwargs):
        '''
        All Player parameters should be passed via keyword arguments, which can include:
            parties (party), attack_multiplier, clone_multiplier
        '''
        game_master = GameMaster.CurrentInstance

        if len(args) > 0:
            if isinstance(args[0], dict):
                kwargs.update(args[0])

        arg_party = kwargs["parties"]
        if isinstance(arg_party, list):
            kwargs["parties"] = [
                Party(pty) for pty in arg_party]
        elif isinstance(arg_party, dict):
            kwargs["parties"] = [
                Party(arg_party)]
        elif isinstance(arg_party, Party):
            kwargs["parties"] = [arg_party]
        else:
            raise TypeError(
                "Wrong type for parties: {}".format(type(arg_party)))

        self.parties = kwargs["parties"]
        if "attack_multiplier" in kwargs:
            self.attack_multiplier = float(kwargs["attack_multiplier"])
        elif "friend" in kwargs:
            self.attack_multiplier = game_master.search_friend(
                kwargs.get("friend", ""))
        else:
            self.attack_multiplier = 1


class Battle:

    def __init__(self, *args, **kwargs):
        '''
        All Battle parameters should be passed via keyword arguments, which can include:
            players (player), weather, time_limit, numSims
        '''
        game_master = GameMaster.CurrentInstance

        if "players" in kwargs or "player" in kwargs:
            arg_player = kwargs.get("players", kwargs["players"])
            if isinstance(arg_player, list):
                kwargs["players"] = [
                    Player(player) for player in arg_player]
            elif isinstance(arg_player, dict) or isinstance(arg_player, Player):
                kwargs["players"] = [
                    Player(arg_player)]
            else:
                raise TypeError(
                    "Wrong type for players: {}".format(type(arg_player)))
        if "weather" in kwargs:
            if isinstance(kwargs["weather"], str):
                kwargs["weather"] = game_master.search_weather(
                    kwargs["weather"])
        self.numSims = max(1, int(kwargs.get("numSims", 1)))
        for k, v in kwargs.items():
            setattr(self, k, v)


'''
    Useful functions
'''


def quick_raid_battle(attacker,
                      boss,
                      party_size=6,
                      player_multiplier=1,
                      friend=0,
                      strategy="ATTACKER_NO_DODGE",
                      rejoin=0,
                      weather="extreme",
                      time_limit=None,
                      numSims=2000,
                      random_seed=0):
    '''
    Simulate a simple raid battle.
    Returns a dict of average outcome.
    '''

    game_master = GameMaster.CurrentInstance

    pkm_list = []
    if isinstance(attacker, list):
        pkm_list = [Pokemon(atkr) for atkr in attacker]
    else:
        pkm_list = [Pokemon(attacker)]

    d_pokemon = Pokemon(boss)
    d_party = Party()
    d_party.pokemon.append(d_pokemon)
    d_player = Player()
    d_player.parties.append(d_party)
    d_player.team = 0
    d_player.strategy = "DEFENDER"

    players_list = [d_player]
    for pkm in pkm_list:
        a_party = Party()
        a_party.pokemon = [pkm] * party_size
        a_party.revive = rejoin
        a_player = Player()
        a_player.parties = [a_party]
        a_player.team = 1
        a_player.strategy = strategy
        a_player.clone_multiplier = player_multiplier
        a_player.attack_multiplier = game_master.search_friend(friend)
        players_list.append(a_player)

    battle = Battle()
    battle.players = players_list
    battle.weather = game_master.search_weather(weather)
    if time_limit is None:
        battle.time_limit = game_master.search_raid_tier(d_pokemon.tier)[
            'timelimit']
    else:
        battle.time_limit = int(time_limit)

    # TODO


def quick_pvp_battle(pokemon_0,
                     pokemon_1,
                     num_shields=[0, 0]):
    '''
    Simulate a quick PvP battle.
    Returns the battle score of pokemon_0.
    '''

    game_master = GameMaster.CurrentInstance

    p0 = Pokemon(pokemon_0, pvp=True)
    p1 = Pokemon(pokemon_1, pvp=True)

    # TODO
