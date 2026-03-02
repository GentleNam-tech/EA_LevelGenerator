"""
plot_results.py - Visualisierung von Experiment-Ergebnissen
===========================================================
Erstellt Plots aus CSV-Daten für die Bachelorarbeit.

PLOTS:
1. Fitness-Verläufe über Generationen
2. Vergleich verschiedener Experimente
3. Konvergenz-Analyse
"""

import csv
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Agg')  # Für Server ohne Display


class PlotCreator:
    """
    Erstellt Plots aus Experiment-Daten.

    Warum separate Klasse statt direkt in experiments.py?
    - Trennung: Experimente vs. Visualisierung
    - Optional: Plots können übersprungen werden (kein matplotlib nötig)
    - Wiederverwendbar: Plots aus gespeicherten CSVs erstellen
    """

    def __init__(self, results_dir: str = "experiment_results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)

    def plot_fitness_verlaeufe(
            self,
            csv_file: str = "fitness_verlaeufe.csv",
            output_file: str = "fitness_evolution.png"
    ):
        """
        Plottet Fitness-Verläufe über Generationen.

        Zeigt wie verschiedene Experimente konvergieren.
        """
        csv_path = self.results_dir / csv_file

        if not csv_path.exists():
            print(f"⚠️  CSV nicht gefunden: {csv_path}")
            return

        # CSV lesen
        generationen = []
        experimente = {}

        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)  # Generation, Exp1, Exp2, ...
            experiment_namen = header[1:]  # Ohne 'Generation'

            for exp_name in experiment_namen:
                experimente[exp_name] = []

            for row in reader:
                gen = int(row[0])
                generationen.append(gen)

                for i, exp_name in enumerate(experiment_namen):
                    value = row[i + 1]
                    if value:  # Nicht leer
                        experimente[exp_name].append(float(value))

        # Plot erstellen
        plt.figure(figsize=(12, 6))

        for exp_name, werte in experimente.items():
            plt.plot(range(1, len(werte) + 1), werte,
                     marker='o', markersize=3, linewidth=2, label=exp_name)

        plt.xlabel('Generation', fontsize=12)
        plt.ylabel('Durchschnittliche Fitness', fontsize=12)
        plt.title('Fitness-Evolution über Generationen', fontsize=14, fontweight='bold')
        plt.legend(loc='best', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        # Speichern
        output_path = self.results_dir / output_file
        plt.savefig(output_path, dpi=300)
        plt.close()

        print(f"✅ Plot erstellt: {output_path}")

    def plot_best_fitness_verlaeufe(
            self,
            csv_file: str = "beste_fitness_verlaeufe.csv",
            output_file: str = "fitness_evolution.png"
    ):
        """
        Plottet Fitness-Verläufe über Generationen.

        Zeigt wie verschiedene Experimente konvergieren.
        """
        csv_path = self.results_dir / csv_file

        if not csv_path.exists():
            print(f"⚠️  CSV nicht gefunden: {csv_path}")
            return

        # CSV lesen
        generationen = []
        experimente = {}

        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)  # Generation, Exp1, Exp2, ...
            experiment_namen = header[1:]  # Ohne 'Generation'

            for exp_name in experiment_namen:
                experimente[exp_name] = []

            for row in reader:
                gen = int(row[0])
                generationen.append(gen)

                for i, exp_name in enumerate(experiment_namen):
                    value = row[i + 1]
                    if value:  # Nicht leer
                        experimente[exp_name].append(float(value))

        # Plot erstellen
        plt.figure(figsize=(12, 6))

        for exp_name, werte in experimente.items():
            plt.plot(range(1, len(werte) + 1), werte,
                     marker='o', markersize=3, linewidth=2, label=exp_name)

        plt.xlabel('Generation', fontsize=12)
        plt.ylabel('Beste Fitness', fontsize=12)
        plt.title('Fitness-Evolution über Generationen', fontsize=14, fontweight='bold')
        plt.legend(loc='best', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        # Speichern
        output_path = self.results_dir / output_file
        plt.savefig(output_path, dpi=300)
        plt.close()

        print(f"✅ Plot erstellt: {output_path}")

    def plot_std_verlaeufe(
            self,
            csv_file: str = "std_verlaeufe.csv",
            output_file: str = "fitness_evolution.png"
    ):
        """
        Plottet Fitness-Verläufe über Generationen.

        Zeigt wie verschiedene Experimente konvergieren.
        """
        csv_path = self.results_dir / csv_file

        if not csv_path.exists():
            print(f"⚠️  CSV nicht gefunden: {csv_path}")
            return

        # CSV lesen
        generationen = []
        experimente = {}

        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)  # Generation, Exp1, Exp2, ...
            experiment_namen = header[1:]  # Ohne 'Generation'

            for exp_name in experiment_namen:
                experimente[exp_name] = []

            for row in reader:
                gen = int(row[0])
                generationen.append(gen)

                for i, exp_name in enumerate(experiment_namen):
                    value = row[i + 1]
                    if value:  # Nicht leer
                        experimente[exp_name].append(float(value))

        # Plot erstellen
        plt.figure(figsize=(12, 6))

        for exp_name, werte in experimente.items():
            plt.plot(range(1, len(werte) + 1), werte,
                     marker='o', markersize=3, linewidth=2, label=exp_name)

        plt.xlabel('Generation', fontsize=12)
        plt.ylabel('Standardabweichung', fontsize=12)
        plt.title('Standardabweichung über Generationen', fontsize=14, fontweight='bold')
        plt.legend(loc='best', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        # Speichern
        output_path = self.results_dir / output_file
        plt.savefig(output_path, dpi=300)
        plt.close()

        print(f"✅ Plot erstellt: {output_path}")

    def plot_vergleich_balken(
            self,
            csv_file: str = "experiment_ergebnisse.csv",
            output_file: str = "experiment_vergleich.png"
    ):
        """
        Balkendiagramm: Vergleich der besten Fitness.

        Zeigt auf einen Blick welches Experiment am besten war.
        """
        csv_path = self.results_dir / csv_file

        if not csv_path.exists():
            print(f"⚠️  CSV nicht gefunden: {csv_path}")
            return

        # CSV lesen
        namen = []
        fitness_mittel = []
        fitness_std = []

        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                namen.append(row['Name'])
                fitness_mittel.append(float(row['Beste_Fitness_Mittel']))
                fitness_std.append(float(row['Beste_Fitness_Std']))

        # Plot erstellen
        plt.figure(figsize=(10, 6))

        x_pos = range(len(namen))

        plt.bar(x_pos, fitness_mittel, yerr=fitness_std,
                alpha=0.8, capsize=5, color='steelblue')

        plt.xlabel('Experiment', fontsize=12)
        plt.ylabel('Beste Fitness (Mittelwert ± Std)', fontsize=12)
        plt.title('Vergleich der Experimente', fontsize=14, fontweight='bold')
        plt.xticks(x_pos, namen, rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()

        # Speichern
        output_path = self.results_dir / output_file
        plt.savefig(output_path, dpi=300)
        plt.close()

        print(f"✅ Plot erstellt: {output_path}")

    def erstelle_alle_plots(self):
        """Erstellt alle Standard-Plots."""
        print("\n" + "=" * 60)
        print("ERSTELLE PLOTS")
        print("=" * 60 + "\n")

        self.plot_fitness_verlaeufe()
        self.plot_vergleich_balken()

        print("\n✅ Alle Plots erstellt!")


# ─── Convenience-Funktionen ────────────────────────────────────────────────────

def erstelle_plots(results_dir: str = "experiment_results"):
    """
    Erstellt alle Plots aus einem Ergebnis-Verzeichnis.

    Nützlich um Plots nachträglich zu erstellen.
    """
    plotter = PlotCreator(results_dir)
    plotter.erstelle_alle_plots()


if __name__ == "__main__":
    # Erstelle Plots aus test_results
    erstelle_plots("all_experiments")
