# ***Wiki Search Engine***

The goal of this project is to build a search engine that utilizes Wikipedia data, utilizing techniques such as cosine similarity and tf-idf. It is composed of several modules, each responsible for a specific aspect of the search engine's functionality.<br>
File explanation and how to use it:<br><br>

## 1. Inverted_Index.py

Inverted index for body, titles, anchors of wiki pages. Also, contains MultiFileWriter and MultiFileReader classes, writing/reading to/from GCP bucket all postings and postings locations from current inverted index
<br><br>


## 2. IndexBuilder.ipynb

Contains all indexing code. Firstly, it gets all wikidata from wikidumps. Then, it creates indexes for body, title (stemmed using Porter Stemmer), anchor. Writes all postings and postings locations (using MultiFileWriter) to GCP, and all inverted indexes data (globals) to GCP. Calculates PageRank and uploads it to GCP to JSON file. Makes id, title JSON file and uploads it to GCP.
<br><br>


## 3. backend.py

Contains all relevant functions to TF-IDF for body searching.
<br><br>


## 4. search_frontend.py

Main script, flask app, containing all searching logic.
<br><br>


## 5. search_frontend_quality.py

Allowes to test different weights on (title, body, anchor, page rank) and see how different measurements (MAP, Recall, Precision, R-Precision) changes respectively.
<br><br>


