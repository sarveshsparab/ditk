from entity_linkage.typing.entity_typing import entity_typing
import preprocess
from task import Task
import logging
from utils import logging_utils, data_utils, embedding_utils, pkl_utils
from model_param_space import param_space_dict
import datetime
import config


class NFETC(entity_typing):

	def __init__(self):
		self.task = None

	def initi_task(self, model_name, data_name, epoch_num) :
		time_str = datetime.datetime.now().isoformat()
		logname = "Final_[Model@%s]_[Data@%s]_%s.log" % (model_name, data_name, time_str)
		logger = logging_utils._get_logger(config.LOG_DIR, logname)
		params_dict = param_space_dict[model_name]
		task = Task(model_name, data_name, epoch_num, params_dict, logger) # default:cv_run=5
		return task

	def preprocess_helper(self, data_name, extension, input_file_path):
		if extension == "txt":
			preprocess.preprocess(data_name, input_file_path)
		elif extension == "tsv":
			preprocess.tsv_preprocess(data_name, input_file_path)

	def read_dataset(self, file_path, options={}):

		data_name = options.get("data_name", "others") # default = "others"
		ratio = options.get("ratio", (0.7, 0.15, 0.15)) 
		model_name = options.get("model_name", "best_nfetc_wiki") # default = "best_nfetc_wiki"
		epoch_num = options.get("epoch_num", 5) # default = 5 epoch

		print(">> Initiate Task")
		self.task = self.initi_task(model_name, data_name, epoch_num)

		return (self.task.train_set, self.task.full_test_set)

	def train(self, train_data, options={}) :

		print(">> In train, train_data size: (", len(train_data), ")")

		if(len(train_data) == 0): 
			print(">> There is NOT enough data to train.")
		else:
			print(">> There is Enough data to train.")
			self.task.add_save(train_data)
			print(">> Training is Done ! ")

		return

	def predict(self, test_data, model_details=None, options={}) :

		print(">> In predict, test_data size: (", len(test_data),  ")")
		
		if(len(test_data) == 0): 
			print(">> There is NOT enough data to predict.")
			prediction_data = None
		else:
			print(">> There is Enough data to predict.")
			prediction_data = self.task.add_evaluate(test_data)
			print(">> prediction_data size: (", len(prediction_data),  ")")
			print(">> Prediction is Done ! ")

		return prediction_data

	def evaluate(self, test_data, prediction_data=None,  options={}) :

		print(">> In evaluate, test_data size: (", len(test_data), ")")

		if(len(test_data) == 0): 
			print(">> There is NOT enough data to evaluate.")
			scores = (0.0, 0.0, 0.0)
		else:
			print(">> There is Enough data to evaluate.")
			if prediction_data is None:
				prediction_data = self.predict(test_data, None, options)

			acc, macro, micro = self.task.add_get_scores(test_data, prediction_data, True) # save = True
			scores = (acc, macro, micro)
			
			print(">> Evaluation is Done ! ")

		return scores

	def split_data_tsv(self, file_path, data_name, split_ratio=(0.7, 0.15, 0.15)): # train.tsv, test.tsv

		split_r = split_ratio[0]+split_ratio[1] # Since [train + dev]/[test]
		print("> Split all.tsv to cleat_train, clean_test data with ratio (", split_r, ",",  split_ratio[2], ")")

		docs = []
		with open(file_path, 'r') as f:
			for line in f:
				docs.append((line.strip()))

		train_dev_split_idx = int(len(docs) * split_r)

		data = {}
		data["train"] = docs[:train_dev_split_idx]
		data["test"] = docs[train_dev_split_idx:]

		folder_path = "others"
		if data_name == "wiki":
			folder_path = config.WIKI_DATA_PATH
		elif data_name == "wikim":
			folder_path = config.WIKIM_DATA_PATH
		elif data_name == "ontonotes":
			folder_path = config.ONTONOTES_DATA_PATH
		else:
			folder_path = config.OTHERS_DATA_PATH

		
		for key in data:
			with open(folder_path+"/"+key+"_clean.tsv", 'w') as f:
				for line in data[key]:
					f.write(line+"\n")

		print(">> Finished! ")

	def split_data_txt(self, file_path, data_name, split_ratio=(0.7, 0.15, 0.15)): # train.txt, dev.txt, test.txt

		docs = []
		with open(file_path, 'r') as f:
			for line in f:
				docs.append((line.strip()))

		train_dev_split_idx = int(len(docs) * split_ratio[0])
		dev_test_split_idx = int(len(docs) * (split_ratio[0] + split_ratio[1]))

		data = {}
		data["train"] = docs[:train_dev_split_idx]
		data["dev"] = docs[train_dev_split_idx:dev_test_split_idx]
		data["test"] = docs[dev_test_split_idx:]

		folder_path = "others"
		if data_name == "wiki":
			folder_path = config.WIKI_DATA_PATH
		elif data_name == "wikim":
			folder_path = config.WIKIM_DATA_PATH
		elif data_name == "ontonotes":
			folder_path = config.ONTONOTES_DATA_PATH
		else:
			folder_path = config.OTHERS_DATA_PATH
		
		for key in data:
			with open(folder_path+"/"+key+".txt", 'w') as f:
				for line in data[key]:
					f.write(line+"\n")

		print(">> Finished! ")

	def save_model(self, file=None):

		file = config.CHECKPOINT_DIR
		print("save model to ", file)
		self.task.save()
		return


	def load_model(self, file=None):

		file = config.CHECKPOINT_DIR
		print("load model from ", file)
		self.task.load()

		return
