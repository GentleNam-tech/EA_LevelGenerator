import pygame
import os
import sys
from grid import (
    Grid, LevelBuilder, LevelValidator,
    LUFT, BODEN, PLATTFORM, START, ZIEL
)

# Farb-Konstanten
FARBEN = {
    LUFT: (135, 206, 235),  # Hellblau (Himmel)
    BODEN: (101, 67, 33),  # Braun (Erde)
    PLATTFORM: (150, 150, 160),  # Grau (Stein/Metall)
    START: (255, 220, 0),  # Gelb (Start-Markierung)
    ZIEL: (50, 205, 50),  # Grün (Ziel-Markierung)
}

FARBE_HINTERGRUND = (30, 30, 40)  # Dunkles Grau
FARBE_TEXT = (240, 240, 240)  # Fast Weiß
FARBE_TEXT_DUNKEL = (180, 180, 180)  # Grau


class GridVisualizer:
    # TODO spieler(x, y), pfad, fitness, generation, vielleicht noch images für Ziel, Start, Spieler?

    # Fenstergröße
    TILE_GROESSE = 48  # Pixel pro Tile
    INFO_LEISTE = 80  # Pixel für Info Leiste unten
    RAND = 20  # Rand um das Grid

    def __init__(self, grid: Grid):
        self.grid = grid

        self.fenster_breite = (grid.breite * self.TILE_GROESSE
                               + 2 * self.RAND)
        self.fenster_hoehe = (grid.hoehe * self.TILE_GROESSE
                              + 2 * self.RAND
                              + self.INFO_LEISTE)

        pygame.init()
        self.fenster = pygame.display.set_mode(
            (self.fenster_breite, self.fenster_hoehe)
        )
        pygame.display.set_caption("Jump'n'Run: Evolutionäre Levelgenerierung")

        self.font_gross = pygame.font.SysFont("monospace", 16, bold=True)
        self.font_normal = pygame.font.SysFont("monospace", 13)
        self.font_klein = pygame.font.SysFont("monospace", 11)

        self.clock = pygame.time.Clock()

    def tile_zu_pixel(self, x: int, y: int) -> tuple:
        px = self.RAND + x * self.TILE_GROESSE
        py = self.RAND + y * self.TILE_GROESSE
        return px, py

    def pixel_zu_tile(self, px: int, py: int) -> tuple:
        x = (px - self.RAND) // self.TILE_GROESSE
        y = (py - self.RAND) // self.TILE_GROESSE
        return x, y

    def render_hintergrund(self):
        self.fenster.fill(FARBE_HINTERGRUND)

    def render_tile(self, x: int, y: int):
        tile_typ = self.grid.get_tile(x, y)
        px, py = self.tile_zu_pixel(x, y)
        g = self.TILE_GROESSE

        pygame.draw.rect(
            self.fenster,
            FARBEN[tile_typ],
            (px, py, g, g)
        )

        if tile_typ == START:
            text = self.font_gross.render("S", True, (50, 50, 50))
            self.fenster.blit(text, (px + g // 2 - 6, py + g // 2 - 8))
        elif tile_typ == ZIEL:
            text = self.font_gross.render("Z", True, (20, 80, 20))
            self.fenster.blit(text, (px + g // 2 - 6, py + g // 2 - 8))

    def render_grid(self):
        for y in range(self.grid.hoehe):
            for x in range(self.grid.breite):
                self.render_tile(x, y)

    def render_grid_linien(self):
        gitter_farbe = (60, 80, 100)  # Sehr dunkel

        for y in range(self.grid.hoehe + 1):
            py = self.RAND + y * self.TILE_GROESSE
            pygame.draw.line(
                self.fenster,
                gitter_farbe,
                (self.RAND, py),
                (self.RAND + self.grid.breite * self.TILE_GROESSE, py),
                1
            )
        for x in range(self.grid.breite + 1):
            px = self.RAND + x * self.TILE_GROESSE
            pygame.draw.line(
                self.fenster,
                gitter_farbe,
                (px, self.RAND),
                (px, self.RAND + self.grid.hoehe * self.TILE_GROESSE),
                1
            )

    def render_info_leiste(self):
        # Informationen werden angezeigt (aktuelle Generation, beste Fitness, Lösbarkeitsrate kommt noch)
        leiste_y = self.fenster_hoehe - self.INFO_LEISTE
        pygame.draw.rect(
            self.fenster,
            (20, 20, 30),
            (0, leiste_y, self.fenster_breite, self.INFO_LEISTE)
        )
        pygame.draw.line(
            self.fenster,
            (80, 80, 100),
            (0, leiste_y),
            (self.fenster_breite, leiste_y),
            2
        )

        # Info zum Level
        start = self.grid.get_start()
        ziel = self.grid.get_ziel()
        plattformen = self.grid.anzahl_tiles(PLATTFORM)

        zeile1 = (f"Grid: {self.grid.breite}x{self.grid.hoehe}  |  "
                  f"Start: {start}  |  Ziel: {ziel}  |  "
                  f"Plattformen: {plattformen}")

        zeile2 = "Tasten: [1] Einfach  [2] Mittel  [3] Zufällig  [S] Screenshot  [ESC] Beenden"

        text1 = self.font_normal.render(zeile1, True, FARBE_TEXT)
        text2 = self.font_klein.render(zeile2, True, FARBE_TEXT_DUNKEL)

        self.fenster.blit(text1, (10, leiste_y + 12))
        self.fenster.blit(text2, (10, leiste_y + 38))

        # Legende
        legende_x = 10
        legende_y = leiste_y + 58
        legende_items = [
            (BODEN, "Boden"),
            (PLATTFORM, "Plattform"),
            (START, "Start"),
            (ZIEL, "Ziel"),
        ]
        for tile_typ, name in legende_items:
            pygame.draw.rect(
                self.fenster,
                FARBEN[tile_typ],
                (legende_x, legende_y, 14, 14)
            )
            text = self.font_klein.render(name, True, FARBE_TEXT_DUNKEL)
            self.fenster.blit(text, (legende_x + 18, legende_y))
            legende_x += 90

    def render_alles(self):
        self.render_hintergrund()
        self.render_grid()
        self.render_grid_linien()
        self.render_info_leiste()
        pygame.display.flip()

    def screenshot_speichern(self, dateiname: str = "level_screenshot.png"):
        ordner = "screenshots"
        pfad = os.path.join(ordner, dateiname)
        pygame.image.save(self.fenster, pfad)
        print(f"Screenshot gespeichert: {pfad}")

    def lade_grid(self, neues_grid: Grid):
        self.grid = neues_grid

    def run(self):
        screenshot_zaehler = 0

        print("\nJump'n'Run Grid Visualizer")
        print("Tasten:")
        print("  [1] Einfaches Level")
        print("  [2] Mittelschweres Level")
        print("  [3] Zufälliges Level")
        print("  [S] Screenshot speichern")
        print("  [ESC] / [Q] Beenden\n")

        while True:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_1:
                        self.lade_grid(LevelBuilder.einfaches_level())
                        print("Level gewechselt: Einfach")

                    elif event.key == pygame.K_2:
                        self.lade_grid(LevelBuilder.mittleres_level())
                        print("Level gewechselt: Mittel")

                    elif event.key == pygame.K_3:
                        zufaellig = LevelBuilder.zufalls_level()
                        self.lade_grid(zufaellig)
                        gueltig, fehler = LevelValidator.ist_gueltig(zufaellig)
                        print(f"Zufälliges Level: {'Gültig' if gueltig else 'Ungültig: ' + str(fehler)}")

                    # Screenshot
                    elif event.key == pygame.K_s:
                        screenshot_zaehler += 1
                        dateiname = f"level_{screenshot_zaehler:03d}.png"
                        self.screenshot_speichern(dateiname)

                    # Beenden
                    elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                        pygame.quit()
                        sys.exit()

            self.render_alles()
            self.clock.tick(60)
