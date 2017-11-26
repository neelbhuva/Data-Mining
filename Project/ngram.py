import math
import numpy as np
from nltk import ngrams
import regex as re
import pandas as pd
from collections import Counter
import itertools

class Ngram():
	#create variables here to share among all instances of this class
	def __init__(self,fd):
		self.entire_text = fd.read()
		self.n_grams = []
		self.n_grams_count = []
		self.bigram_df = pd.DataFrame()	#bigram counts/prob matrix
		self.unigram_count = {}
		self.V = 0	# number of words in vocabulary
		self.N = 0	#total number of words

	def readNGrams(self,n):
		self.n_grams = ngrams(self.entire_text.split(), n)
		self.n_grams = list(self.n_grams)

	def printNGrams(self,n):
		print(self.n_grams_count[:n])

	def getCounts(self):
		self.n_grams_count = [(item, self.n_grams.count(item)) for item in sorted(set(self.n_grams))]

	def getSpecifiedMatches(self,match):
		pattern = re.compile(match)
		temp = pattern.findall(self.entire_text)
		print(set(temp))


	def cleanAndInsertEndToken(self,end_token):
		#convert to lowecase
		self.entire_text = self.entire_text.lower()
		# pattern = re.compile("\s+[a-zA-Z][a-zA-Z]\.")
		# two_char = pattern.findall(self.entire_text)
		# print(set(two_char))
		#single apostrophes
		self.entire_text = re.sub(" ' |(\w)+'|'(\w)+"," ",self.entire_text,flags=re.I)
		#charac like / with spaced around
		self.entire_text = re.sub(" / "," ",self.entire_text,flags=re.I)
		#words like don't, won't, aren't it's...
		#self.entire_text = re.sub("(can't)|(ain't)|(won't)|(shan't)",r" \1 ",self.entire_text,flags=re.I)
		self.entire_text = re.sub("([a-zA-Z])n't",r" \1 not ",self.entire_text,flags=re.I)
		#words like it's
		self.entire_text = re.sub("(it)'s",r" \1 is ",self.entire_text,flags=re.I)
		#single words or numbers inside paranthesis
		self.entire_text = re.sub("\((\s)*(\w)+(\s)*\)|\((\s)*([0-9])+(\s)*\)",r" \2 ",self.entire_text)
		#dates
		self.entire_text = re.sub("(jan|feb|mar|apr|may|jun|jul|aug|sept|oct|nov|dec)(\.)?(\s)?(\d){1,2}",r" \1 <D> ",self.entire_text,flags=re.I)
		self.entire_text = re.sub("(january|february|march|april|may|june|july|august|september|october|november|december)(\.)?(\s)?(\d){1,2}",r" \1 <D> ",self.entire_text,flags=re.I)
		#year
		self.entire_text = re.sub("(jan|feb|mar|apr|may|jun|jul|aug|sept|oct|nov|dec)(\.)?(\s)?(\d){4,4}",r" \1 <Y> ",self.entire_text,flags=re.I)
		self.entire_text = re.sub("(january|february|march|april|may|june|july|august|september|october|november|december)(\.)?(\s)?(\d){4,4}",r" \1 <D> ",self.entire_text,flags=re.I)
		#replace points such as 1), 23) ...with space
		self.entire_text = re.sub("(\d)+\)|(\d)+\)\.|(\d)+\.\)"," ",self.entire_text)
		#do not split compound words like e-email
		self.entire_text = re.sub("(\s)+([a-zA-Z]{1,2})-([a-zA-Z]+)",r" \2\3 ",self.entire_text)
		#remove smileys
		self.entire_text = re.sub("<3|:\)|:\)|:D|:P"," ",self.entire_text)
		#replace ampersand with and
		self.entire_text = re.sub("&"," and ",self.entire_text,flags=re.I)
		#2 & 3 char words like st.,Mr.,Dr.,sq.,etc. ending with . and a newline
		self.entire_text = re.sub("(\s)+([a-zA-Z]{1,3})(\.)(\n)",r"\1\2 "+end_token,self.entire_text,flags=re.I)		
		#2 & 3 character words like st.,Mr.,Dr.,sq. ending with . and not a newline
		self.entire_text = re.sub("(\s)+([a-zA-Z]{1,3})(\.)(\s)?",r"\1\2 ",self.entire_text,flags=re.I)
		#replace double quotes, commas, colon ... with space
		self.entire_text = re.sub("\"|,|:|-|\'"," ",self.entire_text)
		#replace single quotes around words or sentences
		self.entire_text = re.sub("(\')(.*?)(\')",r" \2 ",self.entire_text)
		#multiple dots like Hmm...
		self.entire_text = re.sub("[.][.]+"," ",self.entire_text)
		#find strings inside paranthesis using non-greedy match and remove them
		pattern = re.compile("(\(.*?\))")
		inside_paranthesis = pattern.findall(self.entire_text)
		#print(inside_paranthesis)
		self.entire_text = pattern.sub(" ",self.entire_text)
		#single parantheses
		self.entire_text = re.sub("(\s)+\((\w)+|(\s)+(\w)+\(| \( |(\s)+\)(\w)+|(\s)+(\w)+\)| \) "," ",self.entire_text)
		#add end token at the end of sentences
		pattern = re.compile("\.(\s)*|[!]+(\s)*|(\?)+(\s)*|\)(\s)+",re.IGNORECASE)
		self.entire_text = pattern.sub(end_token,self.entire_text)
		#print(self.entire_text)

	def delNGramsWithEndTokenInWrongPlace(self):
		temp = []
		for i in self.n_grams:
			if(i[0] == "</s>" or i[1] == "</s>"):
				temp.append(i)
		for i in temp:
			self.n_grams.remove(i)

	def saveNGramsCountToFile(self,file):
		with open(file, 'w') as fp:
			for x in self.n_grams_count:
				s = ""
				for i in x[0]:	
					s = s + i + " "
				fp.write('{} {}\n'.format(s,x[1]))
		fp.close()

	def getUnigramCountAndInitializeBigramMatrix(self):
		wordList = self.entire_text.split()
		self.unigram_count = Counter(wordList)
		#keywords = [' '.join(i) for i in itertools.product(wordList, repeat = 3)]
		self.N = len(wordList)
		wordList = list(set(wordList))
		self.V = len(wordList)
		col1 = "WORDS_LIST"
		wordList.insert(0,col1)
		data = np.zeros((len(wordList)-1,len(wordList)))
		self.bigram_df = pd.DataFrame(data=data,columns=wordList)
		self.bigram_df[col1] = wordList[1:len(wordList)]
		self.bigram_df = self.bigram_df.set_index(col1)
		#print(keywords)

	def getCount(self,a,b):
		my_regex = re.escape(a) + "(\s)+" + re.escape(b)
		pat = re.compile(my_regex)
		m = pat.findall(self.entire_text)
		return m
		# t = a + " " + b
		# for i in self.n_grams_count:
		# 	u = i[0][0]
		# 	v = i[0][1]
		# 	s = ' '.join(i[0])

	def populateProbMatrix(self):
		wl = self.entire_text.split()
		for i in range(0,len(wl)-1):
			a = wl[i]
			b = wl[i+1]
			#print(a,b,self.bigram_df[a][b],end = "||||")
			self.bigram_df[a][b] = self.bigram_df[a][b] + 1
		#print(self.bigram_df["makes"]["them"])
		#print(wl)
		# cols = self.bigram_df.columns
		# for i in cols:
		# 	for j in cols:
		# 		df[i][j] = self.getCount(j,i)

def cleanAndGetCounts(x):
	#x.getSpecifiedMatches("(jan|feb|mar|apr|may|jun|jul|aug|sept|oct|nov|dec)(\.)?(\s)?(\d){1,2}")
	x.cleanAndInsertEndToken(" </s> "+start_token)
	fd.close()
	x.readNGrams(n)
	#number of ngrams to print
	x.delNGramsWithEndTokenInWrongPlace()
	x.getCounts()
	p = 100
	#x.printNGrams(p)
	x.saveNGramsCountToFile("blogs_count_bigram.txt")

if __name__ == '__main__':
	fd = open("/home/neel/ngram data/en_US/blogs_test2.txt")
	#fd = open("/home/neel/ngram data/en_US/en_US.blogs.txt")
	#number of grams to be fetched from the text file
	n = 2
	start_token = "<s> "*n
	x = Ngram(fd)
	cleanAndGetCounts(x)
	x.getUnigramCountAndInitializeBigramMatrix()
	x.populateProbMatrix()
	# a = ["neel","am","cool","bro"]
	# keywords = [' '.join(i) for i in itertools.product(a, repeat = 3)]
	# print(keywords)

