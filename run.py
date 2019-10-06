#!/usr/bin/env python3
#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 14 20:49:42 2018

@author: chris
Line 2 needed to run flask with python3
"""

import game as gf
import json
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, send_from_directory, jsonify
app = Flask(__name__)

directory_movehistory = "data"

game = gf.ChessGame(directory_movehistory)
a = game.set_initial_pieces()

@app.route('/')
@app.route('/index')
def index():
    board = game.generate_html_config()
    return render_template("index.html", board=board)

@app.route('/move', methods = ['POST', 'GET'])
def move():
    if request.method=="POST":
        data = request.get_json(force=True)
        # print(data)
        game.human_move(data)
        board = game.generate_html_config()
        print("In function move!")
        print(field)
        if game.piece_chosen == True:
            return redirect(url_for('index'))
        else:
            return redirect(url_for('move'))
    else:
        field = game.field
        # print(boardDict["info"])
    return render_template("index.html", board=board)

@app.route('/remis', methods = ['POST', 'GET'])
## not ready!!!
def remis():
    if request.method=="POST":
        player = request.get_json(force=True)
        print("In function remis!")
        # game.offer_draw(player)
        # if game.piece_chosen == True:
        #     return redirect(url_for('index'))
        # else:
        #     return redirect(url_for('move'))
    board = game.generate_html_config()
    return render_template("index.html", board=board)
    #return redirect(url_for('index'))

@app.route('/resign', methods = ['POST', 'GET'])
## not ready!!!
def resign():
    if request.method=="POST":
        player = request.get_json(force=True)
        # print(data)
        print("In function resign!")
        #game.resign(player)
        # if game.piece_chosen == True:
        #     return redirect(url_for('index'))
        # else:
        #     return redirect(url_for('move'))

    board = game.generate_html_config()
    return render_template("index.html", board=board)
    #return redirect(url_for('index'))

@app.route('/newgame', methods = ['POST', 'GET'])
## not ready!!!
def newgame():
    if request.method=="POST":
        player = request.get_json(force=True)
        # print(data)
        print("In function newgame!")
        #game.newgame(player)
        # if game.piece_chosen == True:
        #     return redirect(url_for('index'))
        # else:
        #     return redirect(url_for('move'))

    board = game.generate_html_config()
    #return render_template("index.html", boardDict=boardDict)
    return redirect(url_for('index'))

# @app.route('/w', methods = ['POST', 'GET'])
# def w():
#     if request.method=="POST":
#         data = request.get_json(force=True)
#         # print(data)
#         game.human_move(data)
#         boardDict = game.boardDict
#         # if game.piece_chosen == True:
#         #     return redirect(url_for('index'))
#         # else:
#         #     return redirect(url_for('move'))
#     else:
#         boardDict = game.boardDict
#     return render_template("index.html", boardDict=boardDict)
#
# @app.route('/b', methods = ['POST', 'GET'])
# def b():
#     if request.method=="POST":
#         data = request.get_json(force=True)
#         # print(data)
#         game.human_move(data)
#         boardDict = game.boardDict
#         # if game.piece_chosen == True:
#         #     return redirect(url_for('index'))
#         # else:
#         #     return redirect(url_for('move'))
#     else:
#         boardDict = game.boardDict
#     return render_template("index.html", boardDict=boardDict)





if __name__ == '__main__':
    app.run(debug=True)