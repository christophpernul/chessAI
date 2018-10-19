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

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, send_from_directory, jsonify
app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def index():
    game = gf.ChessGame()
    a = game.set_initial_pieces()
    field = game.field
    # if request.method=="GET":
       # game.test()
    return render_template("index.html", field=field)
    #return render_template("testFlask_index.html", field=field)





if __name__ == '__main__':
    app.run(debug=True)