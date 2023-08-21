import dash
import pandas as pd
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly_express as px
import pathlib

location = pathlib.Path(__file__).parent.parent
#location = './src'
#location = '/Users/ali/Desktop/Projects/Dashboard/Website/src'
#Users/ali/ for personal, Users/aconway/ for work


#-----------------------------------------------------------------------------------------------------------------------
# Registering page

dash.register_page(
    __name__,
    path='/methodology',
    title='Methodology',
    name='Methodology'
)
#-----------------------------------------------------------------------------------------------------------------------
 #Data of webpage

df_treemap = pd.read_csv(f'{location}/assets/df_treemap.csv')
df_treemap = df_treemap.drop('Unnamed: 0', axis=1)

#-----------------------------------------------------------------------------------------------------------------------
# Build components
#print(df_treemap.head())

treemap = px.treemap(df_treemap, path=[px.Constant("NED"), 'pillar', 'topic', 'subject'] , values=None)
treemap.update_traces(root_color="lightgrey")
treemap.update_layout(margin = dict(t=50, l=25, r=25, b=25))

treemap_graph = dcc.Graph(figure=treemap,config={'displayModeBar': False})
#-----------------------------------------------------------------------------------------------------------------------
# LAYOUT OF THE WEBPAGE
layout= html.Div(
    [
        html.H4("General methodology"),
        dcc.Markdown('''
            The New Economic Development (NED) Index provides a barometer of three key Pillars of equitable local and regional economic development: Place-based Conditions, Human Capital, and Economic Activity. Through this lens, economic development is represented not as a singular value but rather as three mutually inclusive dimensions. By combining research findings with field-generated principles, NED displays factors for inclusive sustainable local economic growth and wellbeing.
        '''),
        dcc.Markdown('''
            NED includes 83 variables spanning the breadth of , These are then aggregated by relatedness into 33 Subjects, themselves forming the following 8 Topics:
        '''),
        dcc.Markdown(children = '''
            * **Basic Needs** – to assess environmental, physical, and food health, security, housing, and transport.
            * **Place-based Access** – to assess access to financial institutions and insurance, and broadband.
            * **Education and Talent** – to assess educational attainment, schooling outcomes, and opportunity youth.
            * **Social Capital** – to access social networks and cohesion.
            * **Growth and Prosperity** – to assess the size and standard of living of local economies, alongside productivity.
            * **Labor Markets** – to assess jobs, employment, participation, and earnings.
            * **Income** – to assess household budgets, poverty, financial assistance, and income inequality.
            * **Wealth** – to assess home and asset ownership, banking availability, and financial resilience.
            * **Business Environment** – to assess entrepreneurial outcomes and opportunities.
        '''),
        dcc.Markdown('''
            See below a Treemap of the pillars, topics, and subjects and how they relate to one-another and to the overall NED framework. Click into the modules to zoom in, and use the bar at the top to zoom out.
        '''),
        dbc.Row([
            dbc.Col([treemap_graph], width=12)
        ]),
        html.H4("Data"),
        dcc.Markdown('''
            Main sources are:
            2018 data was used for two reasons: firstly, I wanted to use a full-year, widely availble indicators pre-pandemic. I selected 2018 in particular because I wanted to include the significant dataset that [Chetty *et al*, 2022](https://socialcapital.org)
        ''', link_target="_blank"),
        dcc.Markdown('''
            The Methodology of aggregating variables into subjects, topics, and Pillars is similar to that used by the OECD in their Better Life Index and the original HDI method. Taking a simple arithmetic average allows for equal weighting to be assigned . The latest HDI methodology involves geometric mean averaging. However, reading Ravilion and LSE guy's critiques, I devided it was best to keep things simple and not assign substitutative value of increases etc. *See below for a discusison on caveats.*
        '''),
        dcc.Markdown('''
            $P\\left( x \\right) = \\frac{{e^{ - \\lambda } \\lambda ^x }}{{x!}}$
            ''',
            mathjax=True,
            style={"font-size": "28pt"},
        ),
        dcc.Markdown('''
            The IHDI introduced an interesting approach to include distritbuional dimension to its single value. in  do the Atkinson approach due to its ability to collect further granular data and calculate distributions. With this dataset, this would be possible but extremely time intensive. 
            As such a simpler way is devised: Inequality is treated as a sort of 'weight' . Again, using a simple arithmetic average allows for no assumptions being made about the 'weight' of this ponderance. However, importantly this could be the subject of future work. 
        '''),
        dcc.Markdown('''
            CAVEATS:
            
            The IHDI is based on the Atkinson index, which satis- fies subgroup consistency. This property ensures that improvements (deteriorations) in the distribution of human development within only a certain group of the society imply improvements (deteriorations) in the distribution across the entire society.
            The main disadvantage is that the IHDI is not association sensitive, so it does not capture overlapping inequalities. To make the measure association sensi- tive, all the data for each individual must be available from a single survey source, which is not currently possible for a large number of countries.
        '''

        )

    ]
)