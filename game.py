#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 14 21:10:17 2018

@author: chris
"""
import numpy as np
import re

images = dict({'whitePawn':'Chess_plt60.png', 'whiteKnight':'Chess_nlt60.png', 'whiteBishop':'Chess_blt60.png', \
               'whiteRook': 'Chess_rlt60.png', 'whiteQueen':'Chess_qlt60.png', 'whiteKing':'Chess_klt60.png',\
                'blackPawn':'Chess_pdt60.png', 'blackKnight':'Chess_ndt60.png', 'blackBishop':'Chess_bdt60.png', \
               'blackRook': 'Chess_rdt60.png', 'blackQueen':'Chess_qdt60.png', 'blackKing':'Chess_kdt60.png'})

def chess2computer(string):
    letter = string[0]
    number = string[1]
    return [8-int(number), ord(letter)-97]

def map_array2fieldconfig(array):
    """ A function mapping the 8x8 board (array: None value means no piece) to a dictionary used for the template
         Dictionary: {key: [imagename, css_class, row_number]} with additional rows 0 and 9, which display the row number"""
    field = dict()
    ### top row
    for i, let in enumerate(['', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', '']):
        field['top'+str(i)] = [let, None, None]
    for i in range(8):
        ### create entry for 0th column displaying only the row number
        field['left'+str(i)] = [str(8 - i), None, None]
        for j, let in enumerate(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']):
            ### get color of pieces
            if str(array[i][j])[0] == 'w':
                color = 'white'
            else:
                color = 'black'
            ### get color of field on the board
            if i%2==0:
                css_class = 'white-box' if j % 2 == 0 else 'box'
            else:
                css_class = 'white-box' if j % 2 == 1 else 'box'
            ### entries for a field on the board
            if array[i][j]!=None:
                key = color+re.sub('[0-9]', '', str(array[i][j]))[1:]
                field[let + str(8 - i) +str(" ")+str(array[i][j])] = [images[key], css_class, str(8 - i)]
            else:
                field[let + str(8 - i)] = [None, css_class, str(8 - i)]
        ### create entry for 9th column displaying only the row number
        field['right'+str(i)] = [str(8 - i), None, None]
    ### bottom row
    for i, let in enumerate(['', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', '']):
        field['bottom'+str(i)] = [let, None, None]
    return field

def invert_fieldconfig(field):
    newfield = dict()
    keys = list(field.keys())[::-1]
    for key in keys:
        if key=="right":
            newkey = "left"
        elif key=="left":
            newkey = "right"
        elif key=="top":
            newkey="bottom"
        elif key=="bottom":
            newkey="top"
        else:
            newkey = key
        newfield[newkey] = field[key]
    return newfield

def map_pieces2array():
    return images

class ChessGame:
    def __init__(self):
        self.moves = []
        self.white2move = True
        self.num_moves = 0
        self.num_same_moves = 0
        ### list of every field on the board: Boolean variable decides whether there is a piece on the given field
        self.board = np.full((8,8), None)
        ### dicts of all pieces of white and black and their position on the board: used to eval winner
        self.white = dict({'Pawn1':'a2', 'Pawn2':'b2', 'Pawn3':'c2', 'Pawn4':'d2', 'Pawn5':'e2', \
                           'Pawn6': 'f2', 'Pawn7':'g2', 'Pawn8':'h2', 'Rook1': 'a1', 'Rook2':'h1',\
                           'Knight1':'b1', 'Knight2':'g1', 'Bishop1':'c1', 'Bishop2':'f1', \
                           'Queen':'d1', 'King':'e1'})
        self.black = dict({'Pawn1': "a7", 'Pawn2': 'b7', 'Pawn3': 'c7', 'Pawn4': 'd7', 'Pawn5': 'e7', \
                           'Pawn6': 'f7', 'Pawn7': 'g7', 'Pawn8': 'h7', 'Rook1': 'a8', 'Rook2': 'h8', \
                           'Knight1': 'b8', 'Knight2': 'g8', 'Bishop1': 'c8', 'Bishop2': 'f8', \
                           'Queen': 'd8', 'King': 'e8'})
        self.field_info = dict() ## stores field config for white to move
        self.inverse_field_info = dict() ## stores field config for black to move
        ## field to use in the template whether black or white has to move
        self.field = dict()
        self.choose_piece = False
        self.choose_piece_position = ''


    def switch_field(self):
        self.field = self.field_info if self.white2move == True else self.inverse_field_info

    def set_initial_pieces(self):
        """Places all figures on the board
        """
        for j in range(8):
            ## fill in all pawns
            self.board[1][j] = 'bPawn{0}'.format(j)
            self.board[6][j] = 'wPawn{0}'.format(j)
        for i in [0, 7]:
            ## fill in all other pieces
            if i==0:
                color = 'b'
            else:
                color = 'w'
            self.board[i][0] = '{0}Rook1'.format(color)
            self.board[i][7] = '{0}Rook2'.format(color)
            self.board[i][1] = '{0}Knight1'.format(color)
            self.board[i][6] = '{0}Knight2'.format(color)
            self.board[i][2] = '{0}Bishop1'.format(color)
            self.board[i][5] = '{0}Bishop2'.format(color)
            self.board[i][3] = '{0}Queen'.format(color)
            self.board[i][4] = '{0}King'.format(color)
        ### create dict used for the template
        self.field_info = map_array2fieldconfig(self.board)
        self.inverse_field_info = invert_fieldconfig(self.field_info)
        self.switch_field()


    def human_move(self, string):
        """Human does a move"""
        if len(string)>2:
            ### there is a piece on the selected field
            print("Piece selected")
            self.choose_piece = True
            self.choose_piece_position = string[:2]
            pos = chess2computer(self.choose_piece_position)
            # print(string[:2])
            # print(pos)
            if string[3:]!=self.board[pos[0]][pos[1]]:
                print("Implementation ERROR: not correct piece selected!")
            if (self.white2move==True and string[3]!='w') or (self.white2move==False and string[3]!='b'):
                print("Wrong piece selected!")
                # print(pos[0], pos[1]);
        else:
            print("No Piece selected")
            ### there is no piece on the selected field
            if self.choose_piece==True:
                print("Adjust board")
                # print("Position der Figur:", self.choose_piece_position)
                # print("Position des Ziels:", string)
                oldpos = chess2computer(self.choose_piece_position)
                newpos = chess2computer(string)
                ### save piece on old field
                piece = self.board[oldpos[0]][oldpos[1]]
                ### set piece to new field
                self.board[newpos[0]][newpos[1]] = piece
                ### remove piece from old field
                self.board[oldpos[0]][oldpos[1]] = None
                ### adjust board layout
                self.field_info = map_array2fieldconfig(self.board)
                self.inverse_field_info = invert_fieldconfig(self.field_info)
                print(self.board)
                self.switch_field()


    def ai_move(self):
        """AI does a move"""
        return 1

    def check_game_status():
        """Checks game status, whether win/loss/remis
        """
        return 1

    def read_input(self):
        """Reads input using a mouse click or chess notation
        """
        return 1
    def test(self):
        self.field['a8'][1] = "box"



