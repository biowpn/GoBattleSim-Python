
'''
Convert smogon pokemon data to Pokemon Go style data.
'''

import argparse
import json


def toTitleCase(string):
    return ' '.join([w.capitalize() for w in string.split()])


def makeFormeName(base_name, default_form_name, form_type_name):
    form_name = default_form_name
    if '-' in base_name:
        base_name, *form_name = base_name.split('-')
        form_name = '-'.join(form_name)
    if form_name and form_type_name:
        return "{} ({} {})".format(base_name, form_name, form_type_name)
    elif form_name:
        return "{} {}".format(base_name, form_name)
    else:
        return base_name


def convertPokemonName(base_name, suffix):
    '''
    Convert smogon pokemon name to GoBattleSim style pokemon name.

    Return the GBS style pokemon name.
    '''

    if suffix == '':
        if base_name.endswith("-Alola"):
            return "Alolan {}".format(base_name[:-6])

        elif base_name.startswith("Aegislash"):
            return makeFormeName(base_name, "Shield", "Forme")

        elif base_name.startswith("Darmanitan"):
            return makeFormeName(base_name, "Standard", "Mode")

        elif base_name.startswith("Deoxys"):
            return makeFormeName(base_name, "Normal", "Forme")

        elif base_name.startswith("Giratina"):
            return makeFormeName(base_name, "Altered", "Forme")

        elif base_name.startswith("Gourgeist"):
            return makeFormeName(base_name, "Average", "Size")

        elif base_name.startswith("Hoopa"):
            return makeFormeName(base_name, "Confined", None)

        elif base_name.startswith("Kyurem"):
            return makeFormeName(base_name, "", None)

        elif base_name.startswith("Lycanroc"):
            return makeFormeName(base_name, "Midday", "Forme")

        elif base_name.startswith("Minior"):
            return makeFormeName(base_name, "Core", "Forme")

        elif base_name.startswith("Oricorio"):
            return makeFormeName(base_name, "Baile", "Style")

        elif base_name.startswith("Pumpkaboo"):
            return makeFormeName(base_name, "Average", "Size")

        elif base_name.startswith("Rotom"):
            return makeFormeName(base_name, "", None)

        elif base_name.startswith("Shaymin"):
            return makeFormeName(base_name, "Land", "Forme")

        elif base_name.startswith("Thundurus") or base_name.startswith("Tornadus") or base_name.startswith("Landorus"):
            return makeFormeName(base_name, "Incarnate", "Forme")

        elif base_name.startswith("Wishiwashi"):
            return makeFormeName(base_name, "Solo", "Forme")

        elif base_name.startswith("Wormadam"):
            return makeFormeName(base_name, "Plant", "Cloak")

        elif base_name.startswith("Zygarde"):
            return makeFormeName(base_name, "", "Forme")

        else:
            return base_name

    elif suffix.startswith("Mega"):
        if '-' in suffix:
            return "Mega {} {}".format(base_name, suffix.split('-')[-1])
        else:
            return "Mega {}".format(base_name)

    elif suffix == "Primal":
        return "Primal {}".format(base_name)

    else:
        if base_name == "Darmanitan":
            return makeFormeName(base_name, "Standard", "Mode")
        else:
            return "{} ({} Forme)".format(base_name, suffix)


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
        for pkmform in pkm['alts']:
            pkmNew = {}

            fullName = convertPokemonName(pkm['name'], pkmform['suffix'])

            if fullName.startswith("Arceus-"):
                continue
            if fullName.startswith("Silvally-"):
                continue

            pkmNew['name'] = fullName.lower()
            pkmNew['label'] = toTitleCase(fullName)

            baseStats = convertStats(pkmform)
            pkmNew['baseAtk'] = baseStats['baseAtk']
            pkmNew['baseDef'] = baseStats['baseDef']
            pkmNew['baseStm'] = baseStats['baseStm']

            pkmform['types'].append('None')
            pkmNew['pokeType1'] = pkmform['types'][0].lower()
            pkmNew['pokeType2'] = pkmform['types'][1].lower()

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
