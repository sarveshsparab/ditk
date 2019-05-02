# Structured Gradient Tree Boosting

## Requirements
* python3
* scikit-learn(0.19.1)
* numpy (1.15.0)

## Data

The preprocessed [AIDA-CoNLL](https://www.mpi-inf.mpg.de/departments/databases-and-information-systems/research/yago-naga/aida/downloads/)
data ('AIDA-PPR-processed-sample.json') is available in the [data](data) folder:
* The entity candidates are generated based on the [PPRforNED](https://github.com/masha-p/PPRforNED) candidate
generation system.
* The system uses 19 local features, including 3 prior features, 4 NER features,
2 entity popularity features, 4 entity type features, and 6 context features. 
Please look into the paper for details.
* The format is:(mentioned_entity, offset_pairs, highest_rank_candidate, set of (candidate_entity, label, features))

The system also uses entity-entity features, which can be quickly computed
on-the-fly. Here, we provide pre-computed entity-entity features (3 features
per entity pair) for the AIDA-CoNLL dataset, which is available in the 
[data](data) folder ('ent_ent_feats.txt.gz').

## Input and Output for Prediction
* input: (mentioned_entity, offset_pairs, highest_rank_candidate, set of (candidate_entity, label, features))
* output: (entity_wiki_ID, predicted_wiki_ID, geolocation_url(optional), geolocation_boundary(optional))

## Input and Output for Training
* input: (mentioned_entity, offset_pairs, highest_rank_candidate, set of (candidate_entity, label, features))
* output: model object

## Usage

### read_data
MUST be called before any other functions
#### required parameters:
* dataset: data file name
* split_ratio: ratio to split the dataset into (train, dev, test)
#### optional parameter:
* num_candidate: number of entity candidates for a mention

### train

#### required parameters:
* train_dev_set: dataset for training 

### predict

#### required parameters:
* model: model from training or loading
* dataset: dataset for predicting

### evaluate

#### required parameters:
* model: model from training or loading
* dataset: dataset for evaluation

### save_model

#### required parameters:
* model: saving model from training
* file_name: file name including path where to save

### load_model

#### required parameters:
* file_name: file name including path where from load


## Benchmarks
* AIDA-CoNLL (currently available-refer the original author for full data)
* AQUANT
* ACE

## Evaluation Metrics
* Accuracy (95.9%)
* F1 (in-progress)

## Demo Video
https://youtu.be/_HIAf5bVSv8

# Original Author
Author: Yi Yang

Contact: yyang464@bloomberg.net


    Yi Yang, Ozan Irsoy, and Kazi Shefaet Rahman 
    "Collective Entity Disambiguation with Structured Gradient Tree Boosting"
    NAACL 2018

[[pdf]](https://arxiv.org/pdf/1802.10229.pdf)

BibTeX

    @inproceedings{yang2018collective,
      title={Collective Entity Disambiguation with Structured Gradient Tree Boosting},
      author={Yang, Yi and Irsoy, Ozan and Rahman, Kazi Shefaet},
      booktitle={Proceedings of the 2018 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long Papers)},
      volume={1},
      pages={777--786},
      year={2018}
    }
