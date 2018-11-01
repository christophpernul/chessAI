#!/usr/bin/env python3
#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 14 20:49:42 2018

@author: chris
Line 2 needed to run flask with python3
"""
### import own module named game
import importlib
gf = importlib.import_module('game')

import json

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, send_from_directory, jsonify
app = Flask(__name__)

game = gf.ChessGame()
a = game.set_initial_pieces()

@app.route('/')
@app.route('/index')
def index():
    field = game.field
    return render_template("index.html", field=field)
    # return render_template("testFlask_index.html", field=field)

@app.route('/move', methods = ['POST', 'GET'])
def move():
    if request.method=="POST":
        data = request.get_json(force=True)
        # print(data)
        game.human_move(data)
        field = game.field
        if game.choose_piece == True:
            return redirect(url_for('index'))
        else:
            return redirect(url_for('move'))
    else:
        field = game.field
    return render_template("index.html", field=field)




if __name__ == '__main__':
    app.run(debug=True)