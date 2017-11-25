import math
import numpy as np
from nltk import ngrams
import regex as re

def cleanAndInsertEndToken(self,end_token):
	#convert to lowecase
	entire_text = self.entire_text.lower()
	pattern = re.compile("\s+[a-zA-Z][a-zA-Z]\.\s+")
	two_char = pattern.findall(self.entire_text)
	print(set(two_char))
	#2 & 3 char words like st.,Mr.,Dr.,sq.,etc. ending with . and a newline
	entire_text = re.sub("(\s)+([a-zA-Z]{1,3})(\.)(\n)",r"\1\2 "+end_token,self.entire_text,flags=re.I)		
	#2 & 3 character words like st.,Mr.,Dr.,sq. ending with . and not a newline
	entire_text = re.sub("(\s)+([a-zA-Z]{1,3})(\.)(\s)?",r"\1\2 ",self.entire_text,flags=re.I)
	entire_text = re.sub("\"|,|:|-"," ",self.entire_text)
	entire_text = re.sub("[.][.]+"," ",self.entire_text)
	#find strings inside brackets using non-greedy match,remove and add them as separate sentence
	pattern = re.compile("(\(.*?\))")
	inside_paranthesis = pattern.findall(self.entire_text)
	#print(inside_paranthesis)
	entire_text = pattern.sub(" ",self.entire_text)
	#add end token at the end of sentences
	pattern = re.compile("\.(\s)+|[!]+(\s)+|(\?)+(\s)+|\)(\s)+",re.IGNORECASE)
	entire_text = pattern.sub(end_token,self.entire_text)
	#print(self.entire_text)

if __name__ == '__main__':
	fd = open("/home/neel/ngram data/en_US/en_US.blogs.txt")
	global
	entire_text = fd.read()
	#number of grams to be fetched from the text file
	n = 2
	cleanAndInsertEndToken(" endtoken ")
	#number of ngrams to print
	p = 500
	#x.printNGrams(p)