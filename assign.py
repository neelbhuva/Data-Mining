import pandas as pd
import numpy as np
import plotly.plotly as py
import plotly.graph_objs as go
import math

def normalize_continuous():	
	age = np.array(df['age']);
	fnlwgt = np.array(df['fnlwgt']);
	education_cat = np.array(df['education_cat']);
	hour_per_week = np.array(df['hour_per_week']);

	missing_data('occupation');

	mean_age = np.mean(age);
	mean_fnlwgt = np.mean(fnlwgt);
	mean_education_cat = np.mean(education_cat);
	mean_hour_per_week = np.mean(hour_per_week);
	#print(mean_age);
	std_age = np.std(age);
	std_fnlwgt = np.std(fnlwgt);
	std_education_cat = np.std(education_cat);
	std_hour_per_week = np.std(hour_per_week);
	#print(std_age);
	normalized_age = [];
	normalized_fnlwgt = [];
	normalized_education_cat = [];
	normalized_hour_per_week = [];

	for i in range(0,len(age)-1):
		normalized_age.append((age[i] - mean_age)/std_age);
		normalized_fnlwgt.append((fnlwgt[i] - mean_fnlwgt)/std_fnlwgt);
		normalized_education_cat.append((education_cat[i] - mean_education_cat)/std_education_cat);
		normalized_hour_per_week.append((hour_per_week[i] - mean_hour_per_week)/std_hour_per_week);
	#print(normalized_hour_per_week);
	#print(normalized_fnlwgt);
	#boxplot(normalized_age,normalized_fnlwgt,normalized_education_cat,normalized_hour_per_week);

def normalize_nominal(labels):
	for i in labels:
		column = df[i]
		unique_column = set(column)
		unique_column.discard(' ?')
		column_map = {};
		t = 0;
		for j in unique_column:
			column_map[j] = t;
			t = t + 1;
		print(column_map)
		for k in range(0,len(column)):
			if(column[k] == " ?"):
				continue
			df[i][k] = column_map[column[k]]

def boxplot(y0,y1,y2,y3):
	#plotly.tools.set_credentials_file(username='neelbhuva', api_key='oceBv21aIoEkkU2YcCLg')
	age = go.Box(y=y0)
	fnlwgt = go.Box(y=y1)
	edu_cat = go.Box(y=y2)
	hr_per_week = go.Box(y=y3)
	data = [age, fnlwgt, edu_cat, hr_per_week]
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
	print(age_group)
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

if __name__ == '__main__':
	global df 
	df = pd.read_csv('income_tr.csv');
	#histoplot();
	#normalize_continuous();
	nominal_labels = ['workclass','education','marital_status','occupation','relationship','race','gender','native_country'];
	normalize_nominal(nominal_labels);
	print(df)