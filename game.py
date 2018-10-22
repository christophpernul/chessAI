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
        self.piece_type = ''
        ### First item checks if en passant move is possible (when the previous move was a double move)
        ### Second item checks whether a piece, which was captured en passant, has to be removed
        self.en_passant_possible = [False, False]
        self.capture = False


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
            piecepos = string[:2]
            piecetype = string[3:]
            if self.choose_piece == True:
                if (self.white2move==True and piecetype[0]!='w') or (self.white2move==False and piecetype[0]!='b'):
                    self.make_move(string)
                else:
                    print("Wrong piece selected - you cannot move onto your own piece!")
                    self.choose_piece = False
                    self.choose_piece_position = ''
                    self.piece_type = ''

            elif self.choose_piece == False:
                self.choose_piece_position = string[:2]
                self.piece_type = string[3:]
                pos = chess2computer(self.choose_piece_position)
                if (self.white2move == True and self.piece_type[0] != 'w') or (self.white2move == False and self.piece_type[0] != 'b'):
                    print("Wrong piece selected!")
                    self.choose_piece = False
                    self.choose_piece_position = ''
                    self.piece_type = ''
                else:
                    self.choose_piece = True
        else:
            if self.choose_piece == True:
                self.make_move(string)
            else:
                print("You have to choose a piece first")


    def make_move(self, string):
            # print("No Piece selected")
            ### there is no piece on the selected field
            # if self.choose_piece==True:
                # print("Adjust board")
                # print("Position der Figur:", self.choose_piece_position)
                # print("Position des Ziels:", string)
        oldpos = chess2computer(self.choose_piece_position)
        newpos = chess2computer(string)
        ### save piece on old field
        piece = self.board[oldpos[0]][oldpos[1]]
        if self.check_if_valid_move(string)==True:
            print("Move was valid")
            ### set piece to new field
            self.board[newpos[0]][newpos[1]] = piece
            ### remove piece from old field
            self.board[oldpos[0]][oldpos[1]] = None
            if self.en_passant_possible[1]==True:
                ### remove piece, which was captured en passant, too
                if piece[0]=='w':
                    self.board[3][newpos[1]] = None
                elif piece[0] == 'b':
                    self.board[4][newpos[1]] = None
                self.en_passant_possible = [False, False]
            ### adjust board layout
            self.field_info = map_array2fieldconfig(self.board)
            self.inverse_field_info = invert_fieldconfig(self.field_info)
            ### No piece selected after move
            self.choose_piece = False
            self.choose_piece_position = ''
            self.piece_type = ''
            self.white2move = True if self.white2move == False else False
            self.switch_field()
        else:
            self.choose_piece = False
            self.choose_piece_position = ''
            self.piece_type = ''


    def check_if_valid_move(self, string):
        oldpos = chess2computer(self.choose_piece_position)
        newpos = chess2computer(string)
        piece_on_newpos = self.board[newpos[0]][newpos[1]]
        ### Rules for pawns
        if 'Pawn' in self.piece_type:
            # print("It is a pawn")
            if abs(newpos[1]-oldpos[1])>1:
                ### not more than 1 field to the side possible
                # print("seitlich 2")
                return False
            if abs(newpos[1]-oldpos[1])==1:
                # print("seitlich 1")
                if piece_on_newpos == None:
                    # print("Feld leer")
                    ### empty field on the side
                    if self.piece_type[0]=='w':
                        # print("weiß")
                        # print(piece_on_newpos, self.board[3][newpos[1]], self.en_passant_possible[0])
                        if newpos[0]==2 and piece_on_newpos==None and \
                                'bPawn' in self.board[3][newpos[1]] and self.en_passant_possible[0] == True:
                            # print("en passant")
                            ### en passante capture by white: correct row with empty target field and
                            ### piece to capture has to be a pawn, which moved in the last move
                            self.capture = True
                            self.en_passant_possible = [False, True]
                            return True
                        else:
                            # print("kein en passante")
                            return False
                    elif self.piece_type[0]=='b':
                        # print("black")
                        # print(piece_on_newpos, self.board[3][newpos[1]], self.en_passant_possible[0])
                        if newpos[0]==5 and piece_on_newpos==None and \
                                'wPawn' in self.board[4][newpos[1]] and self.en_passant_possible[0] == True:
                            # print("en passante")
                            ### en passante capture by black: correct row with empty target field and
                            ### piece to capture has to be a pawn, which moved in the last move
                            self.en_passant_possible = [False, True]
                            self.capture = True
                            return True
                        else:
                            # print("kein en passante")
                            return False
                elif piece_on_newpos[0]==self.piece_type[0]:
                    ### capture of piece with same color not possible
                    # print("Feld durch gleiche Farbe belegt")
                    return False
                elif piece_on_newpos[0]!=self.piece_type[0]:
                    if self.piece_type[0]=='w':
                        if newpos[0]<oldpos[0]:
                            ## capture is only possible in forward direction
                            self.capture = True
                            self.en_passant_possible = [False, False]
                            # print("Schlagen!!")
                            return True
                        else:
                            # print("Schlagen nur in Vorwärtsrichtung!!")
                            return False
                    elif self.piece_type[0]=='b':
                        if newpos[0]>oldpos[0]:
                            ## capture is only possible in forward direction
                            self.capture = True
                            self.en_passant_possible = [False, False]
                            # print("Schlagen!!")
                            return True
                        else:
                            # print("Schlagen nur in Vorwärtsrichtung!!")
                            return False

            else:
                if self.piece_type[0]=='w':
                    # print("weiß")
                    if oldpos[0]-newpos[0]==2:
                        # print("Doppelzug")
                        if oldpos[0]==6:
                            # print("ok")
                            ### double move by white
                            self.en_passant_possible = [True, False]
                            return True
                        else:
                            # print("no")
                            return False
                    elif (oldpos[0]-newpos[0]==1) and piece_on_newpos==None:
                        self.en_passant_possible = [False, False]
                        return True
                    else:
                        # print("zu weit")
                        return False
                if self.piece_type[0]=='b':
                    # print("black")
                    if newpos[0]-oldpos[0]==2:
                        # print("Doppelzug")
                        if oldpos[0]==1:
                            self.en_passant_possible = [True, False]
                            # print("ok")
                            ### double move by white
                            return True
                        else:
                            # print("no")
                            return False
                    elif (newpos[0]-oldpos[0]==1) and piece_on_newpos==None:
                        # print("EInzelzug")
                        self.en_passant_possible = [False, False]
                        return True
                    else:
                        # print("zu weit")
                        return False


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



