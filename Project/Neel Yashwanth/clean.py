import math
import numpy as np
import regex as re
from itertools import islice

def clean(entire_text,end_token,n):
		entire_text = entire_text.lower()
		#single apostrophes
		entire_text = re.sub(" ' |(\w)+'|'(\w)+"," ",entire_text,flags=re.I)
		#charac like / with spaced around
		entire_text = re.sub(" / "," ",entire_text,flags=re.I)
		#words like don't, won't, aren't it's...
		#entire_text = re.sub("(can't)|(ain't)|(won't)|(shan't)",r" \1 ",entire_text,flags=re.I)
		entire_text = re.sub("([a-zA-Z])n't",r" \1 not ",entire_text,flags=re.I)
		#words like it's
		entire_text = re.sub("(it)'s",r" \1 is ",entire_text,flags=re.I)
		#single words or numbers inside paranthesis
		entire_text = re.sub("\((\s)*(\w)+(\s)*\)",r" \2 ",entire_text)
		entire_text = re.sub("\((\s)*([0-9])+(\s)*\)",r" \2 ",entire_text)
		#replace points such as 1), 23) ...with space
		entire_text = re.sub("(\d)+\)|(\d)+\)\.|(\d)+\.\)"," ",entire_text)
		#do not split compound words like e-email
		entire_text = re.sub("(\s)+([a-zA-Z]{1,2})-([a-zA-Z]+)",r" \2\3 ",entire_text)
		#remove smileys
		entire_text = re.sub("<3|:\)|:\)|:D|:P"," ",entire_text)
		#replace ampersand with and
		entire_text = re.sub("&"," and ",entire_text,flags=re.I)
		#2 & 3 char words like st.,Mr.,Dr.,sq.,etc. ending with . and a newline
		entire_text = re.sub("(\s)+([a-zA-Z]{1,3})(\.)(\n)",r"\1\2 "+end_token,entire_text,flags=re.I)		
		#2 & 3 character words like st.,Mr.,Dr.,sq. ending with . and not a newline
		entire_text = re.sub("(\s)+([a-zA-Z]{1,3})(\.)(\s)?",r"\1\2 ",entire_text,flags=re.I)
		#replace double quotes, commas, colon ... with space
		entire_text = re.sub("\"|,|:|-|\'"," ",entire_text)
		#multiple dots like Hmm...
		entire_text = re.sub("[.][.]+"," ",entire_text)
		
		# pattern = re.compile("\s+[a-zA-Z][a-zA-Z]\.")
		# two_char = pattern.findall(entire_text)
		# print(set(two_char))
		#URL
		entire_text = re.sub("http[s]?:.*?(\s)+|www\.(.*?)(\s)+",r"<URL>",entire_text,flags=re.I)
		#dates
		entire_text = re.sub("(jan|feb|mar|apr|may|jun|jul|aug|sept|oct|nov|dec)(\.)?(\s)?(\d){1,2}",r" \1 <D> ",entire_text,flags=re.I)
		entire_text = re.sub("(january|february|march|april|may|june|july|august|september|october|november|december)(\.)?(\s)?(\d){1,2}",r" \1 <D> ",entire_text,flags=re.I)
		#year
		entire_text = re.sub("(jan|feb|mar|apr|may|jun|jul|aug|sept|oct|nov|dec)(\.)?(\s)?(\d){4,4}",r" \1 <Y> ",entire_text,flags=re.I)
		entire_text = re.sub("(january|february|march|april|may|june|july|august|september|october|november|december)(\.)?(\s)?(\d){4,4}",r" \1 <D> ",entire_text,flags=re.I)
		#currencies line $4.50
		entire_text = re.sub("([$€£]\d+(\.?\d{0,5})?)|(\d+(\.?\d{0,5})?[$€£])","<C>",entire_text)
		#currency symbols like $$$
		entire_text = re.sub("[$€£]+"," money ",entire_text)

		#replace single quotes around words or sentences
		entire_text = re.sub("(\')(.*?)(\')",r" \2 ",entire_text)
		#find strings inside paranthesis using non-greedy match and remove them
		pattern = re.compile("(\(.*?\))")
		#inside_paranthesis = pattern.findall(entire_text)
		#print(inside_paranthesis)
		entire_text = pattern.sub(" ",entire_text)
		#single parantheses
		entire_text = re.sub("(\s)+\((\w)+|(\s)+(\w)+\(| \( |(\s)+\)(\w)+|(\s)+(\w)+\)| \) "," ",entire_text)
		#expressions such as 4/3 which means 4 or 3
		entire_text = re.sub("(\s+)(\d+)/(\d+)(\s+)",r"\1\2 or \3\4",entire_text)
		entire_text = re.sub("(\s+)(\w+)/(\w+)(\s+)",r"\1\2 or \3\4",entire_text)
		#add end token at the end of sentences
		pattern = re.compile("\.(\s)*|[!]+(\s)*|(\?)+(\s)*|\)(\s)+",re.IGNORECASE)
		entire_text = pattern.sub(end_token,entire_text)
		entire_text = "<s> "*n + entire_text
		#print(entire_text)
		#print("Done")
		return entire_text


def readInput(N,file,of,test_file):
	c = 0
	of_test = open(test_file,'w',encoding='utf-8')
	N_train = int(0.9 * N)
	with open(file, 'r',encoding='utf-8') as infile:
		lines_gen = islice(infile, N)	#read N lines from file
		for line in lines_gen:
			new_line = clean(line," </s> ",n)	#clean each line using regex.sub
			new_line += '\n'
			c = c+1
			if(c <= N_train):
				of.write(new_line)
			if(c >= N_train):
				of_test.write(new_line)
			if(c%10000 == 0):
				print(c)
	of_test.close()

if __name__ == '__main__':
	s = "twitter"
	y = str(20)
	file = "/home/roy.174/ngram data/en_US/en_US." + s + ".txt"
	o_file ="/home/roy.174/ngram data/en_US/train_" + s + y + ".txt"
	test_file = "/home/roy.174/ngram data/en_US/test_" + s + y + ".txt"
	of = open(o_file,'w',encoding='utf-8')
	n = 4
	start_token = "<s> "*n
	N = 2360148
	readInput(N,file,of,test_file)
	of.close()
