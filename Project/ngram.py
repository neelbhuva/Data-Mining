import math
import numpy as np
from nltk import ngrams
import regex as re
import pandas as pd
from collections import Counter
import itertools

class Ngram():
	#create variables here to share among all instances of this class
	def __init__(self,fd,n):
		self.wl = []
		self.bigrams = []
		self.n = n
		self.entire_text = ""
		self.n_grams = []
		self.n_grams_count = []
		self.bigram_df = pd.DataFrame()	#bigram counts/prob matrix
		self.trigram_df = pd.DataFrame()	#trigram counts/prob matrix
		self.unigram_count = {}
		self.V = 0	# number of words in vocabulary
		self.N = 0	#total number of words

	def tokenize(self,file,end_token):
		self.wl = []
		with open(file, 'r', encoding='utf-8') as f:
			for line in f:
				line = line.lower()
				line = self.cleanLine(line,end_token)
				self.entire_text += line
            	# w = re.findall('\w+', sent)
            	# for word in w:
            	# 	self.wl.append(word)
        #print(self.entire_text)

	def readNGrams(self):
		self.n_grams = ngrams(self.entire_text.split(), self.n)
		self.n_grams = list(self.n_grams)

	def printNGrams(self,k):
		print(self.n_grams_count[:k])

	def getCounts(self):
		self.n_grams_count = [(item, self.n_grams.count(item)) for item in sorted(set(self.n_grams))]

	def getSpecifiedMatches(self,match):
		pattern = re.compile(match)
		temp = pattern.findall(self.entire_text)
		print(set(temp))

	def cleanLine(self,line,end_token):
		#single apostrophes
		line = re.sub(" ' |(\w)+'|'(\w)+"," ",line,flags=re.I)
		#charac like / with spaced around
		line = re.sub(" / "," ",line,flags=re.I)
		#words like don't, won't, aren't it's...
		#line = re.sub("(can't)|(ain't)|(won't)|(shan't)",r" \1 ",line,flags=re.I)
		line = re.sub("([a-zA-Z])n't",r" \1 not ",line,flags=re.I)
		#words like it's
		line = re.sub("(it)'s",r" \1 is ",line,flags=re.I)
		#single words or numbers inside paranthesis
		line = re.sub("\((\s)*(\w)+(\s)*\)|\((\s)*([0-9])+(\s)*\)",r" \2 ",line)
		#replace points such as 1), 23) ...with space
		line = re.sub("(\d)+\)|(\d)+\)\.|(\d)+\.\)"," ",line)
		#do not split compound words like e-email
		line = re.sub("(\s)+([a-zA-Z]{1,2})-([a-zA-Z]+)",r" \2\3 ",line)
		#remove smileys
		line = re.sub("<3|:\)|:\)|:D|:P"," ",line)
		#replace ampersand with and
		line = re.sub("&"," and ",line,flags=re.I)
		#2 & 3 char words like st.,Mr.,Dr.,sq.,etc. ending with . and a newline
		line = re.sub("(\s)+([a-zA-Z]{1,3})(\.)(\n)",r"\1\2 "+end_token,line,flags=re.I)		
		#2 & 3 character words like st.,Mr.,Dr.,sq. ending with . and not a newline
		line = re.sub("(\s)+([a-zA-Z]{1,3})(\.)(\s)?",r"\1\2 ",line,flags=re.I)
		#replace double quotes, commas, colon ... with space
		line = re.sub("\"|,|:|-|\'"," ",line)
		#multiple dots like Hmm...
		line = re.sub("[.][.]+"," ",line)
		return line

	def cleanAndInsertEndToken(self,end_token):
		#convert to lowecase
		self.entire_text = self.entire_text.lower()
		# pattern = re.compile("\s+[a-zA-Z][a-zA-Z]\.")
		# two_char = pattern.findall(self.entire_text)
		# print(set(two_char))
		
		#dates
		self.entire_text = re.sub("(jan|feb|mar|apr|may|jun|jul|aug|sept|oct|nov|dec)(\.)?(\s)?(\d){1,2}",r" \1 <D> ",self.entire_text,flags=re.I)
		self.entire_text = re.sub("(january|february|march|april|may|june|july|august|september|october|november|december)(\.)?(\s)?(\d){1,2}",r" \1 <D> ",self.entire_text,flags=re.I)
		#year
		self.entire_text = re.sub("(jan|feb|mar|apr|may|jun|jul|aug|sept|oct|nov|dec)(\.)?(\s)?(\d){4,4}",r" \1 <Y> ",self.entire_text,flags=re.I)
		self.entire_text = re.sub("(january|february|march|april|may|june|july|august|september|october|november|december)(\.)?(\s)?(\d){4,4}",r" \1 <D> ",self.entire_text,flags=re.I)
		
		#replace single quotes around words or sentences
		self.entire_text = re.sub("(\')(.*?)(\')",r" \2 ",self.entire_text)
		
		#find strings inside paranthesis using non-greedy match and remove them
		pattern = re.compile("(\(.*?\))")
		#inside_paranthesis = pattern.findall(self.entire_text)
		#print(inside_paranthesis)
		self.entire_text = pattern.sub(" ",self.entire_text)
		#single parantheses
		self.entire_text = re.sub("(\s)+\((\w)+|(\s)+(\w)+\(| \( |(\s)+\)(\w)+|(\s)+(\w)+\)| \) "," ",self.entire_text)
		#add end token at the end of sentences
		pattern = re.compile("\.(\s)*|[!]+(\s)*|(\?)+(\s)*|\)(\s)+",re.IGNORECASE)
		self.entire_text = pattern.sub(end_token,self.entire_text)
		self.entire_text = "<s> "*self.n + self.entire_text
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

	# def getCount(self,a,b):
	# 	my_regex = re.escape(a) + "(\s)+" + re.escape(b)
	# 	pat = re.compile(my_regex)
	# 	m = pat.findall(self.entire_text)
	# 	return m

	def populateProbMatrix(self):
		wl = self.entire_text.split()
		for i in range(1,len(wl)):
			a = wl[i]
			b = wl[i-1]
			#print(a,b,self.bigram_df[a][b],end = "||||")
			self.bigram_df[a][b] = self.bigram_df[a][b] + 1
		#fix the bigram count for </s> <s> which should be 0
		self.bigram_df["<s>"]["</s>"] = 0

	def initializeAndPopulateTrigramMatrix(self):
		wl = self.entire_text.split()	
		#wl_index = str(list(range(0,len(wl))))
		wl_set = list(set(wl))
		col1 = "WORD_LIST"
		wl_set.insert(0,col1)
		#wl_set_index = str(list(range(0,len(wl_set))))
		#get all bigrams from cleaned text
		self.bigrams = []
		for i in range(0,len(wl)-1):
			if(wl[i] == "</s>" or wl[i+1] == "</s>"):
				continue
			s = wl[i] + " " + wl[i+1]
			if(not(s in self.bigrams)):
				self.bigrams.append(s)
		self.bigrams = list(set(self.bigrams))
		#initialize trigram matrix
		data = np.zeros((len(self.bigrams),len(wl_set)))
		self.trigram_df = pd.DataFrame(data=data,columns=wl_set)
		self.trigram_df[col1] = self.bigrams
		self.trigram_df = self.trigram_df.set_index(col1)
		wl.pop(0)
		#count
		for i in range(2,len(wl)):
			a = wl[i-2]
			b = wl[i-1]
			if(a == "</s>" or b == "</s>"):
				continue
			c = wl[i]
			s = a + " " + b
			self.trigram_df[c][s] = self.trigram_df[c][s] + 1
		#print(self.trigram_df)
		#print(self.trigram_df["years"]["in the"])

	def laplaceSmoothing(self):
		cols = self.trigram_df.columns
		self.trigram_df[cols] += 1
		#count bigrams for denominator
		x = self.trigram_df.shape[0]	# number of rows in trigram matrix
		bi_counts = []
		for i in range(0,x):
			y = self.bigrams[i]	# the bigram
			a = y.split()	# two words in bigram
			c = self.bigram_df[a[1]][a[0]] # count of the bigram in the denominator
			bi_counts.append(c + self.V)	# the denominator
			self.trigram_df.loc[y] /= bi_counts[i]
		# for i in range(0,len(bi_counts)):
		# 	a = self.bigrams[i]
		# 	self.trigram_df.loc[a] /= bi_counts[i]
		#self.trigram_df /= 
		print(self.trigram_df)
		print(self.bigram_df["<s>"]["</s>"])
		print(self.trigram_df["years"]["in the"])
		print(self.trigram_df.values.sum())

def cleanAndGetCounts(x,file):
	#x.getSpecifiedMatches("(jan|feb|mar|apr|may|jun|jul|aug|sept|oct|nov|dec)(\.)?(\s)?(\d){1,2}")
	x.tokenize(file," </s> "+start_token)
	x.cleanAndInsertEndToken(" </s> "+start_token)
	fd.close()
	#x.readNGrams()
	#number of ngrams to print
	#x.delNGramsWithEndTokenInWrongPlace()
	#x.getCounts()
	p = 100
	#x.printNGrams(p)
	#x.saveNGramsCountToFile("blogs_count_bigram.txt")

if __name__ == '__main__':
	file = "/home/neel/ngram data/en_US/blogs_test.txt"
	fd = open("/home/neel/ngram data/en_US/blogs_test2.txt")
	#fd = open("/home/neel/ngram data/en_US/en_US.blogs.txt")
	#number of grams to be fetched from the text file
	n = 3
	start_token = "<s> "*n
	x = Ngram(fd,n)
	cleanAndGetCounts(x,file)
	x.getUnigramCountAndInitializeBigramMatrix()
	x.populateProbMatrix()
	x.initializeAndPopulateTrigramMatrix()
	x.laplaceSmoothing()
	# a = ["neel","am","cool","bro"]
	# keywords = [' '.join(i) for i in itertools.product(a, repeat = 3)]
	# print(keywords)

