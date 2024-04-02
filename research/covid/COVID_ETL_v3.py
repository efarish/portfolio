#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import sqlite3
import numpy as np
#get_ipython().system('pip install pyunpack')
#get_ipython().system('pip install patool')
from urllib import request
from pyunpack import Archive
import os

'''
Utility method to run SQL SELECT statments. 
An array of arrays is returned.
header - header row for table.
sqlStmt - SQL to execute against reids.db.
'''
def execStatement(conn,header,sqlStmt):
    curs = conn.cursor()
    rows = []
    if header is not None:
        rows.append(list(header))
    try:
        for row in curs.execute(sqlStmt):
            rows.append(list(row))
    except Exception as e: 
        print(e)
    curs.close()
    return rows

def createCOVIDDB():
    # TODO REMOVE THIS TO DOWNLOAD SOURCE FILE
    #os.makedirs("./data",exist_ok=True)
    #url = "https://github.com/network-and-Data-Science-IUT/covid-19/raw/master/" +\
    #  "USA%20covid-19%20data/imputed-data.rar"
    #request.urlretrieve(url, "./data/imputed-data.rar")
    #Archive('./data/imputed-data.rar').extractall('./data')

    conn = sqlite3.connect('./data/COVID_DATA.db')

    url = "./data/imputed-data.csv"
    df = pd.read_csv(url,usecols =["county_fips","covid_19_deaths","percent_of_smokers",
                               "percent_of_diabetes","median_household_income","less_than_high_school_diploma",
                              "high_school_diploma_only","some_college_or_higher","population_density",
                              "social_distancing_total_grade","social_distancing_visitation_grade",
                               "social_distancing_encounters_grade","social_distancing_travel_distance_grade",
                               "percent_of_vaccinated_residents",
                               "age_0_4","age_5_9","age_10_14","age_15_19","age_20_24","age_25_29","age_30_34",
                               "age_35_39","age_40_44","age_45_49","age_50_54","age_55_59","age_60_64","age_65_69",
                               "age_70_74","age_75_79","age_80_84","age_85_or_higher",
                               "total_population", "workplaces_mobility_percent_change"])
    grades = [('A+', 4.0), ('A', 4.0), ('A-', 3.7), ('B+',3.3), ('B',3.0), ('B-',2.7), ('C+',2.3), ('C',2.0),\
          ('C-',1.7),('D+',1.3),('D',1.0),('D-',0.7),('F',0.0)]
    df['social_distance_gpa'] = df['social_distancing_total_grade'].map(dict(grades))
    df['social_distance_gpa_visitation'] = df['social_distancing_visitation_grade'].map(dict(grades))
    df['social_distance_gpa_encounters'] = df['social_distancing_encounters_grade'].map(dict(grades))
    df['social_distance_gpa_travel'] = df['social_distancing_travel_distance_grade'].map(dict(grades))
    df.to_sql('STAGING_COVID', conn, if_exists='replace', index = False, chunksize = 10000)

    grpData = """
    CREATE TABLE COVID_DATA AS SELECT county_fips, sum(covid_19_deaths) covid_19_deaths, 
    MAX(percent_of_smokers) percent_of_smokers, 
    MAX(percent_of_diabetes) percent_of_diabetes, 
    MAX(median_household_income) median_household_income, 
    MAX(less_than_high_school_diploma) less_than_high_school_diploma, 
    MAX(high_school_diploma_only) high_school_diploma_only, 
    MAX(some_college_or_higher) some_college_or_higher, 
    MAX(population_density) population_density, 
    AVG(social_distance_gpa) social_distance_gpa,
    AVG(social_distance_gpa_visitation) social_distance_gpa_visitation,
    AVG(social_distance_gpa_encounters) social_distance_gpa_encounters,
    AVG(social_distance_gpa_travel) social_distance_gpa_travel,
    MAX(percent_of_vaccinated_residents) percent_of_vaccinated_residents, 
    MAX(age_0_4) age_0_4, MAX(age_5_9) age_5_9, 
    MAX(age_10_14) age_10_14, MAX(age_15_19) age_15_19, MAX(age_20_24) age_20_24, MAX(age_25_29) age_25_29, 
    MAX(age_30_34) age_30_34, MAX(age_35_39) age_35_39, MAX(age_40_44) age_40_44, MAX(age_45_49) age_45_49, 
    MAX(age_50_54) age_50_54, MAX(age_55_59) age_55_59, MAX(age_60_64) age_60_64, MAX(age_65_69) age_65_69, 
    MAX(age_70_74) age_70_74, MAX(age_75_79) age_75_79, MAX(age_80_84) age_80_84, MAX(age_85_or_higher) age_85_or_higher, 
    MAX(total_population) total_population,
    AVG(workplaces_mobility_percent_change) workplaces_mobility_percent_change
    FROM STAGING_COVID GROUP BY county_fips;
    """
    result = execStatement(conn,None,"DROP TABLE IF EXISTS COVID_DATA;")
    result = execStatement(conn,None,grpData)

    conn.close()
    
#createCOVIDDB()
