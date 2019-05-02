import numpy as np
import pandas as pd
import nltk
import re

import utils
from configure import FLAGS


def clean_str(text):
    text = text.lower()
    # Clean the text
    text = re.sub(r"[^A-Za-z0-9^,!.\/'+-=]", " ", text)
    text = re.sub(r"what's", "what is ", text)
    text = re.sub(r"that's", "that is ", text)
    text = re.sub(r"there's", "there is ", text)
    text = re.sub(r"it's", "it is ", text)
    text = re.sub(r"\'s", " ", text)
    text = re.sub(r"\'ve", " have ", text)
    text = re.sub(r"can't", "can not ", text)
    text = re.sub(r"n't", " not ", text)
    text = re.sub(r"i'm", "i am ", text)
    text = re.sub(r"\'re", " are ", text)
    text = re.sub(r"\'d", " would ", text)
    text = re.sub(r"\'ll", " will ", text)
    text = re.sub(r",", " ", text)
    text = re.sub(r"\.", " ", text)
    text = re.sub(r"!", " ! ", text)
    text = re.sub(r"\/", " ", text)
    text = re.sub(r"\^", " ^ ", text)
    text = re.sub(r"\+", " + ", text)
    text = re.sub(r"\-", " - ", text)
    text = re.sub(r"\=", " = ", text)
    text = re.sub(r"'", " ", text)
    text = re.sub(r"(\d+)(k)", r"\g<1>000", text)
    text = re.sub(r":", " : ", text)
    text = re.sub(r" e g ", " eg ", text)
    text = re.sub(r" b g ", " bg ", text)
    text = re.sub(r" u s ", " american ", text)
    text = re.sub(r"\0s", "0", text)
    text = re.sub(r" 9 11 ", "911", text)
    text = re.sub(r"e - mail", "email", text)
    text = re.sub(r"j k", "jk", text)
    text = re.sub(r"\s{2,}", " ", text)

    return text.strip()


def Common_token_to_SamEval2010_token(tokens):
    sentence = tokens[0]
    e1 = tokens[1]
    e1_pos_start = int(tokens[3])
    e1_pos_end = int(tokens[4])
    e2 = tokens[5]
    e2_pos_start = int(tokens[7])
    e2_pos_end = int(tokens[8])
    relation = tokens[9]
    sentence = sentence[:e1_pos_start] + '<e1>' + e1 + '</e1>' \
               + sentence[e1_pos_end:e2_pos_start] + '<e2>' + e2 + '</e2>' + sentence[e2_pos_end:]
    return [sentence, relation]


def load_data_from_common_data(path, start_id, label_count=0, data_type='semeval2010'):
    data = []
    lines = [line.strip() for line in open(path)]
    for idx in range(len(lines)):
        tokens = lines[idx].split("\t")
        sam_eval = Common_token_to_SamEval2010_token(tokens)
        data.append([start_id + idx, sam_eval[0], sam_eval[1]])

    print(path)
    return load_data_and_labels(data, label_count, data_type)


def load_data_from_semeval_data(path, label_count=0):
    data = []
    lines = [line.strip() for line in open(path)]
    for idx in range(0, len(lines), 4):
        id = lines[idx].split("\t")[0]
        relation = lines[idx + 1]

        sentence = lines[idx].split("\t")[1][1:-1]
        data.append([id, sentence, relation])

    print(path)
    return load_data_and_labels(data, label_count, 'semeval2010')


def load_data_and_labels(list, label_count, data_type):
    data = []
    max_sentence_length = 0
    for idx in range(len(list)):
        sentence = list[idx][1]
        relation = list[idx][2]
        sentence = sentence.replace('<e1>', ' _e11_ ')
        sentence = sentence.replace('</e1>', ' _e12_ ')
        sentence = sentence.replace('<e2>', ' _e21_ ')
        sentence = sentence.replace('</e2>', ' _e22_ ')

        sentence = clean_str(sentence)
        tokens = nltk.word_tokenize(sentence)
        if max_sentence_length < len(tokens):
            max_sentence_length = len(tokens)
        e1 = tokens.index("e12") - 1
        e2 = tokens.index("e22") - 1
        sentence = " ".join(tokens)

        data.append([list[idx][0], sentence, e1, e2, relation])

    print("max sentence length = {}\n".format(max_sentence_length))

    df = pd.DataFrame(data=data, columns=["id", "sentence", "e1", "e2", "relation"])

    pos1, pos2 = get_relative_position(df, FLAGS.max_sentence_length)

    if data_type == 'semeval2010' or data_type == 'ddi2013' or data_type == 'nyt':
        df['label'] = [utils.class2label[FLAGS.data_type][r] for r in df['relation']]
    else:
        raise Exception('The {0} data type is unavailable.'.format(data_type))

    # Text Data
    x_text = df['sentence'].tolist()
    e1 = df['e1'].tolist()
    e2 = df['e2'].tolist()

    # Label Data
    y = df['label']
    labels_flat = y.values.ravel()
    labels_count = np.unique(labels_flat).shape[0] if label_count == 0 else label_count

    # convert class labels from scalars to one-hot vectors
    # 0  => [1 0 0 0 0 ... 0 0 0 0 0]
    # 1  => [0 1 0 0 0 ... 0 0 0 0 0]
    # ...
    # 18 => [0 0 0 0 0 ... 0 0 0 0 1]
    def dense_to_one_hot(labels_dense, num_classes):
        num_labels = labels_dense.shape[0]
        index_offset = np.arange(num_labels) * num_classes
        labels_one_hot = np.zeros((num_labels, num_classes))
        labels_one_hot.flat[index_offset + labels_dense.ravel()] = 1
        return labels_one_hot

    labels = dense_to_one_hot(labels_flat, labels_count)
    labels = labels.astype(np.uint8)

    return x_text, labels, e1, e2, pos1, pos2, y


def get_relative_position(df, max_sentence_length):
    # Position data
    pos1 = []
    pos2 = []
    for df_idx in range(len(df)):
        sentence = df.iloc[df_idx]['sentence']
        tokens = nltk.word_tokenize(sentence)
        e1 = df.iloc[df_idx]['e1']
        e2 = df.iloc[df_idx]['e2']

        p1 = ""
        p2 = ""
        for word_idx in range(len(tokens)):
            p1 += str((max_sentence_length - 1) + word_idx - e1) + " "
            p2 += str((max_sentence_length - 1) + word_idx - e2) + " "
        pos1.append(p1)
        pos2.append(p2)

    return pos1, pos2


def batch_iter(data, batch_size, num_epochs, shuffle=True):
    """
    Generates a batch iterator for a dataset.
    """
    data = np.array(data)
    data_size = len(data)
    num_batches_per_epoch = int((len(data) - 1) / batch_size) + 1
    for epoch in range(num_epochs):
        # Shuffle the data at each epoch
        if shuffle:
            shuffle_indices = np.random.permutation(np.arange(data_size))
            shuffled_data = data[shuffle_indices]
        else:
            shuffled_data = data
        for batch_num in range(num_batches_per_epoch):
            start_index = batch_num * batch_size
            end_index = min((batch_num + 1) * batch_size, data_size)
            yield shuffled_data[start_index:end_index]


# if __name__ == "__main__":
#     trainFile = 'SemEval2010_task8_all_data/SemEval2010_task8_training/TRAIN_FILE.TXT'
#     testFile = 'SemEval2010_task8_all_data/SemEval2010_task8_testing_keys/TEST_FILE_FULL.TXT'
#
#     load_data_and_labels(testFile)
