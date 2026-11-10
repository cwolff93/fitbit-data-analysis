import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

#Import the necessary libraries
import plotly.express as px
import plotly
import matplotlib.pyplot as plt

#Read the merged daily activity file
df1 = pd.read_csv("../input/datasets/arashnic/fitbit/mturkfitbit_export_3.12.16-4.11.16/Fitabase Data 3.12.16-4.11.16/dailyActivity_merged.csv")
df2 = pd.read_csv("../input/datasets/arashnic/fitbit/mturkfitbit_export_4.12.16-5.12.16/Fitabase Data 4.12.16-5.12.16/dailyActivity_merged.csv")

#Analyze the first five results of the data frame to check how the data is displayed
df1.head()
df2.head()

#Check if there's missing data
df1.isnull().sum()
df2.isnull().sum()

#Check data types and the amount of lines per column
df1.info()
df2.info()

#Concatenate both data frames to get all information in the studied period
df = pd.concat([df1, df2], axis=0, join='outer', ignore_index=True)
df

#Convert the date to datetime specifying the format
df['ActivityDate'] = pd.to_datetime(df['ActivityDate'], format='%m/%d/%Y')

#Create new columns to add all active minutes categories, total minutes, and a category in hours
df['TotalActiveMinutes'] = df['VeryActiveMinutes'] + df['FairlyActiveMinutes'] + df['LightlyActiveMinutes']
df['TotalMinutes'] = df['TotalActiveMinutes'] + df['SedentaryMinutes']
df['TotalActiveHours'] = round(df['TotalActiveMinutes']/60,2)
df['SedentaryHours'] = round(df['SedentaryMinutes']/60,2)

#Create new column with day of the week logged
df["DayOfWeek"] = df["ActivityDate"].dt.day_name()

#Change column order
df = df[['Id', 'ActivityDate', 'DayOfWeek', 'Calories', 'TotalSteps', 'TotalDistance', 'TrackerDistance',
       'LoggedActivitiesDistance', 'VeryActiveDistance', 'ModeratelyActiveDistance', 'LightActiveDistance',
       'SedentaryActiveDistance', 'VeryActiveMinutes', 'FairlyActiveMinutes', 'LightlyActiveMinutes', 'TotalActiveMinutes', 
       'TotalActiveHours', 'SedentaryMinutes', 'SedentaryHours','TotalMinutes']]

#Check the top 5 lines after all changes
df.head()

#Describing the numeric information to understand the data. 
#Used to check if any of the total minutes/sedentary minutes entries surpass a full day (1440 minutes)
df.describe().T

#Checking for irregularities in the data
df[df['TotalMinutes'] <= 10]

#Identifying that close to 11% of Active Hours are equal to 0
df['TotalActiveHours'].value_counts(normalize=True)

#Understanding the difference between the distance columns
df[['TotalDistance', 'TrackerDistance', 'LoggedActivitiesDistance']]

#Checking the LoggedActivitesDistance since it seems to contains many zero values
df['LoggedActivitiesDistance'].value_counts()

#Checking which users usually log their distances
df['Id'][df['LoggedActivitiesDistance'] > 0.0].value_counts()

#Checking user frequency. Most users utilized the fitbit for at least 30 entries.
df['Id'].value_counts()

#Checking the amount of unique users.
df['Id'].nunique()

#Checking which days of the week are most logged
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
df['DayOfWeek'].value_counts().reindex(day_order)

#Detailing how many active hours are logged in each day of the week
hoursperweek = df.groupby(['DayOfWeek'])['TotalActiveHours'].sum().reindex(day_order)

plt.figure(figsize=(10,6))
bars = plt.bar(hoursperweek.index, hoursperweek, width=0.5, zorder=3)
plt.grid(alpha=1, zorder=0)
plt.bar_label(bars, padding=3)
plt.title('Active Hours per Day of the Week')
plt.ylabel('Total Active Hours') 
plt.xlabel('Day of the Week')  
plt.show()

df.groupby(['DayOfWeek'])[['LightActiveDistance', 'ModeratelyActiveDistance', 'VeryActiveDistance', 'TotalDistance']].sum().sort_values(by='TotalDistance', ascending=False)
df.groupby(['DayOfWeek'])[['LightActiveDistance', 'ModeratelyActiveDistance', 'VeryActiveDistance', 'TotalDistance']].median().sort_values(by='TotalDistance', ascending=False)

df.groupby(['DayOfWeek'])[['LightlyActiveMinutes', 'FairlyActiveMinutes', 'VeryActiveMinutes', 'TotalActiveMinutes']].sum().sort_values(by='TotalActiveMinutes', ascending=False)
df.groupby(['DayOfWeek'])[['LightlyActiveMinutes', 'FairlyActiveMinutes', 'VeryActiveMinutes', 'TotalActiveMinutes']].median().sort_values(by='TotalActiveMinutes', ascending=False)

#Sorting users by the most active hours logged
df.groupby('Id')['TotalActiveHours'].sum().sort_values(ascending=False)

#There are not as many outliers for users that logged above 160 hours total
df_high_active = df.groupby('Id').filter(lambda x: x['TotalActiveHours'].sum() > 160)
px.box(df_high_active, y=['LightlyActiveMinutes', 'FairlyActiveMinutes', 'VeryActiveMinutes'], hover_data=['FrequentId'], color='DayOfWeek')

id_counts = df['Id'].value_counts()
df.loc[:, 'FrequentId'] = df['Id'].map(id_counts >= 43)
#There are lots of outliers for moderately and very activer distances, since most users logged light active distances.
px.box(df, y=['LightActiveDistance', 'ModeratelyActiveDistance', 'VeryActiveDistance', 'TotalDistance'], color='FrequentId')

#Analysing users that aren't as active
df_active = df.groupby('Id').filter(lambda x: x['TotalActiveHours'].sum() < 160)
df_active.groupby('Id')[['LightlyActiveMinutes', 'FairlyActiveMinutes','VeryActiveMinutes', 'TotalActiveMinutes']].sum().sort_values(by='TotalActiveMinutes', ascending=False)

#Distribution of active minutes between users
grouped = df.groupby('Id')[['LightlyActiveMinutes', 'FairlyActiveMinutes','VeryActiveMinutes', 'TotalActiveMinutes']].sum()
columns = ['LightlyActiveMinutes', 'FairlyActiveMinutes','VeryActiveMinutes']

for col in columns:
    grouped[col] = round((grouped[col]/grouped['TotalActiveMinutes']) * 100, 2)
    
print(grouped[columns].sort_values(by='LightlyActiveMinutes', ascending=False))

#Percentage of time spent being active and being sedentary for each Id
grouped = df.groupby('Id')[['TotalActiveMinutes', 'SedentaryMinutes', 'TotalMinutes']].sum()
columns = ['TotalActiveMinutes', 'SedentaryMinutes']

for col in columns:
    grouped[col] = round((grouped[col]/grouped['TotalMinutes']) * 100, 2)
    
grouped_sorted = grouped[columns].sort_values(by='TotalActiveMinutes', ascending=False)
print(grouped_sorted)
