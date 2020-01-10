
'''
This file is for a helper for GoBattleSim-Host.
Handles client request and return with output.
'''


def do_BattleMatrix(self, req_input):
    enum_shields = req_input.get('enumShields', False)

    row_pkm = []
    for pkm in req_input['rowPokemon']:
        if "cmove2" in pkm and str(pkm["cmove2"]).strip() == '':
            del pkm["cmove2"]
        row_pkm.extend(GameMaster.CurrentInstance.batch_pokemon(pkm))
    col_pkm = []
    for pkm in req_input['colPokemon']:
        if "cmove2" in pkm and str(pkm["cmove2"]).strip() == '':
            del pkm["cmove2"]
        col_pkm.extend(GameMaster.CurrentInstance.batch_pokemon(pkm))

    row_pkm = get_unique_pokemon(row_pkm)
    col_pkm = get_unique_pokemon(col_pkm)

    row_size = len(row_pkm)
    col_size = len(col_pkm) or row_size
    size_limit = 1000000
    if row_size * col_size > size_limit:
        raise Exception(
            "Request rejected due to matrix size {}*{} exceeding limit {}".format(row_size, col_size, size_limit))
    elif row_size == 0:
        raise Exception("Row pool is empty")
    elif col_size == 0:
        raise Exception("Col pool is empty")
    else:
        print("Request Matrix size: {}*{}".format(row_size, col_size))

    row_ipkm = [IPokemon(**pkm, pvp=True) for pkm in row_pkm]
    col_ipkm = [IPokemon(**pkm, pvp=True) for pkm in col_pkm]
    if len(col_ipkm) == 0:
        col_ipkm = row_ipkm
        col_pkm = row_pkm

    battle_matrix = BattleMatrix(row_ipkm, col_ipkm, enum_shields)
    battle_matrix.run()
    matrix = battle_matrix.get()

    return {
        "rowPokemon": row_pkm,
        "colPokemon": col_pkm,
        "matrix": matrix
    }
