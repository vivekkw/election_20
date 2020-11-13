import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
import numpy as np
import pandas as pd

records = pd.DataFrame(columns=['state', 'county', 'votes_16', 'votes_clinton_16', 'votes_trump_16',
       'votes_dem_12', 'votes_rep_12', 'dem16_pct', 'rep16_pct', 'dem12_pct',
       'rep12_pct'])
counties_per_state = dict()
states = ["Georgia","Arizona","Pennsylvania","Wisconsin","Michigan"]
states_short = ['GA','AZ','PA','WI','MI']

for state_short,state in zip(states_short,states):
    query = "https://public.opendatasoft.com/api/records/1.0/search/?dataset=usa-2016-presidential-election-by-county&q=&rows=1000&facet=state&facet=county&refine.state=" + state
    response = requests.get(query)
    
    counties = len(response.json()['records'])
    counties_per_state[state_short] = counties

    for record in response.json()['records']:
        record_dict = pd.DataFrame(columns=['state', 'county', 'votes_16', 'votes_clinton_16', 'votes_trump_16',
                                            'votes_dem_12', 'votes_rep_12', 'dem16_pct', 'rep16_pct', 'dem12_pct',
                                            'rep12_pct'])
        record_dict['state'] = [record['fields']['st']]
        split_county = record['fields']['county'].split(" ")
        len_county = len(split_county)
        if len_county == 3:
            record_dict['county'] = split_county[0]
        else:
            record_dict['county'] = " ".join(split_county[0:(len_county - 2)])
        record_dict['votes_16'] = int(record['fields']['votes'])
        record_dict['votes_clinton_16'] = int(record['fields']['votes16_clintonh'])
        record_dict['votes_trump_16'] = int(record['fields']['votes16_trumpd'])
        record_dict['votes_dem_12'] = int(record['fields']['dem12'])
        record_dict['votes_rep_12'] = int(record['fields']['rep12'])
        record_dict['dem16_pct'] = float(record['fields']['dem16_frac'])
        record_dict['rep16_pct'] = float(record['fields']['rep16_frac'])
        record_dict['dem12_pct'] = float(record['fields']['dem12_frac'])
        record_dict['rep12_pct'] = float(record['fields']['rep12_frac'])
        records = records.append(record_dict)


rows = records.shape[0]
margin_16 = [0] * rows

for i in range(rows):
    margin_16[i] = records.iloc[i]['votes_trump_16'] - records.iloc[i]['votes_clinton_16']
    
records['margin_16'] = margin_16

records.to_csv("/Users/vivek/Desktop/election_analysis/election_20/2016_data.csv")

states = ['Georgia', 'Arizona', 'Pennsylvania', 'Wisconsin', 'Michigan']
states_short = ['GA','AZ','PA','WI','MI']

all_data = pd.DataFrame(columns=["state","county","biden_count","trump_count","total_count"])

for state_short, state in zip(states_short,states):
    
    print(state_short)
    
    base = "https://www.nbcnews.com/politics/2020-elections/"
    state = state.lower()
    end = "-president-results"
    url = base + state + end

    driver = webdriver.Chrome("/Users/vivek/Downloads/chromedriver")
    driver.get(url)

    try:
        buttons = driver.find_elements_by_class_name('jsx-1765211304')
        buttons[0].click()
    except:
        None

    job_elems = driver.find_elements_by_class_name('publico-txt')

    counties = []

    for i,job_elem in enumerate(job_elems):
        if state_short == "WI":
            if i >= counties_per_state[state_short] + 1:
                break
            elif i == 0:
                continue
        else:
            if i >= counties_per_state[state_short]:
                break
        
        counties.append(job_elem.text)

    # print(counties)

    job_elems = driver.find_elements_by_class_name("jsx-3437879980")

    biden_count = []
    trump_count = []
    jo_count = []
    for i,job_elem in enumerate(job_elems):
    #     print(job_elem.text)
        if (i > 0 and i <= counties_per_state[state_short]):
            biden_count.append(int(job_elem.text.replace(",","")))
        elif (i > counties_per_state[state_short] + 1 and i <= 2*counties_per_state[state_short] + 1):
            trump_count.append(int(job_elem.text.replace(",","")))
        elif (i > 2*counties_per_state[state_short] + 2 and i<= 3*counties_per_state[state_short] + 2):
            jo_count.append(int(job_elem.text.replace(",","")))
        elif (i>= 3*counties_per_state[state_short] + 3):
            break

    total_count = [b + t + j for b,t,j in zip(biden_count,trump_count,jo_count)]

    state_data = pd.DataFrame(columns=["state","county","biden_count","trump_count","total_count"])

    state_data["state"] = [state_short] * counties_per_state[state_short]
    state_data["county"] = counties
    state_data["biden_count"] = biden_count
    state_data["trump_count"] = trump_count
    state_data["total_count"] = total_count

    all_data = all_data.append(state_data)
    
    # Add pct dem or rep

rows = all_data.shape[0]
dem20_pct = [0] * rows
rep20_pct = [0] * rows

for i in range(rows):
    dem20_pct[i] = all_data.iloc[i]['biden_count'] / all_data.iloc[i]['total_count'] * 100
    rep20_pct[i] = all_data.iloc[i]['trump_count'] / all_data.iloc[i]['total_count'] * 100
    
all_data['dem20_pct'] = dem20_pct
all_data['rep20_pct'] = rep20_pct

all_data.to_csv("/Users/vivek/Desktop/election_analysis/election_20/swing_data.csv")