import unittest
import multidelim

class TestSequenceFunctions(unittest.TestCase):

	def setUp(self):
		print("Setup")
		splitted_list = []
		striped_list = []

	def test_split_single(self):
		splitted_list = multidelim.splitlist(['a','b ',' c', 'd'], ',')
		print('Single',   splitted_list)
		self.assertEqual(['a','b ',' c','d'], splitted_list)
	def test_split_single_punkt(self):
		splitted_list = multidelim.splitlist(['a.b . c .d'], '.')
		print('Single punkt',   splitted_list)
		self.assertEqual(['a','b ',' c ','d'], splitted_list)
	def test_split_single_semi (self):
		splitted_list = multidelim.splitlist(['a;b ; c;d '], ';')
		print("Single semi", splitted_list)
		self.assertEqual(['a','b ',' c','d '], splitted_list)
		
	def test_split_single_item(self):
		splitted_list = multidelim.splitlist(['a, b, c,d'], ',')
		print("Single item", splitted_list)
		self.assertEqual(['a',' b',' c','d'], splitted_list)

	def test_split_multiple_delim(self):
		splitted_list = multidelim.splitlist(['a, b; c. d'], ',')
		splitted_list = multidelim.splitlist(splitted_list, ';')
		splitted_list = multidelim.splitlist(splitted_list, '.')
		print("3 delims", splitted_list)
		self.assertEqual(['a',' b',' c',' d'], splitted_list)
		
	def test_strip_list(self):
		striped_list = multidelim.striplist(['a',' b',' c',' d'])
		print("Stripped " , striped_list)
		self.assertEqual(['a','b','c','d'],striped_list)
		
if __name__ == '__main__':
    unittest.main()