import math
import numpy as np
from nltk import ngrams
import regex as re

class Ngram():
	#create variables here to share among all instances of this class
	def __init__(self,fd):
		self.entire_text = fd.read()
		self.n_grams = []

	def readNGrams(self,n):
		self.n_grams = ngrams(self.entire_text.split(), n)

	def printNGrams(self,n):
		for i in list(self.n_grams)[:n]:
			print(i)

	def cleanAndInsertEndToken(self,end_token):
		pattern = re.compile("\s+[a-zA-Z][a-zA-Z]\.\s+")
		two_char = pattern.findall(self.entire_text)
		print(two_char)
		#two character words like st.,Mr.,Dr.,sq. ending with a . and a newline
		self.entire_text = re.sub("(\s)+([MDSJ][rstq]?)(\.)(\n)",r"\1\2 "+end_token,self.entire_text,flags=re.I)		
		#two character words like st.,Mr.,Dr.,sq. ending with a . and not a newline
		self.entire_text = re.sub("(\s)+([MDSJ][rstq]?)(\.)",r"\1\2 ",self.entire_text,flags=re.I)
		self.entire_text = re.sub("\"|,|:|-"," ",self.entire_text)
		self.entire_text = re.sub("[.][.]+"," ",self.entire_text)
		#find strings inside brackets using non-greedy match,remove and add them as separate sentence
		pattern = re.compile("(\(.*?\))")
		inside_paranthesis = pattern.findall(self.entire_text)
		#print(inside_paranthesis)
		self.entire_text = pattern.sub(" ",self.entire_text)
		#add end token at the end of sentences
		pattern = re.compile("\.(\s)+|[!]+(\s)+|(\?)+(\s)+|\)(\s)+",re.IGNORECASE)
		self.entire_text = pattern.sub(end_token,self.entire_text)
		#print(self.entire_text)

if __name__ == '__main__':
	fd = open("/home/neel/ngram data/en_US/en_US.blogs.txt")
	#number of grams to be fetched from the text file
	n = 2
	x = Ngram(fd)
	x.cleanAndInsertEndToken(" endtoken ")
	x.readNGrams(n)
	#number of ngrams to print
	p = 500
	#x.printNGrams(p)
