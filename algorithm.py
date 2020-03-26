from math import inf
from time import time
from collections import OrderedDict
from os import getpid
from multiprocessing import Process, Queue, Pipe, cpu_count
from select import select
from heuristic import Heuristic
from game import Game

class Search:

    def __init__(self, color, weights, timeout = 59.5, depth = 4): 
        self.TIMEOUT = timeout
        self.DEPTH = depth
        self.COLOR = color
        self.NUM_WORKERS = cpu_count()

        self.game = Game()
        self.heuristic = Heuristic(weights)
        # transposition table & history heuristic
        self.tt = Cache(1e7)
        self.hh = Cache(1e7)

        self.cache_pipes = []
        self.sync_pipes = []
        self.jobs_queue = Queue(1)
        self.moves_queue = Queue()
        # start search workers
        self.search_workers = []
        for i in range(self.NUM_WORKERS):
            cache_pipe0, cache_pipe1 = Pipe(True)
            sync_pipe0, sync_pipe1 = Pipe(True)
            self.sync_pipes.append(sync_pipe1)
            self.cache_pipes.append(cache_pipe1)
            process = Process(target=self.search_worker_process, args=[self.jobs_queue, self.moves_queue, cache_pipe0, sync_pipe0, depth, color])
            self.search_workers.append(process)
            process.start()
            cache_pipe0.close() # are used by search workers
            sync_pipe0.close()

        # start cache worker
        self.cache_worker = Process(target=self.cache_worker_process, args=[self.cache_pipes])
        self.cache_worker.start()
        for p in self.cache_pipes: p.close()

        
    def dispose(self):
        self.cache_worker.terminate()
        for w in self.search_workers: w.terminate()
        self.jobs_queue.close()
        self.moves_queue.close()
        for i in range(self.NUM_WORKERS):
            self.cache_pipes[i].close()
            self.sync_pipes[i].close()

        
    def start(self, state):
        started = time()
        α = -inf
        β = inf
        best = [α, None]
        # comupte init state, generate & sort moves
        pawns, hash_ = self.game.compute_state(state)
        moves = self.game.actions(state, self.COLOR, pawns)
        moves.sort(key = self.order_moves)

        running_jobs = 0
        while len(moves) > 0:
            # blocking put on jobs queue (sized 1)
            move = moves.pop(0)
            self.jobs_queue.put((state, hash_, pawns, move, α, β, started), block=True)
            running_jobs += 1
            # if move available: update α and best
            try: recvd = self.moves_queue.get(block=False)
            except Exception: recvd = None
            if recvd != None:
                running_jobs -= 1
                if best[0] < recvd[0]:
                    α = recvd[0]
                    best = recvd
        # wait last moves
        while running_jobs > 0:
            recvd = self.moves_queue.get(block=True)
            running_jobs -= 1
            if best[0] < recvd[0]:
                best = recvd

        # cache sync
        for p in self.sync_pipes:
            p.send("sync")

        return best[1]

    def cache_worker_process(self, pipes):
        try:
            update_counter = 0
            readers = list(map(lambda p: p.fileno(), pipes))
            while True:
                ready, _, __ = select(readers, [], [])
                for r in ready:
                    # merge cache
                    pipe = pipes[readers.index(r)]
                    req = pipe.recv()
                    update_counter += 1
                    self.tt.merge(req[0])
                    self.hh.merge(req[1])
                
                # update searcher cache
                if update_counter == len(pipes):
                    for p in pipes:
                        p.send((self.tt, self.hh))
                    update_counter = 0
        except Exception as e:
            print("\n\n\n", "[cache worker ", getpid(), "] ERRORED:", e)

                
    def search_worker_process(self, jobs_queue, moves_queue, cache_pipe, sync_pipe, depth, color):
        try:
            while True:
                ready, _, __ = select([jobs_queue._reader.fileno(), sync_pipe.fileno()], [], [])
                for r in ready:
                    if r == sync_pipe.fileno():
                        sync_pipe.recv() # it consumes sync signal 
                        cache_pipe.send((self.tt, self.hh))
                        self.tt, self.hh = cache_pipe.recv()
                    else:
                        state, hash_, pawns, move, α, β, started = jobs_queue.get(block=True)
                        next_state, next_hash, next_pawns, terminal = self.game.update_state(state, hash_, pawns, move, color)
                        child_value = -self.negamax(next_state, depth-1, -β, -α, -color, next_pawns, next_hash, terminal, started)
                        moves_queue.put((child_value, move))
        except Exception as e:
            print("\n\n\n", "[search worker ", getpid(), "] ERRORED:", e)


    def negamax(self, state, depth, α, β, color, pawns, hash_, terminal, started):
        alphaOrig = α
        # transposition table lookup
        from_tt = self.tt.get(hash_)
        if from_tt != None and from_tt["depth"] >= depth:
            if from_tt["flag"] == 0:
                return from_tt["val"]
            elif from_tt["flag"] == -1:
                α = max(α, from_tt["val"])
            elif from_tt["flag"] == 1:
                β = min(β, from_tt["val"])
            if α >= β:
                return from_tt["val"]

        # terminal condition check
        if terminal or depth == 0:
            return self.heuristic.evaluation_fn(state, color, terminal, pawns) - depth

        # moves generation & sorting
        moves = self.game.actions(state, color, pawns)
        moves.sort(key = self.order_moves)
        # tree expansion loop
        best_value = -inf
        best_move = None
        for child_move in moves:
            # timeout
            if time() - started >= self.TIMEOUT:
                print("timeout")
                if best_value == -inf:
                    return best_value * self.COLOR * color # should be always the minimum
                break
            # compute next state
            next_state, next_hash, next_pawns, terminal = self.game.update_state(state, hash_, pawns, child_move, color)
            # child evaluation switching player
            child_value = -self.negamax(next_state, depth-1, -β, -α, -color, next_pawns, next_hash, terminal, started)
            if child_value >= best_value:
                best_value = child_value
                best_move = child_move
            α = max(child_value, α)
            # cutoff
            if α >= β:
                break
        
        # update transposition table
        entry = {"val" : best_value, "depth" : depth, "move" : best_move}
        if best_value >= β:
            entry["flag"] = -1
        elif best_value <= alphaOrig:
            entry["flag"] = 1
        else:
            entry["flag"] = 0
        self.tt[hash_] = entry
        # update history heuristic 
        if color == self.COLOR and best_move != None:
            self.hh[(tuple(best_move[0]), tuple(best_move[1]))] = 2**depth
        
        return best_value


    def order_moves(self, move):
        stored = self.hh.get((tuple(move[0]), tuple(move[1])))
        if stored == None:
            # default order criteria: throne-from distance + throne-to distance
            return (4-move[0][0])*(4-move[0][0]) + (4-move[0][1]) * (4-move[0][1]) + (
                (4-move[1][0])*(4-move[1][0]) + (4-move[1][1]) * (4-move[1][1]))
        return stored        


class Cache:
    def __init__(self, size):
        self.od = OrderedDict()
        self.size = size

    def get(self, key, default=None):
        try: return self.od[key]
        except KeyError: return default

    def __setitem__(self, key, value):
        self.od[key] = value
        self._check_size_limit()

    def merge(self, that):
        self.od = {**self.od, **that.od}
        self._check_size_limit()

    def _check_size_limit(self):
        while len(self.od) > self.size:
            self.od.pop(next(iter(self.od.keys())))