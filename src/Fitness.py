from grid import Grid
from autoplayer import Autoplayer
from typing import Dict


class SimpleFitness:

    def __init__(self):
        self.anzahl_level = 0
        self.anzahl_loesbar = 0

    def berechne_fitness(self, grid: Grid) -> float:
        # simple Fitness wo einfach nur Loesbarkeit + Schwierigkeit geprüft wird, wobei Schwierigkeit nur die Anzahl an Spruengen ist
        self.anzahl_level += 1

        autoplayer = Autoplayer(grid)
        loesbar = autoplayer.ist_level_loesbar()

        if not loesbar:
            return 0.0

        self.anzahl_loesbar += 1
        pfad = autoplayer.letzter_pfad
        statistik = autoplayer.berechne_pfad_statistiken(pfad)
        anzahl_spruenge = statistik["anzahl_spruenge"]

        fitness = 1000.0 + anzahl_spruenge * 10.0

        return fitness

    def get_statistiken(self) -> Dict:
        return {'anzahl_evaluationen': self.anzahl_level, 'anzahl_loesbare': self.anzahl_loesbar, 'loesbarkeits_rate': (self.anzahl_loesbar / self.anzahl_level)}
