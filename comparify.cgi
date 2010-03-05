#!/usr/bin/env python3.1

import cgitb; cgitb.enable()

import os
import comparify
import dump_evchain
import cgi
from pprint import pprint, pformat
from textwrap import dedent

def fmt_plaintext(moves):
    pokemon, movesets = zip(*moves)
    combined = comparify.alignn(movesets)
    return dedent("""\
    %s

    %s
    """) % (", ".join(name for _, name in pokemon), pformat(combined))

def fmt_html(moves):
    pokemon, movesets = zip(*moves)
    combined = comparify.alignn(movesets)
    title = "%s Comparify" % "|".join(name for _, name in pokemon)
    colgroups = "<colgroup span=2>" * len(pokemon)
    thead = "".join("<th colspan=2>"+name for _, name in pokemon)
    def fmt_move(move):
        return ("<td>{}<td>{}".format(*move)
            if move is not None else
            "<td><td>") 
    rows = "\n".join("<tr>" + "".join(map(fmt_move, row)) for row in combined)
    return """
    <!doctype html>
    <title>{title}</title>
    <table>
    {colgroups}
    <thead>
    <tr>{thead}</th>
    <tbody>
    {rows}
    </table>
    """.format(**locals())
    

def cgi_main():
    fs = cgi.FieldStorage()
    pokemon_id = int(fs['pokemon_id'].value)
    conn = dump_evchain.connect()
    moves = dump_evchain.extract_moves(conn, pokemon_id)
    accept = os.environ.get('HTTP_ACCEPT', '')
    del conn
    if not accept:
        print("Content-type: text/plain; charset=utf-8")
        print()
        print(fmt_plaintext(moves))
    else:
        print("Content-type: text/html; charset=utf-8")
        print()
        print(fmt_html(moves))


if __name__ == '__main__':
    import os
    cgi_main()

