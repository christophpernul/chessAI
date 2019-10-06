#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 5 2019

@author: chris
This file holds all the functions used in game.py, which have no functionality, which can be seen on the chess board
"""
import re

### Image file names used for the UI
images = dict({'whitePawn':'Chess_plt60.png', 'whiteKnight':'Chess_nlt60.png', 'whiteBishop':'Chess_blt60.png', \
               'whiteRook': 'Chess_rlt60.png', 'whiteQueen':'Chess_qlt60.png', 'whiteKing':'Chess_klt60.png',\
                'blackPawn':'Chess_pdt60.png', 'blackKnight':'Chess_ndt60.png', 'blackBishop':'Chess_bdt60.png', \
               'blackRook': 'Chess_rdt60.png', 'blackQueen':'Chess_qdt60.png', 'blackKing':'Chess_kdt60.png'})

def chess2computer(string):
    """
    TODO: Can be removed when all internal positions are stored as tuples
    This function converts each position on the chessboard to a tuple with array row- and column numbers
    :param string: chess board position (like e4)
    :return tuple: tuple of row- and column numbers used for an array
    """
    letter = string[0]
    number = string[1]
    return [8-int(number), ord(letter)-97]

def computer2chess(string):
    """
    TODO: Can be removed when all internal positions are stored as tuples?
    This function converts each position on the chessboard to a tuple with array row- and column numbers
    :param string:
    :return tuple: tuple of number an letter of a chess board position ( example: e4 = (4,"e") )
    """
    letter = chr(97+int(string[1]))
    return (8 - int(string[0]), letter)

def promotion_fields(board):
    """
    This function gets the board array and returns a list of all fields, where
        a promotion of a pawn is possible
    :param board (np.array): np.array of the chessboard internally stored
    :return fields (list): list of all (i,j)- indizes of the board array, where a promotion is possible
    """
    fields = []
    for j in range(8):
        if board[1][j] != None:
            if 'wPawn' in board[1][j]:
                fields.append((0,j))
                fields.append((0, j-1))
                fields.append((0, j+1))
        if board[6][j] != None:
            if 'bPawn' in board[6][j]:
                fields.append((7,j))
                fields.append((7, j-1))
                fields.append((7, j+1))
    return fields

# def create_boardDict_forHTML(board, white2move, chosen_piece):
def create_boardDict_forHTML(board):
    """
    TODO: two variables are not used, they were used before to add who's turn it is to the boardDict
    Creates a dictionary of the board used in the HTML template.
    Parsing order of the dictionary in the HTML template is the same as the insertion order (here: white side line 1 at the bottom)
    :var board (np.array): This is the configuration of the chess board saved internally
    :param white2move (boolean): indicates, which player has to move
    :param chosen_piece (boolean): indicates, whether a piece is selected or not
    :return boardDict (dictionary): stores all information to be used in the HTML template to render the board:
            {
            "top0": ["empty", "", None], "topT": ["empty", "a/b/.../h", None],  "top9": ["empty", "", None],
            "left0": ["empty", "8", None], "a8 bRookX": ["Piece", "image_name", "CSS_classBoxcolor"], ..., "right0": ["empty", "8", None]
            .                               "e4": ["noPiece", None, "CSS_classBoxcolor"]
            .
            "left7": ["empty", "1", None], "a1 wRookY": ["Piece", "image_name", "CSS_classBoxcolor"], ..., "right7": ["empty", "1", None]
            "bottom0": ["empty", "", None], "bottomB": ["empty", "a/b/.../h", None],  "bottom9": ["empty", "", None],
            }
            The variables T, B are filled in as below:
            T=0 | T=1 | ... | T=8 | T=9
            L=0 | a8  | ... | h8  | R=0
            L=1 | a7  | ... | h7  | R=1
            .
            .
            L=7 | a1  | ... | h1  | R=7
            B=0 | B=1 | ... | B=8 | B=9
            The variables X and Y are counts of the number of pieces of a given type for each player (this can change when pieces are removed or
            added by promotion and is necessary to know exactly which piece is meant)
            CSS_classBoxcolor: holds the name of the corresponding CSS class, if there is a promotion possible add a "P" to the string
    """
    boardDict = {}
    promote_fields = promotion_fields(board)
    # if white2move == True:
    #     ## nextplayer: redirects to same page if no piece is selected
    #     ## redirects to other page if a piece is selected and player switches
    #     nextplayer = 'b' if chosen_piece == True else 'w'
    #     boardDict['moving'] = 'w'+nextplayer
    #     # print(boardDict['moving'])
    # else:
    #     nextplayer = 'w' if chosen_piece == True else 'b'
    #     boardDict['moving'] = 'b'+nextplayer
    #     # print(boardDict['moving'])
    ### top row
    for i, let in enumerate(['', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', '']):
        boardDict['top'+str(i)] = ["empty", let, None]
    for i in range(8):
        ### create entry for 0th column displaying only the row number
        boardDict['left'+str(i)] = ["empty", str(8 - i), None]
        for j, let in enumerate(list('abcdefgh')):
            ### get color of pieces
            if str(board[i][j])[0] == 'w':
                color = 'white'
            else:
                color = 'black'
            ### get color of boardDict on the board
            if i%2 == 0:
                css_class = 'white-box' if j % 2 == 0 else 'box'
            else:
                css_class = 'white-box' if j % 2 == 1 else 'box'
            ### add "promote" to css class, if a pawn is able to promote on that boardDict
            if (i,j) in promote_fields:
                css_class += ' P'
            ### entries for a boardDict on the board
            if board[i][j] != None:
                key = color+ re.sub('[0-9]', '', str(board[i][j]))[1:]
                boardDict[let + str(8 - i) + str(" ") + str(board[i][j])] = ["Piece", images[key], css_class]
            else:
                boardDict[let + str(8 - i)] = ["noPiece", None, css_class]
        ### create entry for 9th column displaying only the row number
        boardDict['right'+str(i)] = ["empty", str(8 - i), None]
    ### bottom row
    for i, let in enumerate(['', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', '']):
        boardDict['bottom'+str(i)] = ["empty", let, None]
    return boardDict

def invert_boardDict(boardDict):
    """
    TODO: line with keys.insert(0,...) is only needed if in function create_boardDict_forHTML the first commented
    block is uncommented -> info about which player to move
    Inverts the boardDict used for the HTML template in case black is the player to move (line 8 at bottom):
    The order of the board positions is simply reversed, such that black side is on the bottom
    of the board. This has to be done, because in the HTML template the order of the parsing of
    the dict is the same order as the insertion order of the dict
    :param boardDict: boardDict generated by create_boardDict_forHTML (line 1 e.g. white side on bottom)
    :return: boardDict
    """
    newboardDict = {}
    keys = list(boardDict.keys())[::-1][:-1]
    ## places the id for the container first
    # keys.insert(0, list(boardDict.keys())[0])
    for key in keys:
        if key == "right":
            newkey = "left"
        elif key == "left":
            newkey = "right"
        elif key == "top":
            newkey="bottom"
        elif key == "bottom":
            newkey="top"
        else:
            newkey = key
        newboardDict[newkey] = boardDict[key]
    return newboardDict