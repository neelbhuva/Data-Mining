import pandas as pd
import numpy as np
import plotly.plotly as py
import plotly.graph_objs as go
import math
import matplotlib.pyplot as plt

def normalize_continuous():	
	age = np.array(df['age']);
	fnlwgt = np.array(df['fnlwgt']);
	hour_per_week = np.array(df['hour_per_week']);

	mean_age = np.mean(age);
	mean_fnlwgt = np.mean(fnlwgt);
	mean_hour_per_week = np.mean(hour_per_week);
	#print(mean_age);
	std_age = np.std(age);
	std_fnlwgt = np.std(fnlwgt);
	std_hour_per_week = np.std(hour_per_week);
	#print(std_age);
	normalized_age = [];
	normalized_fnlwgt = [];
	normalized_hour_per_week = [];

	for i in range(0,len(age)-1):
		normalized_age.append((age[i] - mean_age)/std_age);
		normalized_fnlwgt.append((fnlwgt[i] - mean_fnlwgt)/std_fnlwgt);
		normalized_hour_per_week.append((hour_per_week[i] - mean_hour_per_week)/std_hour_per_week);
	df['age'] = normalized_age;
	df['fnlwgt'] = normalized_fnlwgt;
	df['hour_per_week'] = normalized_hour_per_week;
	#boxplot(normalized_age,normalized_fnlwgt,normalized_education_cat,normalized_hour_per_week);

def normalize_nominal(labels):
	for i in labels:
		column = df[i]
		unique_column = set(column)
		unique_column.discard(' ?')
		column_map = {};
		t = 0;
		#print(df[i].value_counts())
		descending_list = df[i].value_counts().index.tolist()
		for j in descending_list:
			column_map[j] = t;
			t = t + 1;
		#print(column_map)
		for k in range(0,len(column)):
			if(column[k] == " ?"):
				continue
			df[i][k] = column_map[column[k]]

def boxplot(labels):
	#plotly.tools.set_credentials_file(username='neelbhuva', api_key='oceBv21aIoEkkU2YcCLg')
	data = [];
	for i in labels:
		trace = go.Box(y=df[i])
		data.append(trace)
	py.plot(data)

def missing_data(label):
	column = df[label]
	#print(column[57])
	unique_column = set(column)	
	unique_column.discard(' ?')
	#print(unique_column)
	age = np.array(df['age'])
	age_group = {};
	for i in range(1,11):
		age_group[str(i)] = {};
	for i in unique_column:
		#print(i);
		for j in range(1,11):
			age_group[str(j)][i] = 0;
	for i in range(0,len(column)):
		if(column[i] == ' ?'):
			continue
		age_index = int(age[i]/10)+1
		age_group[str(age_index)][column[i]] = 1 + age_group[str(age_index)][column[i]];
	#print(age_group)
	#now find the most repeating workclass in the age group of missing data and replace the value
	for i in range(0,len(column)):
		if(column[i] == " ?"):
			age_index = int(age[i]/10) + 1
			missing_class = find_repeating_class(age_group,age_index);
			df[label][i] = missing_class;
	#print(df[label][57]) 

def find_repeating_class(age_group,age_index):
	max_value = 0;
	for key,value in age_group[str(age_index)].items():
		if(value > max_value):
			max_value = value;
			desired_class = key;
	return desired_class

def histoplot():
	x = df['fnlwgt']
	data = [go.Histogram(x=x)]
	py.plot(data, filename='fnlwgt')

def scatterplot(x,y):
	trace = go.Scatter(x = x, y = y, mode = 'markers')
	data = [trace]
	# Plot and embed in ipython notebook!
	plot_url = py.plot(data, filename='basic-scatter');

def missing_data_native_country():
	print(df['native_country'][404])
	race_native_map = {};
	native_country = df['native_country']
	race = df['race']
	unique_native = set(df['native_country'])
	unique_native.discard(' ?')
	unique_race = set(df['race'])
	for i in unique_race:
		race_native_map[i] = {};
		for j in unique_native:
			race_native_map[i][j] = 0;
	for i in range(0,len(native_country)):
		if(native_country[i] == ' ?'):
			continue
		race_native_map[race[i]][native_country[i]] = 1 + race_native_map[race[i]][native_country[i]]
	print(race_native_map)
	for i in range(0,len(native_country)):
		if(native_country[i] == " ?"):
			missing_class = find_repeating_country(race_native_map,race[i]);
			df['native_country'][i] = missing_class;
	print(df['native_country'][404])
def find_repeating_country(race_native_map,race):
	max_value = 0;
	for key,value in race_native_map[race].items():
		if(value > max_value):
			max_value = value;
			desired_race = key;
	return desired_race

def print_dict(dict):
	for key, value in dict:
		print("")
if __name__ == '__main__':
	global df 
	df = pd.read_csv('income_tr.csv');
	#histoplot();
	#scatterplot(df['workclass'],df['class'])
	#missing_data('marital_status');
	missing_data_native_country()
	#normalize_continuous();
	nominal_labels = ['workclass','education','marital_status','occupation','relationship','race','gender','native_country'];
	#nominal_labels = ['marital_status'];
	#normalize_nominal(nominal_labels);
	#print(df)
	boxplot_labels = ['age','workclass','education','marital_status','occupation']
	#boxplot(boxplot_labels)