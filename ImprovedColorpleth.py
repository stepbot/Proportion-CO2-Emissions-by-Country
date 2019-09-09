# Import libraries
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style('whitegrid')

# Read in datasets
df_em = pd.read_csv('Emissions by Country.csv')
df_po = pd.read_csv('Population by Country.csv')

# Get percent world emissions for 2017
df_em_2017 = df_em[['country_name', '2017']].rename(columns={'2017': 'emissions'}).set_index('country_name')

total_em_2017 = df_em_2017.at['GLOBAL TOTAL', 'emissions']
df_em_2017['percent_emissions'] = (df_em_2017['emissions'] / total_em_2017) * 100

df_em_2017 = df_em_2017.drop(['GLOBAL TOTAL'], axis=0)
del df_em_2017.index.name

# Get percent world population for 2017
cols = ['Country Name', '2017', 'Country Code']
df_po_2017 = df_po[cols].rename(columns={'2017': 'population', 'Country Code': 'code'}).set_index('Country Name')

total_po_2017 = df_po_2017.at['World', 'population']
df_po_2017['percent_population'] = (df_po_2017['population'] / total_po_2017) * 100

df_po_2017 = df_po_2017.drop(['World'], axis=0)
del df_po_2017.index.name

# Get codes for emissions data
rename = {'Bahamas, The': 'Bahamas', 'Brunei Darussalam': 'Brunei', 'Cabo Verde': 'Cape Verde', 'Congo':
          'Republic of the Congo', 'Congo, Rep.': 'Republic of the Congo', 'Côte d’Ivoire': "Cote d'Ivoire",
          'Curaçao': 'Curacao', 'Czech Republic': 'Czechia', 'Congo, Dem. Rep.': 'Democratic Republic of the Congo',
          'Egypt, Arab Rep.': 'Egypt', 'Faroes': 'Faroe Islands', 'former Yugoslav Republic of Macedonia, the':
          'North Macedonia', 'France and Monaco': 'France', 'Hong Kong SAR, China': 'Hong Kong', 'Lao PDR': 'Laos',
          'Iran, Islamic Rep.': 'Iran', 'Israel and Palestine, State of': 'Israel', 'Kyrgyz Republic': 'Kyrgyzstan',
          'Italy, San Marino and the Holy See': 'Italy', 'Macao SAR, China': 'Macao', 'Myanmar/Burma': 'Myanmar',
          'Korea, Dem. People’s Rep.': 'North Korea', 'Russian Federation': 'Russia', 'St. Kitts and Nevis':
          'Saint Kitts and Nevis', 'St. Lucia': 'Saint Lucia', 'São Tomé and Príncipe': 'Sao Tome and Principe',
          'St. Vincent and the Grenadines': 'Saint Vincent and the Grenadines', 'Serbia and Montenegro': 'Serbia',
          'Slovak Republic': 'Slovakia', 'Korea, Rep.': 'South Korea', 'Spain and Andorra': 'Spain', 'Swaziland':
          'Eswatini', 'Sudan and South Sudan': 'Sudan', 'Switzerland and Liechtenstein': 'Switzerland', 'Gambia, The':
          'The Gambia', 'Syrian Arab Republic': 'Syria', 'Venezuela, RB': 'Venezuela', 'Yemen, Rep.': 'Yemen'}

df_em_2017['country'] = df_em_2017.index.to_series().replace(rename)
df_po_2017['country'] = df_po_2017.index.to_series().replace(rename)

df_em_2017_codes = df_em_2017.merge(df_po_2017[['country', 'code']], how='left', on='country')
df_em_2017_codes = df_em_2017_codes.dropna(subset=['code'])

# Recalculate select values for population data
df_po_2017_adj = df_po_2017.drop(['country'], axis=1)
pop = 'population'

df_po_2017_adj.at['France', pop] = df_po_2017.at['France', pop] + df_po_2017.at['Monaco', pop]
df_po_2017_adj.at['Italy', pop] = df_po_2017.at['Italy', pop] + df_po_2017.at['San Marino', pop]
df_po_2017_adj.at['Serbia', pop] = df_po_2017.at['Serbia', pop] + df_po_2017.at['Montenegro', pop]
df_po_2017_adj.at['Spain', pop] = df_po_2017.at['Spain', pop] + df_po_2017.at['Andorra', pop]
df_po_2017_adj.at['Sudan', pop] = df_po_2017.at['Sudan', pop] + df_po_2017.at['South Sudan', pop]
df_po_2017_adj.at['Switzerland', pop] = df_po_2017.at['Switzerland', pop] + df_po_2017.at['Liechtenstein', pop]

# Recalculate population percentages
df_po_2017_adj['percent_population'] = (df_po_2017_adj['population'] / total_po_2017) * 100

# Merge percent world emissions and percent world population
df = df_em_2017_codes[['country', 'code', 'percent_emissions']].merge(df_po_2017_adj[['code', 'percent_population']])

# Create new column for 'score' and 'rounded_score'
df['score'] = df['percent_emissions'] / df['percent_population']
df['rounded_score'] = round(df['score'], 0)

import plotly.graph_objects as go
import plotly.express as px

fig = go.Figure(data=go.Choropleth(
    locations=df['code'], # Spatial coordinates
    z = df['score'].astype(float), # Data to be color-coded
    text = df['country'],
    colorscale = px.colors.sequential.Viridis,
    zmax = 4.0,
    zmin = 0.0,
    marker_line_color='darkgray',
    marker_line_width=0.5,
))

fig.update_layout(
    title_text='proportion of global CO2 emissions vs proportion of the global population',
    geo=dict(
        showframe=False,
        showcoastlines=False,
        projection_type='equirectangular'
    ),
)

fig.show()
