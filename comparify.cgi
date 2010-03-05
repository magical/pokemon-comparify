#!/usr/bin/env python3.1

import cgitb; cgitb.enable()

import comparify
import dump_evchain
import cgi
from pprint import pprint


def cgi_main():
    fs = cgi.FieldStorage()
    pokemon_id = int(fs['pokemon_id'].value)
    conn = dump_evchain.connect()
    moves = dump_evchain.extract_moves(conn, pokemon_id)
    del conn
    pokemon, movesets = zip(*moves)
    combined = comparify.alignn(movesets)
    print("Content-type: text/plain; charset=utf-8")
    print()
    print(", ".join(name for _, name in pokemon))
    print()
    pprint(combined)


if __name__ == '__main__':
    import os
    cgi_main()

