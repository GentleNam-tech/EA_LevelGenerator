from src.fitness import SimpleFitness
from src.grid import Grid, LevelBuilder
from visualizer import GridVisualizer
from src.autoplayer import Autoplayer


def test_einfaches_level():
    grid = LevelBuilder.einfaches_level()
    grid.print_grid()

    autoplayer = Autoplayer(grid)

    loesbar = autoplayer.ist_level_loesbar()
    assert loesbar, "Level sollte loesbar sein"

    pfad = autoplayer.letzter_pfad
    print(autoplayer.berechne_pfad_statistiken(pfad))
    assert pfad.laenge > 0, "Pfad sollte nicht leer sein"


def test_mittelschweres_level():
    grid = LevelBuilder.mittleres_level()
    grid.print_grid()

    autoplayer = Autoplayer(grid)

    loesbar = autoplayer.ist_level_loesbar()
    assert loesbar, "Level sollte loesbar sein"
    pfad = autoplayer.letzter_pfad
    print(autoplayer.berechne_pfad_statistiken(pfad))
    assert pfad.laenge > 0, "Pfad sollte nicht leer sein"


def test_mittelschweres_level2():
    grid = LevelBuilder.mittleres_level2()
    grid.print_grid()

    autoplayer = Autoplayer(grid)

    loesbar = autoplayer.ist_level_loesbar()
    print(loesbar)
    pfad = autoplayer.letzter_pfad
    print(autoplayer.berechne_pfad_statistiken(pfad))
    visualizer = GridVisualizer(grid)
    visualizer.run()


def test_unloesbar_level():
    grid = Grid(20, 10)
    grid.set_tile(1, 8, 3)  # START

    # Ziel ist eingemauert, also Level unloesbar
    grid.set_tile(18, 2, 4)
    grid.set_tile(17, 2, 1)
    grid.set_tile(19, 2, 1)
    grid.set_tile(18, 1, 1)
    grid.set_tile(18, 3, 1)

    grid.print_grid()

    autoplayer = Autoplayer(grid)
    loesbar = autoplayer.ist_level_loesbar()
    assert not loesbar, "Level sollte nicht loesbar sein"
    pfad = autoplayer.letzter_pfad
    print(autoplayer.berechne_pfad_statistiken(pfad))


def test_direkter_weg():
    grid = Grid(20, 10)
    grid.set_tile(1, 8, 3)  # START
    grid.set_tile(18, 8, 4)  # ZIEL

    grid.print_grid()

    autoplayer = Autoplayer(grid)

    loesbar = autoplayer.ist_level_loesbar()
    assert loesbar, "Level sollte loesbar sein"
    pfad = autoplayer.letzter_pfad
    print(autoplayer.berechne_pfad_statistiken(pfad))
    assert pfad.laenge > 0, "Pfad sollte nicht leer sein"

def test_screenshot():
    grid = LevelBuilder.level_aus_screenshot("experiment_result_new_crossover/bestes_level_0.txt")
    grid.print_grid()

    fitness = SimpleFitness()
    score = fitness.berechne_fitness(grid)
    autoplayer = Autoplayer(grid)
    loesbar = autoplayer.ist_level_loesbar()
    pfad = autoplayer.letzter_pfad
    print(score)
    print(autoplayer.berechne_pfad_statistiken(pfad))
    visualizer = GridVisualizer(grid)
    visualizer.run()


def starte_visualisierung():
    start_level = LevelBuilder.einfaches_level()
    visualizer = GridVisualizer(start_level)
    visualizer.run()


if __name__ == "__main__":
    test_screenshot()
