import numpy as np
from typing import Tuple, List, Optional

# Tiles im Grid
LUFT = 0
BODEN = 1
PLATTFORM = 2
START = 3
ZIEL = 4


class Grid:

    def __init__(self, breite: int = 20, hoehe: int = 10):
        self.breite = breite
        self.hoehe = hoehe

        # Kiene Liste von einer Liste, da später mit EA gearbeitet werden und da numpy gut ist
        self.tiles = np.zeros((hoehe, breite), dtype=int)

        # Jedes level sollte erstmal ein Boden haben, diese können bei der Generation von Leveln eventuell mit Lücken gefuellt werden
        self.tiles[hoehe - 1, :] = BODEN

    def ist_im_grid(self, x: int, y: int) -> bool:
        # ist punkt im grid?
        return 0 <= x < self.breite and 0 <= y < self.hoehe

    def get_tile(self, x: int, y: int) -> int:
        if self.ist_im_grid(x, y):
            # numpy ist matrix daher (Reihe/Spalte), deswegen hier y,x anstelle x,y
            return int(self.tiles[y, x])
        return LUFT

    def set_tile(self, x: int, y: int, tile_typ: int) -> None:
        if self.ist_im_grid(x, y):
            self.tiles[y, x] = tile_typ

    def ist_solid(self, x: int, y: int) -> bool:
        # ist tile solide? also boden oder plattform
        tile = self.get_tile(x, y)
        return tile in (BODEN, PLATTFORM)

    def ist_begehbar(self, x: int, y: int) -> bool:
        # Tile darf kein kein Boden/Plattform sein und darunter muss Boden oder PLattform sein
        tile = self.get_tile(x, y)
        return (tile not in (BODEN, PLATTFORM)) and self.hat_boden_darunter(x, y)

    def hat_boden_darunter(self, x: int, y: int) -> bool:
        return self.ist_solid(x, y + 1)

    def get_start(self) -> Optional[Tuple[int, int]]:
        # Hole Start position wenne existiert
        positionen = np.argwhere(self.tiles == START)
        if len(positionen == 1):
            y, x = positionen[0]
            return x, y
        return None

    def get_ziel(self) -> Optional[Tuple[int, int]]:
        # Hole Ziel position wenne existiert
        positionen = np.argwhere(self.tiles == ZIEL)
        if len(positionen == 1):
            y, x = positionen[0]
            return x, y
        return None

    def hat_start_ziel(self) -> bool:
        # muss haben damit level valide ist
        return self.get_start() is not None and self.get_ziel() is not None

    def anzahl_tiles(self, typ: int) -> int:
        # fitness eventuell
        return int(np.sum(self.tiles == typ))

    def grid_matrix(self) -> np.ndarray:
        return self.tiles.copy()

    def print_grid(self) -> None:
        # print methode mithilfe von Copilot
        symbole = {
            LUFT:      "  ",
            BODEN:     "██",
            PLATTFORM: "══",
            START:     "ST",
            ZIEL:      "ZI",
        }
        print(f"\nGrid ({self.breite}x{self.hoehe}):")
        print("+" + "──" * self.breite + "+")
        for y in range(self.hoehe):
            zeile = "|"
            for x in range(self.breite):
                tile = self.get_tile(x, y)
                zeile += symbole.get(tile, "??")
            zeile += "|"
            print(zeile)
        print("+" + "──" * self.breite + "+")

        # Info über Start/Ziel
        start = self.get_start()
        ziel  = self.get_ziel()
        print(f"Start: {start} | Ziel: {ziel}")
        print(f"Plattformen: {self.anzahl_tiles(PLATTFORM)} Tiles")

class LevelBuilder:

    @staticmethod
    def leeres_level() -> Grid:
        return Grid()

    @staticmethod
    def einfaches_level() -> Grid:
        # Start ist unten links und Ziel ist oben rechts mit Plattformtreppen datwischen, Level ist loesbar
        g = Grid()

        g.set_tile(1, 8, START)

        g.set_tile(4, 7, PLATTFORM)
        g.set_tile(5, 7, PLATTFORM)
        g.set_tile(6, 7, PLATTFORM)

        g.set_tile(8, 5, PLATTFORM)
        g.set_tile(9, 5, PLATTFORM)
        g.set_tile(10, 5, PLATTFORM)

        g.set_tile(12, 3, PLATTFORM)
        g.set_tile(13, 3, PLATTFORM)
        g.set_tile(14, 3, PLATTFORM)

        g.set_tile(16, 2, PLATTFORM)
        g.set_tile(17, 2, PLATTFORM)
        g.set_tile(18, 2, PLATTFORM)
        g.set_tile(19, 2, PLATTFORM)

        g.set_tile(18, 1, ZIEL)

        return g

    @staticmethod
    def mittleres_level() -> Grid:
        # so ziemlich genau wie einfaches Level nur mit Lücken im Boden
        g = Grid()

        g.set_tile(1, 8, START)

        for x in [3, 4, 7, 8, 9]:
            g.set_tile(x, 9, LUFT)

        g.set_tile(5, 7, PLATTFORM)
        g.set_tile(6, 7, PLATTFORM)

        g.set_tile(10, 6, PLATTFORM)
        g.set_tile(11, 6, PLATTFORM)

        g.set_tile(13, 4, PLATTFORM)
        g.set_tile(14, 4, PLATTFORM)
        g.set_tile(15, 4, PLATTFORM)

        g.set_tile(17, 4, PLATTFORM)
        g.set_tile(18, 4, PLATTFORM)
        g.set_tile(19, 4, PLATTFORM)

        g.set_tile(18, 3, ZIEL)

        return g

    @staticmethod
    def mittleres_level2() -> Grid:
        # dieses Level wurde hinzugefuegt nachdem fehler in der physik erkannt wurden (Logik fehler beim Springen -> ist durch Plattform gesprungen)
        g = Grid()

        g.set_tile(1, 8, START)

        for x in [3, 4, 7, 8, 9]:
            g.set_tile(x, 9, LUFT)

        g.set_tile(5, 7, PLATTFORM)
        g.set_tile(6, 7, PLATTFORM)

        g.set_tile(10, 6, PLATTFORM)
        g.set_tile(11, 6, PLATTFORM)

        g.set_tile(13, 4, PLATTFORM)
        g.set_tile(14, 4, PLATTFORM)
        g.set_tile(15, 4, PLATTFORM)

        g.set_tile(17, 6, PLATTFORM)
        g.set_tile(18, 6, PLATTFORM)
        g.set_tile(19, 6, PLATTFORM)

        g.set_tile(17, 8, PLATTFORM)
        g.set_tile(18, 8, PLATTFORM)
        g.set_tile(19, 8, PLATTFORM)

        g.set_tile(18, 7, ZIEL)

        return g

    @staticmethod
    def zufalls_level(breite: int = 20, hoehe: int = 10, plattform_wahrscheinlichkeit: float = 0.15, luecken_wahrscheinlichkeit: float = 0.15) -> Grid:
        # zufaelliges Level wird erstellt aber mit dem Start immer links unten und Ziel immer rechts. Start und Ziel müssen immer auf was solides stehen
        g = Grid(breite, hoehe)

        for y in range(1, hoehe - 2):
            for x in range(1, breite - 1):
                if np.random.random() < plattform_wahrscheinlichkeit:
                    g.set_tile(x, y, PLATTFORM)

        # Luft im Boden aber nicht bei Start und Ziel
        for x in range(2, breite - 2):
            if np.random.random() < luecken_wahrscheinlichkeit:
                g.set_tile(x, hoehe - 1, LUFT)

        g.set_tile(1, hoehe - 2, START)

        ziel_y = np.random.randint(1, hoehe - 2)
        g.set_tile(breite - 2, ziel_y, ZIEL)
        g.set_tile(breite - 2, ziel_y + 1, PLATTFORM)

        return g

class LevelValidator:

    @staticmethod
    def ist_gueltig(grid: Grid) -> Tuple[bool, List[str]]:
        # prueft ob Level Mindestanforderungen hat. Wenn nicht muss Level nicht mit Agent geprueft werden
        fehler = []

        start = grid.get_start()
        ziel = grid.get_ziel()

        if start is None:
            fehler.append("Kein Start")
        if ziel is None:
            fehler.append("Kein Ziel")

        if start == ziel:
            fehler.append("Start gleich Ziel")

        return len(fehler) == 0, fehler
