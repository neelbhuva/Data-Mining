from collections import defaultdict
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np

def tokenize(file):
	print("Tokenizing...")
	wl = []
	h = 0
	with open(file, 'r', encoding='utf-8') as f:
		for line in f:
			h += 1
			if(h%400000 == 0):
				print(h)
			#line = line.lower()
			#line = self.cleanLine(line,end_token)
			line = line.split()
			wl.extend(line)
	return wl

def histo(example_list,n):
	word = []
	frequency = []
	for i in range(len(example_list)):
		word.append(example_list[i][0])
		frequency.append(example_list[i][1])
	indices = np.arange(len(example_list))
	plt.bar(indices, frequency, color='r')
	plt.xticks(indices, word, rotation='vertical')
	plt.tight_layout()
	plt.ylabel("Frequency")
	plt.title(str(n) + " gram counts")
	plt.show()

def count(n,p,wl):
	n_grams = [' '.join(wl[i:i+n]) for i in range(len(wl)-n+1)]
	print("Counting : " + str(n) + " grams")
	count = Counter(n_grams)
	a = count.most_common()[:p]
	print(a)
	return a
	

if __name__ == '__main__':
	file = "/home/neel/ngram data/en_US/en_US.blogs.txt"
	wl = tokenize(file)
	n = 1
	p = 15
	g = count(n,p,wl)
	histo(g,n)
	# print(n_grams_count)