from typing import Tuple, List, Optional
from src.grid import Grid
from enum import Enum

# oben links ist (0,0) wegen numpy
LINKS = -1
RECHTS = +1
HOCH = -1
RUNTER = +1

# Diese Konfig kann geändert werden und sollte die Fitness beeinträchtigen
LAUFKOSTEN = 1
SPRINGKOSTEN = 5
FALLKOSTEN = 1
SPRUNG_HOEHE = 3  # kann max. 3 Tiles hoch springen
SPRUNG_WEITE = 4  # kann max. 4 Tiles weit springen
FALL_DISTANZ_MAX = 10  # maximaler Fall


class BewegungTyp(Enum):
    LAUFEN = "laufen"
    SPRINGEN = "springen"
    FALLEN = "fallen"


class Position:

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __repr__(self):
        return f"Position(x={self.x}, y={self.y})"

    def add(self, other: Tuple[int, int]) -> 'Position':
        return Position(self.x + other[0], self.y + other[1])

    def manhattan_distanz_zu(self, andere: 'Position') -> int:
        # Manhattan Distanz, da es keine diagonalen Bewegung existiert ist das für die Heuristik des A* Autoplayer mehr sinnvoll
        # https://www.reddit.com/r/gamedev/comments/z2hpv/pathfinding_in_a_2d_platformer/
        return abs(self.x - andere.x) + abs(self.y - andere.y)


class Bewegung:
    def __init__(self, start: Position, ziel: Position, typ: BewegungTyp, kosten: int = 1):
        self.start = start
        self.ziel = ziel
        self.typ = typ
        self.kosten = kosten

    def __repr__(self):
        return f"Bewegung({self.typ}, {self.start} bis {self.ziel}, kosten={self.kosten})"

    def horizontale_distanz(self) -> int:
        return abs(self.ziel.x - self.start.x)

    def vertikale_distanz(self) -> int:
        return abs(self.ziel.y - self.start.y)


class PhysikEngine:

    def __init__(self, grid: Grid):
        self.grid = grid

    def ist_position_gueltig(self, pos: Position) -> bool:
        # ist die Position begehbar
        return self.grid.ist_im_grid(pos.x, pos.y) and not self.grid.ist_solid(pos.x, pos.y)

    def steht_auf_boden(self, pos: Position) -> bool:
        # kann nur springen/stehen wenn boden da ist
        return self.grid.hat_boden_darunter(pos.x, pos.y)

    def kann_hier_stehen(self, pos: Position) -> bool:
        return self.ist_position_gueltig(pos) and self.steht_auf_boden(pos)

    def kann_laufen(self, von: Position, richtung: int) -> Optional[Position]:
        # Pruefung ob man zu einer Position laufen kann (also wenn nichts im Weg steht und die Position ein Boden zum stehen hat, und die Position existiert)
        ziel = Position(von.x + richtung, von.y)

        if not self.grid.ist_im_grid(ziel.x, ziel.y):
            return None

        if self.grid.ist_solid(ziel.x, ziel.y):
            return None

        if not self.grid.hat_boden_darunter(ziel.x, ziel.y):
            return None

        return ziel

    def berechne_sprung(self, start: Position, richtung: int, ziel_hoehe: int) -> Optional[Position]:
        # berechnet alle möglichen Spruenge von eine Position bis zu einer Position
        if not self.steht_auf_boden(start):
            return None

        if ziel_hoehe > SPRUNG_HOEHE:
            return None

        moegliche_ziele = []

        for horizontale_distanz in range(1, SPRUNG_WEITE + 1):
            ziel_x = start.x + (richtung * horizontale_distanz)
            ziel_y = start.y - ziel_hoehe
            ziel_pos = Position(ziel_x, ziel_y)

            # wenn nicht im grid, solide, kein Boden und Hindernisse im Sprung dann naechster Sprung
            if not self.grid.ist_im_grid(ziel_x, ziel_y):
                continue

            if self.grid.ist_solid(ziel_x, ziel_y):
                continue

            if not self.grid.hat_boden_darunter(ziel_x, ziel_y):
                continue

            if self.ist_sprung_frei(start, ziel_pos):
                moegliche_ziele.append((ziel_pos, horizontale_distanz))

        if moegliche_ziele:
            # der weiteste Sprung wird genommen der moeglich ist
            moegliche_ziele.sort(key=lambda x: x[1], reverse=True)
            return moegliche_ziele[0][0]

        return None

    def ist_sprung_frei(self, start: Position, ziel: Position) -> bool:
       # pruefung ob Linie zwischen start und Ziel frei ist
       # Inspiration: https://deepnight.net/tutorial/bresenham-magic-raycasting-line-of-sight-pathfinding/
        x0, y0 = start.x, start.y
        x1, y1 = ziel.x, ziel.y

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)

        x = x0
        y = y0

        x_step = 1 if x1 > x0 else -1
        y_step = 1 if y1 > y0 else -1

        if dx > dy:
            error = dx / 2.0

            while x != x1:
                x += x_step
                error -= dy

                if error < 0:
                    y += y_step
                    error += dx

                if not (x == x1 and y == y1):
                    if self.grid.ist_solid(x, y):
                        return False
        else:
            error = dy / 2.0

            while y != y1:
                y += y_step
                error -= dx

                if error < 0:
                    x += x_step
                    error += dy

                if not (x == x1 and y == y1):
                    if self.grid.ist_solid(x, y):
                        return False
        return True

    def finde_alle_sprung_ziele(self, von: Position) -> List[Position]:
        if not self.steht_auf_boden(von):
            return []

        sprung_ziele = []

        for richtung in [LINKS, RECHTS]:
            # am anfang von 0- sprung hoehe, aber fall sollte auch betrachtet werden, hoher fall sollte aber vermieden werden
            for hoehe in range(-3, SPRUNG_HOEHE + 1):
                ziel = self.berechne_sprung(von, richtung, hoehe)
                if ziel:
                    sprung_ziele.append(ziel)

        return sprung_ziele

    def berechne_fall_position(self, von: Position) -> Optional[Position]:
        # berechnet Fall, von 1 bis y grid max
        if self.steht_auf_boden(von):
            return von

        aktuelle_y = von.y

        for fall_distanz in range(1, FALL_DISTANZ_MAX + 1):
            naechste_y = aktuelle_y + fall_distanz
            naechste_pos = Position(von.x, naechste_y)

            if not self.grid.ist_im_grid(von.x, naechste_y):
                return None

            if self.grid.hat_boden_darunter(von.x, naechste_y):
                if not self.grid.ist_solid(von.x, naechste_y):
                    return naechste_pos
                else:
                    return None
        return None

    def finde_alle_nachbarn(self, von: Position) -> List[Bewegung]:
        # finde alle möglichen Bewegungen, die drei Optionen sind laufen, springen, fallen
        bewegungen = []

        for richtung in [LINKS, RECHTS]:
            ziel = self.kann_laufen(von, richtung)
            if ziel:
                bewegungen.append(Bewegung(start=von, ziel=ziel, typ=BewegungTyp.LAUFEN, kosten=LAUFKOSTEN))

        if self.steht_auf_boden(von):
            sprung_ziele = self.finde_alle_sprung_ziele(von)
            for ziel in sprung_ziele:
                bewegungen.append(Bewegung(start=von, ziel=ziel, typ=BewegungTyp.SPRINGEN, kosten=SPRINGKOSTEN))

        if not self.steht_auf_boden(von):
            fall_ziel = self.berechne_fall_position(von)
            if fall_ziel:
                bewegungen.append(Bewegung(start=von, ziel=fall_ziel, typ=BewegungTyp.FALLEN, kosten=FALLKOSTEN))

        return bewegungen

