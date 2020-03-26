class Heuristic:
    def __init__(self, weights):
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

        self.weights = weights


    def evaluation_fn(self, state, turn, terminal, pawns):
        if terminal:
            return -1e8
            
        w = len(pawns[1])
        b = len(pawns[0])
        king_pos = pawns[2][0]
       
        val = (self.weights[7] * (self.weights[9] * w - self.weights[10] * b) + 
            self.weights[8] * self.eval_king_pos(state, king_pos))

        return turn * val


    def eval_king_pos(self, state, king_pos): 
        row = king_pos[0]
        col = king_pos[1]
        score = 0
        
        mcol = col - 1
        while mcol >= 0:
            if [row, mcol] == self.throne:
                score += self.weights[2]
                break
            if state[row][mcol] == -1:
                if mcol == col - 1:
                    score += self.weights[6]
                else:
                    score += self.weights[5]
                break
            if state[row][mcol] == 1:
                if mcol == col - 1:
                    score += self.weights[4]
                else:
                    score += self.weights[3]
                break
            if [row, mcol] in self.citadels:
                score += self.weights[1]
                break
            if [row, mcol] in self.escapes:
                score += self.weights[0]
                break
            mcol -= 1

        mcol = col + 1
        while mcol < 9:
            if [row, mcol] == self.throne:
                score += self.weights[2]
                break
            if state[row][mcol] == -1:
                if mcol == col + 1:
                    score += self.weights[6]
                else:
                    score += self.weights[5]
                break
            if state[row][mcol] == 1:
                if mcol == col + 1:
                    score += self.weights[4]
                else:
                    score += self.weights[3]
                break
            if [row, mcol] in self.citadels:
                score += self.weights[1]
                break
            if [row, mcol] in self.escapes:
                score += self.weights[0]
                break
            mcol += 1

        mrow = row - 1
        while mrow >= 0:
            if [row, mcol] == self.throne:
                score += self.weights[2]
                break
            if state[row][mcol] == -1:
                if mrow == row - 1:
                    score += self.weights[6]
                else:
                    score += self.weights[5]
                break
            if state[row][mcol] == 1:
                if mrow == row - 1:
                    score += self.weights[4]
                else:
                    score += self.weights[3]
                break
            if [row, mcol] in self.citadels:
                score += self.weights[1]
                break
            if [row, mcol] in self.escapes:
                score += self.weights[0]
                break
            mrow -= 1

        mrow = row + 1
        while mrow < 9:
            if [row, mcol] == self.throne:
                score += self.weights[2]
                break
            if state[row][mcol] == -1:
                if mrow == row + 1:
                    score += self.weights[6]
                else:
                    score += self.weights[5]
                break
            if state[row][mcol] == 1:
                if mrow == row + 1:
                    score += self.weights[4]
                else:
                    score += self.weights[3]
                break
            if [row, mcol] in self.citadels:
                score += self.weights[1]
                break
            if [row, mcol] in self.escapes:
                score += self.weights[0]
                break
            mrow += 1

        return score