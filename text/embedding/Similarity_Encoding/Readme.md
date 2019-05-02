# Text Similarity Encoding

- Similarity encoding for learning with dirty categorical variables
- Patricio C., Gaël V., Balázs K. (2018). Similarity encoding for learning with dirty categorical variables. Manuscript accepted for publication at: Machine Learning Journal. Springe.

## Original Code

- Github: https://github.com/pcerda/ecml-pkdd-2018

## Description

- Similarity Encoding is a method aim to encode text(string) by its similarity to other text(string) in the corpus. Similarity Encoding models the embeddings of text by using different similarity measuring functions such as "Jaro-Winkler", "Levenshtein-ratio", "3-gram" and more. 
- The Similarity Encoding model provided in this repository contains some main functions such as embedding training data and predicting embeddings using training data. It also provides supporting functions such as finding embedded similarities of two string, and also evaluating the embeddings by finding a similarity value and compare to the original similarity value.

## Benchmarks

- Employee Salary
- SICK
- Semi2017

## Input and Output

- Input for embedding:
  - Files:
    - train_input (this is the training data that will be embedded)
    - predict_input (this is the data that need to be embedding using training data)
    - similarity_input1 & similarity_input2 (only if using predict_similarity, they are the two strings for finding similarity)
  - Parameters:
    - dimension: dimension to embed each entity and relationship to

- Output:
  - Files:
    - train_output.txt (embeddings are outputted in a format of <string, vector of dimension>)
    - predict_output.txt (embeddings are outputted in a format of <string, vector of dimension>)

## About this repository

- Setup: you will need download <a href=http://nlp.stanford.edu/data/glove.6B.zip>glove.6B.zip</a> , unzip it and place it in the <i>src</i> folder.
- Main.py
  - Please run <i>main.py</i> inside <i>src</i> folder to see what this embedding method does. 
  - It will embed the data in <i>data/sample_data/input.txt</i>, and output it to <i>data/sample_data/output.txt</i>. 
  - Also, it will embed the data in <i>data/sample_data/predict.txt</i> and output it to <i>data/sample_data/predict_output.txt</i>
  - It will print out a similarity value between the word 'Viterbi' and 'Engineering'
- Tests: 
  - <i>test_SimilarityEncoding.py</i> will test on all functions in the model. 
  - It preform embeddings on the <i>test_data/input_train.txt</i> and <i>test_data/input_predict.txt</i>  inside the tests folder.
  - It also run a small sample of the benchmark data <i>Semi2017</i> and will show results of the evaluation
- Jupyter Notebook:
  - https://github.com/sandiexie-USC/ditk/blob/develop/text/embedding/Similarity_Encoding/src/Simlarity_Encoding.ipynb
  - This Jupyter Notebook is a notebook format similar to main.py, providing visualization of each step.



## Evaluation

|                 | Normalized average error<br />(predicted_similarity - actual_similarity)/N |
| --------------- | ------------------------------------------------------------ |
| Employee Salary | 0.126                                                        |
| SICK            | 0.648                                                        |
| Semi2017        | 0.375                                                        |



## Demo

- Jupyter Notebook: https://github.com/sandiexie-USC/ditk/blob/develop/text/embedding/Similarity_Encoding/src/Simlarity_Encoding.ipynb
- Youtube video: https://youtu.be/J1DDpjkLxP0