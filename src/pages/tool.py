#========================================PACKAGES

import json
import pandas as pd
import plotly.express as px
import base64
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, callback
import dash
import dash_bootstrap_components as dbc

import numpy as np
from urllib.request import urlopen
import json


with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVR
#========================================


#========================================INPUTING AND CLEANING THE DATA
# Layers

location = '/Users/ali/Desktop/Projects/Dashboard/Website/src'
#Users/ali/ for personal, Users/aconway/ for work

df_p = pd.read_excel(f'{location}/assets/CA_county_data.xlsx', sheet_name='PLACE', header=9,
                     dtype={"fips": str})
df_p = df_p.drop(columns=['neigh_seg', 'Concentration of training providers'])

df_hsc = pd.read_excel(f'{location}/assets/CA_county_data.xlsx', sheet_name='HUM CAP', header=9,
                      dtype={"fips": str})
df_hsc = df_hsc.drop(columns=['Unnamed: 21', 'Unnamed: 22', 'Unnamed: 23', 'Unnamed: 24'])

df_e = pd.read_excel(f'{location}/assets/CA_county_data.xlsx', sheet_name='ECON DEV', header=9,
                     dtype={"fips": str})
df_e = df_e.drop(columns=['under_u'])

df_first2 = pd.merge(df_p, df_hsc, on='fips', how='inner')
df_tot = pd.merge(df_first2, df_e, on='fips', how='inner')
df_tot = df_tot.drop(columns=['county', 'county_y'])
df_tot.rename(columns={"county_x": "county"}, inplace=True)

# Other
df_indices = pd.read_excel(f'{location}/assets/CA_county_data.xlsx', sheet_name='existing indexes',
                           header=1, dtype={"fips": str})

df_industry = pd.read_excel(f'{location}/assets/CA_county_data.xlsx', sheet_name='REGIONAL ECONOMY',
                            header=9, dtype={"fips": str})

df_pop_weight = pd.read_excel(f'{location}/assets/CA_county_data.xlsx', sheet_name='CA_county_data',
                            header=0, usecols='E')
# ------------------------------------------------------------------------------------------------------------
# SETTING UP TOPIC DICTIONARY
def getColNames(allColNames: list, startName: str, endName: str) -> list:
    index1 = allColNames.index(startName)
    index2 = allColNames.index(endName)
    subset = [allColNames[i] for i in range(index1, index2 + 1)]

    return subset


# place
df_p_colnames = list(df_p.columns)
df_p_dict = {"envhealth": ('fips', 'county', *getColNames(df_p_colnames, "water_violation", "particulate_matter")),
             "foodhealth": ('fips', 'county', *getColNames(df_p_colnames, "uninsured", "food_insec")),
             "housing": ('fips', 'county', *getColNames(df_p_colnames, "severe_housing", "crime_rate")),
             "transport": ('fips', 'county', *getColNames(df_p_colnames, "vehicle_avail", "commute_long")),
             "access_bcb": (
                 'fips', 'county', *getColNames(df_p_colnames, "access_finance_insurance", "access_broadband")),
             "innovcreation": ('fips', 'county', *getColNames(df_p_colnames, "r1_univ", "rd_density")),
             "skillbuilding": ('fips', 'county', *getColNames(df_p_colnames, "cc_density", "csu")),
             }
df_p_subj_dict = {"basic_needs": ('county', "envhealth", "foodhealth", "housing", "transport"),
                  "access": ('county', "access_bcb", "innovcreation", "skillbuilding")}

# human and social capital
df_hsc_colnames = list(df_hsc.columns)
df_hsc_dict = {"educattain": ('fips', 'county', *getColNames(df_hsc_colnames, "attain_nohs", "MYS")),
              "schooling": ('fips', 'county', *getColNames(df_hsc_colnames, "enrol_preschool", "juvenile_felony")),
              "oppyouth": ('fips', 'county', *getColNames(df_hsc_colnames, "highered_enroll", "discon_youth")),
              "socialnet": ('fips', 'county', *getColNames(df_hsc_colnames, "econ_con", "clustering")),
              "socialcohesion": ('fips', 'county', *getColNames(df_hsc_colnames, "support_ratio", "civic_orgs")),
              }
df_hsc_subj_dict = {"eductalent": ('county', "educattain", "schooling", "oppyouth"),
                   "socialcapital": ('county', "socialnet", "socialcohesion")}

# economic development
df_e_colnames = list(df_e.columns)
df_e_dict = {"size": ('fips', 'county', *getColNames(df_e_colnames, "rgdp_18", "rgdp_10yr")),
             "stdliving": ('fips', 'county', "rgdp_capita"),
             "prod": ('fips', 'county', *getColNames(df_e_colnames, "prod_jobs", "prod_worker")),
             "jobs": ('fips', 'county', *getColNames(df_e_colnames, "jobs", "jobs_young_prop")),
             "emp": ('fips', 'county', *getColNames(df_e_colnames, "emp_to_pop", "jobs_highskill")),
             "u": ('fips', 'county', *getColNames(df_e_colnames, "u", "u_youth_gap")),
             "lf": ('fips', 'county', *getColNames(df_e_colnames, "lfp", "lfp_youth_gap")),
             "earn": ('fips', 'county', *getColNames(df_e_colnames, "earn_med", "earn_med_gender_gap")),
             "hhinc": ('fips', 'county', *getColNames(df_e_colnames, "hh_inc_med", "hh_rentburden")),
             "poverty": ('fips', 'county', *getColNames(df_e_colnames, "poverty_prop", "poverty_under18")),
             "assistance": ('fips', 'county', *getColNames(df_e_colnames, "assist_food", "assist_cash")),
             "incineq": ('fips', 'county', *getColNames(df_e_colnames, "gini_inc", "inc_ratio")),
             "homeown": ('fips', 'county', *getColNames(df_e_colnames, "home_own", "home_own_edgap")),
             "bank": ('fips', 'county', *getColNames(df_e_colnames, "hh_underbank", "hh_unbank")),
             "finresil": ('fips', 'county', *getColNames(df_e_colnames, "asset_pov_rate", "l_asset_pov_rate")),
             "patents": ('fips', 'county', *getColNames(df_e_colnames, "patents_per1000", "patent_5yr")),
             "bus": ('fips', 'county', "num_establishments"),
             "smallbusloan": ('fips', 'county', *getColNames(df_e_colnames, "loan_smallbus_number", "loan_avg"))
             }
df_e_subj_dict = {"growthprosp": ('county', "size", "stdliving", "prod"),
                  "labormarket": ('county', "jobs", "emp", 'u', "lf", "earn"),
                  "income": ('county', "hhinc", "poverty", "assistance", "incineq"),
                  "wealth": ('county', "homeown", "bank", "finresil"),
                  "busenv": ('county', "patents", "bus", "smallbusloan")}

df_tot_dict = {**df_p_dict, **df_hsc_dict, **df_e_dict}
df_tot_subj_dict = {**df_p_subj_dict, **df_hsc_subj_dict, **df_e_subj_dict}

# PULLING TABLES FROM DICTIONARY

# print(df_e_dict.get("bus"))
# df_test = df_e.loc[:, df_e_dict.get("bus")]
# df_test.head()


# NORMALISATION ROUTINE

# For normalisation of positive components (life expectancy, higher the better), use Min-max (x-min)/(max-min)
# Certain variables have bounds, so will scale non-linearly to account for quality increases (HIHD)
# For normalisation of negative components (unemployment, lower the better), do 1 minus Min Max (or logMinMax)

df_fipscounty = df_tot.iloc[:, 0:2]
df_county = df_tot.iloc[:, 1]

# place
df_p_toscale = df_p.iloc[:, 2:]
scaler = MinMaxScaler()
scaler.fit(df_p_toscale)
MinMaxScaler()
df_p_n = scaler.transform(df_p_toscale)
df_p_n = pd.DataFrame(df_p_n, columns=df_p_toscale.columns)
df_p_n = pd.concat([df_fipscounty, df_p_n], axis=1)
df_p_n["water_violation"] = (1 - df_p_n["water_violation"])
df_p_n["particulate_matter"] = (1 - df_p_n["particulate_matter"])
df_p_n["uninsured"] = (1 - df_p_n["uninsured"])
df_p_n["years_lost"] = (1 - df_p_n["years_lost"])
df_p_n["limited_healthyfood"] = (1 - df_p_n["limited_healthyfood"])
df_p_n["food_insec"] = (1 - df_p_n["food_insec"])
df_p_n["severe_housing"] = (1 - df_p_n["severe_housing"])
df_p_n["rent_costburden"] = (1 - df_p_n["rent_costburden"])
df_p_n["housing_afford"] = (1 - df_p_n["housing_afford"])
df_p_n["homelessness"] = (1 - df_p_n["homelessness"])
df_p_n["resid_vacancy"] = (1 - df_p_n["resid_vacancy"])
df_p_n["crime_rate"] = (1 - df_p_n["crime_rate"])
df_p_n["commute_time"] = (1 - df_p_n["commute_time"])
df_p_n["commute_long"] = (1 - df_p_n["commute_alone"])
df_p_n["access_broadband"] = (1-df_p_n["access_broadband"])

# human and social capital
df_hsc_toscale = df_hsc.iloc[:, 2:]
scaler = MinMaxScaler()
scaler.fit(df_hsc_toscale)
MinMaxScaler()
df_hsc_n = scaler.transform(df_hsc_toscale)
df_hsc_n = pd.DataFrame(df_hsc_n, columns=df_hsc_toscale.columns)
df_hsc_n = pd.concat([df_fipscounty, df_hsc_n], axis=1)
df_hsc_n["suspensions"] = (1 - df_hsc_n["suspensions"])
df_hsc_n["juvenile_felony"] = (1 - df_hsc_n["juvenile_felony"])
df_hsc_n["discon_youth"] = (1 - df_hsc_n["discon_youth"])

#econ dev
df_e_toscale = df_e.iloc[:, 2:]
scaler = MinMaxScaler()
scaler.fit(df_e_toscale)
MinMaxScaler()
df_e_n = scaler.transform(df_e_toscale)
df_e_n = pd.DataFrame(df_e_n, columns=df_e_toscale.columns)
df_e_n = pd.concat([df_fipscounty, df_e_n], axis=1)
df_e_n["jobs_unstable_prop"] = (1 - df_e_n["jobs_unstable_prop"])
df_e_n["u"] = (1 - df_e_n["u"])
df_e_n["u_ed_gap"] = (1 - df_e_n["u_ed_gap"])
df_e_n["u_youth_gap"] = (1 - df_e_n["u_youth_gap"])
df_e_n["below_15000"] = (1 - df_e_n["below_15000"])
df_e_n["below_25000"] = (1 - df_e_n["below_25000"])
df_e_n["hh_houseburden"] = (1 - df_e_n["hh_houseburden"])
df_e_n["hh_rentburden"] = (1 - df_e_n["hh_rentburden"])
df_e_n["poverty_prop"] = (1 - df_e_n["poverty_prop"])
df_e_n["poverty_under18"] = (1 - df_e_n["poverty_under18"])
df_e_n["assist_food"] = (1 - df_e_n["assist_food"])
df_e_n["assist_income"] = (1 - df_e_n["assist_income"])
df_e_n["assist_cash"] = (1 - df_e_n["assist_cash"])
df_e_n["gini_inc"] = (1 - df_e_n["gini_inc"])
df_e_n["inc_ratio"] = (1 - df_e_n["inc_ratio"])
df_e_n["hh_underbank"] = (1 - df_e_n["hh_underbank"])
df_e_n["hh_unbank"] = (1 - df_e_n["hh_unbank"])
df_e_n["asset_pov_rate"] = (1 - df_e_n["asset_pov_rate"])
df_e_n["hh_noNW"] = (1 - df_e_n["hh_noNW"])
df_e_n["l_asset_pov_rate"] = (1 - df_e_n["l_asset_pov_rate"])




# AGGREGATION BY DICT- topic
# for dict in layer, select columns of the normalized df, and then average across to get a new variable vector
# Multiply by 10 to get score out of 10. if best in all scores, then would get 1 overall, this just puts in a more legible scale

# place
df_p_aggs = pd.DataFrame()
for dictentry in df_p_dict:
    subset = df_p_n.loc[:, df_p_dict.get(str(dictentry))]
    vector = subset.mean(axis=1, numeric_only=True)
    df_p_aggs[dictentry] = vector * 10
df_p_aggs.insert(0, "county", df_county)

# human and social capital
df_hsc_aggs = pd.DataFrame()
for dictentry in df_hsc_dict:
    subset = df_hsc_n.loc[:, df_hsc_dict.get(str(dictentry))]
    vector = subset.mean(axis=1, numeric_only=True)
    df_hsc_aggs[dictentry] = vector * 10
df_hsc_aggs.insert(0, "county", df_county)

# econ
df_e_aggs = pd.DataFrame()
for dictentry in df_e_dict:
    subset = df_e_n.loc[:, df_e_dict.get(str(dictentry))]
    vector = subset.mean(axis=1, numeric_only=True)
    df_e_aggs[dictentry] = vector * 10
df_e_aggs.insert(0, "county", df_county)

# total
df_first2_aggs = pd.merge(df_p_aggs, df_hsc_aggs, on='county', how='inner')
df_tot_aggs = pd.merge(df_first2_aggs, df_e_aggs, on='county', how='inner')

# AGGREGATION BY DICT- Subject
# for dict in layer, select columns of the aggregated topic df, and then average across to get a new variable vector

# place
df_p_subj_aggs = pd.DataFrame()
for dictentry in df_p_subj_dict:
    subset = df_p_aggs.loc[:, df_p_subj_dict.get(str(dictentry))]
    vector = subset.mean(axis=1, numeric_only=True)
    df_p_subj_aggs[dictentry] = vector
df_p_subj_aggs.insert(0, "county", df_county)

df_p_pill_aggs = pd.DataFrame(df_p_subj_aggs.mean(axis=1, numeric_only=True), columns=["p"])
df_p_pill_aggs.insert(0, "county", df_county)

# human and social capital
df_hsc_subj_aggs = pd.DataFrame()
for dictentry in df_hsc_subj_dict:
    subset = df_hsc_aggs.loc[:, df_hsc_subj_dict.get(str(dictentry))]
    vector = subset.mean(axis=1, numeric_only=True)
    df_hsc_subj_aggs[dictentry] = vector
df_hsc_subj_aggs.insert(0, "county", df_county)

df_hsc_pill_aggs = pd.DataFrame(df_hsc_subj_aggs.mean(axis=1, numeric_only=True), columns=["hsc"])
df_hsc_pill_aggs.insert(0, "county", df_county)

# econ
df_e_subj_aggs = pd.DataFrame()
for dictentry in df_e_subj_dict:
    subset = df_e_aggs.loc[:, df_e_subj_dict.get(str(dictentry))]
    vector = subset.mean(axis=1, numeric_only=True)
    df_e_subj_aggs[dictentry] = vector
df_e_subj_aggs.insert(0, "county", df_county)

df_e_pill_aggs = pd.DataFrame(df_e_subj_aggs.mean(axis=1, numeric_only=True), columns=["e"])
df_e_pill_aggs.insert(0, "county", df_county)

# total
df_first2_aggs = pd.merge(df_p_subj_aggs, df_hsc_subj_aggs, on='county', how='inner')
df_tot_subj_aggs = pd.merge(df_first2_aggs, df_e_subj_aggs, on='county', how='inner')

df_first2_pillars = pd.merge(df_p_pill_aggs, df_hsc_pill_aggs, on='county', how='inner')
df_pillars = pd.merge(df_first2_pillars, df_e_pill_aggs, on='county', how='inner')
df_pillars_fips = df_pillars.copy()
df_pillars_fips.insert(1, 'fips', df_fipscounty.iloc[:,0])

df_nedscore = pd.DataFrame(df_pillars.mean(axis=1, numeric_only=True), columns=["NED"])
df_nedscore.insert(0, "county", df_county)
df_nedscore_fips = df_nedscore.copy()
df_nedscore_fips.insert(1, 'fips', df_fipscounty.iloc[:,0])

df_nedpillars = pd.merge(df_nedscore, df_pillars, on='county', how='inner')
df_nedpillars_fips = pd.merge(df_nedscore_fips, df_pillars, on='county', how='inner')


# Rankings for topics

df_p_rank = df_p_aggs.set_index('county').transform(pd.Series.rank, 0, method='max', ascending=False,
                                                    na_option='bottom').astype(int).reset_index()
df_hsc_rank = df_hsc_aggs.set_index('county').transform(pd.Series.rank, 0, method='max', ascending=False,
                                                      na_option='bottom').astype(int).reset_index()
df_e_rank = df_e_aggs.set_index('county').transform(pd.Series.rank, 0, method='max', ascending=False,
                                                    na_option='bottom').astype(int).reset_index()

# total
df_first2_rank = pd.merge(df_p_rank, df_hsc_rank, on='county', how='inner')
df_tot_rank = pd.merge(df_first2_rank, df_e_rank, on='county', how='inner')

df_p_subj_rank = df_p_subj_aggs.set_index('county').transform(pd.Series.rank, 0, method='max', ascending=False,
                                                              na_option='bottom').astype(int).reset_index()
df_hsc_subj_rank = df_hsc_subj_aggs.set_index('county').transform(pd.Series.rank, 0, method='max', ascending=False,
                                                                na_option='bottom').astype(int).reset_index()
df_e_subj_rank = df_e_subj_aggs.set_index('county').transform(pd.Series.rank, 0, method='max', ascending=False,
                                                              na_option='bottom').astype(int).reset_index()

# total
df_first2_rank = pd.merge(df_p_rank, df_hsc_rank, on='county', how='inner')
df_tot_rank = pd.merge(df_first2_rank, df_e_rank, on='county', how='inner')

df_first2_subj_rank = pd.merge(df_p_subj_rank, df_hsc_subj_rank, on='county', how='inner')
df_tot_subj_rank = pd.merge(df_first2_subj_rank, df_e_subj_rank, on='county', how='inner')

df_nedpillars_rank = df_nedpillars.set_index('county').transform(pd.Series.rank, 0, method='max', ascending=False,
                                                              na_option='bottom').astype(int).reset_index()

df_nedpillars_rank = df_nedpillars_rank.rename(columns={"NED": "NED_r", "p": "p_r", "hsc": "hsc_r", "e": "e_r"})
#-----------------------------------------------------------------------------------------------------------------------





#=======================================================================================================================
#=======================================================================================================================
#=======================================================================================================================

## DASH

#-----------------------------------------------------------------------------------------------------------------------
#Data of webpage

dict_pillarsintro = {'pillar': ['Place-based Conditions', 'Human and Social Capital', "Economic Activity"],
                     'value': [0, 0, 0],
                     'subjects':[['Environmental Health', 'Food and Physical Health Security', 'Housing', "Transportation", "Access to Banking, Childcare, and Broadband", "Innovation and Creation Institutions", "Skill-building"], ['Educational Attainment', 'Schooling Outcomes', 'Opportunity Youth', 'Social Networks', 'Social Cohesion'], ['Size of Local Economy', 'Standard of Living', 'Productivity', 'Jobs', 'Employment', "Unemployment", "Labor Force Participation", "Earnings", "Household Income", "Poverty", "Budgetary Assistance", "Income Inequality", "Homeownership", "Banking", "Financial Resilience", "Patents", "Businesses", "Small Business Loans"]]}
df_pillarsintro = pd.DataFrame(data=dict_pillarsintro)
hover_pillarsintro = ["<br>".join(subject) for subject in df_pillarsintro['subjects']]

df_pillars = pd.merge(df_nedpillars_fips, df_nedpillars_rank, on='county', how='inner')
df_pillars = df_pillars.round(1)
hover_data={'pillar': False,
                           'value': False,
                           'Subject': hover_pillarsintro,
               },

#make a bar chart of level as compared to CA avg

df_subjects = df_tot_subj_aggs.copy()
#df_subjects.insert(1, 'fips', df_fipscounty.iloc[:,0])

df_topics = df_tot_aggs.copy()
df_topics.insert(1, 'fips', df_fipscounty.iloc[:,0])
df_topics = df_topics.round(1)

df_subjects_rank = df_tot_subj_rank.copy()

df_topics_rank = df_tot_rank.copy()


choromenu: list = [
                    {"label": "New Economic Development", "value": "NED"},
                    {"label": "i. Place-based Conditions", "value": "p"},
                    {"label": "i. Human and Social Capital", "value": "hsc"},
                    {"label": "i. Economic Activity", "value": "e"}
]

countymenu: list = []
for index, row_name in enumerate(df_county):
    countymenu.append({'label': row_name, 'value': row_name})

NED_logo = f'{location}/assets/Oikos2.png'
NED_logo_base64 = base64.b64encode(open(NED_logo, 'rb').read()).decode('ascii')
#-----------------------------------------------------------------------------------------------------------------------
#Build components

intro_text = '''Policymakers are increasingly looking beyond economic activity and growth to gauge a community's 
quality of life. New emphasis is being placed on households' lived experience and local conditions along with 
distributions of wealth and opportunity as part of a deeper understanding. Nevertheless, aside from few local 
examples, no such comprehensive, nationally scalable assessment exists.

The New Economic Development (NED) tool does just that.
'''

ned_text1 = '''
The combination of two main sources make up the NED approach:

1. Recent research shows the determinant role of social networks, geography, education, and wealth (among others) for 
enabling local economic development.

2. Community-based organizations, workforce boards, and community colleges elevate the complementary and equally 
fundamental local role of access, basic needs, and community engagement, particularly for inclusion.

By combining frontier interdisciplinary research with key field-derived learning, three distinct Pillars emerged as 
comprising the drivers of inclusive local economic development. *Hover over the Pillars below to see what each 
entails.*
'''

ned_text2place = '''
###### Place-based Conditions
refer to the physical foundation upon which people live. Health, 
environment, and access are factored along with other metrics of thriving communities.'''

ned_text2humancap = '''
###### Human and Social Capital
cover the enablers of development given by individual 
education to social affiliation. This includes training pipelines and the strength of networks.
'''

ned_text2econact = '''
###### Economic Activity
represents material and financial prosperity, potential, 
and resilience. This is the 'size of the local economic pie' and how its 'slices' are distributed.
'''

ned_text3 = '''
In the NED approach, the three Pillars are not mutually exclusive. For example, a region's incredible Economic Activity score does not make up for woeful Place-based Conditions and/or Human and Social Capital scores (implying exogenous economic growth and lacking endogenous assets and ecosystem). As such, NED is a *barometer* of the three Pillars where some degree of equilibrium leads to inclusive, sustainable prosperity. Economic development strategies can thus be tailored by vieweing the three Pillars together.

The NED tool is made up as follows:
'''
choro_text1 = '''
Explore NED throughout California's 58 counties. An aggregation of the Pillars into a general NED score is presented for comparison to common development metrics like Gross Regional Product or the Human Development Index. *Select a dimension from the menu below, and use the buttons above it to toggle between views.*
'''

county_text = '''
Analyze individual counties' performance the NED way through the three subsequent levels of depth to identify the particular situation they're in.

* Start top left with the Pillars (i.) barometer, which shows the general balance forming inclusive, sustainable economic development.  
*Ex: large magnitudes (Los Angeles) and lack of balance (Butte) showcase the variety of county experiences.*

* Dig deeper with the eight Subjects (ii.) on the right showing the major categories underlying each Pillar.  
*Ex: significant differences within Pillars (Lassen, Economic Activity) highlight the part of an ecosystem policies can focus.*

* Finally, examine the distribution of Topics (iii., below) rankings to see specifically where counties specialize, and where they are weaker.  
*Ex: wide spreads (San Francisco) suggest targeted approaches, whereas more concentrated rankings (Imperial) suggest a comprehensive plan is needed.*

*Start by selecting a county using the dropdown menu below, and hover over the figures for more information.*
'''

futurework_text1 = '''
As this work develops, the aim remains to raise public awareness and provide policymakers a means to make more informed decisions.

There are three main avenues of work that the NED tool opens up:

1. Academic research to understand the significance of the determinants of inclusive local and regional economic development
2. Applying the NED tool to a variety of other studies to provide broader context of community impact/status in specific decisions
3. Informing social entrepreneurs and general investment what areas may be best suited to benefit from dollars
'''

futurework_academia= '''
##### Academic Research
For the retrospective analysis, work is underway to analyze which determinants are most important under what circumtances. A proprietary ML approach has been developed to do so that can help identify the weighting towards
Similarly, are there correlations between the various Subjects that reduce the set of levers that policymakers need to affect for given outcome? And how does this change from sutaiton to sutiation.


As an example, looking at the 3D scatter plot, we see a general positive correlation across the three indicators. Is this more empirical proof of Agglomeration economies, through a lens of inclusive economic development?
'''

futurework_policymaking = '''
##### Use in Policymaking
The NED tool can be useful in specific contexts as the baseline reference of a place (rather than Gross Regional Product for instance). For example, looking at LOCATION QUOTIENTS helps identify. But, what does this mean in the context of a place? What does this mean given the particular industrial . For example, we can look at location quotients of places to identify how its made up. Scatter plot of LQ with NED shows, , which suggests that 

CORRELATION map next to , w


Another example involves the future of work. Fitting into context of Green job creation as an opportunity to spur economic devlopment that's sustainable, and that boosts inclusive prosperity.
'''

futurework_socialinv ='''
##### Social Entrepreneurship
Can help locate areas where ...
'''

pillar_circles = dcc.Graph(figure={},config={'displayModeBar': False})
chorotitle = dcc.Markdown(children='')
choro_graph = dcc.Graph(figure={}, config={'modeBarButtonsToRemove': ['zoom', 'pan', 'select', 'lasso2d']})
nedpillar_graph = dcc.Graph(figure={})
choro_dropdown = dcc.Dropdown(options= choromenu,
                              value='NED',
                              clearable=False)
chorotab_See = dcc.Markdown(children='', link_target="_blank")
chorotab_Mean = dcc.Markdown(children='', link_target="_blank")
chorotab_See_content = dbc.Card(
    dbc.CardBody(
        [
            chorotab_See,
        ]
    ), className="mt-3",
)
chorotab_Mean_content = dbc.Card(
    dbc.CardBody(
        [
            chorotab_Mean,
        ]
    ), className="mt-3",
)

choro_tabs = html.Div(
            [
                dbc.Tabs(
                    [
                        dbc.Tab(chorotab_See_content, label="WHAT THIS SHOWS:"),
                        dbc.Tab(chorotab_Mean_content, label="WHAT THIS MEANS:"),
                    ],
                ),
            ]
)

chorotabSee_NED = '''
NED development across the State is highly variable and distinctly concentrated around major cities (San Francisco Bay Area, Los Angeles, San Diego). The spread is also significant: the score in the lowest county, Tulare, is almost half of top-ranked Marin and Santa Clara's.
'''
chorotabMean_NED = '''
NED reflects the outcomes of 'agglomeration economies' (the benefits from firms and people located near each other in industrial clusters). Geographic proximity boosts economic activity and enables the formation of strong social networks, increasing the supply of workers and businesses as well as the demand for an ecosystem around it. However, agglomeration economies also produce marked inequalities from higher living costs, gentrification, and social exclusion.
This is a significant draw for the development of aspects of the three Pillars concurrently, which happens on a smaller scale in less competitive counties.

Consistent with [recent research](https://www.centreforcities.org/reader/office-politics/the-impact-of-agglomeration-on-the-economy/#:~:text=Agglomeration%20occurs%20because%20of%20the,larger%20cities%20and%20industrial%20concentrations.), agglomeration economy spillovers (both positive and negative) are especially strong in the Financial and Business Service sectors and increase with scale, like in the world-class centers of the San Francisco Bay Area, Los Angeles, and San Diego– the regions with the highest NED scores.
'''
chorotabSee_p = '''
Place-based Conditions also vary across the state and showcase a wide range: Tulare (lowest) scores less than half of San Francisco (highiest). Significant concentrations exist around industrial clusters on the coast, and to a smaller extent in Northern California.
'''
chorotabMean_p = '''
In this Pillar we see geographic idiosyncracies play out, and some of the tradeoffs from agglomeration economies. The central counties forming a major truck transport corridor experience worse environmental quality and . Less-wealthy counties are less able to provide basic necessities. Converseley, more-wealthy counties experience high
However, the widespread presence of higher education institutions allows for residents in more counties to have physical access to traditional training. 
'''
chorotabSee_hsc = '''
We see that HSC is quite localized...
'''
chorotabMean_hsc = '''
Social and Human Capital. This more even concentration around cities is due in part to the greater presence of Higher Ed as well as greater social capital. As [Chetty *et al*, 2022](https://socialcapital.org) find, the strength of social networks is quite conducive to, which occurs when people live closer together. 
'''
chorotabSee_e = '''
We see that E is quite localized...
'''
chorotabMean_e = '''
Agglomeration economies . For instance, we can see that play out in the wine-producing counteis of Northern California. Difference with Ag elsewhere is that:
'''

countytitle = dcc.Markdown(children='')
county_pillarsgraph = dcc.Graph(figure={}, config={'modeBarButtonsToRemove': ['select', 'lasso2d']})
county_flower = dcc.Graph(figure={}, config={'modeBarButtonsToRemove': ['zoom', 'select', 'lasso2d']})
county_dropdown = dcc.Dropdown(options= countymenu,
                              value='Alameda',
                              clearable=False)
county_top5bot5graph = dcc.Graph(figure={}, config={'modeBarButtonsToRemove': ['select', 'lasso2d']})
pillars_correlationgraph = dcc.Graph(figure={})

#------------------------------------------------------
# Radio items
radio_mapbar = dcc.RadioItems(
    id = 'radio_mapbar',
    options = [
        {'label': ' Map ', 'value': 'map'},
        {'label': ' Bar chart (rankings).', 'value': 'bar'}
    ],
    value = 'map',
    inline=True
)

radio_alpharank = dcc.RadioItems(
    id = 'radio_alpharank',
    options = [
        {'label': ' alphabetically ', 'value': 'alph'},
        {'label': ' by rank.', 'value': 'rank'}
    ],
    style={'margin-right': '50px'},
    value = 'alph',
    inline=True
)



color_graphbg = '#fafbfb' #'rgba(247,247,249,255)' #grey of dropdown men, 'rgba(179, 205, 227, 0.15)' light blue
#dbc LUX colors
color_NED = "#d8534f"
color_p = "#4abf73"
color_hsc = "#f0ad4e"
color_e = "#209bcf"

color_red = "rgba(226,126,123,255)"

#screen colors
# color_NED = "#3d1594"
# color_p = "#4611a9"
# color_hsc = "#a11ebe"
# color_e = "#dd6f8d"

#-----------------------------------------------------------------------------------------------------------------------
# Registering page
dash.register_page(
    __name__,
    path='/',
    title='New Economic Development',
    name='NED tool'
)
#-----------------------------------------------------------------------------------------------------------------------
# LAYOUT OF THE WEBPAGE
layout = dbc.Container([
    html.H1('The NED Interactive Tool', style={'fontsize': '48px', 'text-align': 'center', 'color': 'red'}),
    html.Br(),
    dcc.Markdown(intro_text),
    html.Br(),
#------------
    html.H3('The NED approach', style={'fontsize': '24px', 'text-align': 'left', 'color': 'rgb(52,60,68)'}),
    dcc.Markdown(ned_text1),
    dbc.Row(
        [
            dbc.Col([pillar_circles], width = {"size": 12})
        ]
    ),
    dbc.Row(
        [
            dbc.Col(dcc.Markdown(ned_text2place), width = {"size": 4}),
            dbc.Col(dcc.Markdown(ned_text2humancap), width = {"size": 4}),
            dbc.Col(dcc.Markdown(ned_text2econact), width = {"size": 4}),
        ]
    ),
    html.Br(),
    dcc.Markdown(ned_text3),
    dcc.Markdown('''$$
                    NED \impliedby i.~Pillars \impliedby ii.~Subjects \impliedby iii.~Topics
                    $$''', mathjax=True, style={"font-size": "17pt"}),
    dcc.Markdown('''*Visit the [Methodology](/methodology) page for more information about the data and approach. And, see the NED tool in action below!*'''),
    html.Br(),
#------------
    html.H3("California's Status", style={'fontsize': '24px', 'text-align': 'left', 'color': 'rgb(52,60,68)'}),
    dcc.Markdown(children=choro_text1),
    dbc.Row(
        [
            dbc.Col([chorotitle], width='auto'),
            dbc.Col(dcc.Markdown("###### *Sources in Methodology*"), width='auto')
        ],
        justify='between'
    ),
    dbc.Row(
        [
            dbc.Col([choro_graph], width=12)
        ]
    ),
    dbc.Row(
        [
            dbc.Col([choro_dropdown], width=6)
        ],
        justify='center'
    ),
    html.Br(),
    dbc.Row(
        [
            dbc.Col(html.Div("Display:"), width="auto"),
            dbc.Col(radio_mapbar, width='auto'),
        ],
        justify='start',
    ),
    dbc.Row(
        [
            dbc.Col(html.Div("Display counties of Bar chart"), width = "auto"),
            dbc.Col(radio_alpharank, width='auto'),
        ],
        justify='start',
    ),
    html.Br(),
    dbc.Row([choro_tabs]),
    html.Br(),
    html.Br(),
#------------
    html.H3('County Analysis', style={'fontsize': '24px', 'text-align': 'left', 'color': 'rgb(52,60,68)'}),
    dcc.Markdown(children=county_text),
    dbc.Row([
        dbc.Col([county_dropdown], width=3)
    ], justify='left'),
    html.Br(),
    dbc.Row([
        dbc.Col([county_pillarsgraph], width=6),
        dbc.Col([county_flower], width=6)
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([county_top5bot5graph], width=12)
    ]),
    dbc.Row([
        dbc.Col([countytitle], width='auto')
    ], justify='center'),
    html.Br(),
#------------
    html.H3('What does this all mean? Correlations and future developments', style={'fontsize': '24px', 'text-align': 'left', 'color': 'DarkSlateGrey'}),
    html.Br(),
    dbc.Row([
        dcc.Markdown(children=futurework_text1)
    ]),
    dbc.Row([
        dcc.Markdown(children=futurework_academia)
    ]),
    dbc.Row([
        dbc.Col([pillars_correlationgraph], width=12)
    ]),
    dbc.Row([
        dcc.Markdown(children=futurework_policymaking)
    ]),
    dbc.Row([
        dcc.Markdown(children=futurework_socialinv)
    ]),
#------------
#    footerbar
], fluid=True)


#-----------------------------------------------------------------------------------------------------------------------
#Allows components to interact

@callback(     # number of outputs must equal number of returns below
    Output(pillar_circles, 'figure'),
    Output(choro_graph, 'figure'),
    Output(chorotitle, 'children'),
    Output(chorotab_See, 'children'),
    Output(chorotab_Mean, 'children'),########################################################################################################
    Output(county_pillarsgraph, 'figure'),
    Output(county_flower, 'figure'),
    Output(county_top5bot5graph, 'figure'),
    Output(pillars_correlationgraph, 'figure'),
    Output(countytitle, 'children'),
    Input(choro_dropdown, 'value'),
    Input(radio_mapbar, 'value'),
    Input(radio_alpharank, 'value'),
    Input(county_dropdown, 'value'),
)
def update_page(choro_selected, radioitem_mapbar, radioitem_alpharank, county_selected):

    pillarcirclesfig = px.scatter(df_pillarsintro, x='pillar', y='value', color='pillar',
                     color_discrete_map={
                         "Place-based Conditions": color_p,
                         "Human and Social Capital": color_hsc,
                         "Economic Activity": color_e
                     },
                     opacity=0.85,
                     #hover_name='pillar',
                     hover_data={'pillar': False,
                                 'value': False,
                                 'Subject': hover_pillarsintro,
                                 },

                     )
    pillarcirclesfig.update_traces(marker=dict(size=60, line=dict(width=1.5, color='DarkSlateGrey')),
                                  # customdata = np_pillarsintro,
                                  # hovertemplate=("Subjects: %{customdata[1]}")                   ##################################################
                      )
    pillarcirclesfig.update_xaxes(showgrid=False,
                     )
    pillarcirclesfig.update_yaxes(showgrid=False,
                     zeroline=False,
                     showticklabels=False,
                     )
    pillarcirclesfig.layout.xaxis.fixedrange = True
    pillarcirclesfig.layout.yaxis.fixedrange = True
    pillarcirclesfig.update_layout(
        title=None,
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False,
    )
    pillarcirclesfig.update_layout(height=310, plot_bgcolor='white', font=dict(size=17))




    # Graph-title
    def find_label_from_value(the_list:list, the_value:str) -> str:
        the_label = [element["label"] for element in the_list if the_value in element.values()]
        return the_label[0]

    chorovalue = find_label_from_value(choromenu, choro_selected)

    # Color
    if choro_selected == 'NED':
        chorocholor = 'temps_r'
    elif choro_selected == 'p':
        chorocholor = 'emrld'
    elif choro_selected == "hsc":
        chorocholor = 'oryel'
    else:
        chorocholor = 'ice_r'

    # Plotly express
    fig_choro = px.choropleth(df_pillars, geojson=counties, locations='fips', scope="usa", color=choro_selected,
                        color_continuous_scale=chorocholor,
                        height = 450,
                        #labels=False,
                        hover_name=('county'),
                        hover_data={'fips':False}, #would like to round this to 2 significant digits
                        )
    fig_choro.update_geos(fitbounds='locations', visible=False)
    fig_choro.update_layout(
        coloraxis_colorbar=dict(
            title="Score",
        ),
    )

    if choro_selected == 'NED':
        pillar_color = color_NED
    elif choro_selected == 'p':
        pillar_color = color_p
    elif choro_selected == "hsc":
        pillar_color = color_hsc
    else:
        pillar_color = color_e

    if radioitem_alpharank == 'rank':
        df_forpillars = df_pillars.sort_values(choro_selected)
    else:
        df_forpillars= df_pillars

    fig_cabars = px.bar(df_forpillars, x = 'county', y= choro_selected,
                        hover_name = "county",
                        hover_data = {'county': False},
                        text = "county"
    )
    fig_cabars.update_traces(marker_color=pillar_color, opacity=1, marker=dict(line=dict(width=0.33, color='#1a1a1a')))
    fig_cabars.update_xaxes(showgrid=False, showticklabels=False)
    fig_cabars.update_yaxes(showgrid=False, range=[0,6.65])
    fig_cabars.update_layout(
        title=None,
        xaxis_title="County",
        yaxis_title=None
    )
    fig_cabars.update_layout(plot_bgcolor=color_graphbg)
    fig_cabars.update_layout(clickmode="event+select")
    fig_cabars.layout.xaxis.fixedrange = True
    fig_cabars.layout.yaxis.fixedrange = True
    for figure in fig_cabars.data:
        figure.update(
            selected=dict(marker=dict(color=pillar_color)),
            unselected=dict(marker=dict(color=pillar_color, opacity=0.6)),
        )

    if radioitem_mapbar == 'map':
        fig_ca = fig_choro
    else:
        fig_ca = fig_cabars



    if choro_selected == 'NED':
        chorotab_s = chorotabSee_NED
        chorotab_m = chorotabMean_NED
    elif choro_selected == 'p':
        chorotab_s = chorotabSee_p
        chorotab_m = chorotabMean_p
    elif choro_selected == "hsc":
        chorotab_s = chorotabSee_hsc
        chorotab_m = chorotabMean_hsc
    else:
        chorotab_s = chorotabSee_e
        chorotab_m = chorotabMean_e


# ------------------------
    sf_pillars_slice = df_pillars.set_index('county').loc[county_selected]
    df_pillars_slice1 = pd.DataFrame({'Pillar': sf_pillars_slice.index, 'Score': sf_pillars_slice.values})
    df_pillars_slice2 = pd.DataFrame(df_pillars_slice1.loc[df_pillars_slice1['Pillar'].isin(['p', 'hsc', 'e'])])

    NED_wavg = np.average(df_nedpillars["NED"], weights=df_pop_weight["pop_perc"])
    p_wavg = np.average(df_nedpillars["p"], weights=df_pop_weight["pop_perc"])
    hsc_wavg = np.average(df_nedpillars["hsc"], weights=df_pop_weight["pop_perc"])
    e_wavg = np.average(df_nedpillars["e"], weights=df_pop_weight["pop_perc"])

    df_pillars_slice2["Pillar"] = ["Place-based Conditions", "Human and Social Capital", "Economic Activity"]
    df_pillars_slice2["Average"] = [p_wavg, hsc_wavg, e_wavg]


    NED_wavg = np.average(df_nedpillars["NED"], weights=df_pop_weight["pop_perc"])

    # Plotly express
    fig_countypillars = px.bar(
        df_pillars_slice2, x = 'Pillar', y = 'Score',
        hover_name='Pillar',
        hover_data={'Pillar': False,  # remove from hover data
                    'Score': True,  # add other column, customized formatting
                    }
    )
    fig_countypillars.add_hline(y = NED_wavg, line_width=2.5, line_dash="dash", line_color=color_red, annotation_text = "NED Score average", annotation_font = dict({"color":"rgba(226,126,123,1)"}), annotation_bgcolor = "rgba(250, 251, 251, 0.35)")#, annotation_position = "top left")
    fig_countypillars.update_traces(marker=dict(line=dict(width=1,color='#1a1a1a')), marker_color=[color_p, color_hsc, color_e])
    fig_countypillars.update_yaxes(range=[0, np.max(df_pillars['hsc'] + .1)], showgrid=False)
    fig_countypillars.update_xaxes(tickmode = 'array', tickvals = df_pillars_slice2['Pillar'], ticktext = ["PbC", "HSC", "EA"])
    fig_countypillars.update_layout(title="i. Pillar Scores", title_x=0.5, xaxis_title="Pillar", yaxis_title="Score", plot_bgcolor=color_graphbg)
    fig_countypillars.layout.xaxis.fixedrange = True
    fig_countypillars.layout.yaxis.fixedrange = True



    subject_slice = df_subjects.set_index('county').loc[county_selected].round(1)
    print(subject_slice)

    theta9 = [0, 40, 80, 120, 160, 200, 240, 280, 320]

    fig_subjflower = go.Figure(go.Barpolar(
        r=subject_slice,
        theta=theta9,
        width=[20, 20, 20, 20, 20, 20, 20, 20, 20],
        marker_color=[color_p, color_p, color_hsc, color_hsc, color_e, color_e, color_e, color_e, color_e],
        marker_line_color="rgba(26,26,26,255)",
        marker_line_width=1,
        opacity=0.8,
        # hovertemplate=
        # "<b>%{text}</b><br><br>" +
        # "GDP per Capita: %{x:$,.0f}<br>" +
        # "Life Expectation: %{y:.0%}<br>" +
        # "Population: %{marker.size:,}" +
        # "<extra></extra>",
    ))
    fig_subjflower.add_trace(go.Scatterpolar(
        r= [p_wavg, p_wavg],
        theta=[0, 40],
        mode='lines',
        name='Place-based Conditions average',
        line_color=color_red,
        line_dash='dot',
        line_width = 2,
        line_shape = 'spline',
        line_smoothing = 1.3
    ))
    fig_subjflower.add_trace(go.Scatterpolar(
        r= [hsc_wavg, hsc_wavg],
        theta=[80, 120],
        mode='lines',
        name='Human and Social Capital average',
        line_color=color_red,
        line_dash = 'dot',
        line_width = 2,
        line_shape = 'spline',
        line_smoothing = 1.3

    ))
    fig_subjflower.add_trace(go.Scatterpolar(
        r= [e_wavg, e_wavg, e_wavg, e_wavg, e_wavg],
        theta=[160, 200, 240, 280, 320],
        mode='lines',
        name='Economic Activity average',
        line_color=color_red,
        line_dash='dot',
        line_width=2,
        line_shape='spline',
        line_smoothing=1.3
    ))
    fig_subjflower.update_layout(
        grid=None,
        showlegend = False,
        template=None,
        polar=dict(
            radialaxis=dict(range=[0, 8.5], showticklabels=False, ticks=''),
            angularaxis=dict(showticklabels=False, ticks='')
        ),
        #plot_bgcolor=color_graphbg,
        title = 'ii. Subject Scores'
    )

    fig_subjflower.layout.xaxis.fixedrange = True
    fig_subjflower.layout.yaxis.fixedrange = True
    fig_subjflower.update_polars(radialaxis=dict(visible=False), bgcolor=color_graphbg, angularaxis_showgrid = False, angularaxis_showline = False)


    countyslice = df_topics_rank.set_index('county').loc[county_selected]
    #print(len(countyslice))
    bottom5 = countyslice.nlargest(n=15, keep='first')
    top5 = countyslice.nsmallest(n=15, keep='first')

    top5bottom5rank = pd.concat([top5, bottom5])  # Series of top5 and bottom 5, for the rank #
    top5bottom5neg = top5bottom5rank * (-1)  # Series of negative (for graphing)

    # print(countyslice, len(countyslice))
    # print(top5bottom5rank, len(top5bottom5rank))
    # print(top5bottom5neg, len(top5bottom5rank))


    top5bottom5rank = top5bottom5rank.reset_index()  # prep for data frame
    top5bottom5neg = top5bottom5neg.reset_index()  # prep for data frame

    df_top5bottom5 = pd.merge(top5bottom5rank, top5bottom5neg, on='index')  # making data frame
    df_top5bottom5.columns = ['index', 'rank', 'rank_neg']  # rename

    df_top5bottom5['pillars'] = pd.Series()
    df_top5bottom5['zeros'] = 0.075


    for index, row in df_top5bottom5.iterrows():
        current_rank = df_top5bottom5.iloc[index]['rank']

        to_add = 0.2
#        print("INDEX:", index, " RANK:", row["rank"])

        if index >=0 and index <= 14:
            if index == 0:
                df_top5bottom5.loc[index, 'zeros'] = df_top5bottom5.loc[index, 'zeros']
            if index <= 14 and index >=1:
                prev_rank = df_top5bottom5.iloc[index + -1]['rank']
                if current_rank == prev_rank:
                    df_top5bottom5.loc[index, 'zeros'] = df_top5bottom5.loc[index-1, 'zeros'] + to_add
        else:
            if index == 15:
                df_top5bottom5.loc[index, 'zeros'] = df_top5bottom5.loc[index, 'zeros']
            if index <= 29 and index >= 16:
                prev_rank = df_top5bottom5.iloc[index + -1]['rank']
                if current_rank == prev_rank:
                    df_top5bottom5.loc[index, 'zeros'] = df_top5bottom5.loc[index-1, 'zeros'] + to_add

    for index in df_top5bottom5['index']:
        if index in df_e_dict:
            df_top5bottom5.loc[df_top5bottom5['index'] == index, 'pillars'] = 'e'
        elif index in df_hsc_dict:
            df_top5bottom5.loc[df_top5bottom5['index'] == index, 'pillars'] = 'hsc'
        else:
            df_top5bottom5.loc[df_top5bottom5['index'] == index, 'pillars'] = 'p'

    fig_county5 = px.scatter(df_top5bottom5, x='rank_neg', y='zeros', color='pillars',
                     color_discrete_map={
                         "p": color_p,
                         "hsc": color_hsc,
                         "e": color_e
                     },
                     category_orders={"pillars": ["p", "hsc", "e"]},
                     # opacity=0.85,
                     hover_name='index',
                     hover_data={'rank_neg': False,  # remove from hover data
                                 'zeros': False,
                                 'pillars': False,  # add other column, default formatting
                                 'rank': True,  # add other column, customized formatting
                                 }
                     )
    fig_county5.update_traces(marker=dict(size=15,
                                  line=dict(width=1,
                                            color='#1a1a1a')),
                      )
    fig_county5.update_xaxes(showgrid=False,
                     range=[-59, 0],
                     nticks=3,
                     # tick0=-58, dtick=29,
                     tickvals=[-58, -29, -1],
                     ticktext=['58', '29', '1'],
                     )

    fig_county5.update_yaxes(showgrid=False,
                     range=[-0.15,np.max(df_top5bottom5['zeros']+.5)],
                     zeroline=True, zerolinecolor='black', zerolinewidth=3,
                     showticklabels=False,
                     )
    fig_county5.update_layout(
        title="iii. Topics Distribution by Score ranking",
        title_x=0.5,
        xaxis_title="Rank",
        yaxis_title="Frequency",
        legend_title="Pillar",
    )
    fig_county5.update_layout(height=400, plot_bgcolor=color_graphbg)
    fig_county5.layout.xaxis.fixedrange = True
    fig_county5.layout.yaxis.fixedrange = True



    fig_3dscatter = px.scatter_3d(
        df_pillars, x = 'p', y= 'hsc', z='e'
    )
    fig_3dscatter.update_traces(marker=dict(size=5,
                                  line=dict(width=1,
                                            color='#1a1a1a')),
                      )
    fig_3dscatter.update_layout(height=400, plot_bgcolor=color_graphbg)



    return pillarcirclesfig, fig_ca, '#### '+chorovalue+' Score', chorotab_s, chorotab_m, fig_countypillars, fig_subjflower, fig_county5, fig_3dscatter, '#### The most similar countes to '+county_selected+" county are:",
