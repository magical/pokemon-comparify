#!/usr/bin/env python3.1
import sqlite3
import itertools

DATABASE = '/home/andrew/veekun/pokedex/pokedex/data/pokedex.sqlite'

LATEST_VERSION = 10

_conn = None # database connection

def _connect():
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(DATABASE)

def evid_from_pokemonid(pokemon_id):
    _connect()
    query = """
        SELECT evolution_chain_id
        FROM pokemon
        WHERE id = ?
    """
    evid = _conn.execute(query, [pokemon_id]).fetchone()[0]
    return evid

def moves_from_evid(evid, ver=LATEST_VERSION):
    _connect()
    query = """
        SELECT p.id, p.name, p.evolution_parent_pokemon_id,
               pm.level, m.name
        FROM pokemon p
        JOIN pokemon_moves pm ON pm.pokemon_id = p.id
        JOIN moves m ON pm.move_id = m.id
        WHERE pm.version_group_id = ?
            AND p.evolution_chain_id = ?
            AND pm.pokemon_move_method_id = 1
        ORDER BY p.id, pm.level, pm."order"
    """
    cur = _conn.execute(query, [ver, evid])
    movesets = []
    parents = {}
    stages = {None: 0}
    for (id, name, evparent), group in itertools.groupby(cur, lambda x: (x[:3])):
        parents[id] = evparent
        movesets.append(((id, name), [x[3:] for x in group]))

    def stage(id):
        if id is None:
            return 0
        try:
            evparent = parents[id]
        except KeyError:
            # This probably means that the pre-evo was introduced in a later
            # game; therefore, this pokemon is stage 1.
            return 1
        if evparent not in stages:
            stages[evparent] = stage(evparent)

        return 1 + stages[evparent]

    for id in parents.keys():
        stages[id] = stage(id)

    # order the pokemon
    movesets.sort(key=lambda x: stage(x[0][0]))

    return movesets

def moves_from_pokemonid(pokemon_id, ver=LATEST_VERSION):
    _connect()
    query = """
        SELECT p.id, p.name, p.evolution_parent_pokemon_id,
               pm.level, m.name
        FROM pokemon p
        JOIN pokemon_moves pm ON pm.pokemon_id = p.id
        JOIN moves m ON pm.move_id = m.id
        WHERE pm.version_group_id = ?
            AND p.id = ?
            AND pm.pokemon_move_method_id = 1
        ORDER BY p.id, pm.level, pm."order"
    """
    cur = _conn.execute(query, [ver, pokemon_id])
    movesets = []
    for (id, name, evparent), group in itertools.groupby(cur, lambda x: (x[:3])):
        movesets.append(((id, name), [x[3:] for x in group]))

    return movesets[0]


def all_pokemon():
    _connect()
    query = """\
    SELECT id, name FROM pokemon ORDER BY name;
    """
    return _conn.execute(query)

