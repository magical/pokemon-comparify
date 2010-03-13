#!/usr/bin/env python3.1

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')

import cgitb; cgitb.enable()

import os
import cgi

from pprint import pprint, pformat
from textwrap import dedent

import comparify
import pokemon

version_map = 'rb y gs c rs e frlg dp pt hgss'
version_map = {v: i+1 for i, v in enumerate(version_map.split())}


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
    <p>Compare with family
     <form>
      {select1}
      <button type=submit>Go!</button>
     </form>
    <p>Multi compare
     <form>
      {select1}
      {select1}
      {select2}
      {select2}
      <button type=submit>Go!</button>
     </form>
    <p>Quicklinks
     <ul style="list-style: none; padding: 0;">
      <li><a href="?pokemon_id=144&pokemon_id=145&pokemon_id=146">Articuno | Zapdos | Moltres</a>
      <li><a href="?pokemon_id=243&pokemon_id=244&pokemon_id=245">Raikou | Entei | Suicune</a>
      <li><a href="?pokemon_id=249&pokemon_id=250">Lugia | Ho-oh</a>
      <li><a href="?pokemon_id=377&pokemon_id=378&pokemon_id=379">Regirock | Regiice | Registeel</a>
      <li><a href="?pokemon_id=380&pokemon_id=381">Latias | Latios</a>
      <li><a href="?pokemon_id=382&pokemon_id=383&pokemon_id=384">Kyogre | Groudon | Rayquaza</a>
      <li><a href="?pokemon_id=480&pokemon_id=481&pokemon_id=482">Uxie | Mesprit | Azelf</a>
      <li><a href="?pokemon_id=483&pokemon_id=484&pokemon_id=487">Dialga | Palkia | Giratina</a>
      <li><a href="?pokemon_id=488&pokemon_id=491">Cresselia | Darkrai</a>
      <!--<li><a href="?pokemon_id=&pokemon_id=&pokemon_id="></a>-->
     </ul>
    """

    all_pokemon = pokemon.all_pokemon()
    options = "".join(
        "<option value={id}>{name}".format(id=p[0], name=p[1])
        for p in all_pokemon)
    select1 = "<select name=pokemon_id>{}</select>".format(options)
    select2 = "<select name=pokemon_id><option value=\"\">-----------{}</select>".format(options)
    content_type("text/html")
    end_headers()
    print(template.format(**locals()))

def page_compare(fs):
    pokemon_ids = list(map(int, fs.getlist('pokemon_id')))
    ver = fs.getvalue('ver')
    if ver is not None:
        ver = version_map[ver]
    else:
        ver = pokemon.LATEST_VERSION

    if len(pokemon_ids) == 1:
        pokemon_id = pokemon_ids[0]
        evid = pokemon.evid_from_pokemonid(pokemon_id)
        moves = pokemon.moves_from_evid(evid, ver)
    else:
        pokemon_id = None
        moves = [pokemon.moves_from_pokemonid(id, ver) for id in pokemon_ids]
    accept = os.environ.get('HTTP_ACCEPT', '')
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
    combined = comparify.align(movesets)
    return dedent("""\
    %s

    %s
    """) % (", ".join(name for _, name in pokemon), pformat(combined))

def fmt_html(moves, current_id=None):
    pokemon, movesets = zip(*moves)
    title = "%s Comparify" % "|".join(name for _, name in pokemon)
    next = prev = ""
    if current_id:
        prev_id, next_id = get_next_prev(pokemon, current_id)
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
    def fmt_move_bold(move):
        return ("<td>{}<td><b>{}</b>".format(*move)
            if move is not None else
            "<td><td>")
    def fmt_move_italic(move):
        return ("<td>{}<td><i>{}</i>".format(*move)
            if move is not None else
            "<td><td>")
    def fmt_row(row):
        if len(set(x[1] for x in row if x is not None)) == 1:
            if not any(x is None for x in row):
                return "<tr>" + "".join(map(fmt_move_bold, row))
            else:
                return "<tr>" + "".join(map(fmt_move_italic, row))
        else:
            return "<tr>" + "".join(map(fmt_move, row))

    rows = "\n".join(fmt_row(row) for row in combined)
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

