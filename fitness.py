import sys, os
from algorithm import Search
from time import time


def fitness_fn(white_population, black_population, timeout):
    for w in white_population:
        for b in black_population:
            w_player = Search(1, timeout = timeout, weights =w[0])
            b_player = Search(-1, timeout = timeout, weights = b[0])

            result = fight(w_player, b_player)
            w[1] += result
            b[1] -= result

            w_player.dispose()
            b_player.dispose()

def fight(w, b):
    past_states = dict()
    state = [
        [ 0,  0,  0, -1, -1, -1,  0,  0,  0],
        [ 0,  0,  0,  0, -1,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  1,  0,  0,  0,  0],
        [-1,  0,  0,  0,  1,  0,  0,  0, -1], 
        [-1, -1,  1,  1,  2,  1,  1, -1, -1], 
        [-1,  0,  0,  0,  1,  0,  0,  0, -1], 
        [ 0,  0,  0,  0,  1,  0,  0,  0,  0], 
        [ 0,  0,  0,  0, -1,  0,  0,  0,  0], 
        [ 0,  0,  0, -1, -1, -1,  0,  0,  0]]

    color = 1
    pawns, hash_ = w.game.compute_state(state)

    print("\n\n========== FIGHT ==========")
    print("WHITE WEIGHTS:", w.heuristic.weights, "\nBLACK WEIGHTS:", b.heuristic.weights, "\n")

    while True:
        timed_out = 0
        started = time()
        move = w.start(state)
        elapsed = time() - started
        if elapsed > w.TIMEOUT:
            timed_out = 0.4
        state, hash_, pawns, terminal = w.game.update_state(state, hash_, pawns, move, color)
        print("WHITE MOVE: ", move, "TIME:", elapsed)
        if terminal: # ww
            print("\n========== WHITE WIN ==========")
            return 1 - timed_out
        
        color = -color

        timed_out = 0
        started = time()
        move = b.start(state)
        elapsed = time() - started
        if elapsed > w.TIMEOUT:
            timed_out = -0.4
        state, hash_, pawns, terminal = b.game.update_state(state, hash_, pawns, move, color)
        print("BLACK MOVE: ", move, "TIME:", elapsed)
        if terminal: # bw
            print("\n========== BLACK WIN ==========")
            return -1 - timed_out

        color = -color

        try: 
            past_states[hash_]
            print("\n========== DRAW ==========") # draw
            return 0
        except: past_states[hash_] = 1


def print_state(state):
    for r in range(9):
        u = ""
        for i in range(9):
            c = state[r][i]
            if c == -1: 
                u+=u'\u2999'+u'\u25cb'+" "
            elif c == 1: 
                u+=u'\u2999'+u'\u25cf'+" "
            elif c == 2: 
                u+=u'\u2999'+u'\u2654'+" "
            else: 
                if r == 4 and i == 4: u+=u'\u2999'+"x "
                else: u+=u'\u2999'+"  "
        print(r," ", u+u'\u2999', "\n")
    print("    ", "  ".join(str(x) for x in range(9)))

if __name__ == "__main__": 
    timeout = float('59.5')
    w_player = Search( 1, timeout = timeout, weights = [10, -1, 1, 1, 1, -2, -4, 2, 5, 1, 1])
    b_player = Search(-1, timeout = timeout, weights = [10, -1, 1, 1, 1, -2, -4, 2, 5, 1, 1])

    fight(w_player, b_player)