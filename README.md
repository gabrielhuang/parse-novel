# Augmented Novels
Read novels without effort!

Project Structure
-----------------

`data/`: contains books and datasets
`legacy/`: contains legacy code for named entity and character description
`www/`: folder to contain the Augmented Novel


Dependencies
-----------------
- Python 2.7
- NLTK
- numpy and scipy
- scikit-learn (only for weight.py)


Generate the Augmented Novel and the interactions graph
-------------------------------------------------------

- Open `main.py` and change variable `txt_file` to open the desired book.
- Adjust `max_chars` to control the number of characters in the generated graph
- Adjust parameter `smallest` of `draw_graphviz` to scale the generated graph
- Run `main.py`

It will generate `www/peopleA.html` the Augmented Novel with dialog segmentation and character detection.
It will also generate `www/graph.gv` which you can open with [GraphViz Neato](http://www.graphviz.org/) to generate the interactions graph.


Generate Character profiles
---------------------------

- Open `legacy/main.py` and change variable `filetoread` to open the desired book.
- Run `legacy/main.py`

It will print word associations with each detected character.


Highlight Important Sentences
-----------------------------

- Open `weight.py` and change the book file
- Adjust `num_segments` and constants as desired
- Run `weight.py`

It will generate `www/scores.html` which contains the highlighted text.