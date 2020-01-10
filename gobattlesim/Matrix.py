
'''
This module provides methods to create, load, run and save battle matrix.
'''

import argparse
import copy
import csv
import json
import math
import sys

from .GameMaster import GameMaster
from .Pokemon import Pokemon
from .Engine import GBS


def set_stats(pkm, league, game_master=None):
    '''
    set the core stats (pokeType1, pokeType2, attack, defense, maxHP) for Pokemon @param pkm according to @param league

    @param pkm dict-like object containing field "name", or all of the core stats to avoid GameMaster look-up
    @param league one of {"great", "ultra", "master"}, or an int for target cp
    @param game_master GameMaster to search stats data for
    '''
    if game_master is None:
        game_master = GameMaster.CurrentInstance

    CoreStats = ["pokeType1", "pokeType2", "attack", "defense", "maxHP"]
    CoreBaseStats = ["pokeType1", "pokeType2", "baseAtk", "baseDef", "baseStm"]

    if all([stat in pkm for stat in CoreStats]):
        return pkm

    if all([stat in pkm for stat in CoreBaseStats]):
        pass
    else:
        game_master.apply()
        species = game_master.search_pokemon(pkm["name"])
        if species is None:
            return None
        for stat in CoreBaseStats:
            pkm[stat] = species[stat]

    if league == "master":
        cpm = game_master.CPMultipliers[-1]
        atkiv = 15
        defiv = 15
        stmiv = 15
    else:
        if league == "ultra":
            target_cp = 2500
        elif league == "great":
            target_cp = 1500
        elif type(league) is int:
            target_cp = league
        else:
            raise Exception("bad league {}".format(league))
        target_cp = 2500 if league == "ultra" else 1500
        cpm, atkiv, defiv, stmiv = Pokemon.infer_cpm_and_IVs(
            pkm["baseAtk"], pkm["baseDef"], pkm["baseStm"], target_cp)

    pkm["attack"] = (pkm["baseAtk"] + atkiv) * cpm
    pkm["defense"] = (pkm["baseDef"] + defiv) * cpm
    pkm["maxHP"] = math.floor((pkm["baseStm"] + stmiv) * cpm)

    return pkm


def set_moves(pkm, game_master=None):
    '''
    set the moves for Pokemon @param pkm
    '''
    if type(pkm.get("fmove")) is dict and all([type(move) is dict for move in pkm.get("cmoves", [0])]):
        return pkm

    if game_master is None:
        game_master = GameMaster.CurrentInstance

    fmove = game_master.search_pvp_fmove(pkm["fmove"])
    if fmove is None:
        return None
    pkm["fmove"] = fmove

    cmoves = pkm.get("cmoves", [])
    if "cmove" in pkm:
        cmoves.append(pkm["cmove"])
    if "cmove2" in pkm:
        cmoves.append(pkm["cmove2"])
    cmoves = set(cmoves)

    pkm["cmoves"] = []
    for cmove in cmoves:
        cmove = game_master.search_pvp_cmove(cmove)
        if cmove:
            pkm["cmoves"].append(cmove)

    return pkm


def load_pokemon(file, fmt="tsv"):
    '''
    load pokemon list from file @param file.

    @file file object
    @fmt format of Pokemon list file, one of {"tsv", "csv", "json"}
    @return a list of Pokemon with set stats and moves
    '''
    pkm_list = []
    if fmt == "tsv":
        reader = csv.DictReader(file, dialect="excel-tab")
        pkm_list = [pkm for pkm in reader]
    elif fmt == "csv":
        reader = csv.DictReader(file)
        pkm_list = [pkm for pkm in reader]
    elif fmt == "json":
        pkm_list = json.load(file)
    else:
        raise Exception("bad Pokemon list format {}".format(fmt))

    return pkm_list


def save_pokemon(pkm_list, file, fmt="tsv"):
    '''
    save pokemon list to file @param file.

    @param pkm_list a list of Pokemon with set stats and moves
    @file file object
    @fmt format of Pokemon list file, one of {"tsv", "csv", "json"}
    '''
    if not pkm_list:
        return
    if fmt == "tsv":
        fields = pkm_list[0].keys()
        writer = csv.DictWriter(file, fields, dialect="excel-tab")
        writer.writer()
        writer.writerows(pkm_list)
    elif fmt == "csv":
        fields = pkm_list[0].keys()
        writer = csv.DictWriter(file, fields)
        writer.writer()
        writer.writerows(pkm_list)
    elif fmt == "json":
        json.dump(pkm_list, file)
    else:
        raise Exception("bad format {}".format(fmt))


def do_run_matrix(row_pkm, col_pkm=[], shield=0):
    '''
    actually run the Battle Matrix.

    @param row_pkm list of Pokemon objects
    @param col_pkm list of Pokemon objects
    @param shield shield setting
    @return matrix as 2D list
    '''
    if shield > 0:
        print("warning: will use average shield")

    reqInput = {
        "battleMode": "battlematrix",
        "rowPokemon": row_pkm,
        "colPokemon": col_pkm,
        "avergeByShield": shield != 0
    }

    GBS.prepare(reqInput)
    GBS.run()
    return GBS.collect()


def load_and_set_pokemon(filepath, league="master", game_master=None):
    if game_master is None:
        game_master = GameMaster.CurrentInstance

    with open(filepath) as fd:
        pkm_list = load_pokemon(fd, filepath.split('.')[-1])
        pkm_list_filtered = []
        for pkm in pkm_list:
            if not set_stats(pkm, league, game_master):
                continue
            if not set_moves(pkm, game_master):
                continue
            pkm_list_filtered.append(pkm)
    return pkm_list_filtered


def run_matrix(row_pkm, col_pkm=None, shield=-1, league="master", game_master=None):
    '''
    create and run Battle Matrix.

    @param row_pkm path to a Pokemon list file
    @param col_pkm path to a Pokemon list file
    @param shield shield setting
    @return matrix as 2D list
    '''
    if game_master is None:
        game_master = GameMaster.CurrentInstance

    row_pkm = load_and_set_pokemon(row_pkm, league, game_master)
    if col_pkm is not None:
        col_pkm = load_and_set_pokemon(col_pkm, league, game_master)
    else:
        col_pkm = []

    return do_run_matrix(row_pkm, col_pkm, shield)


def save_matrix(matrix, file, fmt="tsv"):
    '''
    save battle matrix @param matrix to file @file with format @param fmt
    '''
    if fmt == "tsv":
        writer = csv.writer(file, dialect="excel-tab")
        writer.writerows(matrix)
    elif fmt == "csv":
        writer = csv.writer(file)
        writer.writerows(matrix)
    elif fmt == "json":
        json.dump(matrix, file)
    else:
        raise Exception("bad format {}".format(fmt))


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("row_pokemon",
                        help="path to a file containing list of Pokemon")
    parser.add_argument("col_pokemon", nargs='?',
                        help="path to a file containing list of Pokemon. If unset, will be set to row Pokemon")
    parser.add_argument("-s", "--shield", type=int, default=0,
                        help="shield strategy setting. -1 for average")
    parser.add_argument("-l", "--league", choices=["great", "ultra", "master"],
                        help="PvP league to decide Pokemon stats. If not set, will use raw Pokemon input")
    parser.add_argument("-c", "--config", type=argparse.FileType('r'), required=True,
                        help="path to game master json")
    parser.add_argument("-p", "--pokemon", action="store_true",
                        help="only show the parsed row Pokemon list")
    parser.add_argument("-f", "--format", choices=["tsv", "csv", "json"], default="tsv",
                        help="matrix output format")
    parser.add_argument("-o", "--out", type=argparse.FileType('w'), default=sys.stdout,
                        help="file to store output matrix")
    args = parser.parse_args()

    GameMaster(args.config).apply()

    row_pkm = load_and_set_pokemon(args.row_pokemon, args.league)

    if args.pokemon:
        save_pokemon(row_pkm, args.out, args.format)
        return 0

    if args.col_pokemon is not None:
        col_pkm = load_and_set_pokemon(args.col_pokemon, args.league)
    else:
        col_pkm = []

    matrix = do_run_matrix(row_pkm, col_pkm, args.shield)

    save_matrix(matrix, args.out, args.fmt)


if __name__ == "__main__":
    main()
