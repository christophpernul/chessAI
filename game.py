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

def computer2chess(string):
    letter = chr(97+int(string[1]))
    return [8 - int(string[0]), letter]

def promotion_fields(array):
    """ This function gets the board array and returns a list of all fields, where
        a promotion of a pawn is possible"""
    fields = []
    for j in range(7):
        if array[1][j] != None:
            if 'wPawn' in array[1][j]:
                fields.append((0,j))
                fields.append((0, j-1))
                fields.append((0, j+1))
        if array[6][j] != None:
            if 'bPawn' in array[6][j]:
                fields.append((7,j))
                fields.append((7, j-1))
                fields.append((7, j+1))
    return fields


def map_array2fieldconfig(array):
    """ A function mapping the 8x8 board (array: None value means no piece) to a dictionary used for the template
         Dictionary: {key: [imagename, css_class, row_number]} with additional rows 0 and 9, which display the row number"""
    field = {}
    promote_fields = promotion_fields(array)
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
            if i%2 == 0:
                css_class = 'white-box' if j % 2 == 0 else 'box'
            else:
                css_class = 'white-box' if j % 2 == 1 else 'box'
            ### add "promote" to css class, if a pawn is able to promote on that field
            if (i,j) in promote_fields:
                css_class += ' P'
            ### entries for a field on the board
            if array[i][j] != None:
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
    newfield = {}
    keys = list(field.keys())[::-1]
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
        newfield[newkey] = field[key]
    return newfield

class ChessGame:
    def __init__(self):
        self.moves = []
        self.white2move = True
        self.num_moves = 0
        self.num_same_moves = 0
        ###  list of every field on the board: Boolean variable decides whether there is a piece on the given field
        self.board = np.full((8,8), None)
        ###  dicts of all pieces of white and black and their position on the board: used to eval winner
        self.white = dict({'Pawn0' : 'a2', 'Pawn1':'b2', 'Pawn2':'c2', 'Pawn3':'d2', 'Pawn4':'e2', \
                           'Pawn5': 'f2', 'Pawn6':'g2', 'Pawn7':'h2', 'Rook0': 'a1', 'Rook1':'h1',\
                           'Knight0':'b1', 'Knight1':'g1', 'Bishop0':'c1', 'Bishop1':'f1', \
                           'Queen':'d1', 'King':'e1'})
        self.black = dict({'Pawn0': "a7", 'Pawn1': 'b7', 'Pawn2': 'c7', 'Pawn3': 'd7', 'Pawn4': 'e7', \
                           'Pawn5': 'f7', 'Pawn6': 'g7', 'Pawn7': 'h7', 'Rook0': 'a8', 'Rook1': 'h8', \
                           'Knight0': 'b8', 'Knight1': 'g8', 'Bishop0': 'c8', 'Bishop1': 'f8', \
                           'Queen': 'd8', 'King': 'e8'})
        self.field_info = {} ## stores field config for white to move
        self.inverse_field_info = {} ## stores field config for black to move
        ## field to use in the template whether black or white has to move
        self.field = {}
        self.choose_piece = False
        self.choose_piece_position = ''
        self.piece_type = ''
        ### First item checks if en passant move is possible (when the previous move was a double move)
        ### Second item checks whether a piece, which was captured en passant, has to be removed
        self.en_passant_possible = [False, False]
        self.capture = False
        ### counts number of promotions for both players
        self.num_promos = [0, 0]


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
            if i is 0:
                color = 'b'
            else:
                color = 'w'
            self.board[i][0] = '{0}Rook0'.format(color)
            self.board[i][7] = '{0}Rook1'.format(color)
            self.board[i][1] = '{0}Knight0'.format(color)
            self.board[i][6] = '{0}Knight1'.format(color)
            self.board[i][2] = '{0}Bishop0'.format(color)
            self.board[i][5] = '{0}Bishop1'.format(color)
            self.board[i][3] = '{0}Queen'.format(color)
            self.board[i][4] = '{0}King'.format(color)
        ### create dict used for the template
        self.field_info = map_array2fieldconfig(self.board)
        self.inverse_field_info = invert_fieldconfig(self.field_info)
        self.switch_field()


    def human_move(self, string):
        """Human does a move"""
        promoted_piece = 'w' if self.white2move == True else 'b'
        # print(string)
        if string[0] in ['K', 'B', 'R', 'Q']:
            if string[0] == 'K':
                promoted_piece += 'Knight'
            elif string[0] == 'B':
                promoted_piece += 'B==hop'
            elif string[0] == 'R':
                promoted_piece += 'Rook'
            elif string[0] == 'Q':
                promoted_piece += 'Queen'
            promotion = [True, promoted_piece]
            # print("promotion!!!", promotion)
            string = string[1:]
        else:
            promotion = [False, None]
        if len(string)>2:
            ### there is a piece on the selected field
            piecepos = string[:2]
            piecetype = string[3:]
            if self.choose_piece == True:
                if (self.white2move == True and piecetype[0] != 'w') or (self.white2move == False and piecetype[0] != 'b'):
                    self.make_move(string, promotion)
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
                self.make_move(string, promotion)
            else:
                print("You have to choose a piece first")
        self.check_game_status()


    def make_move(self, string, promotion):
        oldpos = chess2computer(self.choose_piece_position)
        newpos = chess2computer(string)
        ### save piece on old field
        # print(string, newpos, oldpos)
        piece = self.board[oldpos[0]][oldpos[1]]
        if self.check_if_valid_move(oldpos, newpos) == True and self.king_in_check(oldpos, newpos) == False:
            # print("Move was valid")
            if self.board[newpos[0]][newpos[1]] == None:
                ### set piece to new field
                self.board[newpos[0]][newpos[1]] = piece
                if piece[0] == 'w':
                    self.white[piece[1:]] = '{0}{1}'.format(computer2chess(newpos)[1], computer2chess(newpos)[0])
                elif piece[0] == 'b':
                    self.black[piece[1:]] = '{0}{1}'.format(computer2chess(newpos)[1], computer2chess(newpos)[0])

            else:
                if self.piece_type[0] == 'w':
                    captured_piece = self.board[newpos[0]][newpos[1]][1:]
                    self.white[piece[1:]] = '{0}{1}'.format(computer2chess(newpos)[1], computer2chess(newpos)[0])
                    del self.black[captured_piece]
                elif self.piece_type[0] == 'b':
                    captured_piece = self.board[newpos[0]][newpos[1]][1:]
                    self.black[piece[1:]] = '{0}{1}'.format(computer2chess(newpos)[1], computer2chess(newpos)[0])
                    del self.white[captured_piece]
                self.board[newpos[0]][newpos[1]] = piece

            ### remove piece from old field
            self.board[oldpos[0]][oldpos[1]] = None
            if self.en_passant_possible[1] == True:
                ### remove piece, which was captured en passant, too
                if piece[0] == 'w':
                    captured_piece = self.board[3][newpos[1]][1:]
                    del self.black[captured_piece]
                    self.board[3][newpos[1]] = None
                elif piece[0] == 'b':
                    captured_piece = self.board[4][newpos[1]][1:]
                    del self.white[captured_piece]
                    self.board[4][newpos[1]] = None
                self.en_passant_possible = [False, False]
            ### promote a pawn
            if promotion[0] == True:
                self.board[newpos[0]][newpos[1]] = promotion[1]
                if self.white2move == True:
                    # del self.black[piece]
                    position = computer2chess('{0}{1}'.format(newpos[0], newpos[1]))
                    del self.white[piece[1:]]
                    self.white[promotion[1][1:] + str(self.num_promos[0]+2)] = '{0}{1}'.format(position[1], position[0])
                    self.num_promos[0] += 1
                elif self.white2move == False:
                    # del self.white[piece]
                    position = computer2chess('{0}{1}'.format(newpos[0], newpos[1]))
                    del self.black[piece[1:]]
                    self.black[promotion[1][1:] + str(self.num_promos[1]+2)] = '{0}{1}'.format(position[1], position[0])
                    self.num_promos[1] += 1
            ### adjust board layout and save move
            self.save_move()
            # print(self.white)
            # print(self.black)
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

    def king_in_check(self, oldpos, newpos):
        """checks if after a given valid move the king is in check:
            False: move valid   True: move not valid because of check"""
        ### TODO: check whether the king is in check
        return False


    def check_if_valid_move(self, oldpos, newpos):
        piece_on_newpos = self.board[newpos[0]][newpos[1]]
        ### Rules for Kings
        if 'King' in self.piece_type:
            ### TODO: Rochade
            ##
            ##
            if abs(newpos[1] - oldpos[1]) > 1 or abs(newpos[0] - oldpos[0]) > 1:
                return False
            else:
                if piece_on_newpos == None:
                    return True
                else:
                    if self.piece_type[0] == piece_on_newpos[0]:
                        return False
                    else:
                        self.capture = True
                        return True
        ### Rules for Queens
        elif 'Queen' in self.piece_type:
            if abs(newpos[0]-oldpos[0]) == abs(newpos[1]-oldpos[1]):
                ### moving diagonal
                return self.check_diagonal(oldpos, newpos)
            else:
                return self.check_straight(oldpos, newpos)

        elif 'Rook' in self.piece_type:
            return self.check_straight(oldpos, newpos)

        elif 'Bishop' in self.piece_type:
            if abs(newpos[0] - oldpos[0]) == abs(newpos[1] - oldpos[1]):
                return self.check_diagonal(oldpos, newpos)
            else:
                return False
        elif 'Knight' in self.piece_type:
            moves = [[-2, -1], [-2, +1], [+2, -1], [+2, +1], [+1, +2], [-1, +2], [+1, -2], [-1, -2]]
            for x in moves:
                if (np.array(newpos) == (np.array(oldpos) + np.array(x))).all():
                    if self.board[newpos[0]][newpos[1]] != None:
                        if self.board[newpos[0]][newpos[1]][0] != self.piece_type[0]:
                            self.capture = True
                            return True
                        # else:
                            # continue
                    else:
                        return True
                else:
                    continue
            return False

        ### Rules for pawns
        elif 'Pawn' in self.piece_type:
            if abs(newpos[1]-oldpos[1])>1:
                ### not more than 1 field to the side possible
                # print("seitlich 2")
                return False
            if abs(newpos[1]-oldpos[1]) == 1:
                # print("seitlich 1")
                if piece_on_newpos == None:
                    # print("Feld leer")
                    ### empty field on the side
                    if self.piece_type[0] == 'w':
                        # print("weiß")
                        # print(piece_on_newpos, self.board[3][newpos[1]], self.en_passant_possible[0])
                        if newpos[0] == 2 and piece_on_newpos == None and \
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
                    elif self.piece_type[0] == 'b':
                        # print("black")
                        # print(piece_on_newpos, self.board[3][newpos[1]], self.en_passant_possible[0])
                        if newpos[0] == 5 and piece_on_newpos == None and \
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
                elif piece_on_newpos[0] == self.piece_type[0]:
                    ### capture of piece with same color not possible
                    # print("Feld durch gleiche Farbe belegt")
                    return False
                elif piece_on_newpos[0] != self.piece_type[0]:
                    if self.piece_type[0] == 'w':
                        if newpos[0]<oldpos[0]:
                            ## capture is only possible in forward direction
                            self.capture = True
                            self.en_passant_possible = [False, False]
                            # print("Schlagen!!")
                            return True
                        else:
                            # print("Schlagen nur in Vorwärtsrichtung!!")
                            return False
                    elif self.piece_type[0] == 'b':
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
                if self.piece_type[0] == 'w':
                    # print("weiß")
                    if oldpos[0]-newpos[0] == 2:
                        # print("Doppelzug")
                        if oldpos[0] == 6:
                            # print("ok")
                            ### double move by white
                            self.en_passant_possible = [True, False]
                            return True
                        else:
                            # print("no")
                            return False
                    elif (oldpos[0]-newpos[0] == 1) and piece_on_newpos == None:
                        self.en_passant_possible = [False, False]
                        return True
                    else:
                        # print("zu weit")
                        return False
                if self.piece_type[0] == 'b':
                    # print("black")
                    if newpos[0]-oldpos[0] == 2:
                        # print("Doppelzug")
                        if oldpos[0] == 1:
                            self.en_passant_possible = [True, False]
                            # print("ok")
                            ### double move by white
                            return True
                        else:
                            # print("no")
                            return False
                    elif (newpos[0]-oldpos[0] == 1) and piece_on_newpos == None:
                        # print("EInzelzug")
                        self.en_passant_possible = [False, False]
                        return True
                    else:
                        # print("zu weit")
                        return False

    def check_if_piece_on_1darray(self, array, start, end):
        """checks whether a move  is  valid if performed along the array direction
        in array is important: index(oldposition) < index(newposition) """
        for i in range(start, end + 1):
            if i == end:
                if array[i] == None:
                    return True
                else:
                    # print("end position is")
                    if array[i][0] != self.piece_type[0]:
                        # print("other color")
                        self.capture = True
                        return True
                    else:
                        return False
            else:
                # print("between")
                if array[i] == None:
                    continue
                else:
                    # print("is a piece")
                    return False

    def check_straight(self, oldpos, newpos):
        ### checks if a straight move along a row or column is valid
        if newpos[0] == oldpos[0]:
            # print("same row")
            ### moving in the same row
            checkpath_row = self.board[newpos[0]]
            if oldpos[1] < newpos[1]:
                start = oldpos[1] + 1
                end = newpos[1]
            else:
                start = 7 - (oldpos[1] - 1)
                end = 7 - newpos[1]
                checkpath_row = checkpath_row[::-1]
            return self.check_if_piece_on_1darray(checkpath_row, start, end)

        elif newpos[1] == oldpos[1]:
            # print("same col")
            ### moving in the same column
            checkpath_col = self.board[:,newpos[1]]
            if oldpos[0] < newpos[0]:
                start = oldpos[0] + 1
                end = newpos[0]
            else:
                start = 7 - (oldpos[0] - 1)
                end = 7 - newpos[0]
                checkpath_col = checkpath_col[::-1]
            return self.check_if_piece_on_1darray(checkpath_col, start, end)

    def check_diagonal(self, oldpos, newpos):
        ### checks whether a move along a diagonal is valid
        fliparray = np.fliplr(self.board)
        idx = np.array(['{0}{1}'.format(i, j) for i in range(8) for j in range(8)]).reshape((8, 8))
        diag = np.diagonal(idx, oldpos[1] - oldpos[0])
        flipdiag = np.diagonal(np.fliplr(idx), 7 - (oldpos[0] + oldpos[1]))
        if (newpos[0] - newpos[1]) == (oldpos[0] - oldpos[1]):
            ### the old and new positions are along the diagonal (upper left to lower right)
            # print("normal diag")
            arr = diag
            check_diag = np.diagonal(self.board, oldpos[1] - oldpos[0])
            ### get the correct indices for start- and endfield
            if oldpos[0] < newpos[0]:
                startfield = '{0}{1}'.format(oldpos[0] + 1, oldpos[1] + 1)
                endfield = '{0}{1}'.format(newpos[0], newpos[1])
            else:
                startfield = '{0}{1}'.format(oldpos[0] - 1, oldpos[1] - 1)
                endfield = '{0}{1}'.format(newpos[0], newpos[1])
                check_diag = check_diag[::-1]
                arr = arr[::-1]

        else:
            arr = flipdiag
            check_diag = np.diagonal(fliparray, 7 - (oldpos[0] + oldpos[1]))
            # print("flip diag")
            ### get the correct indices for start- and endfield
            if oldpos[0] < newpos[0]:
                startfield = '{0}{1}'.format(oldpos[0] + 1, oldpos[1] - 1)
                endfield = '{0}{1}'.format(newpos[0], newpos[1])
            else:
                startfield = '{0}{1}'.format(oldpos[0] - 1, oldpos[1] + 1)
                endfield = '{0}{1}'.format(newpos[0], newpos[1])
                check_diag = check_diag[::-1]
                arr = arr[::-1]
        ### convert from indices on the board to indices in the flip/diagonal array
        start, end = None, None
        for j in range(len(arr)):
            if arr[j] == startfield:
                start = j
            elif arr[j] == endfield:
                end = j
        if startfield == endfield:
            end = start
        if start != None and end != None:
            return self.check_if_piece_on_1darray(check_diag, start, end)
        else:
            print("Indices for diagonal not found!")



    def save_move(self):
        """saves move to game database"""



    def ai_move(self):
        """AI does a move"""
        return 1

    def check_game_status(self):
        """Checks game status, whether win/loss/remis
        """
        if 'King' not in self.white:
            print('Black wins')
            return 1
        elif 'King' not in self.black:
            print('White wins')
            return 1
        else:
            return 0

    def read_input(self):
        """Reads input using a mouse click or chess notation
        """
        return 1
    def test(self):
        self.field['a8'][1] = "box"



