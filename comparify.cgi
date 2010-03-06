#!/usr/bin/env python3.1

import cgitb; cgitb.enable()

import os
import comparify
import dump_evchain
import cgi
from pprint import pprint, pformat
from textwrap import dedent

# UTF-8
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')

def cgi_main():
    if os.environ.get('REQUEST_METHOD', "GET") != 'GET':
        print("Status: 400")
        end_headers()
        return

    fs = cgi.FieldStorage()
    if 'pokemon_id' in fs:
        page_compare(fs)
    else:
        page_index(fs)

def page_index(fs):
    template = """\
    <!doctype>
    <title>Comparifier</title>
    <form>
    {select}
    <button type=submit>Go!</button>
    </form>
    """

    conn = dump_evchain.connect()
    all_pokemon = dump_evchain.all_pokemon(conn)
    options = "".join(
        "<option value={id}>{name}".format(id=p[0], name=p[1])
        for p in all_pokemon)
    select = "<select name=pokemon_id>{}</select>".format(options)
    content_type("text/html")
    end_headers()
    print(template.format(**locals()))

def page_compare(fs):
    pokemon_id = int(fs['pokemon_id'].value)
    conn = dump_evchain.connect()
    moves = dump_evchain.extract_moves(conn, pokemon_id)
    accept = os.environ.get('HTTP_ACCEPT', '')
    del conn
    if not accept:
        content_type("text/plain")
        end_headers()
        print(fmt_plaintext(moves))
    else:
        content_type("text/html")
        end_headers()
        print(fmt_html(moves))

def content_type(type):
    if type.startswith("text/") and "charset" not in type:
        type += "; charset=utf-8"
    print("Content-type:", type)

def end_headers():
    print()

def fmt_plaintext(moves):
    pokemon, movesets = zip(*moves)
    combined = comparify.alignn(movesets)
    return dedent("""\
    %s

    %s
    """) % (", ".join(name for _, name in pokemon), pformat(combined))

def fmt_html(moves):
    pokemon, movesets = zip(*moves)
    time, combined = comparify.time_alignn(moves)
    time *= 1000
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
    <p>{time:f} milliseconds</p>
    """.format(**locals())


if __name__ == '__main__':
    cgi_main()

