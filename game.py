import random
import numpy as np

class Game:

    def __init__(self):
        self.citadels = [[0,3], [0,4], [0,5], [1,4], 
                         [8,3], [8,4], [8,5], [7,4], 
                         [3,8], [4,8], [5,8], [4,7], 
                         [3,0], [4,0], [5,0], [4,1]]
                         
        self.safe_citadels = [[0,3], [0,4], [0,5], 
                              [8,3], [8,4], [8,5], 
                              [3,8], [4,8], [5,8], 
                              [3,0], [4,0], [5,0]]
        
        self.throne = [4,4]

        self.escapes = [[0,1],[0,2],[0,6],[0,7], 
                        [8,1],[8,2],[8,6],[8,7],
                        [1,0],[2,0],[6,0],[7,0],
                        [1,8],[2,8],[6,8],[7,8]]

        self.zobrist_table = [[[random.randint(1,2**64 - 1) for i in [0, 1, 2]]for j in range(9)]for k in range(9)]


    def actions(self, state, color, pawns):
        moves = []
        owned = pawns[1] + pawns[2] if color == 1 else pawns[0]

        for p in owned:
            row, col = p[0], p[1]
            mcol = col - 1
            while mcol >= 0:
                if [row, mcol] == self.throne:
                    break
                if ([row, mcol] in self.citadels and
                    (color == 1 or [row, col] not in self.citadels)):
                    break
                if state[row][mcol] != 0:
                    break
                moves.append([[row, col], [row, mcol]])
                mcol -= 1
            mcol = col +1
            while mcol < 9:
                if [row, mcol] == self.throne:
                    break
                if ([row, mcol] in self.citadels and
                    (color == 1 or [row, col] not in self.citadels)):
                    break
                if state[row][mcol] != 0:
                    break
                moves.append([[row, col], [row, mcol]])
                mcol += 1

            mrow = row - 1
            while mrow >= 0:
                if [mrow, col] == self.throne:
                    break
                if ([mrow, col] in self.citadels and
                    (color == 1 or [row, col] not in self.citadels)):
                    break
                if state[mrow][col] != 0:
                    break
                moves.append([[row, col], [mrow, col]])
                mrow -= 1
            mrow = row +1
            while mrow < 9:
                if [mrow, col] == self.throne:
                    break
                if ([mrow, col] in self.citadels and
                    (color == 1 or [row, col] not in self.citadels)):
                    break
                if state[mrow][col] != 0:
                    break
                moves.append([[row, col], [mrow, col]])
                mrow += 1

        return moves


    def compute_state(self, state):
        pawns = [[], [], []]
        hash_ = 0
        for i in range(9):
            for j in range(9):
                if state[i][j] == 0:
                    continue
                piece = state[i][j] if state[i][j] != -1 else 0
                hash_ ^= self.zobrist_table[i][j][piece]
                pawns[piece].append([i, j])

        return pawns, hash_


    def update_state(self, state, hash_, pawns, move, color):
        from_ = [move[0][0], move[0][1]]
        piece = state[from_[0]][from_[1]] if state[from_[0]][from_[1]] != -1 else 0
        to_ = [move[1][0], move[1][1]]
        
        next_state = self.deepcopy(state)
        next_pawns = [self.deepcopy(pawns[0]), self.deepcopy(pawns[1]), self.deepcopy(pawns[2])]

        next_state[to_[0]][to_[1]] = state[from_[0]][from_[1]]
        next_state[from_[0]][from_[1]] = 0

        next_pawns[piece].remove(from_)
        next_pawns[piece].append(to_)

        next_hash = hash_ ^ self.zobrist_table[from_[0]][from_[1]][piece]
        next_hash ^= self.zobrist_table[to_[0]][to_[1]][piece]

        if color == 1:
            next_state, captured = self._white_capture_black(next_state, move)
            if captured != None:
                next_hash ^= self.zobrist_table[captured[0]][captured[1]][0]
                next_pawns[0].remove(captured)
            terminal = self._king_escape(next_state)
        else:
            next_state, captured = self._black_capture_white(next_state, move)
            if captured != None:
                next_hash ^= self.zobrist_table[captured[0]][captured[1]][1]
                next_pawns[1].remove(captured)
            terminal = self._capture_king(next_state, next_pawns)

        return next_state, next_hash, next_pawns, terminal


    def _white_capture_black(self, state, move):
        my_row = move[1][0]
        my_column =  move[1][1]

        #Capture Down
        if (my_row < 7 
            and state[my_row + 1][my_column] == -1 
            and not [my_row + 1, my_column] in self.safe_citadels
            and ( state[my_row + 2][my_column] == 1 
                or [my_row + 2, my_column] in self.citadels
                or [my_row + 2, my_column] == self.throne)): 
            
            state[my_row + 1][my_column] = 0
            return state, [my_row + 1, my_column]

        #Capture Up
        if (my_row > 1 
            and state[my_row - 1][my_column] == -1
            and not [my_row - 1, my_column] in self.safe_citadels 
            and ( state[my_row - 2][my_column] == 1 
                or [my_row - 2, my_column] in self.citadels
                or [my_row - 2, my_column] == self.throne)):
            
            state[my_row - 1][my_column] = 0
            return state, [my_row - 1, my_column]

        #Capture Left
        if (my_column > 1 
            and state[my_row][my_column - 1] == -1 
            and not [my_row, my_column - 1] in self.safe_citadels
            and ( state[my_row][my_column - 2]  == 1 
                or [my_row, my_column - 2] in self.citadels
                or [my_row, my_column - 2] == self.throne)):
            
            state[my_row][my_column - 1]  = 0
            return state, [my_row, my_column -1]
        
        #Capture Right
        if (my_column < 7 
            and state[my_row][my_column + 1] == -1 
            and not [my_row, my_column + 1] in self.safe_citadels
            and ( state[my_row][my_column + 2]  == 1 
                or [my_row, my_column + 2] in self.citadels
                or [my_row, my_column + 2] == self.throne)):
            
            state[my_row][my_column + 1]  = 0
            return state, [my_row, my_column + 1]

        return state, None


    def _black_capture_white(self, state, move):
        my_row = move[1][0]
        my_column =  move[1][1]

        #Capture Down
        if (my_row < 7 
            and state[my_row + 1][my_column] == 1 
            and ( state[my_row + 2][my_column] == -1 
                or [my_row + 2, my_column] in self.citadels
                or [my_row + 2, my_column] == self.throne)): 
            
            state[my_row + 1][my_column] = 0
            return state, [my_row + 1, my_column]

        #Capture Up
        if (my_row > 1 
            and state[my_row - 1][my_column] == 1 
            and ( state[my_row - 2][my_column] == -1 
                or [my_row - 2, my_column] in self.citadels
                or [my_row - 2, my_column] == self.throne)):
            
            state[my_row - 1][my_column] = 0
            return state, [my_row - 1, my_column]

        #Capture Left
        if (my_column > 1 
            and state[my_row][my_column - 1] == 1 
            and ( state[my_row][my_column - 2]  == -1 
                or [my_row, my_column - 2] in self.citadels
                or [my_row, my_column - 2] == self.throne)):
            
            state[my_row][my_column - 1]  = 0
            return state, [my_row, my_column -1]
        
        #Capture Right
        if (my_column < 7 
            and state[my_row][my_column + 1] == 1 
            and ( state[my_row][my_column + 2]  == -1 
                or [my_row, my_column + 2] in self.citadels
                or [my_row, my_column + 2] == self.throne)):
            
            state[my_row][my_column + 1]  = 0
            return state, [my_row, my_column + 1]

        return state, None


    def _capture_king(self, state, pawns):
        #King on the throne
        if (    state[4][4] == 2 
            and state[4][5] == -1   
            and state[4][3] == -1 
            and state[3][4] == -1
            and state[5][4] == -1):
            return True

        #King on the right of the throne
        if (    state[4][5] == 2 
            and state[3][5] == -1 
            and state[5][5] == -1 
            and state[4][6] == -1):
            return True
            
        #King on the left of the throne
        if (    state[4][3] == 2 
            and state[3][3] == -1 
            and state[5][3] == -1 
            and state[4][2] == -1):
            return True
        
        #King above the throne
        if (    state[3][4] == 2             
            and state[3][2] == -1 
            and state[3][5] == -1 
            and state[2][4] == -1):
            return True

        #King below the throne
        if (    state[5][4] == 2             
            and state[5][5] == -1 
            and state[5][3] == -1 
            and state[6][4] == -1):
            return True
                
        if state[4][4] != 2 and state[4][5] != 2 and state[5][4] != 2 and state[4][3] != 2 and state[3][4] != 2:
            k_row = pawns[2][0][0]
            k_column = pawns[2][0][1]
            
            #Vertical capture
            if (k_row < 8 and k_row > 0
                and ( state[k_row + 1][ k_column] == -1 or [k_row + 1,k_column] in self.citadels or [k_row + 1,k_column] == self.throne)  
                and (state[k_row - 1][ k_column] == -1 or [k_row - 1, k_column] in self.citadels or [k_row - 1,k_column] == self.throne )):
                return True

            #Horizontal capture
            if (k_column < 8 and k_column > 0
                and ( state[k_row][ k_column + 1] == -1 or [k_row, k_column + 1] in self.citadels or [k_row,k_column + 1]  == self.throne)  
                and (state[k_row][ k_column - 1] == -1 or [k_row, k_column - 1]  in self.citadels or [k_row, k_column - 1]  == self.throne )):
                return True
                    
        return False


    def _king_escape(self, state):
        for escape in self.escapes:
            if state[escape[0]][escape[1]] == 2:
                return True
        return False


    def deepcopy(self, state):
        return np.copy(state).tolist()
    