import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import random as rd
from sklearn.cluster import KMeans

def getEucledian(a,b):
    #print(a,b)
    total = 0;
    for i in range(0,len(a)):
        diff = b[i] - a[i];
        total += diff * diff;
    return np.sqrt(total)

def normContinuousAttributes(df,labels):
    for i in labels:
        df[i] = df[[i]].apply(lambda x : (x - np.min(x))/(np.max(x) - np.min(x)))
    return df


def clusterSSE(x,k_clusters,k_centers):
    total = {} 
    for key,value in k_clusters.items():
        s = 0
        center = k_centers[key]
        for i in value:
            s = s + math.pow(getEucledian(x[i],center),2)
        total[key] = s
    return total 

def overallSSE(cluster_sse):
    s = 0
    for key,value in cluster_sse.items():
        s = s + cluster_sse[key]
    return s

def SSB(x,k_clusters,k_centers):
    c = getMeanUsingIndex(x,list(range(0,len(x))))
    keys = list(k_centers.keys())
    s =  0
    for j in keys:
        t = len(k_clusters[j])
        s = s + (t * math.pow(getEucledian(k_centers[j],c),2))
    return s

def getMeanUsingIndex(x,indices):
    total = []
    for i in x[0]:
        total.append(0)
    #print(total)
    for i in indices:
        for j in range(0,len(total)):
            total[j] = total[j] + x[i][j]
    total = [f/len(indices) for f in total]
    return (total)


def getOutFrame(k_clusters):
    columns = ["Row ID","Cluster"]
    df_out = pd.DataFrame() 
    for key,values in k_clusters.items():
        t = []
        for i in values:
            t.append(key)
        df = pd.DataFrame({"Row ID" : values, "Cluster" : t})
        df_out = df_out.append(df)
        df_out = df_out.sort_values("Row ID",ascending=True)
    return df_out


def plotClusters(x,k_clusters,title,xlabel,ylabel):
    fig1 = plt.figure(1)
    for key,value in k_clusters.items():
        c = [x[index] for index in value]
        #print(c)
        plt.scatter(*zip(*c),label="Cluster " + str(key))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.show()


def getTrueClusters(df,label):
    k_clusters = {}
    k_centers = {}
    clusters = set(df[label])
    #print(clusters)
    df_temp = df.drop(["ID",label],axis=1)
    x = df_temp.values.tolist()
    for i in clusters:
        a = df.loc[df[label] == i].index
        #print(a)
        k_clusters[i] = list(a)
        k_centers[i] = getMeanUsingIndex(x,list(a))
    #print(k_clusters)
    return k_clusters,k_centers

def crossTabMatrix(k_clusters,true_clusters):
    df = pd.DataFrame()
    t = []
    for key,value in k_clusters.items():
        for a,b in true_clusters.items():
            b3 = [val for val in value if val in b]
            t.append(len(b3))
    t = np.reshape(t,(len(k_clusters),len(true_clusters)))
    columns = list(true_clusters.keys())
    df_temp = pd.DataFrame(data=list(k_clusters.keys()),columns=["Cluster"])
    df = pd.DataFrame(data=t,columns=columns)
    df = pd.concat([df_temp,df],axis=1)
    df = df.set_index('Cluster')
    return df

def readWine(file):
	df = pd.read_csv(file)
	df = df.drop(["class"],axis=1)
	#df['quality'] = df['quality'].map({3:1,4:2,5:3,6:4,7:5,8:6})
	labels = ["fx_acidity","resid_sugar","free_sulf_d","tot_sulf_d","pH","alcohol"]
	df = normContinuousAttributes(df,labels)
	true_clusters,true_centers = getTrueClusters(df,"quality")
	df = df.drop(["ID","quality"],axis=1)
	x = df.values.tolist()
	return x,true_clusters,true_centers

def readTwoDimHard(file):
	df_tdh = pd.read_csv(file)
	true_clusters,true_centers = getTrueClusters(df_tdh,"cluster")
	df_tdh = df_tdh.drop(["ID","cluster"],axis=1)
	x = df_tdh.values.tolist()
	return x,true_clusters,true_centers

def convertListToDict(a):
	d = {}
	j = 1
	for i in a:
		d[j] = list(i)
		j = j + 1
	return d

def getIndexFromLabel(labels):
	d = {}
	l = set(labels)
	labels = list(labels)
	for j in l:
		d[j] = [i for i, x in enumerate(labels) if x == j]
	return d

def offTheShelf(x,true_clusters,true_centers,k):
	# Number of clusters
	kmeans = KMeans(n_clusters=k)
	# Fitting the input data
	kmeans = kmeans.fit(x)
	# Getting the cluster labels
	labels = kmeans.predict(x)
	labels = [t+1 for t in labels]
	labels = getIndexFromLabel(labels)
	# Centroid values
	centroids = kmeans.cluster_centers_
	centroids = convertListToDict(centroids)
	return centroids,labels

def evaluationMetrics(x,true_clusters,true_centers,k_clusters,k_centers):	
	sse = clusterSSE(x,k_clusters,k_centers)
	print("Cluster SSE : " + str(sse))
	overall_sse = overallSSE(sse)
	print("Overall SSE : " + str(overall_sse))
	#t.append(overall_sse)
	ssb = SSB(x,k_clusters,k_centers)
	print("SSB : " + str(ssb))
	#t1.append(ssb)
	return sse,overall_sse,ssb

def plot(y,k_list,ylabel,title):
    my_xticks = k_list
    s = list(range(0,len(k_list)))
    plt.xticks(s, my_xticks)
    print(s,y)
    plt.plot(s,y)
    plt.xlabel("k")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.show()

if __name__ == '__main__':
	wine = True
	x = []
	t = []
	t1 = []
	if(wine):
		x,true_clusters,true_centers = readWine("wine.csv")
	else:
		x,true_clusters,true_centers = readTwoDimHard("TwoDimHard.csv")
	#print(true_clusters)
	best_clusters = {}
	best_centers = {}
	best_sse = 300
	best_cluster_sse = {}
	best_ssb = 0
	k = int(input("Enter number of clusters : "))
	n = 12
	n1 = 2
	for i in range(n1,n):
		print("Iteration : " + str(i))
		k_centers,k_clusters = offTheShelf(x,true_clusters,true_centers,k)
		sse,overall_sse,ssb = evaluationMetrics(x,true_clusters,true_centers,k_clusters,k_centers)
		t.append(overall_sse)
		t1.append(ssb)
		if(i == 4):
			best_sse = overall_sse
			best_clusters = k_clusters
			best_centers = k_centers
			best_ssb = ssb
			best_cluster_sse = sse
	# print(centroids)
	# print(labels)
	true_sse = clusterSSE(x,true_clusters,true_centers)
	print("True Cluster SSE : " + str(true_sse))
	true_overall_sse = overallSSE(true_sse)
	print("True Overall SSE : " + str(true_overall_sse))
	true_ssb = SSB(x,true_clusters,true_centers)
	print("True SSB : " + str(true_ssb))
	
	# df_cross = crossTabMatrix(k_clusters,true_clusters)
	# print(df_cross)
	# # plotClusters(x,k_clusters,"Clusters with K = " + str(k),"x1","x2")
	# # plotClusters(x,true_clusters,"True Clusters with K = " + str(len(true_centers)),"x1","x2")
	df_cross = crossTabMatrix(best_clusters,true_clusters)
	print(df_cross)
	plot(t,list(range(n1,n)),"Overall SSE","Overall SSE vs K")
	plot(t1,list(range(n1,n)),"SSB","SSB vs K")