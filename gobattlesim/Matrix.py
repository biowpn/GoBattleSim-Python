
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

try:
    from .Engine import GBS
except Exception as e:
    GBS = e


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
        pkm["cpm"] = game_master.CPMultipliers[-1]
        pkm["atkiv"] = 15
        pkm["defiv"] = 15
        pkm["stmiv"] = 15
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
        pkm["cpm"], pkm["atkiv"], pkm["defiv"], pkm["stmiv"] = Pokemon.infer_cpm_and_IVs(
            pkm["baseAtk"], pkm["baseDef"], pkm["baseStm"], target_cp)

    pkm["attack"] = (pkm["baseAtk"] + pkm["atkiv"]) * pkm["cpm"]
    pkm["defense"] = (pkm["baseDef"] + pkm["defiv"]) * pkm["cpm"]
    pkm["maxHP"] = math.floor((pkm["baseStm"] + pkm["stmiv"]) * pkm["cpm"])

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


def minimize_pokemon(pkm_list):
    CoreFields = ["name", "pokeType1", "pokeType2",
                  "attack", "defense", "maxHP", "fmove", "cmoves"]
    pkm_list_minimized = []
    for pkm in pkm_list:
        pkm_min = {k: pkm[k] for k in CoreFields}
        if "fmove" in pkm_min and "movetype" in pkm_min["fmove"]:
            pkm_min["fmove"].pop("movetype")
        for cmove in pkm_min.get("cmoves", []):
            if "movetype" in cmove:
                cmove.pop("movetype")
        pkm_list_minimized.append(pkm_min)
    return pkm_list_minimized


def save_pokemon(pkm_list, file, fmt="csv"):
    '''
    save pokemon list to file @param file.

    @param pkm_list a list of Pokemon with set stats and moves
    @file file object
    @fmt format of Pokemon list file, one of {"tsv", "csv", "json"}
    '''
    if not pkm_list:
        return
    if fmt == "tsv" or fmt == "csv":
        fields = list(pkm_list[0].keys())
        if "cmoves" in fields:
            fields.remove("cmoves")
            if "cmove" not in fields:
                fields.append("cmove")
            if "cmove2" not in fields and any([pkm.get("cmoves", [])[1:] for pkm in pkm_list]):
                fields.append("cmove2")
        if fmt == "tsv":
            writer = csv.DictWriter(file, fields, dialect="excel-tab")
        else:
            writer = csv.DictWriter(file, fields)
        writer.writeheader()
        for pkm in pkm_list:
            pkm_copy = copy.copy(pkm)
            if "cmoves" in pkm_copy:
                cmoves = pkm_copy.pop("cmoves")
                pkm_copy["cmove"] = cmoves[0].get("name")
                if cmoves[1:]:
                    pkm_copy["cmove2"] = cmoves[1].get("name")
            if type(pkm_copy.get("fmove")) is dict:
                pkm_copy["fmove"] = pkm_copy["fmove"].get("name")
            writer.writerow(pkm_copy)
    elif fmt == "json":
        json.dump(pkm_list, file, indent=4)
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


def save_matrix(matrix, file, fmt="csv"):
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
    parser.add_argument("-c", "--config", required=True,
                        help="path to GBS game master json")
    parser.add_argument("-p", "--pokemon", action="store_true",
                        help="only show the parsed row Pokemon list")
    parser.add_argument("-z", "--minimize", action="store_true",
                        help="for showing the Pokemon list, keeping only the necessary fields")
    parser.add_argument("-i", "--input", action="store_true",
                        help="only show the battle matrix input")
    parser.add_argument("-f", "--format", choices=["tsv", "csv", "json"], default="csv",
                        help="matrix output format")
    parser.add_argument("-o", "--out",
                        help="file to store output matrix")
    args = parser.parse_args()

    if args.out is None:
        args.out = sys.stdout
    else:
        args.out = open(args.out, "w", newline="")

    gm = GameMaster()
    with open(args.config, encoding="utf8") as fd:
        gm.from_json(json.load(fd))
    gm.apply()

    row_pkm = load_and_set_pokemon(args.row_pokemon, args.league)
    if args.minimize:
        row_pkm = minimize_pokemon(row_pkm)

    if args.pokemon:
        save_pokemon(row_pkm, args.out, args.format)
        return 0

    if args.col_pokemon is not None:
        col_pkm = load_and_set_pokemon(args.col_pokemon, args.league)
        if args.minimize:
            col_pkm = minimize_pokemon(col_pkm)
    else:
        col_pkm = []

    reqInput = {
        "battleMode": "battlematrix",
        "rowPokemon": row_pkm,
        "colPokemon": col_pkm,
        "avergeByShield": args.shield != 0
    }

    if args.input:
        json.dump(reqInput, args.out, indent=4)
        return 0

    if type(GBS) is Exception:
        raise GBS

    GBS.config(gm.to_json())
    GBS.prepare(reqInput)
    GBS.run()
    matrix = GBS.collect()

    save_matrix(matrix, args.out, args.format)


if __name__ == "__main__":
    main()
