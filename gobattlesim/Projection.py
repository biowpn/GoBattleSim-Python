
'''
Convert smogon pokemon data to Pokemon Go style data.
'''

import argparse
import json


def toTitleCase(string):
    return ' '.join([w.capitalize() for w in string.split()])


def makeFormeName(org_name, default_forme_name, forme_category_name=None):
    segs = org_name.split('-')
    base_name = segs[0]
    if forme_category_name is not None:
        if len(segs) == 1:
            return "{} ({} {})".format(base_name, default_forme_name, forme_category_name)
        else:
            return "{} ({} {})".format(base_name, segs[1], forme_category_name)
    else:
        if len(segs) == 1:
            return "{} {}".format(base_name, default_forme_name)
        else:
            return "{} {}".format(base_name, segs[1])


def convertPokemonName(org_name):
    '''
    Convert smogon pokemon name to GoBattleSim style pokemon name.

    Return the GBS style pokemon name.
    '''

    segs = org_name.split('-')
    base_name = segs[0]

    if base_name == "Aegislash":
        return makeFormeName(org_name, "Shield", "Forme")

    if base_name == "Arceus":
        return ' '.join(segs)

    if base_name == "Darmanitan":
        return makeFormeName(org_name, "Standard", "Mode")

    if base_name == "Deoxys":
        return makeFormeName(org_name, "Normal", "Forme")

    if base_name == "Giratina":
        return makeFormeName(org_name, "Altered", "Forme")

    if base_name == "Gourgeist":
        return makeFormeName(org_name, "Average", "Size")

    if base_name == "Hoopa":
        return makeFormeName(org_name, "Confined")

    if base_name == "Kyurem":
        return ' '.join(segs[::-1])

    if base_name == "Lycanroc":
        return makeFormeName(org_name, "Midday", "Forme")

    if base_name == "Minior":
        return makeFormeName(org_name, "Core", "Forme")

    if base_name == "Oricorio":
        return makeFormeName(org_name, "Baile", "Style")

    if base_name == "Pumpkaboo":
        return makeFormeName(org_name, "Average", "Size")

    if base_name == "Rotom":
        return ' '.join(segs)

    if base_name == "Shaymin":
        return makeFormeName(org_name, "Land", "Forme")

    if base_name == "Silvally":
        return ' '.join(segs)

    if base_name == "Landorus":
        return makeFormeName(org_name, "Incarnate", "Forme")

    if base_name == "Thundurus":
        return makeFormeName(org_name, "Incarnate", "Forme")

    if base_name == "Tornadus":
        return makeFormeName(org_name, "Incarnate", "Forme")

    if base_name == "Wishiwashi":
        return makeFormeName(org_name, "Solo", "Forme")

    if base_name == "Wormadam":
        return makeFormeName(org_name, "Plant", "Cloak")

    if base_name == "Zygarde":
        if len(segs) == 1:
            return base_name
        else:
            return makeFormeName(org_name, "Base", "Forme")

    if len(segs) == 1:
        return org_name

    if "Mega" in segs:
        if len(segs) >= 3:
            # Charizard-Mega-X
            return "Mega {} {}".format(base_name, ' '.join(segs[2:]))
        else:
            return "Mega {}".format(base_name)

    if "Primal" in segs:
        return "Primal {}".format(base_name)

    if "Alola" in segs:
        if len(segs) >= 3:
            # Raticate-Alola-Totem
            return "Alolan {} {}".format(' '.join(segs[2:]), base_name)
        else:
            return "Alolan {}".format(base_name)

    return org_name


def rd(x):
    '''
    Round a number to the nearest integer.
    '''
    return int(x + 0.5)


def convertStats(p):
    '''
    Convert main series base stats to Pokemon Go base stats.
    '''

    speedMod = (1 + (p['spe'] - 75)/500)
    baseAtk = rd(rd(7/4 * max(p['atk'], p['spa']) +
                    1/4 * min(p['atk'], p['spa'])) * speedMod)
    baseDef = rd(rd(5/4 * max(p['def'], p['spd']) +
                    3/4 * min(p['def'], p['spd'])) * speedMod)
    baseStm = int(1.75 * p['hp'] + 50)

    return {
        'baseAtk': baseAtk,
        'baseDef': baseDef,
        'baseStm': baseStm
    }


def convertMoves(learnset, database):
    '''
    Convert smogon move names to Pokemon Go move names.
    '''

    moves = []
    for name in learnset:
        if name == 'Mud-Slap':
            name = 'Mud Slap'
        if 'Hidden Power' in name:
            continue
        name = name.lower()
        if name in database:
            moves.append(name)

    return moves


def loadMoveNames(gm):
    '''
    return set of move fast and charge names in a 2-tuple
    '''
    fmoves, cmoves = set(), set()
    for move in gm["PvEMoves"]:
        if move["movetype"] == "fast":
            fmoves.add(move["name"])
        else:
            cmoves.add(move["name"])
    for move in gm["PvPMoves"]:
        if move["movetype"] == "fast":
            fmoves.add(move["name"])
        else:
            cmoves.add(move["name"])
    return fmoves, cmoves


def convertPokemon(smogon_pkm, fmoves, cmoves):
    '''
    convert a smogon Pokemon entry to PoGo-like Pokemon
    '''

    pkm_list = []

    for pkm in smogon_pkm:
        pkmNew = {}

        fullName = convertPokemonName(pkm['name'])

        if fullName.startswith("Arceus-"):
            continue
        if fullName.startswith("Silvally-"):
            continue

        pkmNew['name'] = fullName.lower()
        pkmNew['label'] = fullName
        if "oob" in pkm:
            if pkm["oob"] is not None and "dex_number" in pkm["oob"]:
                pkmNew['dex'] = pkm["oob"]["dex_number"]

        baseStats = convertStats(pkm)
        pkmNew['baseAtk'] = baseStats['baseAtk']
        pkmNew['baseDef'] = baseStats['baseDef']
        pkmNew['baseStm'] = baseStats['baseStm']

        pkm['types'].append('None')
        pkmNew['pokeType1'] = pkm['types'][0].lower()
        pkmNew['pokeType2'] = pkm['types'][1].lower()

        pkmNew['fastMoves'] = convertMoves(pkm['learnset'], fmoves)
        pkmNew['chargedMoves'] = convertMoves(pkm['learnset'], cmoves)

        pkm_list.append(pkmNew)

    return pkm_list


def leftJoin(left, right, on="name"):
    for x in left:
        for y in right:
            if x[on] == y[on]:
                for a in y:
                    x[a] = y[a]
    return left


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("smogon_file",
                        help="path to smogon pokemon data file in json")
    parser.add_argument("-c", "--config", default="./GBS.json",
                        help="path to GBS setting")
    parser.add_argument("--join",
                        help="path to addtional settings to left join")
    parser.add_argument("-z", "--minimize", action="store_true",
                        help="minimize json output")
    parser.add_argument("-o", "--out", default="out.json",
                        help="output file path")
    args = parser.parse_args()

    with open(args.smogon_file) as F:
        smogon_pkm = json.load(F)

    with open(args.config) as F:
        GBSData = json.load(F)
    fmoves, cmoves = loadMoveNames(GBSData)

    pkm_list = convertPokemon(smogon_pkm, fmoves, cmoves)

    if args.join:
        with open(args.join) as F:
            pkm_icon_map = json.load(F)
            leftJoin(pkm_list, pkm_icon_map)

    with open(args.out, 'w') as F:
        if args.minimize:
            json.dump(pkm_list, F)
        else:
            json.dump(pkm_list, F, indent=4)


if __name__ == "__main__":
    main()
