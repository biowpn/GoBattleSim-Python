
import argparse
import copy
import itertools

from .GameMaster import PoketypeList, InversedPoketypeList, GameMaster


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
    @param pkm is needed if the entity is Move.
    Return a callback predicate that accepts one parameter (the entity to be examined).
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
            return lambda x: True

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
            return entity.get('rarity') == 'POKEMON_RARITY_LEGENDARY'

    # Match by rarity Mythical. For Pokemon
    elif query_str == "mythic" or query_str == "mythical":
        def predicate(entity):
            return entity.get('rarity') == 'POKEMON_RARITY_MYTHIC'

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
    Create a PokeQuery from string {query_str}. Supports logical operators and parenthesis.
    The {pkm} is needed if the entity if moves.
    Return a callback predicate that accepts one parameter (the entity to be examined).
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

    return vstack.pop()


def batch_pokemon(self, pkm_dict):
    '''
    Return the product by all possible values of all the wild card queries, if any.

    The attribute fields that can contain wild card query:
        name
        fmove
        cmove
        cmove2
    [cmove2] is optional, while the others are mandoratory.
    '''
    results = []
    species_matches = []
    fmove_matches = []
    cmove_matches = []
    cmove2_matches = []
    has_cmove2 = "cmove2" in pkm_dict
    pkm_dict['fmove'] = pkm_dict.get("fmove", "*")
    pkm_dict['cmove'] = pkm_dict.get("cmove", "*")

    # Try for direct match first. Only if no direct match will the program try for query match.
    try:
        species_matches = [self.search_pokemon(pkm_dict['name'])]
    except:
        species_matches = self.search_pokemon(
            PokeQuery(pkm_dict['name']), True)
    try:
        fmove_matches = [self.search_fmove(pkm_dict['fmove'])]
    except:
        pass
    try:
        cmove_matches = [self.search_cmove(pkm_dict['cmove'])]
    except:
        pass
    if has_cmove2:
        try:
            cmove2_matches = [self.search_cmove(pkm_dict['cmove2'])]
        except:
            pass

    for species in species_matches:
        if fmove_matches:
            cur_fmove_matches = fmove_matches
        else:
            cur_fmove_matches = self.search_fmove(
                PokeQuery(pkm_dict['fmove'], species, "fast"), True)
        if cmove_matches:
            cur_cmove_matches = cmove_matches
        else:
            cur_cmove_matches = self.search_cmove(
                PokeQuery(pkm_dict['cmove'], species, "charged"), True)
        if has_cmove2:
            if cmove2_matches:
                cur_cmove2_matches = cmove2_matches
            else:
                cur_cmove2_matches = self.search_cmove(
                    PokeQuery(pkm_dict['cmove2'], species, "charged"), True)
            for fmove, cmove, cmove2 in itertools.product(cur_fmove_matches, cur_cmove_matches, cur_cmove2_matches):
                cur_pokemon = copy.copy(pkm_dict)
                cur_pokemon['name'] = species['name']
                cur_pokemon['fmove'] = fmove['name']
                cur_pokemon['cmove'] = cmove['name']
                cur_pokemon['cmove2'] = cmove2['name']
                if cur_pokemon['cmove2'] != cur_pokemon['cmove']:
                    results.append(cur_pokemon)
        else:
            for fmove, cmove in itertools.product(cur_fmove_matches, cur_cmove_matches):
                cur_pokemon = copy.copy(pkm_dict)
                cur_pokemon['name'] = species['name']
                cur_pokemon['fmove'] = fmove['name']
                cur_pokemon['cmove'] = cmove['name']
                results.append(cur_pokemon)

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", type=str,
                        help="PokeQuery string")
    parser.add_argument("game_master", type=str,
                        help="path to official game master json")
    parser.add_argument("-c", "--count", action="store_true",
                        help="only show the number of matches")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print out each matched item in details")
    args = parser.parse_args()

    gm = GameMaster(args.game_master)
    pred = PokeQuery(args.query)

    total = 0
    for pkm in gm.Pokemon:
        if pred(pkm):
            if args.count:
                total += 1
            elif args.verbose:
                print(pkm)
            else:
                print(pkm["name"])
    if args.count:
        print(total)


if __name__ == "__main__":
    main()
