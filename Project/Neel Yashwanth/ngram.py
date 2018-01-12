import math
import numpy as np
import regex as re
import pandas as pd
from collections import Counter
import itertools
import time
import gc
import operator

class Ngram():
	#create variables here to share among all instances of this class
	def __init__(self,fd,n):
		self.wl = []
		self.bigrams = []
		self.bigrams_count = dict()
		self.trigrams_count = dict()
		self.fourgrams_count = dict()
		self.fivegrams_count = dict()
		self.n = n
		self.entire_text = ""
		self.n_grams = []
		self.n_grams_count = []
		self.unigram_count = {}
		self.V = 0	# number of words in vocabulary
		self.N = 0	#total number of words

	def tokenize(self,file,end_token):
		self.wl = []
		with open(file, 'r', encoding='utf-8') as f:
			for line in f:
				#line = line.lower()
				#line = self.cleanLine(line,end_token)
				line = line.split()
				self.wl.extend(line)

	def printNGrams(self,k):
		print(self.n_grams_count[:k])

	def getCounts(self):
		self.n_grams_count = [(item, self.n_grams.count(item)) for item in sorted(set(self.n_grams))]

	def getSpecifiedMatches(self,match):
		pattern = re.compile(match)
		temp = pattern.findall(self.entire_text)
		print(set(temp))

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
		print("Unigram count ...")
		#self.end_text = ""
		gc.collect()
		t0 = time.time()
		#self.wl = self.entire_text.split()
		self.unigram_count = Counter(self.wl)
		t1 = time.time()
		self.N = len(self.wl)
		self.V = len(set(self.wl)) # number of unique words in the vocabulary

	def populateProbMatrix(self,n):
		print("bigram probabilities ...")
		self.bigrams = [' '.join(self.wl[i:i+n]) for i in range(len(self.wl)-n+1)]
		h = 0
		for gram in self.bigrams:
			h += 1
			if(h%960000 == 0):
				print(h)
			w = gram.split()
			if(w[0] == "</s>"):
				continue
			if(gram not in self.bigrams_count):
				self.bigrams_count[gram] = []
				self.bigrams_count[gram].append(1)
				self.bigrams_count[gram].append(0)
			else:
				self.bigrams_count[gram][0] += 1
		self.bigrams_count["<s> <s>"][0] /= 3 
		self.bigrams = []
		gc.collect()

	def laplaceSmoothing(self,n):
		print("Laplace smoothing ..." + str(n))
		if(n == 2):
			t = self.bigrams_count
		elif(n == 3):
			t = self.trigrams_count
		elif(n == 4):
			t = self.fourgrams_count
			r = len(set(self.trigrams_count.keys()))
		elif(n == 5):
			t = self.fivegrams_count
			r = len(set(self.fourgrams_count.keys()))
		h = 0
		for key,value in t.items():
			h += 1
			if(h%1000000 == 0):
				print(h)
			e = key.split()
			a = e[0:n-1]
			s = ' '.join(a)
			if(n-1 == 4):
				count = self.fourgrams_count[s][0]
				#self.fivegrams_count[key][1] = (value[0] + 1)/(count + self.V)
				self.fivegrams_count[key][1] = math.log((value[0] + 1)/(count + r))
			elif(n-1 == 3):
				count = self.trigrams_count[s][0]
				#self.fourgrams_count[key][1] = (value[0] + 1)/(count + self.V)
				self.fourgrams_count[key][1] = math.log((value[0] + 1)/(count + r))
			elif(n-1 == 2):
				count = self.bigrams_count[s][0]
				#self.trigrams_count[key][1] = float(value[0] + 1)/float(count + self.V)
				self.trigrams_count[key][1] = math.log((value[0] + 1)/(count + self.V))
			elif(n-1 == 1):
				count = self.unigram_count[s]
				#self.bigrams_count[key][1] = (value[0] + 1)/(count + self.V)
				self.bigrams_count[key][1] = math.log((value[0] + 1)/(count + self.V))
		#print(math.pow(10,self.fourgrams_count["in the years thereafter"]))
		#print(self.fourgrams_count)
		#print(self.fourgrams_count["in the years thereafter"])
		gc.collect()

	def initializeAndPopulateTrigramMatrix(self,n):
		print("Tigram probabilities ...")
		trigrams = [' '.join(self.wl[i:i+n]) for i in range(len(self.wl)-n+1)]
		h = 0
		for gram in trigrams:
			h += 1
			if(h%960000 == 0):
				print(h)
			l = gram.split()
			if(l[0] == "</s>" or l[1] == "</s>"):
				continue
			if(gram not in self.trigrams_count):
				self.trigrams_count[gram] = []
				self.trigrams_count[gram].append(1)
				self.trigrams_count[gram].append(0)
			else:
				self.trigrams_count[gram][0] += 1
		self.trigrams_count["<s> <s> <s>"][0] /= 2
		#print(self.trigrams_count["in the years"])
		

	def initializeAndPopulateFourgramMatrix(self,n):
		print("Fourgram prob ...")
		fourgrams = [' '.join(self.wl[i:i+n]) for i in range(len(self.wl)-n+1)]
		h = 0
		for gram in fourgrams:
			h += 1
			if(h%960000 == 0):
				print(h)
			l = gram.split()
			#u = ' '.join(l)
			if(l[0] == "</s>" or l[1] == "</s>" or l[2] == "</s>"):
				continue
			if(gram not in self.fourgrams_count):
				self.fourgrams_count[gram] = []
				self.fourgrams_count[gram].append(1)
				self.fourgrams_count[gram].append(0)
			else:
				self.fourgrams_count[gram][0] += 1
		#print(self.fourgrams_count)
		#print(self.fourgrams_count["in the years thereafter"])
		gc.collect()

	def initializeAndPopulateFivegramMatrix(self,n):
		print("Fivegram prob ...")
		fivegrams = [' '.join(self.wl[i:i+n]) for i in range(len(self.wl)-n+1)]
		h = 0
		for gram in fivegrams:
			h += 1
			if(h%960000 == 0):
				print(h)
			l = gram.split()
			u = ' '.join(l)
			if(l[0] == "</s>" or l[1] == "</s>" or l[2] == "</s>" or l[3] == "</s>" or u == "<s> <s> <s> <s> <s>"):
				continue
			if(gram not in self.fivegrams_count):
				self.fivegrams_count[gram] = []
				self.fivegrams_count[gram].append(1)
				self.fivegrams_count[gram].append(0)
			else:
				self.fivegrams_count[gram][0] += 1
		#print(self.fivegrams_count)
		#print(self.fourgrams_count["in the years thereafter"])
		gc.collect()

	def saveProbabilitiesToFile(self,file,n):
		fd = open(file,'w',encoding='utf-8')
		t = dict()
		if(n == 3):
			t = self.trigrams_count
		elif(n == 4):
			t = self.fourgrams_count
		for key,value in t.items():
			fd.write('{} {}\n'.format(key,value))
		fd.close()


	def perplexity(self,sent,n):
		print("Perplexity ...")
		n = int(n)
		sent = list(sent.split())
		grams = [' '.join(sent[i:i+n]) for i in range(len(sent)-n+1)]
		#print(grams)
		ind_prob = []
		g = []
		p = 0
		if(n == 2):
			keys = self.bigrams_count.keys()
			uni_keys = self.unigram_count.keys()		
			for gram in grams:
				h = gram.split()
				if(h[0] == "<\s>" or h[1] == "<s>"):
					continue
				if(gram not in keys):
					e = gram.split()
					g = " ".join(e[0:n-1])
					#calculate probability
					if(g not in uni_keys):
						c = 0
					else:
						c = self.unigram_count[g]
					prob = 1/(c + self.V) # laplace
					ind_prob.append(prob)
					p += prob # add since prob are in terms of log
					#p *= prob # if not using log of prob
					#print(prob,g)
				else:
					p += self.bigrams_count[gram][1]
					#p *= self.bigrams_count[gram][1]
					ind_prob.append(self.bigrams_count[gram][1])
					#print(self.bigrams_count[gram][1],gram)
		if(n == 3):
			keys = self.trigrams_count.keys()
			bi_keys = self.bigrams_count.keys()	
			for gram in grams:
				if(gram not in keys):
					e = gram.split()
					g = " ".join(e[0:n-1])
					#calculate probability
					if(g not in bi_keys):
						c = 0
					else:
						c = self.bigrams_count[g][0]
					prob = 1/(c + self.V) # laplace
					ind_prob.append(prob)
					p += prob # add since prob are in terms of log
					#p *= prob # if not using log of prob
				else:
					p += self.trigrams_count[gram][1]
					#p *= self.trigrams_count[gram][1]
					ind_prob.append(self.trigrams_count[gram][1])
		elif(n == 4):
			keys = self.fourgrams_count.keys()	
			#bi_keys = self.bigrams_count.keys()
			tri_keys = self.trigrams_count.keys()		
			for gram in grams:
				if(gram not in keys):
					e = gram.split()
					g = " ".join(e[0:n-1]) # get n-1 gram i.e trigram
					#calculate probability
					if(g not in tri_keys):
						c = 0
					else:
						c = self.trigrams_count[g][0]
					prob = 1/(c + self.V) # laplace
					ind_prob.append(prob)
					p += prob # add since prob are in terms of log
					#p *= prob
					#print(prob,g)
				else:
					p += self.fourgrams_count[gram][1]
					#p *= self.fourgrams_count[gram][1]
					ind_prob.append(self.fourgrams_count[gram][1])
					#print(self.fourgrams_count[gram][1],gram)
		elif(n == 5):
			keys = self.fivegrams_count.keys()	
			four_keys = self.fourgrams_count.keys()
			tri_keys = self.trigrams_count.keys()		
			for gram in grams:
				if(gram not in keys):
					#calculate probability for gram not seen in training
					e = gram.split()
					g = " ".join(e[0:n-1]) # get n-1 gram i.e fourgram
					#get count
					if(g not in four_keys):
						c = 0
					else:
						c = self.fourgrams_count[g][0]
					prob = 1/(c + self.V) # laplace
					ind_prob.append(prob)
					p += prob # add since prob are in terms of log
					#p *= prob
				else:
					p += self.fivegrams_count[gram][1]
					#p *= self.fivegrams_count[gram][1]
					ind_prob.append(self.fivegrams_count[gram][1])
				#print(p,end=" ")
		#print(ind_prob)
		sent = list(filter(lambda a: a != "<s>", sent))
		N = len(sent)
		entropy = (-1)*(p)/N
		p = math.exp(entropy)
		gc.collect()
		return np.absolute(p)

	def getFirstNWords(self,p,n,text):
		print("\nPredicted completions : ")
		if(len(p) == 0):
			print("Could not predict\n")
			return
		#print(n,len(p.keys()))
		n = min(n,len(p))
		new_p = dict(sorted(p.items(), key=operator.itemgetter(1), reverse=True)[:n])
		for key,value in new_p.items():
			print(key,math.exp(value))
		return new_p

	def test(self,text,n):
		text = text.lower()
		print("testing...")
		p = {}
		if(self.n == 5):
			t = self.fivegrams_count
		if(self.n == 4):
			t = self.fourgrams_count
		elif(self.n == 3):
			t = self.trigrams_count
		elif(self.n == 2):
			t = self.bigrams_count
		text_words = text.split()
		t1 = ' '.join(text_words[len(text_words)-self.n+1:len(text_words)])
		for key,value in t.items():
			if(t1 in key):
				w = key.split()	
				t = ' '.join(w[0:len(w)-1])	
				if(t1 == t):
					#print(text,t)
					p[key] = value[1]
		#print(p)
		self.getFirstNWords(p,n,text)
		print("\n")

def printTime():
	# print("Clean time :" + str(t1-t0))
	# print("Matrix calculation time : " + str(t3-t1))
	# print("Laplace smoothing time : " + str(t4-t3))
	# print("Bigram initialize time : " + str(t11-t1))
	# print("Bigram populate time : " + str(t12-t11))
	# print("Trigram init and pop time : " + str(t2-t12))
	print("Total time : " + str(t4-t0))


if __name__ == '__main__':
	#file = "/home/neel/ngram data/en_US/blogs_test.txt"
	f = input("What dataset you want to use? news, blog, or twitter? : ")
	y = str(2)
	file = "/home/neel/ngram data/en_US/train_" + f + y + ".txt"
	test_file = "/home/neel/ngram data/en_US/test_" + f + y + ".txt"
	fd = open("/home/neel/ngram data/en_US/blogs_test.txt")
	#fd = open("/home/neel/ngram data/en_US/en_US.blogs.txt")
	#number of grams to be fetched from the text file
	n = int(input("What model do you want to use ? 1-5 : "))
	global start_token
	start_token = "<s> "*n
	x = Ngram(fd,n)
	t0 = time.time()
	x.tokenize(file," </s> "+start_token)
	t1 = time.time()
	x.getUnigramCountAndInitializeBigramMatrix()
	t11 = time.time()
	x.populateProbMatrix(2)

	t12 = time.time()
	if(x.n >= 3):
		x.initializeAndPopulateTrigramMatrix(3)
		x.unigram_count = dict()
		gc.collect()
	t2 = time.time()
	#x.laplaceSmoothing()
	t3 = time.time()
	if(x.n >= 4):
		x.initializeAndPopulateFourgramMatrix(4)
		x.bigrams_count = dict()
		x.unigram_count = dict()
		gc.collect()
	if(x.n == 5):
		x.initializeAndPopulateFivegramMatrix(5)
		x.bigrams_count = dict()
		x.trigrams_count = dict()
		x.unigram_count = dict()
		gc.collect()
	x.laplaceSmoothing(x.n)
	
	test = "he is one of the"
	x.test(test,5)
	test = "whether we will do the"
	x.test(test,5)
	test = "i did not come to condemn the world but to save the world"
	x.test(test,5)
	test = "i embrace them and try to keep them happy and"
	x.test(test,5)
	# x.saveProbabilitiesToFile("four_gram_prob.txt",4)
	# x.saveProbabilitiesToFile("tri_gram_prob.txt",3)
	t_f = open(test_file,'r',encoding='utf-8')
	t = t_f.read()
	print("Perplexity : "+ str(x.perplexity(t,x.n)))
	print("Number of Unique words : " + str(len(set(x.wl))))
	t4 = time.time()
	printTime()
	

