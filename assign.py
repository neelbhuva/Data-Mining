import pandas as pd
import numpy as np
def normalize():
	df = pd.read_csv('income_tr.csv');
	age = df['age'];
	fnlwgt = df['fnlwgt'];
	education_cat = df['education_cat'];
	hour_per_week = df['hour_per_week'];
	#print(fnlwgt);
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
	print(normalized_hour_per_week);
if __name__ == '__main__':
	normalize();
