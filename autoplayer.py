from typing import Optional, List
import heapq
from grid import Grid
from physics import PhysikEngine, Position, Bewegung


class Pfad:

    def __init__(self, positionen: List[Position], bewegungen: List[Bewegung]):
        self.positionen = positionen
        self.bewegungen = bewegungen
        self.laenge = len(positionen)

    def ist_leer(self) -> bool:
        return len(self.positionen) == 0


class ANode:

    def __init__(self, position: Position, g_kosten: float, h_kosten: float, parent: Optional['ANode'] = None,
                 bewegung: Optional[Bewegung] = None):
        self.position = position
        self.g_kosten = g_kosten
        self.h_kosten = h_kosten
        self.f_kosten = g_kosten + h_kosten
        self.parent = parent
        self.bewegung = bewegung

    def __lt__(self, other):
        # fuer A*
        return self.f_kosten < other.f_kosten

    def __eq__(self, other):
        if not isinstance(other, ANode):
            return False
        return self.position == other.position

    def __repr__(self):
        return f"ANode({self.position}, f={self.f_kosten:.1f})"


class Autoplayer:
    """A* Algorithm
    1. Create a search graph G, consisting only of the start node n₀. Put n₀ on a list called OPEN.
    2. Create a list called CLOSED that is initially empty.
    3. If OPEN is empty, exit with failure.
    4. Select the first node on OPEN, remove it from OPEN, and put it on CLOSED. Call this node n.
    5. If n is a goal node, exit successfully with the solution obtained by tracing a path along the pointers from n to n₀ in G. (The pointers define a search tree and are established in step 7.)
    6. Expand node n, generating the set M of its successors that are not already ancestors of n in G. Install these members of M as successors of n in G.
    7. Establish a pointer to n from each member of M that was not already in G (i.e., not already on either OPEN or CLOSED). Add these members of M to OPEN.
    For each member m of M that was already on OPEN or CLOSED, redirect its pointer to n if the best path to m found so far is through n.
    For each member of M already on CLOSED, redirect the pointers of each of its descendants in G so that they point backward along the best paths found so far to these descendants.
    8. Reorder the list OPEN in order of increasing f values. (Ties among minimal f values are resolved in favor of the deepest node in the search tree.)
    9. Go to step 3.
    von Nils J.Nilsson - Artificial Intelligence A new synthesis"""

    def __init__(self, grid: Grid):
        self.grid = grid
        self.physik = PhysikEngine(grid)

        self.letzter_pfad: Optional[Pfad] = None
        self.anzahl_evaluierte_nodes = 0
        self.anzahl_pfadsuchen = 0

    def ist_level_loesbar(self) -> bool:
        start_pos = self.grid.get_start()
        ziel_pos = self.grid.get_ziel()

        if start_pos is None or ziel_pos is None:
            return False

        start_pos = Position(start_pos[0], start_pos[1])
        ziel_pos = Position(ziel_pos[0], ziel_pos[1])

        pfad = self.finde_pfad(start_pos, ziel_pos)
        return not pfad.ist_leer()

    def finde_pfad(self, start: Position, ziel: Position, max_iterationen: int = 10000) -> Pfad:
        self.anzahl_pfadsuchen += 1
        self.anzahl_evaluierte_nodes = 0

        # Sollte vorher schon beim LevelValidator verhindert werden
        if start == ziel:
            return Pfad([start], [])

        open_list = []  # nutzung eines Heaps anstelle Liste siehe unten
        closed_set = set()  # schon besuchte Positionen

        g_kosten_map = {start: 0}

        start_node = ANode(position=start, g_kosten=0, h_kosten=start.manhattan_distanz_zu(ziel))
        heapq.heappush(open_list, start_node)

        iterationen = 0
        while open_list and iterationen < max_iterationen:
            iterationen += 1
            self.anzahl_evaluierte_nodes += 1

            # Node mit niedrigsten f-Kosten
            current = heapq.heappop(open_list)

            # wenn schon besucht dann skip
            if current.position in closed_set:
                continue

            if current.position == ziel:
                pfad = self.rekonstruiere_pfad(current)
                self.letzter_pfad = pfad
                return pfad

            closed_set.add(current.position)

            nachbarn = self.finde_nachbar_nodes(current, ziel)

            for nachbar in nachbarn:
                if nachbar.position in closed_set:
                    continue

                # Mit g kosten schauen ob das ein besserer weg ist
                if (nachbar.position not in g_kosten_map or
                        nachbar.g_kosten < g_kosten_map[nachbar.position]):
                    g_kosten_map[nachbar.position] = nachbar.g_kosten
                    heapq.heappush(open_list, nachbar)

        return Pfad([], [])

    def finde_nachbar_nodes(self, current: ANode, ziel: Position) -> List[ANode]:
        nachbar_nodes = []

        moegliche_bewegungen = self.physik.finde_alle_nachbarn(current.position)
        print(moegliche_bewegungen)

        for bewegung in moegliche_bewegungen:
            neue_g_kosten = current.g_kosten + bewegung.kosten

            h_kosten = bewegung.ziel.manhattan_distanz_zu(ziel)

            nachbar = ANode(position=bewegung.ziel, g_kosten=neue_g_kosten, h_kosten=h_kosten, parent=current,
                            bewegung=bewegung)
            nachbar_nodes.append(nachbar)

        return nachbar_nodes

    def rekonstruiere_pfad(self, ziel_node: ANode) -> Pfad:
        positionen = []
        bewegungen = []

        current = ziel_node
        while current is not None:
            positionen.append(current.position)
            if current.bewegung:
                bewegungen.append(current.bewegung)
            current = current.parent

        positionen.reverse()
        bewegungen.reverse()

        return Pfad(positionen, bewegungen)

    def berechne_pfad_statistiken(self, pfad: Optional[Pfad] = None) -> dict:
        if pfad is None:
            pfad = self.letzter_pfad

        anzahl_sprunge = 0
        if pfad is not None:
            anzahl_spruenge = sum(1 for bew in pfad.bewegungen if bew.typ == "springen")

        if pfad is None or pfad.ist_leer():
            return {"loesbar": False, "pfad_laenge": 0, "anzahl_spruenge": 0, "evaluierte_nodes": self.anzahl_evaluierte_nodes}
        return {"loesbar": True, "pfad_laenge": pfad.laenge, "anzahl_spruenge": anzahl_spruenge, "evaluierte_nodes": self.anzahl_evaluierte_nodes}
