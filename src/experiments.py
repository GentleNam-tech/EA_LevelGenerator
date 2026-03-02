import os
import time
import csv
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np

from fitness import SimpleFitness, Fitness
from genetics import GeneticAlgorithm
from src.grid import LevelBuilder, Grid
from src.visualizer import GridVisualizer


class Experiment:
    def __init__(self, output: str = "results"):
        self.output = Path(output)
        self.output.mkdir(exist_ok=True)
        self.all_experiments: List[Dict] = []

    def execute_experiments(self, ga_config: Dict, fitness_config: Optional[Dict], generationen: int = 50, wiederholungen: int = 3, name: str = ""):
        runs_ergebnisse = []
        for run in range(wiederholungen):
            ga = GeneticAlgorithm(**ga_config)
            if fitness_config is None:
                evaluator = SimpleFitness()
            else:
                evaluator = Fitness(**fitness_config)
            ga.initialisiere_population()

            start_zeit = time.time()
            ga.evolution(
                generationen=generationen,
                fitness_evaluator=evaluator,
                verbose=False
            )
            end_zeit = time.time()

            konvergenz = self.analysiere_konvergenz(ga.beste_fitness_generation)

            run_ergebnis = {
                'name': name,
                'dauer_sekunden': end_zeit - start_zeit,
                'beste_fitness': ga.beste_fitness,
                'fitness_verlauf': ga.beste_fitness_generation.copy(),
                'durchschnitt_verlauf': ga.durchschnitt_fitness_generation.copy(),
                'bestes_level': ga.best_level.copy(),
                'evaluator_stats': evaluator.get_statistiken(),
                'konvergenz': konvergenz
            }

            runs_ergebnisse.append(run_ergebnis)

            print(f"Beste Fitness: {run_ergebnis['beste_fitness']:.2f}")
            print(f"Dauer: {run_ergebnis['dauer_sekunden']:.1f}s")
            print(f"Lösbarkeits-Rate: {run_ergebnis['evaluator_stats']['loesbarkeits_rate']:.1%}")

        ergebnis = self.aggregiere_runs(runs_ergebnisse, ga_config)

        self.all_experiments.append(ergebnis)
        return ergebnis

    def aggregiere_runs(   self, runs: List[Dict], ga_config: Dict) -> Dict:
        beste_fitness_werte = [r['beste_fitness'] for r in runs]
        name = runs[0]['name']
        alle_verlaeufe = [r['durchschnitt_verlauf'] for r in runs]
        beste_fitness_verlauf = [r['fitness_verlauf'] for r in runs]
        fitness_verlauf = np.mean(beste_fitness_verlauf, axis=0).tolist()
        durchschnitt_verlauf = np.mean(alle_verlaeufe, axis=0).tolist()
        std_verlauf = np.std(alle_verlaeufe, axis=0).tolist()
        stagnationen = [r['konvergenz']['keine_verbesserung_seit_gen'] for r in runs]
        bester_run = beste_fitness_werte.index(max(beste_fitness_werte))
        zwischen_level = [r['bestes_level'] for r in runs[::10]]

        return {
            'name': name,
            'ga_config': ga_config,
            'anzahl_runs': len(runs),
            'beste_fitness_mittel': np.mean(beste_fitness_werte),
            'beste_fitness_std': np.std(beste_fitness_werte),
            'beste_fitness_max': max(beste_fitness_werte),
            'durchschnitt_verlauf': durchschnitt_verlauf,
            'fitness_verlauf': fitness_verlauf,
            'std_verlauf': std_verlauf,
            'bestes_level': runs[bester_run]['bestes_level'],
            'zwischen_level': zwischen_level,
            'durchschnittliche_dauer': np.mean([r['dauer_sekunden'] for r in runs]),
            'mittlere_stagnation': float(np.mean(stagnationen))
        }

    def analysiere_konvergenz(self, fitness_verlauf: List[float], epsilon: float = 1e-9) -> Dict:
        if not fitness_verlauf:
            return {
                'letzte_verbesserung_gen': 0,
                'keine_verbesserung_seit_gen': 0,
                'ist_konvergiert': False
            }

        best_so_far = fitness_verlauf[0]
        letzte_verbesserung = 0

        for gen, value in enumerate(fitness_verlauf):
            if value > best_so_far + epsilon:
                best_so_far = value
                letzte_verbesserung = gen

        stagnation = len(fitness_verlauf) - 1 - letzte_verbesserung

        ist_konvergiert = stagnation >= 10

        return {
            'letzte_verbesserung_gen': letzte_verbesserung,
            'keine_verbesserung_seit_gen': stagnation,
            'ist_konvergiert': ist_konvergiert
        }


    def experiment_simple(self):
        return self.execute_experiments(name="simple",
            ga_config={
                'population_size': 50,
                'crossover_wahrscheinlichkeit': 0.7,
                'mutation_wahrscheinlichkeit': 0.01,
                'elite': 2
            },
            fitness_config=None,
            generationen=50,
            wiederholungen=3
        )
    def experiment_kleine_population(self):
        return self.execute_experiments(
            name="Kleine_Population",
            ga_config={
                'population_size': 20,
                'crossover_wahrscheinlichkeit': 0.7,
                'mutation_wahrscheinlichkeit': 0.01,
                'elite': 2
            },
            fitness_config={
                'gewicht_loesbarkeit': 1000.0,
                'gewicht_schwierigkeit': 5.0,
                'gewicht_plattformen': 2.0
            },
            generationen=50,
            wiederholungen=3
        )
    def experiment_hohe_schwierigkeit(self):
        return self.execute_experiments(
            name="Hohe_Schwierigkeit",
            ga_config={
                'population_size': 50,
                'crossover_wahrscheinlichkeit': 0.7,
                'mutation_wahrscheinlichkeit': 0.01,
                'elite': 2
            },
            fitness_config={
                'gewicht_loesbarkeit': 1000.0,
                'gewicht_schwierigkeit': 20.0,
                'gewicht_plattformen': 2.0
            },
            generationen=50,
            wiederholungen=3
        )

    def experiment_nur_loesbarkeit(self):
        return self.execute_experiments(
            name="Nur_Loesbarkeit",
            ga_config={
                'population_size': 50,
                'crossover_wahrscheinlichkeit': 0.7,
                'mutation_wahrscheinlichkeit': 0.01,
                'elite': 2
            },
            fitness_config={
                'gewicht_loesbarkeit': 1000.0,
                'gewicht_schwierigkeit': 0.0,
                'gewicht_plattformen': 0.0
            },
            generationen=50,
            wiederholungen=3
        )

    def experiment_baseline(self):
        return self.execute_experiments(
            name="Baseline",
            ga_config={
                'population_size': 50,
                'crossover_wahrscheinlichkeit': 0.7,
                'mutation_wahrscheinlichkeit': 0.01,
                'elite': 2
            },
            fitness_config={
                'gewicht_loesbarkeit': 1000.0,
                'gewicht_schwierigkeit': 5.0,
                'gewicht_plattformen': 2.0
            },
            generationen=50,
            wiederholungen=3
        )

    def experiment_hohe_mutation(self):
        return self.execute_experiments(
            name="Hohe_Mutation",
            ga_config={
                'population_size': 50,
                'crossover_wahrscheinlichkeit': 0.7,
                'mutation_wahrscheinlichkeit': 0.1,
                'elite': 2
            },
            fitness_config={
                'gewicht_loesbarkeit': 1000.0,
                'gewicht_schwierigkeit': 5.0,
                'gewicht_plattformen': 2.0
            },
            generationen=50,
            wiederholungen=3
        )

    def exportiere_csv(self, filename: str = "experiment_ergebnisse.csv"):
        """
        Exportiert Experiment-Ergebnisse als CSV.

        Spalten:
        - Experiment-Name
        - GA-Parameter
        - Fitness-Parameter
        - Beste Fitness (Mittel, Std, Max)
        - Durchschnittliche Dauer
        """
        filepath = self.output / filename

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'Name'
                'Population',
                'Crossover-Rate',
                'Mutation-Rate',
                'Elite',
                'Beste_Fitness_Mittel',
                'Beste_Fitness_Std',
                'Beste_Fitness_Max',
                'Dauer_Sekunden',
                'Konvergenz'
            ])

            # Daten
            for exp in self.all_experiments:
                writer.writerow([
                    exp['name'],
                    exp['ga_config']['population_size'],
                    exp['ga_config']['crossover_wahrscheinlichkeit'],
                    exp['ga_config']['mutation_wahrscheinlichkeit'],
                    exp['ga_config']['elite'],
                    f"{exp['beste_fitness_mittel']:.2f}",
                    f"{exp['beste_fitness_std']:.2f}",
                    f"{exp['beste_fitness_max']:.2f}",
                    f"{exp['durchschnittliche_dauer']:.2f}",
                    f"{exp['mittlere_stagnation']:.2f}"
                ])

        print(f"\n✅ CSV exportiert: {filepath}")

    def exportiere_fitness_verlauf_csv(self, filename: str = "fitness_verlaeufe.csv"):
        """
        Exportiert Fitness-Verläufe für Plots.

        Format: Eine Zeile pro Generation, eine Spalte pro Experiment.
        """
        filepath = self.output / filename

        # Finde maximale Generationenzahl
        max_gens = max(len(exp['durchschnitt_verlauf']) for exp in self.all_experiments)

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)

            header = ['Generation'] + [exp['name'] for exp in self.all_experiments]
            writer.writerow(header)

            # Daten
            for gen in range(max_gens):
                row = [gen + 1]
                for exp in self.all_experiments:
                    if gen < len(exp['durchschnitt_verlauf']):
                        row.append(f"{exp['durchschnitt_verlauf'][gen]:.2f}")
                    else:
                        row.append('')
                writer.writerow(row)

        print(f"✅ fitness_verlauf exportiert: {filepath}")

    def exportiere_beste_fitness_verlauf_csv(self, filename: str = "beste_fitness_verlaeufe.csv"):
        """
        Exportiert Fitness-Verläufe für Plots.

        Format: Eine Zeile pro Generation, eine Spalte pro Experiment.
        """
        filepath = self.output / filename

        # Finde maximale Generationenzahl
        max_gens = max(len(exp['fitness_verlauf']) for exp in self.all_experiments)

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)

            header = ['Generation'] + [exp['name'] for exp in self.all_experiments]
            writer.writerow(header)
            # Daten
            for gen in range(max_gens):
                row = [gen + 1]
                for exp in self.all_experiments:
                    if gen < len(exp['fitness_verlauf']):
                        row.append(f"{exp['fitness_verlauf'][gen]:.2f}")
                    else:
                        row.append('')
                writer.writerow(row)

        print(f"✅ fitness_verlauf exportiert: {filepath}")

    def exportiere_std_verlauf_csv(self, filename: str = "std_verlaeufe.csv"):
        """
        Exportiert Std-Verläufe für Plots.

        Format: Eine Zeile pro Generation, eine Spalte pro Experiment.
        """
        filepath = self.output / filename

        # Finde maximale Generationenzahl
        max_gens = max(len(exp['std_verlauf']) for exp in self.all_experiments)

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            header = ['Generation'] + [exp['name'] for exp in self.all_experiments]
            writer.writerow(header)
            # Daten
            for gen in range(max_gens):
                row = [gen + 1]
                for exp in self.all_experiments:
                    if gen < len(exp['std_verlauf']):
                        row.append(f"{exp['std_verlauf'][gen]:.2f}")
                    else:
                        row.append('')
                writer.writerow(row)

        print(f"✅ std_verlauf exportiert: {filepath}")

    def speichere_beste_level(self) -> Grid:
        for i, exp in enumerate(self.all_experiments):
            name = exp['name']
            filepath = os.path.join(self.output, f"bestes_level_{name}.txt")
            level = exp['bestes_level']
            best_level = LevelBuilder.matrix_grid(level)
            with open(filepath, 'w') as f:
                f.write(f"Beste Fitness: {exp['beste_fitness_max']:.2f}\n\n")
                for y in range(best_level.hoehe):
                    for x in range(best_level.breite):
                        tile = best_level.get_tile(x, y)
                        if tile == 0:
                            f.write('.')
                        elif tile == 1:
                            f.write('#')
                        elif tile == 2:
                            f.write('=')
                        elif tile == 3:
                            f.write('S')
                        elif tile == 4:
                            f.write('Z')
                    f.write('\n')

        print(f"✅ Beste Level gespeichert in: {self.output}")
        return best_level

    def speichere_zwischen_level(self):
        for i, exp in enumerate(self.all_experiments):
            name = exp['name']
            level_list = exp['zwischen_level']
            for j in range(len(level_list)):
                filepath = os.path.join(self.output, f"bestes_level_{name}_{j}.txt")
                level = level_list[j]
                zwischen_level = LevelBuilder.matrix_grid(level)
                with open(filepath, 'w') as f:
                    f.write(f"Beste Fitness: {exp['beste_fitness_max']:.2f}\n\n")
                    for y in range(zwischen_level.hoehe):
                        for x in range(zwischen_level.breite):
                            tile = zwischen_level.get_tile(x, y)
                            if tile == 0:
                                f.write('.')
                            elif tile == 1:
                                f.write('#')
                            elif tile == 2:
                                f.write('=')
                            elif tile == 3:
                                f.write('S')
                            elif tile == 4:
                                f.write('Z')
                        f.write('\n')

        print(f"✅ Zwischen Level gespeichert in: {self.output}")

    def drucke_zusammenfassung(self):
        """Druckt Zusammenfassung aller Experimente."""
        print(f"\n{'=' * 70}")
        print("ZUSAMMENFASSUNG ALLER EXPERIMENTE")
        print(f"{'=' * 70}\n")

        print(f"{'Experiment':<25} {'Beste Fitness':>15} {'Std':>10} {'Dauer (s)':>12}")
        print("-" * 70)

        for exp in self.all_experiments:
            print(f"{exp['beste_fitness_mittel']:>15.2f} "
                  f"{exp['beste_fitness_std']:>10.2f} "
                  f"{exp['durchschnittliche_dauer']:>12.2f}")

        print(f"{'=' * 70}\n")


def fuehre_alle_experimente_aus(output: str = "experiment_results"):
    runner = Experiment(output=output)

    print("\n" + "=" * 70)
    print("STARTE EXPERIMENT-SUITE")
    print("=" * 70)

    # Experimente durchführen
    runner.experiment_simple()
    runner.experiment_baseline()
    runner.experiment_nur_loesbarkeit()
    runner.experiment_hohe_schwierigkeit()
    runner.experiment_kleine_population()
    runner.experiment_hohe_mutation()

    # Ergebnisse exportieren
    print("\n" + "=" * 70)
    print("EXPORTIERE ERGEBNISSE")
    print("=" * 70)

    runner.exportiere_csv()
    runner.exportiere_fitness_verlauf_csv()
    runner.exportiere_beste_fitness_verlauf_csv()
    runner.exportiere_std_verlauf_csv()
    best_level = runner.speichere_beste_level()
    runner.speichere_zwischen_level()
    runner.drucke_zusammenfassung()

    visualizer = GridVisualizer(best_level)
    visualizer.run()

    print("\n✅ Alle Experimente abgeschlossen!")
    print(f"📁 Ergebnisse in: {runner.output}")


if __name__ == "__main__":
    fuehre_alle_experimente_aus("all_experiments")
