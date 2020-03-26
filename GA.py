import sys, os
from random import randint, randrange, uniform, seed
from fitness import fitness_fn

def main():
    Genotype().start()    

class Genotype:
    def __init__(self, N = 10, n_offsprings = 2, n_genes = 11, mutation_prob = 0.2, 
                tourn_size = 3, max_generation = 3, timeout = 59.5,
                    genes_dict ={   0 : "escape_w" ,
                                    1 : "citadel_w" ,
                                    2 : "throne_w",
                                    3 : "near_white_w",
                                    4 : "adjacent_white_w",
                                    5 : "near_black_w" ,
                                    6 : "adjacent_black_w" ,
                                    7 : "material_w" ,
                                    8 : "king_pos_w" ,
                                    9 : "white_w" ,
                                    10 :"black_w" },

                    genes_bounds = {"escape_w" : (1,20),
                                "citadel_w" : (-2,0),
                                "throne_w" : (-2,0),
                                "near_white_w" : (-2,2),
                                "adjacent_white_w" : (-2,2),
                                "near_black_w" : (-5, 0),
                                "adjacent_black_w" : (-5,0),
                                "material_w" : (0,100),
                                "king_pos_w" : (0,100),
                                "white_w" : (0,100),
                                "black_w" : (0,100)
                    }):

        self.N = N #must be even
        self.n_offsprings = n_offsprings
        self.n_genes = n_genes
        self.genes_bounds = genes_bounds
        self.mutation_prob = mutation_prob
        self.genes_dict = genes_dict
        self.tournament_size = tourn_size
        self.max_generation = max_generation
        self.timeout = timeout
        self.white_population = list()
        self.black_population  = list()
        self.roulette_prob = list() 
    

    def start(self):
        self.initialize_population()
        print("--------------Initial Population Games--------------")
        fitness_fn(self.white_population, self.black_population, self.timeout)
        generation = 0
        while generation < self.max_generation:

            generation += 1
            new_white_population = list()
            new_black_population = list()
            
            while len(new_white_population) < self.N :
                w_parent_1, b_parent_1 = self.tournament_selection()
                w_parent_2, b_parent_2 = self.tournament_selection()

                w_child_1, w_child_2 = self.two_point_cross_over(w_parent_1, w_parent_2)
                b_child_1, b_child_2 = self.two_point_cross_over(b_parent_1, b_parent_2)

                new_white_population.append(w_child_1)
                new_white_population.append(w_child_2)
                new_black_population.append(b_child_1)
                new_black_population.append(b_child_2)

            print("------------------New Population ", generation, " Games------------------")
            fitness_fn(new_white_population, new_black_population, self.timeout)
            self.truncation_replacement(new_white_population, new_black_population)
            print("------------------Generation ", generation, " Games------------------")
            fitness_fn(self.white_population, self.black_population, self.timeout)
        
        self.white_population.sort(key = lambda x: x[1], reverse = True)
        self.black_population.sort(key = lambda x: x[1], reverse = True)

        print("\n\nBest white player\n", self.white_population[0], "\n Best black player\n", self.black_population[0])
        fd = open("population_w.txt", "w")
        fd.write(str(self.white_population))
        fd.close()
        fd = open("population_b.txt", "w")
        fd.write(str(self.black_population))
        fd.close()

    def initialize_population(self):

        for i in range(2 * self.N):
            escape_w = randrange(self.genes_bounds["escape_w"][0], self.genes_bounds["escape_w"][1])
            citadel_w = 0.1 * randrange(self.genes_bounds["citadel_w"][0], self.genes_bounds["citadel_w"][1])
            throne_w = 0.1 * randrange(self.genes_bounds["throne_w"][0], self.genes_bounds["throne_w"][1])
            near_white_w = 0.1 * randrange(self.genes_bounds["near_white_w"][0], self.genes_bounds["near_white_w"][1])
            adjacent_white_w = 0.1 * randrange(self.genes_bounds["adjacent_white_w"][0], self.genes_bounds["adjacent_white_w"][1])
            near_black_w = 0.1 * randrange(self.genes_bounds["near_black_w"][0], self.genes_bounds["near_black_w"][1])
            adjacent_black_w = 0.1 * randrange(self.genes_bounds["adjacent_black_w"][0], self.genes_bounds["adjacent_black_w"][1])
            material_w = 0.01 * randrange(self.genes_bounds["material_w"][0], self.genes_bounds["material_w"][1])
            king_pos_w = 0.01 * randrange(self.genes_bounds["king_pos_w"][0], self.genes_bounds["king_pos_w"][1])
            white_w = 0.01 * randrange(self.genes_bounds["white_w"][0], self.genes_bounds["white_w"][1])
            black_w = 0.01 * randrange(self.genes_bounds["black_w"][0], self.genes_bounds["black_w"][1])

            agent = [[escape_w, 
                    citadel_w, 
                    throne_w, 
                    near_white_w, 
                    adjacent_white_w,
                    near_black_w,
                    adjacent_black_w,
                    material_w,
                    king_pos_w,
                    white_w,
                    black_w], 0.]
        
            if i < self.N:
                self.white_population.append(agent) 
            else :
                self.black_population.append(agent)


    def two_point_cross_over(self, parent_1, parent_2):
        print("\n2 points crossover\n")
        p1, p2 = 3,7
        offspring_1 = [None, 0.]
        offspring_2 = [None, 0.]
        offspring_1[0] = parent_1[0][:p1] + parent_2[0][p1:p2] + parent_1[0][p2:]
        offspring_2[0] = parent_2[0][:p1] + parent_1[0][p1:p2] + parent_2[0][p2:]

        self.mutation(offspring_1)
        self.mutation(offspring_2)

        return offspring_1, offspring_2

    def mutation(self, offspring):
        if uniform(0,1) <= self.mutation_prob:
            print("\nMutation\n")
            gene_number = randrange(0, self.n_genes)
            mutated_gene = self.genes_dict[gene_number]
            if gene_number > 6 and gene_number < 11 :
                offspring[0][gene_number] = 0.01 * randrange(self.genes_bounds[mutated_gene][0], self.genes_bounds[mutated_gene][1])
            if gene_number > 0 and gene_number < 7:
                offspring[0][gene_number] = 0.1 * randrange(self.genes_bounds[mutated_gene][0], self.genes_bounds[mutated_gene][1])
            else:
                offspring[0][gene_number] = randrange(self.genes_bounds[mutated_gene][0], self.genes_bounds[mutated_gene][1])

    def tournament_selection(self) :
        print("\nTournament selection\n")
        best_white_player = None
        best_black_player = None  

        for i in range(self.tournament_size):
            white_player = self.white_population[randrange(0, self.N)]
            black_player = self.black_population[randrange(0, self.N)]

            if best_white_player == None or white_player[1] > best_white_player[1]:
                best_white_player = white_player
            if best_black_player == None or black_player[1] > best_black_player[1]:
                best_black_player = black_player

        return best_white_player, best_black_player

    
    def truncation_replacement(self, new_white_population, new_black_population):
        
        print("\nTruncation_replacement\n")
        self.white_population.sort(key = lambda x: x[1], reverse = True)
        self.black_population.sort(key = lambda x: x[1], reverse = True)
        new_white_population.sort(key = lambda x: x[1], reverse = True)
        new_black_population.sort(key = lambda x: x[1], reverse = True)

        n = int(self.N/2)
        self.white_population = self.white_population[:n] + new_white_population[:n]
        self.black_population = self.black_population[:n] + new_black_population[:n]


if __name__ == '__main__': main()