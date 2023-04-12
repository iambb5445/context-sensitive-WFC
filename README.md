# Context-sensitive WFC

This is the code for the "Better Resemblance without Bigger Patterns: Making Context-sensitive Decisions in WFC" paper by Bahar Bateni, Isaac Karth and Adam Smith. 
The paper was published at FDG 2023 and is available at https://dl.acm.org/doi/10.1145/3582437.3582441.

![Figure_1](https://user-images.githubusercontent.com/25642714/231170868-24e1baa5-e98f-4236-ace0-d76263a730c0.png)

The paper proposes a small and easy to implement modification to the WaveFunctionCollapse algorithm which significantly improves the quality fo results.

WaveFunctionCollapse (WFC) is a Procedural Content Generation algorithm which generates an image similar to some input image. The input image is broken into tiles or patterns
which can be composed by the algorithm to create a new image. A set of constraints extracted from the input are satisfied during the process which results in the similarity
between the input and output. For more information about the WFC algorithm refer to https://github.com/mxgmn/WaveFunctionCollapse.

For more information about this modification refer to the paper. To run this code, refer to the [How to Run](#how-to-run) section. If you want to implement the context-sensitive
heuristic in your own work, refer to the [Porting Context-sensitive Heuristic](#porting-context-sensitive-heuristic) section.
To use an interactive tool and get some outputs, use the colab notebook available at [TODO add link].

## How to Run

### Requirements

The list of requirements are available in the `requirements.txt` file. You can install these requirements with `pip` by using:

```
pip install -r requirements.txt
```

It is suggested to use a virtual environment when installing the requirements. You can use virtualenv by running:

```
pip install virtualenv
virtualenv venv
[windows] venv\Scripts\activate
[linux] source venv/bin/activate
pip install -r requirements.txt
```

To learn more, refer to virtualenv documents.

### Running WFC

You can run the WFC algorithm by running the main script:

`python main.py`

This would results in generating one output per each of the *Decision Heuristic*s for the zelda example.
The result will differ each time. To get the same results everytime, change the `GLOBAL_HASH_TYPE` in the `utility.py` file:

```
GLOBAL_HASH_TYPE = HASH_TYPE.NUMBER_HASH
```

This will run a deterministic hashing algorithm which is significantly slower than the other implementation, but will remove the randomnetss and generate the same output
every time the algorithm is executed with the same seed.

### Available Options

The following options are available in the `main.py` file to get the desired outputs. The examples in the `main.py` file show how the same code can be used for bigger patterns,
as well as visualizing those patterns.

- `backtrack=False` shows if backtracking will be used for satisfying all the constraints. The default value is `False`, meaning that when there are no possible options for
a tile, that tile can be left blank (showing with a white tile). By using `backtrack=True` the execution time will significantly increase based on how limiting the constraints
are, but the result will feel all the tile positions with valid tiles.
- `weighting_option` is the heuristic which gives weights to each tile option in the *Decicion* process. For more information refer to the
[Decition Heuristic](#decision-heuristics) section.
- `entropy_option` is the heuristic which gives entropy values to each position in the *Selection* process. For more information refer to the
[Selection Heuristic](#selection-heuristics) section.

## Overview

### WFC's main loop

The main loop of WFC does the following:

1. Start with an empty grid of the desired size
2. Iteratively, while an empty position exists on the grid:
    1. Select an empty position on the grid (sometimes refered to as *Selection Heuristic*)
    2. Decide which one of the **valid** tiles to put in the target position (refered to as *Decision Process*). By deciding this tile, we say that the wave function for this position has collapsed to one single tile value.
    3. Update the set of **valid** tiles. Collapsing one position may eliminiate some of the options at other positions based on the constraints.
3. Once all positions have been filled with tiles, the output has been generated and the algorithm terminates.

A tile is considered **valid** for a position if the tile is not resulting in contradiction with the available constraints. These constraints decide which pair of tiles can
appear as neighbors in the output based on if the same pair have appeared as neighbors in the input. For instance, if tile A have never been an immediate
neighbor above tile B in the input, then tile B can't be chosen for a position that has A immediately above it in the output.

### Selection Heuristics

As mentioned above, *Selection Heuristic* is the process in which an empty position on the output grid is selected to be filled with a tile.
Different *Selection Heuristic*s have been implemented in this project, and can be changed by changing the `entropy_option` argument. Please note that
even though changing the *Selection Heuristic*s can change the quality of the result, the paper is focused on the effect of the *Decision Heurisitic*.

The following options are available for the *Selection Heuristic*:

1. `TOP_LEFT` starts by selecting the top-left corner tile, then row by row (left to right) until the bottom-right corner tile.
2. `TOP_RIGHT` starts by selecting the top-right corner tile, then row by row (right to left) until the bottom-left corner tile.
The reason to have this heuristic is for comparison with the previous one and showing the bias these two heuristics are causing.
3. `NUMBER_OF_OPTIONS` selects the position with minimum number of options at each step.
4. `SHANNON` uses shannon entropy to calculate the entropy of each position and chooses the position with minimum entropy.
Note that the shannon entropy is defined based on the probability of each option, which means that the *Decision Heuristic*, which defines this probability,
will also affect the *Selection* process. For example, when the *Decision Heuristic* is set to `Uniform`, `SHANNON` option will be the same as `NUMBER_OF_OPTIONS`.

For visualizing the *Selection Heuristic*s side-by-side, `visualize_wfc_selection_heuristics` function in the `main.py` file can be used. An example of this generated with the Context-sensitive *Decision Heuristic* on zelda example is shown below:

![Figure_2](https://user-images.githubusercontent.com/25642714/231180741-ca1caaee-b6e6-4d56-84b5-08168d6a36dd.png)

As you can see, using the `TOP_LEFT` and `TOP_RIGHT` option results in some diagonal pattern artifacts in the output.

### Decision Heuristics

The *Decision Heuristic* is the process which decides which one of the **valid** tiles to use for some target position.
The heuristic assigns probabilities to **valid** tile options and then samples these probabilities. The following *Decision Heuristic*s are available in this implementation:

1. `NONE` uses a uniform probability distribution for the tile options. In other words, it chooses one of the **valid** options randomly.
2. `FREQUENCY_WEIGHTED` uses the frequency of tiles to assign probability to options. The frequency for each tile is the number of times that tile have
appeared in the input. The probability of each option is its frequency devided by sum of all the frequencies for all **valid** options.
3. `CONTEXT_WEIGHTED` uses the frequency of tiles in the same **context** to assign the probability of options. We define **context** as a tuple of tiles adjacent to
the target tile (which is a tuple of 4 tiles in this 2D implementation). Basically, for the target position, we first extract the context around it (for any tile which haven't
been decided yet or which is out of bound, a special unknown toke is used which is shown by `None` in this implementation). Then we access a look-up table to get the
frequency of each of the tile options in the same context in the input. We then devide this frequency by sum of the same frequencies for all the options to get a probability.
If the context is new to us, we use the general frequency of tile in a completely unknown context, which is the same as `FREQUENCY_WEIGHTED` option.

For visualizing the *Decision Heuristic*s side-by-side, `visualize_wfc_decision_heuristics` function in the `main.py` file can be used. An example of this generated with the number of options *Selection Heuristic* on zelda example is shown below:

![Figure_3](https://user-images.githubusercontent.com/25642714/231361694-20e6d57b-3d85-4297-bcf4-1cf29a5b7dc4.png)

## Implementaiton Details

This implementation contains the following files:

1. `image.py` defines an image unit as a 2D array of pixels which can be converted to a single number with the `_get_number` function.
In this README file we refer to image unit as tile, but it can be any unit of image we assign to positions on the image.
Some example of this unit which are implemented in here are `Tile`, and two bigger `Pattern`s called `nxmPattern` and `UpLeftLPattern`.
The `nxmPattern` is a rectangular pattern with the shape n by m (nxm tiles in total).
The `UpLeftLPattern` is a L shaped pattern containing a center tile, n tiles above it, and m tiles left of it (n+m+1 tiles in total).
New patterns can be easily defined by listing the set of tiles in the pattern as relative indices to a center tile.
2. `tiled_image.py` defines a process of extracting the image units from an image. The image contains a 2D array of numbers representing tiles at each position of the input, and a one-to-one mapping from number to tile.
3. `image_distribution` is the class which extracts the frequency of tiles, frequency of tile pairs, and frequency of tiles in different contexts. It also extracts the 
valid tile pairs.
4. `WFC.py` is the WFC implemetation containing different heuristics. For more details about how this is implemented, refer to the [WFC Implementation](#wfc-implementation) subsection.
5. `utility.py` contains some utility functions used by other files.

More information about each of the files can be found in the subsections.

### WFC Implementation

As mentioned above, the core loop of WFC is implemented in the `WFC.py` file. This core loop uses a supermap to run the WFC. Supermap is a 2D map representing the output.
Each position (i, j) in the supermap is a list of possible **valid** options available for the position (i, j). If only one option is available at some position, that position have already collapsed. If all positions have only one option each, the output is ready. If at some position there are no options available, depending on the `backtrack` paramter it either returns None for that position or uses backtrack to revert steps and try other options.

Each option is a single number which represents a tile or a pattern. The one-to-one mapping from this number to pixel values is in the `TiledImage` object, and WFC only works with the number representing that option. To get the final pixel values, the result of `WFC.generate` function should be passed to `TiledImage.from_generated` function.

### Selection Heuristics Implementation

The *Selection Heuristic* is implemented in a single function in the `WFC.py` file called `_get_entropy`. Given the supermap, x, y, and output size, this function returns the entropy of position (x, y) of supermap. The entropy can be any number, and the WFC algorithm will select the empty position with minimum entropy at each step to collapse.

For instance, the `TOP_LEFT` entropy option returns `i*n+j` as entropy of position (i, j), which n being the number of columns. This means that 

### Decision Heuristics Implementation

## Porting Context-sensitive Heuristic

## References

## TODO list

The following features have been implemetned but are not part of this repository yet:

- Interactive WFC notebook
- Resemblance Metrics
- Gif generator
- 3D WFC
- Expressive Range Analysis

If you think some other features should be added here or some bugs should be fixed, please submit an issue.

Alternatively if you have already implemented some features or fixed something that you want to add to the repository, please submit a pull request.

If you want to talk about this feel free to contact me by emailing me at bbateni@ucsc.edu.

## FAQ

**Some tiles in the output are blank (completely white). What's wrong?**

This is because the algorithm can't find any valid tiles for those positions. Try running the algorithm with backtracking by setting `backtrack=True`. This will increase the
exection time but will search all the available options to get a valid result. If there are no valid results available, the code will return a `Not possible` exception.

**There are some artifact in the results: there is a diagonal pattern seen in the outputs. What should I do?**

This shows some bias in the output, which can be a result of selection heuristic. Changing the selection heuristic to `SHANNON` or `NUMBER_OF_OPTIONS` will resolve this problem.

**Running the WFC algorithm with the same seed results in different values. How can I solve this?**

The reason is that the main process which turns a tile to a number uses the python hash function. The python hash function is undeterministic and changes every time you run the program because of security reasons. To change this, you can change hash method by changing
```
GLOBAL_HASH_TYPE = HASH_TYPE.PYTHON_HASH
```
to
```
GLOBAL_HASH_TYPE = HASH_TYPE.NUMBER_HASH
```
in the `utility.py` file. The `NUMBER_HASH` hashing method is deterministic, but will make the tile extraction process significantly slower, but doesn't have any impact on the execution time of other parts such as the WFC algorithm.
