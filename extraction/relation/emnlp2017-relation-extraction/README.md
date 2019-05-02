Student Name: Debankur Ghosh
# Context-Aware Representations for Knowledge Base Relation Extraction

## Relation extraction on an open-domain knowledge base



```
@inproceedings{TUD-CS-2017-0119,
	title = {{Context-Aware Representations for Knowledge Base Relation Extraction}},
	author = {Sorokin, Daniil and Gurevych, Iryna},
	booktitle = {Proceedings of the 2017 Conference on Empirical Methods in Natural Language Processing (EMNLP)},
	pages = {1784-1789},
	year = {2017},
	location = {Copenhagen, Denmark},
	publisher = {Association for Computational Linguistics},
	doi = {10.18653/v1/D17-1188}
}
```

### Paper abstract:
> We demonstrate that for sentence-level relation extraction it is beneficial to consider other relations in the sentential context while predicting the target relation. Our architecture uses an LSTM-based encoder to jointly learn representations for all relations in a single sentence. 
We combine the context representations with an attention mechanism to make the final prediction. 
> We use the Wikidata knowledge base to construct a dataset of multiple relations per sentence and to evaluate our approach. Compared to a baseline system, our method results in an average error reduction of 24\% on a held-out set of relations.

Please, refer to the paper for more details.

The dataset described in the paper can be found here:
 * https://www.informatik.tu-darmstadt.de/ukp/research_6/data/lexical_resources/wikipedia_wikidata_relations/

 
  


### Demo:


http://semanticparsing.ukp.informatik.tu-darmstadt.de:5000/relation-extraction/

### Input Data
* SemEval2010
* DDI2013
* NYT


### Project structure:
```
relation_extraction/
├── eval.py
├── model-train-and-test.py
├── notebooks
├── optimization_space.py
├── core
│   ├── parser.py
│   ├── embeddings.py
│   ├── entity_extraction.py
│   └── keras_models.py
├── relextserver
│   └── server.py
├── graph
│   ├── graph_utils.py
│   ├── io.py
│   └── vis_utils.py
├── stanford_tag_dataset.py
└── evaluation
    └── metrics.py
resources/
├── properties-with-labels.txt
└── property_blacklist.txt
```

<table>
    <tr>
        <th>File</th><th>Description</th>
    </tr>
    <tr>
        <td>relation_extraction/</td><td>Main Python module</td>
    </tr>
    <tr>
        <td>relation_extraction/core</td><td>Models for joint relation extraction</td>
    </tr>
    <tr>
        <td>relation_extraction/relextserver</td><td>The code for the web demo.</td>
    </tr>
    <tr>
        <td>relation_extraction/graph</td><td>IO and processing for relation graphs</td>
    </tr>
    <tr>
        <td>relation_extraction/evaluation</td><td>Evaluation metrics</td>
    </tr>
    <tr>
        <td>resources/</td><td>Necessary resources</td>
    </tr>
    <tr>
        <td>data/curves/</td><td>The precision-recall curves for each model on the held out data</td>
    </tr>
</table>

### Setup:

1. We recommend that you setup a new pip environment first: http://docs.python-guide.org/en/latest/dev/virtualenvs/

2. Check out the repository and run:
```
pip3 install -r requirements.txt
```

3. Set the Keras (deep learning library) backend to TensorFlow  with the following command:
```
export KERAS_BACKEND=tensorflow
```
   You can also permanently change Keras backend (read more: https://keras.io/backend/). 
   Note that in order to reproduce the experiments in the paper you have to use Theano as a backend instead.

4. Download the [data](https://www.informatik.tu-darmstadt.de/ukp/research_6/data/lexical_resources/wikipedia_wikidata_relations/), if you want to replicate the experiments from the paper.
Extract the archive inside `emnlp2017-relation-extraction/data/wikipedia-wikidata/`. The data was preprocessed using Stanford Core NLP 3.7.0 models. See `stanford_tag_dataset.py` for more information.

5. Download the [GloVe embeddings, glove.6B.zip](https://nlp.stanford.edu/projects/glove/)
and put them into the folder `emnlp2017-relation-extraction/resources/glove/`. You can change the path to word embeddings in the `model_params.json` file if needed.

### Pre-trained models:
* You can download the models that were used in the experiments [here](https://fileserver.ukp.informatik.tu-darmstadt.de/emnlp2017-relation-extraction/EMNLP2017_DS_IG_relation_extraction_trained_models.zip)
* See `Using pre-trained models.ipynb` for a detailed example on how to use the pre-trained models in your code

#### Reproducing the experiments from the paper
To reproduce the experiments please refer to the version of the code that was published with the paper:
[tag emnlp17](https://github.com/UKPLab/emnlp2017-relation-extraction/tree/emnlp17)

In any other case, we recommend using the most recent version.

1. Complete the setup above 

2. Run `python model_train.py` in `emnlp2017-relation-extraction/relation_extraction/` to see the list of parameters

3. If you put the data into the default folders you can train the `ContextWeighted` model with the following command:
```
python model_train.py model_ContextWeighted train ../data/wikipedia-wikidata/enwiki-20160501/semantic-graphs-filtered-training.02_06.json ../data/wikipedia-wikidata/enwiki-20160501/semantic-graphs-filtered-validation.02_06.json
```

4. Run the following command to compute the precision-recall curves:
```
python precision_recall_curves.py model_ContextWeighted ../data/wikipedia-wikidata/enwiki-20160501/semantic-graphs-filtered-held-out.02_06.json
```

### Demo video
*  [video](https://youtu.be/bNx2YYsoYmA)<br>

### Benchmark datasets
* SemEval2010
* Precision = 0.73
* Recall = 0.82
* F1 = 78.2
<br>
* DDI2013
* Precision = 0.7
* Recall = 0.69
* F1 = 69.4
<br>
* NYT
* Precision = 0.45
* Recall = 0.32
* F1 = 37.4

#### Requirements:
* Python 3.6
* Keras 2.1.5
* TensorFlow 1.6.0
* See requirements.txt for library requirements. 

