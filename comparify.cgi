#!/usr/bin/env python3.1

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')

import cgitb; cgitb.enable()

import os
import cgi

from pprint import pprint, pformat
from textwrap import dedent

import comparify
import dump_evchain


def cgi_main():
    if os.environ.get('REQUEST_METHOD', "GET") != "GET":
        print("Status: 405")
        print("Allow: GET")
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
        print(fmt_html(moves, pokemon_id))

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

def fmt_html(moves, current_id):
    pokemon, movesets = zip(*moves)
    title = "%s Comparify" % "|".join(name for _, name in pokemon)
    prev_id, next_id = get_next_prev(pokemon, current_id)
    next = prev = ""
    if prev_id:
        prev = """<link rel=prev href="?pokemon_id=%d">""" % prev_id
    if next_id:
        next = """<link rel=next href="?pokemon_id=%d">""" % next_id
    time, combined = comparify.time_align(movesets,
                                          comparify.HeuristicMoveAlignerRTL)
    time2, combined2 = comparify.time_align(movesets,
                                            comparify.NeedlemanWunschMoveAligner)
    if time < time2:
        multiplier = (time2 / time) - 1
        slower = "slower"
        faster = "faster"
    else:
        multiplier = (time / time2) - 1
        slower = "faster"
        faster = "slower"
    time *= 1000
    time2 *= 1000

    if combined == combined2:
        table = fmt_table(pokemon, combined)
        return dedent("""\
        <!doctype html>
        <title>{title}</title>
        {prev}{next}
        {table}
        <p>{time:.3f} milliseconds vs {time2:.3f} milliseconds
           ({multiplier:.3f}\xd7 {faster})</p>
        """).format(**locals())
    else:
        table = fmt_table(pokemon, combined)
        table2 = fmt_table(pokemon, combined2)
        return dedent("""\
        <!doctype html>
        <title>{title}</title>
        {prev}{next}
        {table}
        <p>{time:f} milliseconds ({multiplier:.3f}\xd7 {faster})</p>
        {table2}
        <p>{time2:f} milliseconds ({multiplier:.3f}\xd7 {slower})</p>
        """).format(**locals())

def fmt_table(pokemon, combined):
    colgroups = "<colgroup span=2>" * len(pokemon)
    thead = "".join("<th colspan=2>"+name for _, name in pokemon)
    def fmt_move(move):
        return ("<td>{}<td>{}".format(*move)
            if move is not None else
            "<td><td>")
    rows = "\n".join("<tr>" + "".join(map(fmt_move, row)) for row in combined)
    return dedent("""\
    <table>
    {colgroups}
    <thead>
    <tr>{thead}</th>
    <tbody>
    {rows}
    </table>
    """).format(**locals())

def get_next_prev(pokemon, current_id):
    ids = set(x[0] for x in pokemon)
    prev_id = next_id = current_id
    while prev_id in ids:
        prev_id -= 1
    while next_id in ids:
        next_id += 1
    if prev_id < 1:
        prev_id = None
    if 493 < next_id:
        next_id = None
    return prev_id, next_id


if __name__ == '__main__':
    cgi_main()

