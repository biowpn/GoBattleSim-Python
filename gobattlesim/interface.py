
'''
The interface module.

This module provides game master file parsing, setting game parameters,
and more convenient battle objects initialization (built on top of engine.py).

'''

import json
import re
import copy
import itertools

from .engine import *
from .GameMaster import GameMaster
from .PokeQuery import PokeQuery


'''
    Inferface Classes for engine.
'''


ROLE_PVE_ATTACKER = "ae"
ROLE_PVP_ATTACKER = "ap"
ROLE_GYM_DEFENDER = "gd"
ROLE_RAID_BOSS = "rb"


class IMove(Move):
    '''
    Interface Move class.
    Convinient for contructing gobattlesim.engine.Move objects.
    '''

    def __init__(self, *args, game_master=None, pvp=False, **kwargs):
        '''
        The named move paramters can be passed via keyword arguments,
        or via a str or dict as the first positional argument:

            Move("Counter"), Move({"name": "Counter"}), Move(name="Counter")

        give the same thing.
        '''
        game_master = game_master or GameMaster.CurrentInstance
        if len(args) > 0:
            if isinstance(args[0], str):
                kwargs["name"] = args[0]
                args = args[1:]
            elif isinstance(args[0], dict):
                kwargs.update(args[0])
                args = args[1:]
            elif isinstance(args[0], Move):
                temp = Move.cast(args[0]._addr)
                self.__dict__.update(temp.__dict__)
                return
        if "name" in kwargs:
            if pvp:
                kwargs.update(game_master.search_pvp_move(kwargs["name"]))
            else:
                kwargs.update(game_master.search_pve_move(kwargs["name"]))
        core_arg_names = ["pokeType", "power", "energy", "duration", "dws"]
        core_arg_values = [args[i] if len(args) > i else kwargs.get(
            name, 0) for i, name in enumerate(core_arg_names)]
        super().__init__(*core_arg_values)
        if kwargs.get("effect"):
            self.effect = kwargs["effect"]


class IPokemon(PvPPokemon):
    '''
    Interface Pokemon class.
    Convinient for contructing gobattlesim.engine.Pokemon(/PvPPokemon) objects.
    '''

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
            if IPokemon.calc_cp(bAtk, bDef, bStm, CPMultipliers[min_cpm_i], 15, 15, 15) >= target_cp:
                break
            min_cpm_i += 1
        while max_cpm_i > min_cpm_i:
            if IPokemon.calc_cp(bAtk, bDef, bStm, CPMultipliers[max_cpm_i], 0, 0, 0) <= target_cp:
                break
            max_cpm_i -= 1
        for cpm in CPMultipliers[min_cpm_i: max_cpm_i + 1]:
            for stmiv in range(16):
                for defiv in range(16):
                    for atkiv in range(16):
                        cp = IPokemon.calc_cp(
                            bAtk, bDef, bStm, cpm, atkiv, defiv, stmiv)
                        if cp == target_cp:
                            return (cpm, atkiv, defiv, stmiv)
                        elif closest_cp < cp and cp < target_cp:
                            closest_cp = cp
                            closest = (cpm, atkiv, defiv, stmiv)
        return closest

    def __init__(self, *args, game_master=None, **kwargs):
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
        game_master = game_master or GameMaster.CurrentInstance
        if len(args) > 0:
            if isinstance(args[0], str):
                kwargs["name"] = args[0]
                args = args[1:]
            elif isinstance(args[0], dict):
                kwargs.update(args[0])
                args = args[1:]
            elif isinstance(args[0], Pokemon):
                temp = Pokemon.cast(args[0]._addr)
                self.__dict__.update(temp.__dict__)
                return
        if "name" in kwargs:
            kwargs.update(game_master.search_pokemon(kwargs["name"]))

        role = kwargs.get("role", ROLE_PVE_ATTACKER)
        self.__dict__["tier"] = None
        if role == ROLE_RAID_BOSS or "tier" in kwargs:
            self.__dict__["tier"] = str(kwargs["tier"])
            tier_setting = game_master.search_raid_tier(self.__dict__["tier"])
            kwargs["attack"] = (kwargs["baseAtk"] + 15) * tier_setting["cpm"]
            kwargs["defense"] = (kwargs["baseDef"] + 15) * tier_setting["cpm"]
            kwargs["max_hp"] = tier_setting["maxHP"]
        elif len(args) < 5:
            if "cp" in kwargs:
                cp = kwargs["cp"]
                if not isinstance(cp, int):
                    raise TypeError("Expected int, got {}".format(type(cp)))
                cpm, atkiv, defiv, stmiv = IPokemon.infer_level_and_IVs(
                    kwargs["baseAtk"], kwargs["baseDef"], kwargs["baseStm"], cp)
            else:
                cpm = game_master.search_cpm(kwargs.get("level", 40))
                atkiv = int(kwargs.get("atkiv", 15))
                defiv = int(kwargs.get("defiv", 15))
                stmiv = int(kwargs.get("stmiv", 15))
            kwargs["attack"] = (kwargs["baseAtk"] + atkiv) * cpm
            kwargs["defense"] = (kwargs["baseDef"] + defiv) * cpm
            kwargs["max_hp"] = int((kwargs["baseStm"] + stmiv) * cpm)
            if role == ROLE_GYM_DEFENDER:
                kwargs["max_hp"] *= 2

        core_arg_names = ["pokeType1", "pokeType2",
                          "attack", "defense", "max_hp"]
        core_arg_values = [args[i] if len(args) > i else kwargs.get(
            name, 0) for i, name in enumerate(core_arg_names)]
        super().__init__(*core_arg_values)

        # Set up moves
        pvp = (role == ROLE_PVP_ATTACKER) or kwargs.get("pvp", False)
        if "fmove" in kwargs:
            self.fmove = IMove(kwargs["fmove"], pvp=pvp,
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
            cmoves.append(IMove(move, pvp=pvp, game_master=game_master))
        self.cmoves = cmoves

        # Set up other attributes
        self.immortal = kwargs.get("immortal", False)
        if "num_shields" in kwargs or "strategy2" in kwargs or "shield" in kwargs:
            self.num_shields = kwargs.get(
                "num_shields", kwargs.get("strategy2", kwargs.get("shield")))


class IParty(Party):
    '''
    Interface Party class.
    Convinient for contructing gobattlesim.engine.Party objects.
    '''

    def __init__(self, *args, game_master=None, **kwargs):
        '''
        All Party parameters should be passed via keyword arguments, which can include:
            pokemon, revive (revive_policy)
        '''
        game_master = game_master or GameMaster.CurrentInstance

        if len(args) > 0:
            if isinstance(args[0], dict):
                kwargs.update(args[0])
            elif isinstance(args[0], Party):
                temp = Party.cast(args[0]._addr)
                self.__dict__.update(temp.__dict__)
                return
        super().__init__()

        if "pokemon" in kwargs:
            arg_pkm = kwargs["pokemon"]
            if isinstance(arg_pkm, list):
                kwargs["pokemon"] = [
                    IPokemon(pkm, game_master=game_master) for pkm in arg_pkm]
            elif isinstance(arg_pkm, dict):
                kwargs["pokemon"] = [
                    IPokemon(arg_pkm, game_master=game_master)]
            elif isinstance(arg_pkm, Pokemon):
                kwargs["pokemon"] = [arg_pkm]
            else:
                raise TypeError(
                    "Expected list/dict/Pokemon, got {}".format(type(arg_pkm)))

        revive_policy = kwargs.get("revive_policy", kwargs.get("revive", 0))
        if isinstance(revive_policy, int) or isinstance(revive_policy, str):
            kwargs["revive_policy"] = int(kwargs["revive_policy"])
        elif isinstance(revive_policy, bool):
            kwargs["revive_policy"] = -1 if kwargs["revive_policy"] else 0
        else:
            TypeError(
                "Expected int/str/bool, got {}".format(type(kwargs["revive_policy"])))
        for k, v in kwargs.items():
            setattr(self, k, v)


class IPlayer(Player):
    '''
    Interface Player class.
    Convinient for contructing gobattlesim.engine.Player objects.
    '''

    def __init__(self, *args, game_master=None, **kwargs):
        '''
        All Player parameters should be passed via keyword arguments, which can include:
            parties (party), attack_multiplier, clone_multiplier
        '''
        game_master = game_master or GameMaster.CurrentInstance

        if len(args) > 0:
            if isinstance(args[0], dict):
                kwargs.update(args[0])
            elif isinstance(args[0], Player):
                temp = Player.cast(args[0]._addr)
                self.__dict__.update(temp.__dict__)
                return
        super().__init__()

        if "parties" in kwargs or "party" in kwargs:
            arg_party = kwargs.get("parties", kwargs["party"])
            if isinstance(arg_party, list):
                kwargs["parties"] = [
                    IParty(pty, game_master=game_master) for pty in arg_party]
            elif isinstance(arg_party, dict):
                kwargs["parties"] = [
                    IParty(arg_party, game_master=game_master)]
            elif isinstance(arg_party, Party):
                kwargs["parties"] = [arg_party]
            else:
                raise TypeError(
                    "Wrong type for parties: {}".format(type(arg_party)))
        if "attack_multiplier" in kwargs or "friend" in kwargs:
            kwargs["attack_multiplier"] = kwargs.get(
                "attack_multiplier", 1) * game_master.search_friend(kwargs.get("friend", ""))
        for k, v in kwargs.items():
            setattr(self, k, v)


class IBattle(Battle):
    '''
    Interface Battle class.
    Convinient for contructing gobattlesim.engine.Battle objects.
    '''

    def __init__(self, *args, game_master=None, **kwargs):
        '''
        All Battle parameters should be passed via keyword arguments, which can include:
            players (player), weather, time_limit, num_sims
        '''
        game_master = game_master or GameMaster.CurrentInstance
        super().__init__()

        if "players" in kwargs or "player" in kwargs:
            arg_player = kwargs.get("players", kwargs["players"])
            if isinstance(arg_player, list):
                kwargs["players"] = [
                    IPlayer(player, game_master=game_master) for player in arg_player]
            elif isinstance(arg_player, dict) or isinstance(arg_player, Player):
                kwargs["players"] = [
                    IPlayer(arg_player, game_master=game_master)]
            else:
                raise TypeError(
                    "Wrong type for players: {}".format(type(arg_player)))
        if "weather" in kwargs:
            if isinstance(kwargs["weather"], str):
                kwargs["weather"] = game_master.search_weather(
                    kwargs["weather"])
        self.__dict__['num_sims'] = max(1, int(kwargs.get("num_sims", 1)))
        for k, v in kwargs.items():
            setattr(self, k, v)

    def run(self):
        '''
        Run the battle for {num_sims} times and returns the average outcome.
        '''

        # Run many simulations
        sum_duration = sum_wins = sum_tdo_percent = sum_deaths = 0
        for _ in range(self.num_sims):
            self.init()
            self.start()
            battle_outcome = self.get_outcome(1)
            sum_duration += battle_outcome.duration
            sum_wins += 1 if battle_outcome.win else 0
            sum_tdo_percent += battle_outcome.tdo_percent
            sum_deaths += battle_outcome.num_deaths
        return {
            "win": sum_wins / self.num_sims,
            "duration": sum_duration / self.num_sims,
            "tdo_percent": sum_tdo_percent / self.num_sims,
            "num_deaths": sum_deaths / self.num_sims
        }


'''
    Useful functions
'''


def quick_raid_battle(attacker,
                      boss,
                      party_size=6,
                      player_multiplier=1,
                      friend=0,
                      strategy=STRATEGY_ATTACKER_NO_DODGE,
                      rejoin=0,
                      weather="extreme",
                      time_limit=None,
                      num_sims=2000,
                      random_seed=0,
                      game_master=None):
    '''
    Simulate a simple raid battle.
    Returns a dict of average outcome.
    '''

    game_master = game_master or GameMaster.CurrentInstance
    set_random_seed(random_seed)

    pkm_list = []
    if isinstance(attacker, list):
        pkm_list = [IPokemon(atkr, game_master=game_master)
                    for atkr in attacker]
    else:
        pkm_list = [IPokemon(attacker, game_master=game_master)]

    d_pokemon = IPokemon(boss, game_master=game_master)
    d_party = Party()
    d_party.add(d_pokemon)
    d_player = Player()
    d_player.add(d_party)
    d_player.team = 0
    d_player.strategy = STRATEGY_DEFENDER

    players_list = [d_player]
    for pkm in pkm_list:
        a_party = Party()
        a_party.pokemon = [pkm] * party_size
        a_party.revive_policy = rejoin
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

    sum_duration = sum_wins = sum_tdo_percent = sum_deaths = 0
    for i in range(num_sims):
        battle.init()
        battle.start()
        battle_outcome = battle.get_outcome(1)
        sum_duration += battle_outcome.duration
        sum_wins += 1 if battle_outcome.win else 0
        sum_tdo_percent += battle_outcome.tdo_percent
        sum_deaths += battle_outcome.num_deaths
    return {
        "win": sum_wins / num_sims,
        "duration": sum_duration / num_sims,
        "tdo_percent": sum_tdo_percent / num_sims,
        "num_deaths": sum_deaths / num_sims
    }


def quick_pvp_battle(pokemon_0,
                     pokemon_1,
                     num_shields=[0, 0],
                     game_master=None):
    '''
    Simulate a quick PvP battle.
    Returns the battle score of pokemon_0.
    '''

    game_master = game_master or GameMaster.CurrentInstance

    p0 = IPokemon(pokemon_0, pvp=True, game_master=game_master)
    p1 = IPokemon(pokemon_1, pvp=True, game_master=game_master)

    battle = SimplePvPBattle(p0, p1)
    battle.set_num_shields_max(num_shields[0], num_shields[1])
    battle.init()
    battle.start()
    tdo_percent = battle.get_outcome().tdo_percent

    return min(tdo_percent[0], 1) - min(tdo_percent[1], 1)
