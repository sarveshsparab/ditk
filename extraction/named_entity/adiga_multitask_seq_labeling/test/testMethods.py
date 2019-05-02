import unittest
import pandas as pd
import sys
import os
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from sequence_lableler_final import main


class TestNERMethods(unittest.TestCase):

	def setUp(self):

		
	   
		self.input_file = './test/ner_input.txt'
		# self.input_file = '../data/sample/ner_test_input.txt'
		self.output_file = main(self.input_file)

	def row_col_count(self, file_name):
		with open(file_name, mode='r', encoding='utf-8') as f:
			lines = f.readlines()
			row = len(lines)
			cols = len(lines[0].split())
		return (row, cols)

	def test_outputformat(self):
		input_row_count = self.row_col_count(self.input_file)[0]
		input_col_count = self.row_col_count(self.input_file)[1]
		output_row_count = self.row_col_count(self.output_file)[0]
		output_col_count = self.row_col_count(self.output_file)[1]

		self.assertEqual(input_row_count, output_row_count)
		self.assertEqual(output_col_count, 3)


if __name__ == '__main__':
	unittest.main()