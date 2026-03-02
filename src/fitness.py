from grid import Grid, PLATTFORM
from autoplayer import Autoplayer, Pfad
from typing import Dict

from src.physics import Position


class SimpleFitness:

    def __init__(self):
        self.anzahl_level = 0
        self.anzahl_loesbar = 0

    def berechne_fitness(self, grid: Grid) -> float:
        # simple Fitness wo einfach nur Loesbarkeit + Schwierigkeit geprüft wird, wobei Schwierigkeit nur die Anzahl an Spruengen ist
        self.anzahl_level += 1

        autoplayer = Autoplayer(grid)
        loesbar = autoplayer.ist_level_loesbar()
        pfad = autoplayer.letzter_pfad
        statistik = autoplayer.berechne_pfad_statistiken(pfad)
        if not loesbar:
            return -50

        self.anzahl_loesbar += 1
        anzahl_spruenge = statistik["anzahl_spruenge"]
        fitness = 1000.0 + anzahl_spruenge * 10.0

        return fitness

    def get_statistiken(self) -> Dict:
        return {'anzahl_level': self.anzahl_level, 'anzahl_loesbare': self.anzahl_loesbar,
                'loesbarkeits_rate': (self.anzahl_loesbar / self.anzahl_level)}


class Fitness:
    def __init__(self, gewicht_loesbarkeit: float = 1000.0, gewicht_schwierigkeit: float = 3.0,
                 gewicht_plattformen: float = 2.0):
        self.gewicht_loesbarkeit = gewicht_loesbarkeit
        self.gewicht_schwierigkeit = gewicht_schwierigkeit
        self.gewicht_plattformen = gewicht_plattformen

        self.anzahl_level = 0
        self.anzahl_loesbar = 0

    def berechne_fitness(self, grid: Grid) -> float:
        self.anzahl_level += 1
        autoplayer = Autoplayer(grid)
        loesbar = autoplayer.ist_level_loesbar()
        if not loesbar:
            return -50

        self.anzahl_loesbar += 1
        pfad = autoplayer.letzter_pfad
        statistik = autoplayer.berechne_pfad_statistiken(pfad)

        loesbarkeit = self.gewicht_loesbarkeit
        schwierigkeit = self.berechne_schwierigkeit(statistik)
        plattform_nutzung = self.berechne_plattform(grid, pfad)

        fitness = loesbarkeit + schwierigkeit + plattform_nutzung

        return fitness

    def berechne_schwierigkeit(self, statistik: Dict) -> float:
        # Da Sprungkosten teuer ist, ist jeder Sprung auch ein Höhenunterschied des Levels -> Wenn möglich wird gelaufen, daher keine Vertikalitätscheck
        schwierigkeit = 0.0
        schwierigkeit += statistik.get('anzahl_spruenge', 0) * 3.0
        schwierigkeit += statistik.get('pfad_laenge', 0) * 3.0

        return schwierigkeit * self.gewicht_schwierigkeit

    def berechne_plattform(self, grid: Grid, pfad: Pfad) -> float:
        # berechne Plattformnutzung, anhand der Pfad Positionen
        # Ebenfalls die Plattform isolierung, wenn pfad nicht genutzt wird, dann die Nachbarn und schauen ob das eine PLattform ist
        plattformen = []
        pfad_set = set(pfad.positionen)
        genutzte_plattformen = 0
        isolierte_plattformen = 0

        for y in range(grid.hoehe):
            for x in range(grid.breite):
                if grid.get_tile(x, y) == PLATTFORM:
                    pos = Position(x, y)
                    plattformen.append(pos)
                    if pos in pfad_set:
                        genutzte_plattformen += 1
                    else:
                        nachbarn = [(x - 1, y),
                                    (x + 1, y),
                                    (x, y - 1),
                                    (x, y + 1)]
                        hat_nachbar = any(
                            0 <= nx < grid.breite and
                            0 <= ny < grid.hoehe and
                            grid.get_tile(nx, ny) == PLATTFORM
                            for nx, ny in nachbarn
                        )
                        if not hat_nachbar:
                            isolierte_plattformen += 1
        if len(plattformen) == 0:
            return 0.0
        nutzungs_ratio = genutzte_plattformen / len(plattformen)
        isolations_strafe = isolierte_plattformen / len(plattformen)
        score = (nutzungs_ratio * 100.0 - isolations_strafe * 50.0)

        return max(0.0, score) * self.gewicht_plattformen

    def get_statistiken(self) -> Dict:
        return {'anzahl_level': self.anzahl_level, 'anzahl_loesbare': self.anzahl_loesbar,
                'loesbarkeits_rate': (self.anzahl_loesbar / self.anzahl_level)}
