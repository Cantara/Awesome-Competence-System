class Splitter():
		
	def data_as_list(self):
		splitresult = splitlist(self.data,',') 
		
	
		
if __name__ == '__main__':
	print("hei");
	
def splitlist(list, delim):
		splitresult = []
		tmpsplitresult = []
		for word in list:
			tmpsplitresult = word.split(delim)
			splitresult = splitresult + tmpsplitresult
		return splitresult
		
def striplist(l):
	return([x.strip() for x in l])
		