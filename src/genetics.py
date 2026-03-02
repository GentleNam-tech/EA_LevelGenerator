from typing import List, Optional, Tuple, Dict
from grid import Grid, LevelBuilder, LUFT, PLATTFORM, START, ZIEL
from fitness import SimpleFitness

import numpy as np

PLATTFORM_WAHRSCHEINLICHKEIT = 0.15
# StandardWert
TOURNAMENT = 3
# Selbst ausgewählte Werte: Ein Level soll nicht zu viele Plattformen haben
LUFT_MUTATION = 0.7
PLATTFORM_MUTATION = 0.3


class GeneticAlgorithm:
    # erste Paraneter values hiervon inspierert https://www.woodruff.dev/day-31-best-practices-for-tuning-genetic-algorithm-parameters/
    def __init__(self, population_size: int = 50, crossover_wahrscheinlichkeit: float = 0.7, mutation_wahrscheinlichkeit: float = 0.1, elite: int = 2,
                 breite: int = 20, hoehe: int = 10):
        self.population_size = population_size
        self.crossover_wahrscheinlichkeit = crossover_wahrscheinlichkeit
        self.mutation_wahrscheinlichkeit = mutation_wahrscheinlichkeit
        self.elite = elite
        self.breite = breite
        self.hoehe = hoehe

        self.population: List[np.ndarray] = []
        self.fitnesses: List[float] = []
        self.generation = 0

        # fuer Statistik spaeter zum Vergleich
        self.beste_fitness_generation: List[float] = []
        self.durchschnitt_fitness_generation: List[float] = []
        self.best_level: Optional[np.ndarray] = None
        self.beste_fitness: float = float('-inf')

    def initialisiere_population(self):
        self.population = []

        for i in range(self.population_size):
            # zufallslevel wird zu matrix
            grid = LevelBuilder.zufalls_level(self.breite, self.hoehe, PLATTFORM_WAHRSCHEINLICHKEIT)

            matrix = grid.grid_matrix()
            self.population.append(matrix)
        print(f"Population initialisiert: {len(self.population)} Level")

    def evaluiere_population(self, fitness_evaluator: SimpleFitness):
        self.fitnesses = []

        for i, matrix in enumerate(self.population):
            # matrix wird wieder zu grid
            grid = LevelBuilder.matrix_grid(matrix)

            fitness = fitness_evaluator.berechne_fitness(grid)
            print(fitness)
            self.fitnesses.append(fitness)

            if (i + 1) % 10 == 0:
                print(f"  Evaluiert: {i + 1}/{len(self.population)}")

        self.update_statistiken()

    def update_statistiken(self):
        beste = max(self.fitnesses)
        durchschnitt = sum(self.fitnesses) / len(self.fitnesses)

        self.beste_fitness_generation.append(beste)
        self.durchschnitt_fitness_generation.append(durchschnitt)

        if beste > self.beste_fitness:
            self.beste_fitness = beste
            beste_index = self.fitnesses.index(beste)
            self.best_level = self.population[beste_index].copy()

    def selektiere(self) -> Tuple[np.ndarray, np.ndarray]:
        # https://www.baeldung.com/cs/ga-tournament-selection#bd-the-algorithm
        def tournament() -> np.ndarray:
            individuen = np.random.choice(len(self.population), size=TOURNAMENT, replace=False)

            tournament_fitnesses = [self.fitnesses[i] for i in individuen]
            best = np.argmax(tournament_fitnesses)
            best_index = individuen[best]

            return self.population[best_index].copy()

        return tournament(), tournament()

    def crossover(self, eltern: Tuple[np.ndarray, np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
        kind1 = eltern[0].copy()
        kind2 = eltern[1].copy()

        split_y = np.random.randint(2, self.hoehe - 1)

        kind1[:split_y, :] = eltern[1][:split_y, :]
        kind2[:split_y, :] = eltern[0][:split_y, :]

        kind1 = self.repariere_level(kind1)
        kind2 = self.repariere_level(kind2)

        return kind1, kind2

    def mutiere(self, individuum: np.ndarray) -> np.ndarray:
        # Mutiere ein Individuum (Nicht Boden oder Start/Ziel)
        # Level soll nicht dadurch instantly failen (Start/Ziel) oder Boden weg
        mutiert = individuum.copy()

        for y in range(self.hoehe - 1):
            for x in range(self.breite):
                if np.random.random() < self.mutation_wahrscheinlichkeit:
                    if mutiert[y, x] not in [START, ZIEL]:
                        if np.random.random() < LUFT_MUTATION:
                            mutiert[y, x] = LUFT
                        else:
                            mutiert[y, x] = PLATTFORM
        mutiert = self.repariere_level(mutiert)
        return mutiert

    def repariere_level(self, individuum: np.ndarray) -> np.ndarray:
        # Soll das komplette Zerstören beim Crossover und Mutation verhindern
        # Wenn Ziel/Start fehlt/zu viel gibt wird eins erstellt/ausgesucht
        repariert = individuum.copy()
        start_pos = np.argwhere(repariert == START)
        ziel_pos = np.argwhere(repariert == ZIEL)

        if len(start_pos) == 0:
            repariert[self.hoehe - 2, 1] = START
            start_pos = [(self.hoehe - 2, 1)]
        elif len(start_pos) > 1:
            for i in range(1, len(start_pos)):
                y, x = start_pos[i]
                repariert[y, x] = LUFT
            start_pos = [start_pos[0]]

        if len(ziel_pos) == 0:
            ziel_y = np.random.randint(2, self.hoehe - 2)
            repariert[ziel_y, self.breite - 2] = ZIEL
            ziel_pos = [(ziel_y, self.breite - 2)]
        elif len(ziel_pos) > 1:
            for i in range(1, len(ziel_pos)):
                y, x = ziel_pos[i]
                repariert[y, x] = LUFT
            ziel_pos = [ziel_pos[0]]

        ziel_y, ziel_x = ziel_pos[0]
        if ziel_y + 1 < self.hoehe:
            repariert[ziel_y + 1, ziel_x] = PLATTFORM

        return repariert

    def next_generation(self):
        # naechte Generation mit Elite (Top2) und der Rest mit Crossover/Mutation
        population = []
        index = np.argsort(self.fitnesses)[::-1]

        for i in range(self.elite):
            elite_index = index[i]
            population.append(self.population[elite_index].copy())

        while len(population) < self.population_size:
            eltern = self.selektiere()

            if np.random.random() < self.crossover_wahrscheinlichkeit:
                kind1, kind2 = self.crossover(eltern)
            else:
                kind1, kind2 = eltern[0].copy(), eltern[1].copy()

            kind1 = self.mutiere(kind1)
            kind2 = self.mutiere(kind2)

            population.append(kind1)
            if len(population) < self.population_size:
                population.append(kind2)

        self.population = population
        self.generation += 1

    def evolution(self, generationen: int, fitness_evaluator: SimpleFitness, verbose: bool = True):
        # print methode wurde generiert mit Copilot
        print(f"\n{'='*60}")
        print(f"STARTE EVOLUTION")
        print(f"{'='*60}")
        print(f"Generationen: {generationen}")
        print(f"Population: {self.population_size}")
        print(f"Crossover-Rate: {self.crossover_wahrscheinlichkeit}")
        print(f"Mutation-Rate: {self.mutation_wahrscheinlichkeit}")
        print(f"{'='*60}\n")

        for gen in range(generationen):
            if verbose:
                print(f"\nGeneration {gen+1}/{generationen}")

            # Evaluiere
            self.evaluiere_population(fitness_evaluator)

            # Statistiken
            if verbose:
                stats = fitness_evaluator.get_statistiken()
                print(f"  Beste Fitness: {self.beste_fitness:.2f}")
                print(f"  Durchschnitt: {self.durchschnitt_fitness_generation[-1]:.2f}")
                print(f"  Lösbare Level: {stats['anzahl_loesbare']}/{stats['anzahl_level']}")

            # Nächste Generation (außer bei letzter)
            if gen < generationen - 1:
                self.next_generation()

        print(f"\n{'='*60}")
        print(f"EVOLUTION ABGESCHLOSSEN")
        print(f"{'='*60}")
        print(f"Beste Fitness: {self.beste_fitness:.2f}")
        print(f"Beste Generation: {self.beste_fitness_generation.index(self.beste_fitness) + 1}")

    def get_best_level(self) -> Grid:
        if self.best_level is None:
            raise ValueError("Noch keine Evolution durchgeführt!")

        grid = LevelBuilder.matrix_grid(self.best_level)
        return grid

    def get_statistiken(self) -> Dict:
        return {
            'generationen': self.generation,
            'beste_fitness': self.beste_fitness,
            'beste_fitness_pro_generation': self.beste_fitness_generation,
            'durchschnitt_pro_generation': self.durchschnitt_fitness_generation
        }