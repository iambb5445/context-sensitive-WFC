import numpy as np
import imageio.v2 as imageio
import matplotlib.pyplot as plt
from tiled_image import TiledImage, TileGenerator, nxmPatternGenerator, UpLeftLPatternGenerator
from WFC import EntropyOptions, WeightingOptions, UpdatingOptions, WFC
from image_distribution import ImageDistribution

def get_stick_data():
    arr = np.ones((7, 7, 3)) * 0.4
    arr[1, 3] = 0.9
    arr[2, 3] = 0.9
    arr[3, 3] = 0.9
    arr[4, 3] = 0.9
    arr[5, 3] = 0.9
    return arr

def get_image_data(filename):
    im = imageio.imread(filename)
    arr = np.asarray(im)/255
    return arr

def draw_tile_vs_pattern(image_data, tile_size, pattern_generator_func):
    n, m, _ = image_data.shape
    if n % tile_size[0] != 0 or m % tile_size[1] != 0:
        print("Warning: the data is not divisible by the tile size, not all of the data is shown.")
    n = round(n / tile_size[0])
    m = round(m / tile_size[1])
    ti = TiledImage.from_unit_generator(TileGenerator(image_data, tile_size))
    # _, axs = plt.subplots(nrows=1, ncols=1, figsize=(5, 5))
    # ti.display(axs)
    _, axs = plt.subplots(nrows=n, ncols=2*m+1, figsize=(2*m+1, n))
    for i in range(n):
        for j in range(m):
            ti.number_to_unit[ti.unit_numbers[i, j]].display(axs[i, j])
            ti.blank.display(axs[i, 9])
    ti = TiledImage.from_unit_generator(pattern_generator_func(image_data, tile_size))
    for i in range(n):
        for j in range(m):
            ti.number_to_unit[ti.unit_numbers[i, j]].display(axs[i, j+m+1], full_pattern=True)
    for i in range(n):
        for j in range(2*m+1):
            axs[i, j].axis("off")
    plt.show()


def draw_wfc_heuristics(unit_generator, size, seed=42, backtrack=False, axs=None,
                        entropy_option=EntropyOptions.UP_LEFT, updating_option=UpdatingOptions.CHAIN):
    print("breaking input into tiles...")
    ti = TiledImage.from_unit_generator(unit_generator)
    if axs is None:
        _, axs = plt.subplots(nrows=1, ncols=4, figsize=(16, 4))
    axs[0].set_title('source', fontsize=22)
    ti.display(axs[0])
    print("training the distribution...")
    id = ImageDistribution()
    id.train(ti)
    print("running wfc with uniform heuristic...")
    axs[1].set_title('uniform', fontsize=22)
    wfc = WFC(id, WeightingOptions.NONE, updating_option, entropy_option)
    ti.from_generated(wfc.generate(size, seed=seed, backtrack=backtrack)).display(axs[1])
    print("running wfc with tile-frequency heuristic...")
    axs[2].set_title('tile-frequency', fontsize=22)
    wfc = WFC(id, WeightingOptions.FREQUENCY_WEIGHTED, updating_option, entropy_option)
    ti.from_generated(wfc.generate(size, seed=seed, backtrack=backtrack)).display(axs[2])
    print("running wfc with context-sensitive heuristic...")
    axs[3].set_title('context-sensitive', fontsize=22)
    wfc = WFC(id, WeightingOptions.CONTEXT_WEIGHTED, updating_option, entropy_option)
    ti.from_generated(wfc.generate(size, seed=seed, backtrack=backtrack)).display(axs[3])
    plt.show()

def main():
    stick_data = get_stick_data()
    stick_tile_size = (1, 1) # each tile is 1x1 pixels
    zelda_data = get_image_data('zeldaMap.png')
    zelda_tile_size = (16, 16) # each tile is 16x16 pixels

    output_size = (20, 20)

    draw_wfc_heuristics(TileGenerator(stick_data, stick_tile_size), output_size)
    draw_wfc_heuristics(TileGenerator(zelda_data, zelda_tile_size), output_size, backtrack=True)

    # Bigger patterns (can take sometime, because of exponential growth in the number of options in bigger patterns):
    # (e.g. zelda has 90 tiles, but over 2900 3x3 patterns)
    # 3x3 patterns
    # draw_wfc_heuristics(nxmPatternGenerator(zelda_data, zelda_tile_size, 3, 3), output_size)
    # L shape patterns
    # draw_wfc_heuristics(UpLeftLPatternGenerator(zelda_data, zelda_tile_size, 3, 3), output_size)

    # to see how the patterns look like, you can run something like this:
    # draw_tile_vs_pattern(zelda_data[16*45:16*50, 16*84:16*89], zelda_tile_size,
    #                    lambda data, tile_size: nxmPatternGenerator(data, tile_size, 3, 3))
    # in this example, we are showing part of zelda data as both 3x3 patterns and tiles. 16x16 is the tile size in the zelda example.
    
    # Other options:

    # - backtrack
    # If you see white tiles, these are contradictions.
    # You can use backtracking to ensure no contradictions by adding backtrack=True,
    # but this will increase the execution time significantly, specially for bigger patterns.
    # example:
    # draw_wfc_heuristics(TileGenerator(zelda_data, zelda_tile_size), output_size, backtrack=True)

    # - entropy
    # If you see some artifacts of tile regions going from top left to bottom right
    # (specially apparent when generating bigger grids - try generating 100x100 intstaed of 20x20),
    # this can be because of the fact that the tiles are selected in order from top left to bottom right
    # this creates biasses in the result that can be solved with using another entropy option such as shannon
    # example:
    # draw_wfc_heuristics(TileGenerator(zelda_data, zelda_tile_size), output_size, entropy_option=EntropyOptions.SHANNON)


if __name__ == "__main__":
    main()
