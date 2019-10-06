#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 14 21:10:17 2018

@author: chris
This file serves the complete game engine
"""
import numpy as np
import uuid
import datetime

import game_lib

### Image file names used for the UI
images = dict({'whitePawn':'Chess_plt60.png', 'whiteKnight':'Chess_nlt60.png', 'whiteBishop':'Chess_blt60.png', \
               'whiteRook': 'Chess_rlt60.png', 'whiteQueen':'Chess_qlt60.png', 'whiteKing':'Chess_klt60.png',\
                'blackPawn':'Chess_pdt60.png', 'blackKnight':'Chess_ndt60.png', 'blackBishop':'Chess_bdt60.png', \
               'blackRook': 'Chess_rdt60.png', 'blackQueen':'Chess_qdt60.png', 'blackKing':'Chess_kdt60.png'})



class ChessGame:
    """
        This class is used to initialize a chess game. It has to be called once and initializes the board configuration
    """
    def __init__(self, directory_movehistory):
        """

        :param directory_movehistory: directory, where to save the sequence of moves
        """
        now = datetime.datetime.now()
        directory_movehistory = directory_movehistory if directory_movehistory[-1] == "/" else directory_movehistory + "/"
        self.filename_movehistory = directory_movehistory + str(now.strftime("%Y-%m-%d_%H:%M:%S")) + "_" + str(uuid.uuid4().hex) + ".txt"
        self.moves = []
        self.white2move = True
        self.num_moves = 0
        self.num_same_moves = 0
        ###  array of every boardDict on the board: Boolean variable decides whether there is a piece on the given boardDict
        self.board = np.full((8,8), None)
        ###  dicts of all pieces of white and black and their position on the board: used to evaluate winner
        self.white = dict({'Pawn0' : 'a2', 'Pawn1':'b2', 'Pawn2':'c2', 'Pawn3':'d2', 'Pawn4':'e2', \
                           'Pawn5': 'f2', 'Pawn6':'g2', 'Pawn7':'h2', 'Rook0': 'a1', 'Rook1':'h1',\
                           'Knight0':'b1', 'Knight1':'g1', 'Bishop0':'c1', 'Bishop1':'f1', \
                           'Queen':'d1', 'King':'e1'})
        self.black = dict({'Pawn0': "a7", 'Pawn1': 'b7', 'Pawn2': 'c7', 'Pawn3': 'd7', 'Pawn4': 'e7', \
                           'Pawn5': 'f7', 'Pawn6': 'g7', 'Pawn7': 'h7', 'Rook0': 'a8', 'Rook1': 'h8', \
                           'Knight0': 'b8', 'Knight1': 'g8', 'Bishop0': 'c8', 'Bishop1': 'f8', \
                           'Queen': 'd8', 'King': 'e8'})
        # self.white = dict({'King':'e4', 'Pawn1':'d6'})
        # self.black = dict({'King': 'e2', 'Queen': 'f2'})
        self.piece_chosen = False
        self.chosen_piece_position = ''
        self.piece_type = ''
        ### First item checks if en passant move is possible (when the previous move was a double move)
        ### Second item checks whether a piece, which was captured en passant, has to be removed
        self.en_passant = False
        self.en_passant_possible = [False, False]
        self.capture = False
        ### counts number of promotions for both players
        self.num_promos = [0, 0]
        ### checks if castling is possible [white:short, white: long, black:short, black:long]
        self.castling = [True, True, True, True]
        self.castle = -1

    def generate_html_config(self):
        """
        The correct html configuration is created depending on, which player's turn we have
        :return boardDict: dictionary of the board configuration used for the HTML template
        """
        boardDict = game_lib.create_boardDict_forHTML(self.board)
        boardDict = boardDict if self.white2move == True else game_lib.invert_boardDict(boardDict)
        return boardDict

    def set_initial_pieces(self, type=None):
        """
        Places all figures on the board for a classic game of chess
        :param type (string): One can use different types of initial piece arangement, which is
                            stored in game_lib.py -> use for testing purposes
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

        # self.board = np.full((8, 8), None)
        # self.board[4][4] = 'wKing'
        # self.board[6][4] = 'bKing'
        # self.board[2][3] = 'wPawn1'
        # self.board[6][5] = 'bQueen'


    def human_move(self, string):
        """Human does a move"""
        promoted_piece = 'w' if self.white2move == True else 'b'
        if string[0] in ['N', 'B', 'R', 'Q']:
            if string[0] == 'N':
                promoted_piece += 'Knight'
            elif string[0] == 'B':
                promoted_piece += 'Bishop'
            elif string[0] == 'R':
                promoted_piece += 'Rook'
            elif string[0] == 'Q':
                promoted_piece += 'Queen'
            promotion = [True, promoted_piece]
            string = string[1:]
        else:
            promotion = [False, None]
        if len(string)>2:
            ### there is a piece on the selected boardDict
            piecepos = string[:2]
            piecetype = string[3:]
            if self.piece_chosen == True:
                if (self.white2move == True and piecetype[0] != 'w') or (self.white2move == False and piecetype[0] != 'b'):
                    self.make_move(string, promotion)
                else:
                    print("Wrong piece selected - you cannot move onto your own piece!")
                    self.piece_chosen = False
                    self.chosen_piece_position = ''
                    self.piece_type = ''

            elif self.piece_chosen == False:
                self.chosen_piece_position = string[:2]
                self.piece_type = string[3:]
                pos = chess2computer(self.chosen_piece_position)
                if (self.white2move == True and self.piece_type[0] != 'w') or (self.white2move == False and self.piece_type[0] != 'b'):
                    print("Wrong piece selected!")
                    self.piece_chosen = False
                    self.chosen_piece_position = ''
                    self.piece_type = ''
                else:
                    self.piece_chosen = True
        else:
            if self.piece_chosen == True:
                self.make_move(string, promotion)
            else:
                print("You have to choose a piece first")
        self.check_game_status()


    def make_move(self, string, promotion):
        oldpos = chess2computer(self.chosen_piece_position)
        newpos = chess2computer(string[:2])
        params = [self.chosen_piece_position, self.piece_type, string, promotion, self.board, \
                  self.white, self.black, self.en_passant_possible, self.num_promos]
        color2move = 'w' if self.white2move == True else 'b'
        color2check = color2move
        if self.check_if_valid_move(params, oldpos, newpos) == True and self.king_in_check(params, color2check, color2move, False) == False:
            params[7] = self.en_passant_possible
            params = self.make_atomic_move(params, False)
            ### adjust board layout and save move
            if self.capture == True:
                action = 'x'
                if promotion[0] == True:
                    action += 'PR:{0}'.format(promotion[1])
                if self.en_passant == True:
                    action += 'e.p.'
            else:
                if promotion[0] == True:
                    action = 'PR:{0}'.format(promotion[1])
                else:
                    if self.castle == 0:
                        action = '0-0'
                    elif self.castle == 1:
                        action = '0-0-0'
                    else:
                        action = ''
            params = [self.chosen_piece_position, self.piece_type, string, promotion, self.board, \
                      self.white, self.black, self.en_passant_possible, self.num_promos]
            color2check = 'b' if self.white2move == True else 'w'
            if self.king_in_check(params, color2check, color2move, False) == True:
                action += '+'
            self.save_move(oldpos, newpos, action)
            self.white2move = True if self.white2move == False else False
            ### No piece selected after move
            self.piece_chosen = False
            self.capture = False
            self.castle = -1
            self.chosen_piece_position = ''
            self.piece_type = ''
            # self.white2move = True if self.white2move == False else False
        else:
            self.piece_chosen = False
            self.chosen_piece_position = ''
            self.piece_type = ''

    def make_atomic_move(self, params, virtual):
        """atomic function making a move on some virtual or real board-layout
            make virtual move: virtual = True: make a move on a virtual (copied) board
            make real move: virtual = False: make a move on the real board"""
        piece_pos = params[0]
        piece_type = params[1]
        string = params[2]
        if virtual == True:
            promotion = params[3].copy()
            board = params[4].copy()
            white = params[5].copy()
            black = params[6].copy()
            en_passant_possible = params[7].copy()
            num_promos = params[8].copy()
        elif virtual == False:
            promotion = params[3]
            board = params[4]
            white = params[5]
            black = params[6]
            en_passant_possible = params[7]
            num_promos = params[8]
        oldpos = chess2computer(piece_pos)
        newpos = chess2computer(string[:2])
        piece = board[oldpos[0]][oldpos[1]]
        if board[newpos[0]][newpos[1]] == None:
            ### set piece to new boardDict
            board[newpos[0]][newpos[1]] = piece
            if piece[0] == 'w':
                white[piece[1:]] = '{0}{1}'.format(computer2chess(newpos)[1], computer2chess(newpos)[0])
                if virtual == False:
                    ## white castling
                    if 'King' in piece and newpos[1] == 2 and self.castling[1] == True:
                        ## white castling long
                        board[7][3] = board[7][0]
                        board[7][0] = None
                        white['Rook0'] = 'd1'
                        self.castle = 1
                        self.castling[1] = False
                    elif 'King' in piece and newpos[1] == 6 and self.castling[0] == True:
                        ## white castling short
                        board[7][5] = board[7][7]
                        board[7][7] = None
                        white['Rook1'] = 'f1'
                        self.castle = 0
                        self.castling[0] = False
                    if 'King' in piece or 'Rook0' in piece or 'Rook1' in piece:
                        self.castling[0] = False
                        self.castling[1] = False

            elif piece[0] == 'b':
                black[piece[1:]] = '{0}{1}'.format(computer2chess(newpos)[1], computer2chess(newpos)[0])
                if virtual == False:
                    ## black castling
                    if 'King' in piece and newpos[1] == 2 and self.castling[3] == True:
                        ## black castling long
                        board[0][3] = board[0][0]
                        board[0][0] = None
                        white['Rook0'] = 'd8'
                        self.castle = 1
                        self.castling[3] = False
                    elif 'King' in piece and newpos[1] == 6 and self.castling[2] == True:
                        ## black castling short
                        board[0][5] = board[0][7]
                        board[0][7] = None
                        white['Rook1'] = 'f8'
                        self.castle = 0
                        self.castling[2] = False
                    if 'King' in piece or 'Rook0' in piece or 'Rook1' in piece:
                        self.castling[2] = False
                        self.castling[3] = False



        else:
            if piece_type[0] == 'w':
                captured_piece = board[newpos[0]][newpos[1]][1:]
                white[piece[1:]] = '{0}{1}'.format(computer2chess(newpos)[1], computer2chess(newpos)[0])
                del black[captured_piece]
                position = computer2chess('{0}{1}'.format(newpos[0], newpos[1]))
            elif piece_type[0] == 'b':
                captured_piece = board[newpos[0]][newpos[1]][1:]
                black[piece[1:]] = '{0}{1}'.format(computer2chess(newpos)[1], computer2chess(newpos)[0])
                del white[captured_piece]
            board[newpos[0]][newpos[1]] = piece
        ### remove piece from old boardDict
        board[oldpos[0]][oldpos[1]] = None
        if en_passant_possible[1] == True:
            ### remove piece, which was captured en passant, too
            if piece[0] == 'w':
                captured_piece = board[3][newpos[1]][1:]
                del black[captured_piece]
                board[3][newpos[1]] = None
                self.en_passant = True
            elif piece[0] == 'b':
                captured_piece = board[4][newpos[1]][1:]
                del white[captured_piece]
                board[4][newpos[1]] = None
                self.en_passant = True
            en_passant_possible = [False, False]
        ### promote a pawn
        if promotion[0] == True:
            board[newpos[0]][newpos[1]] = promotion[1]+str(num_promos[1] + 2)
            if self.white2move == True:
                # del black[piece]
                position = computer2chess('{0}{1}'.format(newpos[0], newpos[1]))
                del white[piece[1:]]
                white[promotion[1][1:] + str(num_promos[0] + 2)] = '{0}{1}'.format(position[1], position[0])
                num_promos[0] += 1
            elif self.white2move == False:
                # del white[piece]
                position = computer2chess('{0}{1}'.format(newpos[0], newpos[1]))
                del black[piece[1:]]
                black[promotion[1][1:] + str(num_promos[1] + 2)] = '{0}{1}'.format(position[1], position[0])
                num_promos[1] += 1
        params = [piece_pos, piece_type, string, promotion, board, \
                  white, black, en_passant_possible, num_promos]
        return params

    def king_in_check(self, params, color2check, color2move, castling):
        """checks if after a given valid move (no castling -> is checked in valid_move) the king of color is in check: """
        if color2move != color2check:
            field = self.white['King'] if color2check == 'w' else self.black['King']
        else:
            if color2move == 'w':
                if 'wKing' in params[1] and castling == False:
                    ## king move without castling
                    field = params[2]
                else:
                    ### no king move
                    field = self.white['King']
            else:
                if 'bKing' in params[1] and castling == False:
                    ## king move without castling
                    field = params[2]
                else:
                    ## no king move
                    field  = self.black['King']
        return self.field_in_check(params, field, color2check, color2move, True)

    def field_in_check(self, params, field, color2check, color2move, virtual):
        """checks if after a given valid move some boardDict is in check:
            False: move valid   True: move not valid because of check"""
        ### check variable: [ pawns/kings, rooks/queens, bishops/queens, knights ]
        check = np.array([ False, False, False, False ])
        myfield = chess2computer(field)
        if color2check != color2move:
            color_opponent = 'w' if color2move == 'w' else 'b'
            params = params
        else:
            color_opponent = 'w' if color2move == 'b' else 'b'
            params = self.make_atomic_move(params, virtual)
        board = params[4].copy()
        ### check one boardDict around myfield (pawn or king)
        idx = []
        fields = [[myfield[0] + x, myfield[1] + y] for x in [-1, 0, +1] for y in [-1, 0, +1]]
        del_idx = []
        for j, field in enumerate(fields):
            if (np.array(field) > 7).any() or (np.array(field) < 0).any() or field == myfield:
                del_idx.append(j)
        for j in del_idx[::-1]:
            del fields[j]
        for field in fields:
            piece = board[field[0]][field[1]]
            if piece == None:
                continue
            else:
                if board[myfield[0]][myfield[1]] != None:
                    ## there is a king on myfield: myfield color = kingcolor
                    color_king = board[myfield[0]][myfield[1]][0]
                    if color_king == 'w':
                        if (field[0] < myfield[0]) and field[1] != myfield[1] and color_opponent+'Pawn' in piece:
                            ### black pawn
                            check[0] = True
                        if color_opponent+'King' in piece:
                            check[0] = True
                    else:
                        if (field[0] > myfield[0]) and field[1] != myfield[1] and color_opponent + 'Pawn' in piece:
                            ### white pawn
                            check[0] = True
                        if color_opponent+'King' in piece:
                            check[0] = True
                else:
                    ## there is an empty boardDict to check in case of castling (get "myfield color" from player to move
                    if color2move == 'w':
                        if (field[0] < myfield[0]) and field[1] != myfield[1] and color_opponent+'Pawn' in piece:
                            ### black pawn
                            check[0] = True
                        if color_opponent+'King' in piece:
                            check[0] = True
                    else:
                        if (field[0] > myfield[0]) and field[1] != myfield[1] and color_opponent + 'Pawn' in piece:
                            ### white pawn
                            check[0] = True
                        if color_opponent+'King' in piece:
                            check[0] = True

        ### check on a straight line (rook or queen)
        idx = []
        row = myfield[0]
        col = myfield[1]
        for i,line in enumerate([board[row], board[:,col]]):
            ## check whether a rook or queen is on a straight line
            idxKing = myfield[(i+1)%2]
            for j in range(8):
                if line[j] == None:
                    continue
                if color_opponent+'Rook' in line[j] or color_opponent+'Queen' in line[j]:
                    if i==0:
                        idx.append([row, j])
                    else:
                        idx.append([j, col])
        for myidx in idx:
            check[1] = self.check_straight(board, myfield, myidx, virtual=True)
        ### check on a diagonal (bishop or queen)
        idx = []
        fliparray = np.fliplr(board)
        idx_arr = np.array(['{0}{1}'.format(i, j) for i in range(8) for j in range(8)]).reshape((8, 8))
        diag = np.diagonal(idx_arr, myfield[1] - myfield[0])
        flipdiag = np.diagonal(np.fliplr(idx_arr), 7 - (myfield[0] + myfield[1]))
        for i, line in enumerate([diag, flipdiag]):
            arr = np.diagonal(board, myfield[1] - myfield[0]) if i == 0 else np.diagonal(fliparray, 7 - (myfield[0] + myfield[1]))
            for j, index in enumerate(line):
                if arr[j] == None:
                    continue
                else:
                    piece = arr[j]
                if color_opponent+'Bishop' in piece or color_opponent+'Queen' in piece:
                    idx.append([int(index[0]), int(index[1])])
        for myidx in idx:
            check[2] = self.check_diagonal(board, myfield, myidx, virtual=True)
        ### check for knights
        fields = [np.array(myfield) + np.array(x) for x in \
                  [[-2, -1], [-2, +1], [+2, -1], [+2, +1], [+1, +2], [-1, +2], [+1, -2], [-1, -2]]]
        del_idx = []
        for j, field in enumerate(fields):
            if (np.array(field) > 7).any() or (np.array(field) < 0).any():
                del_idx.append(j)
        for j in del_idx[::-1]:
            del fields[j]
        for field in fields:
            piece = board[field[0]][field[1]]
            if piece == None:
                continue
            else:
                if color_opponent + 'Knight' in piece:
                    check[3] = True
        if check.any() == True:
            print("You are in check!!!")
        return check.any()


    def check_if_valid_move(self, params, oldpos, newpos):
        piece_on_newpos = self.board[newpos[0]][newpos[1]]
        ### Rules for Kings
        if 'King' in self.piece_type:
            idx = [0, 1] if self.white2move == True else [2, 3]
            check = []
            if abs(newpos[1] - oldpos[1]) == 2:
                color2move = 'w' if self.white2move == True else 'b'
                color2check = color2move
                if self.king_in_check(params, color2check, color2move, True) == False:
                    ## check if king is in check before castling
                    if (newpos[0] == 0 or newpos[0] == 7):
                        if newpos[1] == 6 and self.castling[idx[0]] == True:
                            ### short castling
                            for j in [5, 6]:
                                myfield = '{0}{1}'.format(list('abcdefgh')[j], 8-newpos[0])
                                if self.field_in_check(params, myfield, color2check, color2move, True) == False and \
                                    self.board[newpos[0]][j] == None:
                                    check.append(True)
                                else:
                                    check.append(False)
                            if (np.array(check) == True).all():
                                self.en_passant_possible = [False, False]
                                return True
                            else:
                                return False
                        elif newpos[1] == 2 and self.castling[idx[1]] == True:
                            ### long castling
                            for j in [2, 3]:
                                myfield = '{0}{1}'.format(list('abcdefgh')[j], 8-newpos[0])
                                if self.field_in_check(params, myfield, color2check, color2move, True) == False and \
                                    self.board[newpos[0]][j] == None:
                                    check.append(True)
                                else:
                                    check.append(False)
                            if (np.array(check) == True).all():
                                self.en_passant_possible = [False, False]
                                return True
                            else:
                                return False
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
            elif abs(newpos[1] - oldpos[1]) > 2 or abs(newpos[0] - oldpos[0]) > 1:
                return False
            else:
                if piece_on_newpos == None:
                    for j in idx:
                        self.castling[j] = False
                    self.en_passant_possible = [False, False]
                    return True
                else:
                    if self.piece_type[0] == piece_on_newpos[0]:
                        return False
                    else:
                        self.capture = True
                        for j in idx:
                            self.castling[j] = False
                        self.en_passant_possible = [False, False]
                        return True
        ### Rules for Queens
        elif 'Queen' in self.piece_type:
            if abs(newpos[0]-oldpos[0]) == abs(newpos[1]-oldpos[1]):
                ### moving diagonal
                if self.check_diagonal(self.board, oldpos, newpos, False) == True:
                    self.en_passant_possible = [False, False]
                    return True
                else:
                    return False
            else:
                if self.check_straight(self.board, oldpos, newpos, False) == True:
                    self.en_passant_possible = [False, False]
                    return True
                else:
                    return False

        elif 'Rook' in self.piece_type:
            validmove = self.check_straight(self.board, oldpos, newpos, False)
            if validmove == True:
                if self.white2move == True:
                    self.en_passant_possible = [False, False]
                    if 'Rook0' in self.piece_type:
                       ## short castling not possible anymore
                       self.castling[0] = False
                    elif 'Rook1' in self.piece_type:
                       ## long castling not possible anymore
                       self.castling[1] = False
                else:
                    self.en_passant_possible = [False, False]
                    if 'Rook1' in self.piece_type:
                        ## short castling not possible anymore
                        self.castling[2] = False
                    elif 'Rook0' in self.piece_type:
                        ## long castling not possible anymore
                        self.castling[3] = False
            return validmove

        elif 'Bishop' in self.piece_type:
            if abs(newpos[0] - oldpos[0]) == abs(newpos[1] - oldpos[1]):
                if self.check_diagonal(self.board, oldpos, newpos, False) == True:
                    self.en_passant_possible = [False, False]
                    return True
                else:
                    return False
            else:
                return False
        elif 'Knight' in self.piece_type:
            moves = [[-2, -1], [-2, +1], [+2, -1], [+2, +1], [+1, +2], [-1, +2], [+1, -2], [-1, -2]]
            for x in moves:
                if (np.array(newpos) == (np.array(oldpos) + np.array(x))).all():
                    if self.board[newpos[0]][newpos[1]] != None:
                        if self.board[newpos[0]][newpos[1]][0] != self.piece_type[0]:
                            self.capture = True
                            self.en_passant_possible = [False, False]
                            return True
                        # else:
                            # continue
                    else:
                        self.en_passant_possible = [False, False]
                        return True
                else:
                    continue
            return False

        ### Rules for pawns
        elif 'Pawn' in self.piece_type:
            if abs(newpos[1]-oldpos[1])>1:
                ### not more than 1 boardDict to the side possible
                return False
            if abs(newpos[1]-oldpos[1]) == 1:
                if piece_on_newpos == None:
                    ### empty boardDict on the side
                    if self.piece_type[0] == 'w':
                        if newpos[0] == 2 and piece_on_newpos == None and \
                                'bPawn' in self.board[3][newpos[1]] and self.en_passant_possible[0] == True:
                            ### en passante capture by white: correct row with empty target boardDict and
                            ### piece to capture has to be a pawn, which moved in the last move
                            self.capture = True
                            self.en_passant_possible = [False, True]
                            return True
                        else:
                            return False
                    elif self.piece_type[0] == 'b':
                        if newpos[0] == 5 and piece_on_newpos == None and \
                                'wPawn' in self.board[4][newpos[1]] and self.en_passant_possible[0] == True:
                            ### en passante capture by black: correct row with empty target boardDict and
                            ### piece to capture has to be a pawn, which moved in the last move
                            self.en_passant_possible = [False, True]
                            self.capture = True
                            return True
                        else:
                            return False
                elif piece_on_newpos[0] == self.piece_type[0]:
                    ### capture of piece with same color not possible
                    return False
                elif piece_on_newpos[0] != self.piece_type[0]:
                    if self.piece_type[0] == 'w':
                        if newpos[0]<oldpos[0]:
                            ## capture is only possible in forward direction
                            self.capture = True
                            self.en_passant_possible = [False, False]
                            return True
                        else:
                            return False
                    elif self.piece_type[0] == 'b':
                        if newpos[0]>oldpos[0]:
                            ## capture is only possible in forward direction
                            self.capture = True
                            self.en_passant_possible = [False, False]
                            return True
                        else:
                            return False

            else:
                if self.piece_type[0] == 'w':
                    if oldpos[0]-newpos[0] == 2:
                        if oldpos[0] == 6:
                            ### double move by white
                            self.en_passant_possible = [True, False]
                            return True
                        else:
                            return False
                    elif (oldpos[0]-newpos[0] == 1) and piece_on_newpos == None:
                        self.en_passant_possible = [False, False]
                        return True
                    else:
                        return False
                if self.piece_type[0] == 'b':
                    if newpos[0]-oldpos[0] == 2:
                        if oldpos[0] == 1:
                            self.en_passant_possible = [True, False]
                            ### double move by white
                            return True
                        else:
                            return False
                    elif (newpos[0]-oldpos[0] == 1) and piece_on_newpos == None:
                        self.en_passant_possible = [False, False]
                        return True
                    else:
                        return False

    def check_if_piece_on_1darray(self, array, start, end, virtual):
        """checks whether a move  is  valid if performed along the array direction
        in array is important: index(oldposition) < index(newposition) """
        for i in range(start, end + 1):
            if i == end:
                if array[i] == None:
                    return True
                else:
                    if array[start-1] == None:
                        color = self.piece_type[0]
                    else:
                        color = array[start - 1][0]
                    if array[i][0] != color:
                        if virtual == False:
                            self.capture = True
                        return True
                    else:
                        return False
            else:
                if array[i] == None:
                    continue
                else:
                    return False

    def check_straight(self, board, oldpos, newpos, virtual = False):
        ### checks if a straight move along a row or column is valid
        if newpos[0] == oldpos[0]:
            ### moving in the same row
            checkpath_row = board[newpos[0]]
            if oldpos[1] < newpos[1]:
                start = oldpos[1] + 1
                end = newpos[1]
            else:
                start = 7 - (oldpos[1] - 1)
                end = 7 - newpos[1]
                checkpath_row = checkpath_row[::-1]
            return self.check_if_piece_on_1darray(checkpath_row, start, end, virtual)

        elif newpos[1] == oldpos[1]:
            ### moving in the same column
            checkpath_col = board[:,newpos[1]]
            if oldpos[0] < newpos[0]:
                start = oldpos[0] + 1
                end = newpos[0]
            else:
                start = 7 - (oldpos[0] - 1)
                end = 7 - newpos[0]
                checkpath_col = checkpath_col[::-1]
            return self.check_if_piece_on_1darray(checkpath_col, start, end, virtual)

    def check_diagonal(self, board, oldpos, newpos, virtual = False):
        ### checks whether a move along a diagonal is valid
        fliparray = np.fliplr(board)
        idx = np.array(['{0}{1}'.format(i, j) for i in range(8) for j in range(8)]).reshape((8, 8))
        diag = np.diagonal(idx, oldpos[1] - oldpos[0])
        flipdiag = np.diagonal(np.fliplr(idx), 7 - (oldpos[0] + oldpos[1]))
        if (newpos[0] - newpos[1]) == (oldpos[0] - oldpos[1]):
            ### the old and new positions are along the diagonal (upper left to lower right)
            arr = diag
            check_diag = np.diagonal(board, oldpos[1] - oldpos[0])
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
            return self.check_if_piece_on_1darray(check_diag, start, end, virtual)
        else:
            print("Indices for diagonal not found!")



    def save_move(self, oldpos, newpos, action):
        """saves move to game database"""
        piece = self.piece_type
        oldpos = computer2chess(oldpos)
        newpos = computer2chess(newpos)
        castling = False
        if 'Pawn' in piece:
            add = ''
        elif 'Knight' in piece:
            add = 'N'
        elif 'Bishop' in piece:
            add = 'B'
        elif 'Rook' in piece:
            add = 'R'
        elif 'Queen' in piece:
            add = 'Q'
        elif 'King' in piece:
            add = 'K'
        if action == '':
            action = ' '
            last = ''
            check = ''
        else:
            if action[0] == 'x':
                if action[-1] == '+':
                    check = '+'
                    action = action[:-1]
                else:
                    check = ''
                if 'e.p.' in action:
                    action = 'x'
                    last = 'e.p.'
                else:
                    last = ''
            else:
                last = ''
                if action[-1] == '+':
                    check = '+'
                    action = action[:-1]
                else:
                    check = ''
                if '0-0' in action:
                    castling = True
                else:
                    castling = False
                    action = ' '
        if 'PR:' in action:
            if action[-1] == '+':
                check = '+'
                action = action[:-1]
            else:
                check = ''
            if 'Knight' in action:
                last2 = '(N)'
            elif 'Bishop' in action:
                last2 = '(B)'
            elif 'Rook' in action:
                last2 = '(R)'
            elif 'Queen' in action:
                last2 = '(Q)'
            else:
                last2 = ''
            if action[0] == 'x':
                action = 'x'
            else:
                action = ' '
        else:
            last2 = ''
        if castling == True:
            str = action + check
        else:
            str = add + '{0}{1}'.format(oldpos[1], oldpos[0]) + action + '{0}{1}'.format(newpos[1], newpos[0]) + last + last2 + check
        if self.white2move == True:
            self.moves.append([str, ''])
        else:
            self.moves[self.num_moves][1] = str
            self.num_moves += 1
            with open(self.filename_movehistory, 'a') as dfile:
                dfile.write("{0}:{1}___{2}\n".format(self.num_moves, self.moves[-1][0], self.moves[-1][1]))


    def ai_move(self):
        """AI does a move"""
        return 1

    def check_game_status(self):
        #TODO
        """Checks game status, whether win/loss/remis
        """
        if 'King' not in self.white:
            print('Black wins')
            return "win:b"
        elif 'King' not in self.black:
            print('White wins')
            return "win:w"
        # elif self.check_remis == True:
        #     print("Remis!")
        #     return("draw")
        else:
            return 0
    # def resign(self, player):
        ## not ready!!!
        #TODO
        """Some human player resigns"""
        #     if player == 'w' else 'Black resigns. White wins!'





