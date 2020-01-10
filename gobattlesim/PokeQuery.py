
'''
This module provides PokeQuery, a scheme to search Pokemon/Move.
'''

import argparse
import copy
import csv
import itertools
import json
import sys

from .GameMaster import PoketypeList, GameMaster


POKE_QUERY_LOGICAL_OPERATORS = {
    ':': 0,
    ',': 0,
    ';': 0,
    '&': 1,
    '|': 1,
    '!': 2
}


def BasicPokeQuery(query_str, pkm=None, movetype="fast"):
    '''
    Create a basic PokeQuery from string @param query_str.

    @param pkm subject Pokemon. This parameter is needed if the entity to search is Move
    @param movetype used with searching Move
    @return a predicate/callback that accepts one parameter (the entity to be examined)
    '''

    query_str = str(query_str).lower().strip(" *")

    # Default predicate for empty query
    if query_str == "":
        if pkm is not None:
            pd1 = BasicPokeQuery("current", pkm, movetype)
            pd2 = BasicPokeQuery("legacy", pkm, movetype)
            pd3 = BasicPokeQuery("exclusive", pkm, movetype)
            return lambda x: (pd1(x) or pd2(x) or pd3(x))
        else:
            return lambda x: False

    # Match by dex. For Pokemon
    elif query_str.isdigit():
        dex = int(query_str)

        def predicate(entity):
            return entity.get('dex') == dex
    elif query_str[:3] == 'dex':
        num_part = query_str[3:]
        if '-' in num_part:
            min_dex, max_dex = [int(v.strip())
                                for v in num_part.split('-')][:2]
        else:
            min_dex = max_dex = int(num_part)

        def predicate(entity):
            return min_dex <= entity.get('dex') <= max_dex

    # Match by type. For Pokemon, Move
    elif query_str in PoketypeList or query_str == 'none':
        def predicate(entity):
            return query_str in [entity.get('pokeType'), entity.get('pokeType1'), entity.get('pokeType2')]

    # Match by rarity Legendary. For Pokemon
    elif query_str == "legendary":
        def predicate(entity):
            return entity.get("rarity") == "POKEMON_RARITY_LEGENDARY"

    # Match by rarity Mythical. For Pokemon
    elif query_str == "mythic" or query_str == "mythical":
        def predicate(entity):
            return entity.get("rarity") == "POKEMON_RARITY_MYTHIC"

    # Match by current move availability
    elif query_str == "current":
        movepool = pkm.get(movetype + "Moves", [])

        def predicate(entity):
            return entity['name'] in movepool
    elif query_str == "legacy":
        movepool = pkm.get(movetype + "Moves_legacy", [])

        def predicate(entity):
            return entity['name'] in movepool
    elif query_str == "exclusive":
        movepool = pkm.get(movetype + "Moves_exclusive", [])

        def predicate(entity):
            return entity['name'] in movepool

    # Default: Match by name. For Pokemon, Move
    else:
        def predicate(entity):
            return query_str in entity['name']

    return predicate


def PokeQuery(query_str, pkm=None, movetype="fast"):
    '''
    Create a PokeQuery from string @param query_str.
    Supports logical operators and parenthesis.

    @param pkm subject Pokemon. This parameter is needed if the entity to search is Move.
    @param movetype used with searching Move
    @return a callback/predicate that accepts one parameter (the entity to be examined).
    '''

    global POKE_QUERY_LOGICAL_OPERATORS
    OPS = POKE_QUERY_LOGICAL_OPERATORS

    # Tokenize the input query string
    tokens = []
    tk = ""
    for c in query_str:
        if c in OPS or c in ['(', ')']:
            tk = tk.strip()
            if tk:
                tokens.append(tk)
            tokens.append(c)
            tk = ""
        else:
            tk += c
    tk = tk.strip()
    if tk:
        tokens.append(tk)

    vstack = []
    opstack = []

    def default_pred(x):
        return False

    def eval_simple(op, vstack):
        if OPS[op] == 0:
            if len(vstack) < 2:
                raise Exception(f"missing operand for operator {op}")
            rhs = vstack.pop()
            lhs = vstack.pop()
            vstack.append(lambda x: lhs(x) or rhs(x))
        elif OPS[op] == 1:
            if len(vstack) < 2:
                raise Exception(f"missing operand for operator {op}")
            rhs = vstack.pop()
            lhs = vstack.pop()
            vstack.append(lambda x: lhs(x) and rhs(x))
        elif OPS[op] == 2:
            if len(vstack) < 1:
                raise Exception(f"missing operand for operator {op}")
            rhs = vstack.pop()
            vstack.append(lambda x: not rhs(x))

    for tk in tokens:
        if tk in OPS:
            while opstack and opstack[-1] != '(' and OPS[opstack[-1]] > OPS[tk]:
                eval_simple(opstack.pop(), vstack)
            opstack.append(tk)
        elif tk == '(':
            opstack.append(tk)
        elif tk == ')':
            while opstack:
                op = opstack.pop()
                if op == '(':
                    break
                eval_simple(op, vstack)
        else:
            vstack.append(BasicPokeQuery(tk, pkm=pkm, movetype=movetype))
    while opstack:
        eval_simple(opstack.pop(), vstack)

    return vstack.pop() if vstack else default_pred


def get_unique_pokemon(pkm_list):
    '''
    remove duplicates where {cmove, cmove2} are the same set.
    '''
    unique_pkm_list = []
    for pkm in pkm_list:
        unique = True
        for pkm2 in unique_pkm_list:
            if set([pkm['cmove'], pkm.get('cmove2')]) == set([pkm2['cmove'], pkm2.get('cmove2')]):
                unique = any([v != pkm2.get(k) for k, v in pkm.items()
                              if k != 'cmove' and k != 'cmove2'])
        if unique:
            unique_pkm_list.append(pkm)
    return unique_pkm_list


def batch_pokemon(pkm_qry, game_master: GameMaster):
    '''
    Return a list of Pokemon-Move combinations that match the query input @param pkm_qry in GameMaster @param game_master.

    @param pkm_qry is a dict, which may have the following fields:

        name
        fmove
        cmove
        [optional] cmove2

    All fields must be str, and can be PokeQuery.
    '''
    matches = []

    species_qry = pkm_qry["name"]
    fmove_qry = pkm_qry["fmove"]
    cmove_qry = pkm_qry["cmove"]
    cmove2_qry = pkm_qry.get("cmove2", "")

    species_matches = []
    fmove_matches = []
    cmove_matches = []
    cmove2_matches = []

    species_direct_match = game_master.search_pokemon(species_qry)
    if species_direct_match:
        species_matches.append(species_direct_match)
    else:
        species_matches = game_master.search_pokemon(
            PokeQuery(species_qry), True)

    for species in species_matches:
        cur_matches = []

        fmove_direct_match = game_master.search_pve_fmove(fmove_qry)
        if fmove_direct_match:
            fmove_matches.append(fmove_direct_match)
        else:
            fmove_matches = game_master.search_pve_fmove(
                PokeQuery(fmove_qry, species, "fast"), True)

        cmove_direct_match = game_master.search_pve_cmove(cmove_qry)
        if cmove_direct_match:
            cmove_matches.append(cmove_direct_match)
        else:
            cmove_matches = game_master.search_pve_cmove(
                PokeQuery(cmove_qry, species, "charged"), True)

        cmove2_direct_match = game_master.search_pve_cmove(cmove2_qry)
        if cmove2_direct_match:
            cmove2_matches.append(cmove2_direct_match)
        else:
            cmove2_matches = game_master.search_pve_cmove(
                PokeQuery(cmove2_qry, species, "charged"), True)

        for fmove, cmove in itertools.product(fmove_matches, cmove_matches):
            pkm = copy.copy(pkm_qry)
            for k in species:
                pkm[k] = species[k]
            pkm["fmove"] = fmove["name"]
            pkm["cmove"] = cmove["name"]
            if cmove2_matches:
                for cmove2 in cmove2_matches:
                    if cmove2["name"] != cmove["name"]:
                        pkm = copy.copy(pkm)
                        pkm["cmove2"] = cmove2["name"]
                        cur_matches.append(pkm)
            else:
                cur_matches.append(pkm)

        if cmove2_matches:
            cur_matches = get_unique_pokemon(cur_matches)

        matches.extend(cur_matches)

    return matches


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", type=str, nargs='+',
                        help="species_query [, fmove_query] [, cmove_query] [, cmove2_query]")
    parser.add_argument("-c", "--config", required=True,
                        help="path to GBS game master json")
    parser.add_argument("-n", "--number", action="store_true",
                        help="only show the number of matches")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print out each match in details")
    parser.add_argument("-f", "--format", choices=["tsv", "csv", "json"], default="csv",
                        help="format of output")
    parser.add_argument("-o", "--out",
                        help="file to store output")
    args = parser.parse_args()

    if args.out is None:
        args.out = sys.stdout
    else:
        args.out = open(args.out, mode="w", newline="")

    gm = GameMaster()
    with open(args.config, encoding="utf8") as fd:
        gm.from_json(json.load(fd))
    gm.apply()

    fields = []
    matches = []

    if len(args.query) == 1:
        fields = ["name"]
        matches = list(filter(PokeQuery(args.query[0]), gm.Pokemon))
    elif len(args.query) >= 3:
        fields = ["name", "fmove", "cmove"]
        pkm_qry = {
            "name": args.query[0],
            "fmove": args.query[1],
            "cmove": args.query[2]
        }
        if len(args.query) >= 4:
            fields.append("cmove2")
            pkm_qry["cmove2"] = args.query[3]
        matches = batch_pokemon(pkm_qry, gm)
    else:
        print("cannot query fast move but not primary charged move")
        return -2

    number = len(matches)
    if args.number:
        print(number)
        return 0
    if number == 0:
        return 0

    if args.verbose:
        for attr in matches[0].keys():
            if attr not in fields:
                fields.append(attr)
    else:
        matches = [{k: pkm[k] for k in fields} for pkm in matches]

    if args.format == "tsv":
        writer = csv.DictWriter(args.out, fields, dialect="excel-tab")
        writer.writeheader()
        writer.writerows(matches)
    elif args.format == "csv":
        writer = csv.DictWriter(args.out, fields)
        writer.writeheader()
        writer.writerows(matches)
    elif args.format == "json":
        json.dump(matches, args.out, indent=4)

    return 0


if __name__ == "__main__":
    exit(main())
