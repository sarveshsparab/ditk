from model_param_space import ModelParamSpace
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials, space_eval
from optparse import OptionParser
from utils import logging_utils, data_utils, embedding_utils, pkl_utils
from utils.eval_utils import strict, loose_macro, loose_micro, label_path, complete_path
import numpy as np
from sklearn.model_selection import ShuffleSplit
import os
import config
import datetime
import tensorflow as tf
from nfetc import NFETC

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

class Task:
    def __init__(self, model_name, data_name, cv_runs, params_dict, logger):
        print(">>> Loading data...")
        if data_name == "wiki":
            words_train, mentions_train, positions_train, labels_train = data_utils.load(config.WIKI_TRAIN_CLEAN)
            words, mentions, positions, labels = data_utils.load(config.WIKI_TEST_CLEAN)
            type2id, typeDict = pkl_utils._load(config.WIKI_TYPE)
            num_types = len(type2id)
            type_info = config.WIKI_TYPE
        elif data_name == "ontonotes":
            words_train, mentions_train, positions_train, labels_train = data_utils.load(config.ONTONOTES_TRAIN_CLEAN)
            words, mentions, positions, labels = data_utils.load(config.ONTONOTES_TEST_CLEAN)
            type2id, typeDict = pkl_utils._load(config.ONTONOTES_TYPE)
            num_types = len(type2id)
            type_info = config.ONTONOTES_TYPE
        elif data_name == "wikim":
            words_train, mentions_train, positions_train, labels_train = data_utils.load(config.WIKIM_TRAIN_CLEAN)
            words, mentions, positions, labels = data_utils.load(config.WIKIM_TEST_CLEAN)
            type2id, typeDict = pkl_utils._load(config.WIKIM_TYPE)
            num_types = len(type2id)
            type_info = config.WIKIM_TYPE
        elif data_name == "others":
            words_train, mentions_train, positions_train, labels_train = data_utils.load(config.OTHERS_TRAIN_CLEAN)
            words, mentions, positions, labels = data_utils.load(config.OTHERS_TEST_CLEAN)
            type2id, typeDict = pkl_utils._load(config.OTHERS_TYPE)
            num_types = len(type2id)
            type_info = config.OTHERS_TYPE

        self.id2type = {type2id[x]:x for x in type2id.keys()}
        def type2vec(types):
            tmp = np.zeros(num_types)
            for t in types.split():
                tmp[type2id[t]] = 1.0
            return tmp
        labels_train = np.array([type2vec(t) for t in labels_train])
        labels = np.array([type2vec(t) for t in labels])

        self.embedding = embedding_utils.Embedding.fromCorpus(config.EMBEDDING_DATA, list(words_train)+list(words), config.MAX_DOCUMENT_LENGTH, config.MENTION_SIZE)

        print(">>> Preprocessing data...")
        textlen_train = np.array([self.embedding.len_transform1(x) for x in words_train])
        words_train = np.array([self.embedding.text_transform1(x) for x in words_train])
        mentionlen_train = np.array([self.embedding.len_transform2(x) for x in mentions_train])
        mentions_train = np.array([self.embedding.text_transform2(x) for x in mentions_train])
        positions_train = np.array([self.embedding.position_transform(x) for x in positions_train])

        textlen = np.array([self.embedding.len_transform1(x) for x in words])
        words = np.array([self.embedding.text_transform1(x) for x in words])
        mentionlen = np.array([self.embedding.len_transform2(x) for x in mentions])
        mentions = np.array([self.embedding.text_transform2(x) for x in mentions])
        positions = np.array([self.embedding.position_transform(x) for x in positions])

        ss = ShuffleSplit(n_splits=1, test_size=0.1, random_state=config.RANDOM_SEED)
        for test_index, valid_index in ss.split(np.zeros(len(labels)), labels):
            textlen_test, textlen_valid = textlen[test_index], textlen[valid_index]
            words_test, words_valid = words[test_index], words[valid_index]
            mentionlen_test, mentionlen_valid = mentionlen[test_index], mentionlen[valid_index]
            mentions_test, mentions_valid = mentions[test_index], mentions[valid_index]
            positions_test, positions_valid = positions[test_index], positions[valid_index]
            labels_test, labels_valid = labels[test_index], labels[valid_index]

        self.train_set = list(zip(words_train, textlen_train, mentions_train, mentionlen_train, positions_train, labels_train))
        self.valid_set = list(zip(words_valid, textlen_valid, mentions_valid, mentionlen_valid, positions_valid, labels_valid))
        self.test_set = list(zip(words_test, textlen_test, mentions_test, mentionlen_test, positions_test, labels_test))
        self.full_test_set = list(zip(words, textlen, mentions, mentionlen, positions, labels))

        self.labels_test = labels_test
        self.labels = labels

        self.model_name = model_name
        self.data_name = data_name
        self.cv_runs = cv_runs
        self.params_dict = params_dict
        self.hparams = AttrDict(params_dict)
        self.logger = logger

        self.num_types = num_types
        self.type_info = type_info

        self.model = self._get_model()
        self.saver = tf.train.Saver(tf.global_variables())
        checkpoint_dir = os.path.abspath(config.CHECKPOINT_DIR)
        if not os.path.exists(checkpoint_dir):
            os.makedirs(checkpoint_dir)
        self.checkpoint_prefix = os.path.join(checkpoint_dir, self.__str__())

    def __str__(self):
        return self.model_name

    def _get_model(self):
        np.random.seed(config.RANDOM_SEED)
        kwargs = {
            "sequence_length": config.MAX_DOCUMENT_LENGTH,
            "mention_length": config.MENTION_SIZE,
            "num_classes": self.num_types,
            "vocab_size": self.embedding.vocab_size,
            "embedding_size": self.embedding.embedding_dim,
            "position_size": self.embedding.position_size,
            "pretrained_embedding": self.embedding.embedding,
            "wpe": np.random.random_sample((self.embedding.position_size, self.hparams.wpe_dim)),
            "type_info": self.type_info,
            "hparams": self.hparams
        }
        if "nfetc" in self.model_name:
            return NFETC(**kwargs)
        else:
            raise AttributeError("Invalid model name!")

    def _print_param_dict(self, d, prefix="      ", incr_prefix="      "):
        for k, v in sorted(d.items()):
            if isinstance(v, dict):
                self.logger.info("%s%s:" % (prefix, k))
                self.print_param_dict(v, prefix + incr_prefix, incr_prefix)
            else:
                self.logger.info("%s%s: %s" % (prefix, k, v))

    def create_session(self):
        session_conf = tf.ConfigProto(
            intra_op_parallelism_threads=8,
            allow_soft_placement=True,
            log_device_placement=False)
        return tf.Session(config=session_conf)

    def cv(self):
        self.logger.info("=" * 50)
        self.logger.info("Params")
        self._print_param_dict(self.params_dict)
        self.logger.info("Results")
        self.logger.info("\t\tRun\t\tStep\t\tLoss\t\tPAcc\t\tEAcc")

        cv_loss = []
        cv_pacc = []
        cv_eacc = []
        for i in range(self.cv_runs):
            sess = self.create_session()
            sess.run(tf.global_variables_initializer())
            step, loss, pacc, eacc = self.model.fit(sess, self.train_set, self.valid_set)
            self.logger.info("\t\t%d\t\t%d\t\t%.3f\t\t%.3f\t\t%.3f" % (i+1, step, loss, pacc, eacc))
            cv_loss.append(loss)
            cv_pacc.append(pacc)
            cv_eacc.append(eacc)
            sess.close()

        self.loss = np.mean(cv_loss)
        self.pacc = np.mean(cv_pacc)
        self.eacc = np.mean(cv_eacc)

        self.logger.info("CV Loss: %.3f" % self.loss)
        self.logger.info("CV Partial Accuracy: %.3f" % self.pacc)
        self.logger.info("CV Exact Accuracy: %.3f" % self.eacc)
        self.logger.info("-" * 50)

    def add_get_scores(self, truths, preds, save=False):

        preds = [label_path(self.id2type[x]) for x in preds]

        def vec2type(v):
            s = []
            for i in range(len(v)):
                if v[i]:
                    s.extend(label_path(self.id2type[i]))
            return set(s)

        # words_all = list(zip(*truths))[0] #Added
        truth_label = list(zip(*truths))[-1]
        labels_test = [vec2type(x) for x in truth_label] # ADDed
        # labels_words = [vec2type(x) for x in words_all] # ADDed

        acc = strict(labels_test, preds)
        _, _, macro = loose_macro(labels_test, preds)
        _, _, micro = loose_micro(labels_test, preds)

        if save:
            outfile = open(os.path.join(config.OUTPUT_DIR, self.__str__() + ".tsv"), "w")
            for x, y in zip(preds, labels_test):
                t1 = "|".join(list(x))
                t2 = "|".join(list(y))
                outfile.write(t1 + "\t" + t2 + "\n")
            outfile.close()

        return acc, macro, micro

    def get_scores(self, preds, save=False):
        preds = [label_path(self.id2type[x]) for x in preds]
        def vec2type(v):
            s = []
            for i in range(len(v)):
                if v[i]:
                    s.extend(label_path(self.id2type[i]))
            return set(s)
        labels_test = [vec2type(x) for x in self.labels_test]
        if save:
            labels_test = [vec2type(x) for x in self.labels]
        acc = strict(labels_test, preds)
        _, _, macro = loose_macro(labels_test, preds)
        _, _, micro = loose_micro(labels_test, preds)

        if save:
            outfile = open(os.path.join(config.OUTPUT_DIR, self.__str__() + ".tsv"), "w")
            for x, y in zip(preds, labels_test):
                t1 = "|".join(list(x))
                t2 = "|".join(list(y))
                outfile.write(t1 + "\t" + t2 + "\n")
            outfile.close()

        return acc, macro, micro

    def refit(self):
        self.logger.info("Params")
        self._print_param_dict(self.params_dict)
        self.logger.info("Evaluation for each epoch")
        self.logger.info("\t\tEpoch\t\tAcc\t\tMacro\t\tMicro")

        sess = self.create_session()
        sess.run(tf.global_variables_initializer())
        epochs = 0
        for preds in self.model.evaluate(sess, self.train_set, self.test_set):
            epochs += 1
            acc, macro, micro = self.get_scores(preds)
            self.logger.info("\t\t%d\t\t%.3f\t\t%.3f\t\t%.3f" % (epochs, acc, macro, micro))
        sess.close()

    def add_evaluate(self, test_data): # full=True

        self.logger.info("Params")
        self._print_param_dict(self.params_dict)
        self.logger.info("Final Evaluation")
        self.logger.info("\t\tRun\t\tAcc\t\tMacro\t\tMicro")

        # for i in range(self.cv_runs):
        sess = self.create_session()

        if os.access(config.CHECKPOINT_DIR + "/checkpoint", os.R_OK): 
            # Restored pre-trained model
            print(">>> Restored prev-trained model...")
            self.saver.restore(sess, self.checkpoint_prefix)

        else : 
            print(">>> Create new Model model...")
            sess.run(tf.global_variables_initializer())

        preds = self.model.predict(sess, test_data) # test_data == self.full_test_set
        sess.close()

        return preds

    def load(self):
        # for i in range(self.cv_runs):
        sess = self.create_session()

        if os.access(config.CHECKPOINT_DIR + "/checkpoint", os.R_OK): 
            # Restored pre-trained model
            print(">>> Restored prev-trained model...")
            self.saver.restore(sess, self.checkpoint_prefix)

        else : 
            print(">>> There is NO pre-trained model...")
            sess.run(tf.global_variables_initializer())

        sess.close()


    def evaluate(self, full=False):
        self.logger.info("Params")
        self._print_param_dict(self.params_dict)
        self.logger.info("Final Evaluation")
        self.logger.info("\t\tRun\t\tAcc\t\tMacro\t\tMicro")
        accs = []
        macros = []
        micros = []

        for i in range(self.cv_runs):
            sess = self.create_session()
            sess.run(tf.global_variables_initializer())
            self.model.fit(sess, self.train_set)
            if full:
                preds = self.model.predict(sess, self.full_test_set)
                acc, macro, micro = self.get_scores(preds, True)
            else:
                preds = self.model.predict(sess, self.test_set)
                acc, macro, micro = self.get_scores(preds)

            accs.append(acc)
            macros.append(macro)
            micros.append(micro)
            sess.close()
        avg_acc = np.mean(accs)
        avg_macro = np.mean(macros)
        avg_micro = np.mean(micros)
        std_acc = np.std(accs)
        std_macro = np.std(macros)
        std_micro = np.std(micros)
        for i in range(self.cv_runs):
            self.logger.info("\t\t%d\t\t%.3f\t\t%.3f\t\t%.3f" %
                    (i + 1, accs[i], macros[i], micros[i]))
        self.logger.info("-" * 50)
        self.logger.info("Avg Acc %.3f(+-%.3f) Macro %.3f(+-%.3f) Micro %.3f(+-%.3f)" %
                (avg_acc, std_acc, avg_macro, std_macro, avg_micro, std_micro))

    def add_save(self, train_data):
        sess = self.create_session()
        sess.run(tf.global_variables_initializer())


        for i in range(self.cv_runs):
            print(">>> Training", i, "epoch")
            self.model.fit(sess, train_data)

        path = self.saver.save(sess, self.checkpoint_prefix)
        self.embedding.save(self.checkpoint_prefix)
        print("Saved model to {}".format(path))
        sess.close() # ADDed

    def save(self):
        sess = self.create_session()
        sess.run(tf.global_variables_initializer())
        self.model.fit(sess, self.train_set)
        path = self.saver.save(sess, self.checkpoint_prefix)
        self.embedding.save(self.checkpoint_prefix)
        print("Saved model to {}".format(path))


class TaskOptimizer:
    def __init__(self, model_name, data_name, cv_runs, max_evals, logger):
        self.model_name = model_name
        self.data_name = data_name
        self.cv_runs = cv_runs
        self.max_evals = max_evals
        self.logger = logger
        self.model_param_space = ModelParamSpace(self.model_name)

    def _obj(self, param_dict):
        param_dict = self.model_param_space._convert_into_param(param_dict)
        self.task = Task(self.model_name, self.data_name, self.cv_runs, param_dict, self.logger)
        self.task.cv()
        tf.reset_default_graph()
        ret = {
            "loss": -self.task.eacc,
            "attachments": {
                "pacc": self.task.pacc,
                # "eacc": self.task.eacc,
            },
            "status": STATUS_OK
        }
        return ret

    def run(self):
        trials = Trials()
        best = fmin(self._obj, self.model_param_space._build_space(), tpe.suggest, self.max_evals, trials)
        best_params = space_eval(self.model_param_space._build_space(), best)
        best_params = self.model_param_space._convert_into_param(best_params)
        trial_loss = np.asarray(trials.losses(), dtype=float)
        best_ind = np.argmin(trial_loss)
        best_loss = -trial_loss[best_ind]
        best_pacc = trials.trial_attachments(trials.trials[best_ind])["pacc"]
        # best_eacc = trials.trial_attachments(trials.trials[best_ind])["eacc"]
        self.logger.info("-" * 50)
        self.logger.info("Best Exact Accuracy %.3f with Parital Accuracy %.3f" % (best_loss, best_pacc))
        self.logger.info("Best Param:")
        self.task._print_param_dict(best_params)
        self.logger.info("-" * 50)

def parse_args(parser):
    parser.add_option("-m", "--model", type="string", dest="model_name")
    parser.add_option("-d", "--data", type="string", dest="data_name")
    parser.add_option("-e", "--eval", type="int", dest="max_evals", default=100)
    parser.add_option("-c", "--cv_runs", type="int", dest="cv_runs", default=3)
    options, args = parser.parse_args()
    return options, args

def main(options):
    time_str = datetime.datetime.now().isoformat()
    logname = "[Model@%s]_[Data@%s]_%s.log" % (options.model_name, options.data_name, time_str)
    logger = logging_utils._get_logger(config.LOG_DIR, logname)
    optimizer = TaskOptimizer(options.model_name, options.data_name, options.cv_runs, options.max_evals, logger)
    optimizer.run()

if __name__ == "__main__":
    parser = OptionParser()
    options, args = parse_args(parser)
    main(options)
