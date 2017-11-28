import math
import numpy as np
from nltk import ngrams
import regex as re
import pandas as pd
from collections import Counter
import itertools
import time
import gc

class Ngram():
	#create variables here to share among all instances of this class
	def __init__(self,fd,n):
		self.wl = []
		self.wl_set = []
		self.bigrams = []
		self.bigrams_count = dict()
		self.trigrams_count = dict()
		self.trigrams_prob = dict()
		self.fourgrams_count = dict()
		self.fourgrams_prob = dict()
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
		line = re.sub("\((\s)*(\w)+(\s)*\)",r" \2 ",line)
		line = re.sub("\((\s)*([0-9])+(\s)*\)",r" \2 ",line)
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
		#URL
		self.entire_text = re.sub("http[s]?:.*?(\s)+|www\.(.*?)(\s)+",r"<URL>",self.entire_text,flags=re.I)
		#dates
		self.entire_text = re.sub("(jan|feb|mar|apr|may|jun|jul|aug|sept|oct|nov|dec)(\.)?(\s)?(\d){1,2}",r" \1 <D> ",self.entire_text,flags=re.I)
		self.entire_text = re.sub("(january|february|march|april|may|june|july|august|september|october|november|december)(\.)?(\s)?(\d){1,2}",r" \1 <D> ",self.entire_text,flags=re.I)
		#year
		self.entire_text = re.sub("(jan|feb|mar|apr|may|jun|jul|aug|sept|oct|nov|dec)(\.)?(\s)?(\d){4,4}",r" \1 <Y> ",self.entire_text,flags=re.I)
		self.entire_text = re.sub("(january|february|march|april|may|june|july|august|september|october|november|december)(\.)?(\s)?(\d){4,4}",r" \1 <D> ",self.entire_text,flags=re.I)
		#currencies line $4.50
		self.entire_text = re.sub("([$€£]\d+(\.?\d{0,5})?)|(\d+(\.?\d{0,5})?[$€£])","<C>",self.entire_text)
		#currency symbols like $$$
		self.entire_text = re.sub("[$€£]+"," money ",self.entire_text)

		#replace single quotes around words or sentences
		self.entire_text = re.sub("(\')(.*?)(\')",r" \2 ",self.entire_text)
		#find strings inside paranthesis using non-greedy match and remove them
		pattern = re.compile("(\(.*?\))")
		#inside_paranthesis = pattern.findall(self.entire_text)
		#print(inside_paranthesis)
		self.entire_text = pattern.sub(" ",self.entire_text)
		#single parantheses
		self.entire_text = re.sub("(\s)+\((\w)+|(\s)+(\w)+\(| \( |(\s)+\)(\w)+|(\s)+(\w)+\)| \) "," ",self.entire_text)
		#expressions such as 4/3 which means 4 or 3
		self.entire_text = re.sub("(\s+)(\d+)/(\d+)(\s+)",r"\1\2 or \3\4",self.entire_text)
		self.entire_text = re.sub("(\s+)(\w+)/(\w+)(\s+)",r"\1\2 or \3\4",self.entire_text)
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
		#self.end_text = ""
		gc.collect()
		t0 = time.time()
		self.wl = self.entire_text.split()
		self.unigram_count = Counter(self.wl)
		t1 = time.time()
		#print("Word list and unigram count time : " + str(t1-t0))
		#keywords = [' '.join(i) for i in itertools.product(self.wl, repeat = 3)]
		self.N = len(self.wl)
		self.wl_set = list(set(self.wl))
		self.V = len(self.wl_set)	# number of unique words in the vocabulary
		# col1 = "WORDS_LIST"
		# self.wl_set.insert(0,col1)
		# t2 = time.time()
		# data = np.zeros((len(self.wl_set)-1,len(self.wl_set)))
		# self.bigram_df = pd.DataFrame(data=data,columns=self.wl_set)
		# self.bigram_df[col1] = self.wl_set[1:len(self.wl_set)]
		# self.bigram_df = self.bigram_df.set_index(col1)
		# t3 = time.time()
		#print("Bigram dataframe init time : " + str(t1-t0))
		# self.wl_set.pop(0)
		#print(keywords)

	# def getCount(self,a,b):
	# 	my_regex = re.escape(a) + "(\s)+" + re.escape(b)
	# 	pat = re.compile(my_regex)
	# 	m = pat.findall(self.entire_text)
	# 	return m

	def populateProbMatrix(self,n):
		self.bigrams = [' '.join(self.wl[i:i+n]) for i in range(len(self.wl)-n+1)]
		for gram in self.bigrams:
			# gram = gram.split()
			# a = gram[0]
			# b = gram[1]
			if(gram not in self.bigrams_count):
				self.bigrams_count[gram] = 1
			else:
				self.bigrams_count[gram] += 1
			#self.bigram_df[a][b] = self.bigram_df[a][b] + 1
       
		# for i in range(1,len(self.wl)):
		# 	a = self.wl[i]
		# 	b = self.wl[i-1]
		# 	if(not(a == "</s>" or b == "</s>")):
		# 		s = b + " " + a
		# 		if(not(s in self.bigrams)):
		# 			self.bigrams.append(s)
			#print(a,b,self.bigram_df[a][b],end = "||||")
			#self.bigram_df[a][b] = self.bigram_df[a][b] + 1
		self.bigrams.remove("<s> </s>")
		self.bigrams.remove("</s> <s>")
		self.bigrams.remove("<s> <s>")
		self.bigrams = list(set(self.bigrams))
		# #fix the bigram count for </s> <s> which should be 0
		# self.bigram_df["<s>"]["</s>"] = 0
		# self.bigram_df["<s>"]["<s>"] = 0
		# self.bigram_df["</s>"]["<s>"] = 0

	def laplaceSmoothing(self,n):
		if(n == 2):
			t = self.bigrams_count
		elif(n == 3):
			t = self.trigrams_count
		elif(n == 4):
			t = self.fourgrams_count
		for key,value in t.items():
			e = key.split()
			a = e[0:n-1]
			s = ' '.join(a)
			if(n-1 == 3):
				count = self.trigrams_count[s]
				self.fourgrams_prob[key] = (value + 1)/(count + self.V)
			elif(n-1 == 2):
				count = self.bigrams_count[s]
				self.trigrams_prob[key] = (value + 1)/(count + self.V)
			elif(n-1 == 1):
				count = self.unigram_count[s]
				self.bigrams_prob[key] = (value + 1)/(count + self.V)
		#print(math.pow(10,self.fourgrams_prob["in the years thereafter"]))
		#print(self.fourgrams_prob)
		print(self.fourgrams_prob["in the years thereafter"])
		gc.collect()

	def initializeAndPopulateTrigramMatrix(self,n):
		trigrams = [' '.join(self.wl[i:i+n]) for i in range(len(self.wl)-n+1)]
		for gram in trigrams:
			l = gram.split()
			if(l[0] == "</s>" or l[1] == "</s>"):
				continue
			if(gram not in self.trigrams_count):
				self.trigrams_count[gram] = 1
			else:
				self.trigrams_count[gram] += 1
		#print(self.trigrams_count["in the years"])
		# col1 = "WORD_LIST"
		# self.wl_set.insert(0,col1)
		#wl_set_index = str(list(range(0,len(wl_set))))
		#get all bigrams from cleaned text
		# self.bigrams = []
		# for i in range(0,len(wl)-1):
		# 	if(wl[i] == "</s>" or wl[i+1] == "</s>"):
		# 		continue
		# 	s = wl[i] + " " + wl[i+1]
		# 	if(not(s in self.bigrams)):
		# 		self.bigrams.append(s)
		# self.bigrams = list(set(self.bigrams))
		#initialize trigram matrix
		# data = np.zeros((len(self.bigrams),len(self.wl_set)))
		# self.trigram_df = pd.DataFrame(data=data,columns=self.wl_set)
		# self.trigram_df[col1] = self.bigrams
		# self.trigram_df = self.trigram_df.set_index(col1)
		# self.wl_set.pop(0)
		#count
		# for i in range(2,len(self.wl)):
		# 	a = self.wl[i-2]
		# 	b = self.wl[i-1]
		# 	if(a == "</s>" or b == "</s>"):
		# 		continue
		# 	c = self.wl[i]
		# 	s = a + " " + b
		# 	self.trigram_df[c][s] = self.trigram_df[c][s] + 1
		#print(self.trigram_df)
		#print(self.trigram_df["years"]["in the"])

	def laplaceSmoothingTrigram(self):
		for key,value in self.trigrams_count.items():
			e = key.split()	# trigram words
			a = e[0]
			b = e[1]
			c = e[2]
			s = a + " " + b
			bi_count = self.bigrams_count[s]
			#self.trigrams_prob[key] = math.log((value + 1)/(bi_count + self.V),10)
			self.trigrams_prob[key] = (value + 1)/(bi_count + self.V)
		# print(self.trigrams_count["in the years"])
		# print(self.trigrams_prob["in the years"])
		gc.collect()
		# cols = self.trigram_df.columns
		# self.trigram_df[cols] += 1
		# #count bigrams for denominator
		# x = self.trigram_df.shape[0]	# number of rows in trigram matrix
		# bi_counts = []
		# for i in range(0,x):
		# 	y = self.bigrams[i]	# the bigram
		# 	a = y.split()	# two words in bigram
		# 	c = self.bigram_df[a[1]][a[0]] # count of the bigram in the denominator
		# 	bi_counts.append(c + self.V)	# the denominator
		# 	self.trigram_df.loc[y] /= bi_counts[i]
		# for i in range(0,len(bi_counts)):
		# 	a = self.bigrams[i]
		# 	self.trigram_df.loc[a] /= bi_counts[i]
		#self.trigram_df /= 
		# print(self.trigram_df)
		# print(self.bigram_df["<s>"]["</s>"])
		# print(self.trigram_df["years"]["in the"])
		# print(self.trigram_df.values.sum())

	def initializeAndPopulateFourgramMatrix(self,n):
		fourgrams = [' '.join(self.wl[i:i+n]) for i in range(len(self.wl)-n+1)]
		for gram in fourgrams:
			l = gram.split()
			if(l[0] == "</s>" or l[1] == "</s>" or l[2] == "</s>"):
				continue
			if(gram not in self.fourgrams_count):
				self.fourgrams_count[gram] = 1
			else:
				self.fourgrams_count[gram] += 1
		#print(self.fourgrams_count)
		#print(self.fourgrams_count["in the years thereafter"])
		gc.collect()

	def laplaceSmoothingFourgram(self):
		for key,value in self.fourgrams_count.items():
			e = key.split()	# trigram words
			a = e[0]
			b = e[1]
			c = e[2]
			d = e[3]
			s = a + " " + b + " " + c
			tri_count = self.trigrams_count[s]
			#self.fourgrams_prob[key] = math.log((value + 1)/(tri_count + self.V),10)
			self.fourgrams_prob[key] = (value + 1)/(tri_count + self.V)
		#print(math.pow(10,self.fourgrams_prob["in the years thereafter"]))
		print(self.fourgrams_prob["in the years thereafter"])
		gc.collect()

	def saveProbabilitiesToFile(self,file,n):
		fd = open(file,'w',encoding='utf-8')
		t = dict()
		if(n == 3):
			t = self.trigrams_prob
		elif(n == 4):
			t = self.fourgrams_prob
		for key,value in t.items():
			fd.write('{} {}\n'.format(key,value))
		fd.close()


	def perplexity(self,sent,n):
		n = int(n)
		sent = list(sent.split())
		grams = [' '.join(sent[i:i+n]) for i in range(len(sent)-n+1)]
		print(grams)
		ind_prob = []
		g = []
		p = 1
		if(n == 3):
			keys = self.trigrams_prob.keys()
			bi_keys = self.bigrams_count.keys()			
			for gram in grams:
				if(gram not in keys):
					e = gram.split()
					g = " ".join(e[0:n-1])
					#calculate probability
					if(g not in bi_keys):
						c = 0
					else:
						c = self.bigrams_count[g]
					prob = 1/(c + self.V) # laplace
					ind_prob.append(prob)
					#p += prob # add since prob are in terms of log
					p *= prob # if not using log of prob
				else:
					#p += self.trigrams_prob[gram]
					p *= self.trigrams_prob[gram]
					ind_prob.append(self.trigrams_prob[gram])
		elif(n == 4):
			keys = self.fourgrams_prob.keys()	
			bi_keys = self.bigrams_count.keys()
			tri_keys = self.trigrams_count.keys()		
			for gram in grams:
				if(gram not in keys):
					e = gram.split()
					g = " ".join(e[0:n-1]) # get n-1 gram i.e trigram
					#calculate probability
					if(g not in tri_keys):
						c = 0
					else:
						c = self.trigrams_count[g]
					prob = 1/(c + self.V) # laplace
					ind_prob.append(prob)
					p += prob # add since prob are in terms of log
					p *= prob
				else:
					#p += self.fourgrams_prob[gram]
					p *= self.fourgrams_prob[gram]
					ind_prob.append(self.fourgrams_prob[gram])
		# print(ind_prob)
		# print("Multiplied prob : " + str(p))
		p = 1/p
		#p = math.pow(10,p)
		p = p**(1/float(n))
		#p = math.pow(p,(1/float(n)))
		return p

def cleanAndGetCounts(x,file):
	
	x.tokenize(file," </s> "+start_token)
	#x.getSpecifiedMatches("(\s+)(\d+)/(\d+)|([a-zA-Z]+)/([a-zA-Z]+)(\s+)")
	#x.getSpecifiedMatches("http[s]?:(.*)(\s)+")
	#x.getSpecifiedMatches("((\s+|\n)[$€£]+(\s+|\n))")
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
	n = 4
	start_token = "<s> "*n
	x = Ngram(fd,n)
	t0 = time.time()
	cleanAndGetCounts(x,file)
	t1 = time.time()
	x.getUnigramCountAndInitializeBigramMatrix()
	t11 = time.time()
	x.populateProbMatrix(2)
	t12 = time.time()
	x.initializeAndPopulateTrigramMatrix(3)
	t2 = time.time()
	#x.laplaceSmoothing()
	t3 = time.time()
	x.initializeAndPopulateFourgramMatrix(4)
	x.laplaceSmoothing(4)
	x.laplaceSmoothing(3)
	#x.laplaceSmoothing(2)
	x.saveProbabilitiesToFile("four_gram_prob.txt",4)
	x.saveProbabilitiesToFile("tri_gram_prob.txt",3)
	t = " in the years thereafter and"
	print("Perplexity : "+ str(x.perplexity(t,4)))
	#test(x,n)
	# print("Clean time :" + str(t1-t0))
	# print("Matrix calculation time : " + str(t3-t1))
	# print("Laplace smoothing time : " + str(t3-t2))
	# print("Bigram initialize time : " + str(t11-t1))
	# print("Bigram populate time : " + str(t12-t11))
	# print("Trigram init and pop time : " + str(t2-t12))
	# print("Total time : " + str(t3-t0))
	# a = ["neel","am","cool","bro"]
	# keywords = [' '.join(i) for i in itertools.product(a, repeat = 3)]
	# print(keywords)

