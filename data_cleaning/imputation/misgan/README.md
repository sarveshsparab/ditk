# MisGAN
Data can be found in "imputation/data"
MisGAN is compatible with all three datasets
*Note: Moved to sample test location to main folder because path dependencies could not be resolved. I also modified sample test to suit MisGAN method since after preprocessing the code assume pytorch data loader are ready instead of searching for another csv file. This makes loading at evaluation time much faster.

### Title of the paper
Learning from Incomplete Data with Generative Adversarial Networks

### Full citation
Li, S. C. X., Jiang, B., & Marlin, B. (2018). [Learning from Incomplete Data with Generative Adversarial Networks. ICLR 2019](https://arxiv.org/abs/1902.09599) <br/>
[Github Link](https://github.com/steveli/misgan) <br/>

### Input/Output format for prediction
Input:<br/>
-Incomplete data table in csv<br/>
Output:<br/>
-Complete data table in csv<br/>

### Input/Output format for training
Input:<br/>
-Incomplete data table in csv<br/>
-Complete data table with missing rate in csv<br/>
Output:<br/>
-Complete data table in csv<br/>

### A paragraph describing the overall task, the method and model
The method uses three generator and three discriminator to train a generative adverserial network (GAN) throught
blocks of data segments in the hope to be able to regenerate complete missing data giving small fragments of real
data. 

### A figure describing the model
<p align="center"><img width="100%" src="img/misgan.png" /></p>
<p align="center"><img width="100%" src="img/misgan-impute.png" /></p>

### Benchmark datasets
1. UCI Letter Recognition
2. UCI Breast Cancer 
3. UCI Spambase

### Evaluation metrics and results


### Link to Jupyter notebook and Youtube videos
Jupyter Notebook:
[Zhilin's Github](https://github.com/uyuyuyjk/ditk/blob/develop/data_cleaning/imputation/misgan/misgan.ipynb)<br/>

Youtube Video:
https://www.youtube.com/watch?v=UGUKTw2Tb6k&feature=youtu.be

## Process for running the code using the main file

### Preprocessing:
For preprocessing training data without split run:
```bash
python main.py --preprocess
```

For preprocessing training data with split run:
```bash
python main.py --preprocess --split=<ratio>
```
, where ratio is a float


### Training
For training misgan, run
```bash
python main.py --train --fname=<file>
```
, where file name is the file name of the data loader

eg
```bash
python main.py --train --fname=wdbc.csv_train
```

### Testing
For testing misgan, run
```bash
python main.py --test --fname=<fname> --model=<model>
```
, where file name is the file name of the data loader, and model is

the name of the model before .csv
eg.
```bash
python main.py --test --fname=wdbc.csv_test --model=wdbc
```

### Evaluation
```bash
python main.py --evaluate --fname=<file> --model=<model>
```
, where file is input data name and model is imputer 
model name.
eg.
```bash
python main.py --evaluate --fname="data/wdbc.csv" --model="wdbc.csv_train"
```

To introduce missing value manually, use:
```bash
python main.py --evaluate --fname="data/wdbc.csv" --model="wdbc.csv_train" --ims --ratio=<ratio>
```
, ratio is float

### Imputation
```bash
python main.py --impute --fname=<file> --model=<model>
```
, where file is input data name and model is imputer 
model name.
eg.
```bash
python main.py --impute --fname="data/wdbc.csv" --model="wdbc.csv_train"
```

To introduce missing value manually, use:
```bash
python main.py --evaluate --fname="data/wdbc.csv" --model="wdbc.csv_train" --ims --ratio=<ratio>
```
, ratio is float