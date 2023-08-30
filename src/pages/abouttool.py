#========================================PACKAGES

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State, callback
import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
load_figure_template("lux")
import pathlib
#========================================


location = pathlib.Path(__file__).parent.parent

## DASH

#-----------------------------------------------------------------------------------------------------------------------
#Data of webpage
color_graphbg = '#fafbfb' #'rgba(247,247,249,255)' #grey of dropdown men, 'rgba(179, 205, 227, 0.15)' light blue
#dbc LUX colors
color_NED = "#d8534f"
color_p = "#4abf73"
color_hsc = "#f0ad4e"
color_e = "#209bcf"

color_red = "rgba(226,126,123,255)"

# data
df_treemap = pd.read_csv(f'{location}/assets/df_treemap.csv')
df_treemap = df_treemap.drop('Unnamed: 0', axis=1)
colorscale_phsce = [color_e,color_p,color_hsc]

#  text
ned_text1 = '''
The NED approach combines two main sources:

1. Recent research shows the determinant role of social networks, geography, education, and wealth (among others) for 
enabling local economic development.

2. Community-based organizations, workforce boards, and community colleges elevate the complementary and equally 
fundamental role of access, basic needs, and community engagement, particularly for inclusion.

By combining frontier interdisciplinary research with key field-derived learning, three distinct Pillars emerged as 
comprising the drivers of inclusive local economic development. *Hover over the Pillars below to see what each 
entails.*
'''

ned_text2place = '''
...refer to the physical foundation upon which people live. Health, 
environment, and access are factored along with other metrics of thriving communities.'''

ned_text2humancap = '''
...cover the enablers of development given by individual 
education to social affiliation. This includes training pipelines and the strength of networks.
'''

ned_text2econact = '''
...represents material and financial prosperity, potential, 
and resilience. This is the 'size of the local economic pie' and how its 'slices' are distributed.
'''

ned_text3 = '''
In NED, the three Pillars are not mutually exclusive.
High Economic Activity scores do not make up for low Place-based Conditions and/or Human and Social Capital scores (which might imply exogenous economic growth and lacking endogenous assets and ecosystem, and thus inequal opportunity).
As such, NED is a *barometer* of the three Pillars where some degree of equilibrium leads to inclusive, sustainable prosperity.
Economic development strategies can thus be tailored by vieweing the three Pillars together.
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



Another example involves the future of work. Fitting into context of Green job creation as an opportunity to spur economic devlopment that's sustainable, and that boosts inclusive prosperity.
'''

futurework_socialinv ='''
##### Social Entrepreneurship
Can help locate areas where ...
'''

#-----------------------------------------------------------------------------------------------------------------------
# Build components
dict_pillarsintro = {'pillar': ['Place-based Conditions', 'Human and Social Capital', "Economic Activity"],
                     'value': [0, 0, 0],
                     'subjects':[['Environmental Health', 'Food and Physical Health Security', 'Housing and Neighborhoods', "Transportation", "Access to Finance Institutions, Childcare, and Broadband", "Density of Innovation and Creation Organizations", "Density of Skill-building Centers"], ['Educational Attainment, current adults', 'Schooling Outcomes, current students', 'Transitional and Opportunity Youth', 'Social Networks', 'Social Cohesion'], ['Size of Local Economy', 'Standard of Living', 'Productivity', 'Jobs', 'Employment', "Unemployment", "Labor Force", "Earnings", "Household Income", "Poverty", "Budgetary Assistance", "Income Inequality", "Homeownership", "Banking", "Financial Resilience", "Patents", "Business Establishments", "Loans to Small Business"]]}
df_pillarsintro = pd.DataFrame(data=dict_pillarsintro)
hover_pillarsintro = ["<br>".join(subject) for subject in df_pillarsintro['subjects']]

pillarcirclesfig = px.scatter(df_pillarsintro, x='pillar', y='value', color='pillar', #template = "lux",
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


pillar_circles = dcc.Graph(figure=pillarcirclesfig,config={'displayModeBar': False})



treemap = px.treemap(df_treemap, path=[px.Constant("NED"), 'pillar', 'topic', 'subject'], values=None,
                     color_discrete_sequence= colorscale_phsce)
treemap.update_traces(root_color='lightgrey')
treemap.update_layout(margin = dict(t=50, l=25, r=25, b=25))
treemap.update_traces(hovertemplate = None, hoverinfo = "skip")

treemap_graph = dcc.Graph(figure=treemap,config={'displayModeBar': False})
#-----------------------------------------------------------------------------------------------------------------------
# Registering page
dash.register_page(
    __name__,
    path='/about',
    title='About this tool',
    name='About tool'
)
#-----------------------------------------------------------------------------------------------------------------------


layout = dbc.Container([
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
    html.Br(),
#------------
    html.H3('NED Hierarchy', style={'fontsize': '24px', 'text-align': 'left', 'color': 'rgb(52,60,68)'}),
    dcc.Markdown('''The NED tool is made up as follows:'''),
    dcc.Markdown('''
                    $$
                    NED \impliedby i.~Pillars \impliedby ii.~Subjects \impliedby iii.~Topics
                    $$''', mathjax=True, style={"font-size": "17pt"}),
    html.Br(),
    dcc.Markdown('''
    See below a Treemap showcasing the data that comprise hierarchy of i. Pillars, ii. Subjects, and iii. Topics in the overall NED framework. Click into the modules to zoom in, and use the bar at the top to zoom out.
    '''),
    dbc.Row([
        dbc.Col([treemap_graph], width=12)
    ]),
    dcc.Markdown('''
        *Visit the [Methodology](/methodology) page for more information about the data and approach. And, see the [NED tool](/) in action!*'''),
    html.Br(),
#------------
    html.H3('Future Developments', style={'fontsize': '24px', 'text-align': 'left', 'color': 'DarkSlateGrey'}),
    html.Br(),
    dbc.Row([
        dcc.Markdown(children=futurework_text1)
    ]),
    dbc.Row([
        dcc.Markdown(children=futurework_academia)
    ]),
    dbc.Row([
        dcc.Markdown(children=futurework_policymaking)
    ]),
    dbc.Row([
        dcc.Markdown(children=futurework_socialinv)
    ]),
#------------
#    footerbar
], fluid=False, className="dbc")
#------------