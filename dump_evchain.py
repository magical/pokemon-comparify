#!/usr/bin/env python3.1
import sqlite3
import itertools

DATABASE = '/home/andrew/veekun/pokedex/pokedex/data/pokedex.sqlite'

LATEST_VERSION = 10

def extract_moves(conn, pokemon_id):
    query = """
        SELECT evolution_chain_id 
        FROM pokemon
        WHERE id = ?
    """
    evid = conn.execute(query, [pokemon_id]).fetchone()[0]

    query = """
        SELECT p.id, p.name, p.evolution_parent_pokemon_id,
               pm.level, m.name
        FROM pokemon p
        JOIN pokemon_moves pm ON pm.pokemon_id = p.id
        JOIN moves m ON pm.move_id = m.id
        WHERE pm.version_group_id = ?
            AND p.evolution_chain_id = ?
            AND pm.pokemon_move_method_id = 1
        ORDER BY p.id, pm.level, 'pm.order'
    """
    q = conn.execute(query, [LATEST_VERSION, evid])
    movesets = []
    parents = {}
    stages = {None: 0}
    for (id, name, evparent), group in itertools.groupby(q, lambda x: (x[:3])):
        parents[id] = evparent
        movesets.append(((id, name), list(x[3:] for x in group)))


    def stage(id):
        if id is None:
            return 0
        try:
            evparent = parents[id]
        except IndexError:
            raise ValueError('no parent')
        if evparent in stages:
            return 1 + stages[evparent]
        return 1 + stage(evparent)

    for id in parents.keys():
        stages[id] = stage(id)

    # order the pokemon
    movesets.sort(key=lambda x: stage(x[0][0]))

    return movesets

def connect():
    return sqlite3.connect(DATABASE)
    

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print ("Usage: dump_evchain.py pokemon_id")
        sys.exit(-1)

    from pprint import pprint
    conn = connect()
    pprint(extract_moves(conn, sys.argv[1]))


