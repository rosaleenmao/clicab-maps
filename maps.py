import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import credentials
from pyairtable import Table

# SETUP
# this is just to get rid of an annoying warning that doesn't actually apply to this code
pd.options.mode.chained_assignment = None

# pull data from airtable
api_key = credentials.AIRTABLE_API_KEY

base_id = 'appK4hPIw3yecviBP'
table_id = 'tblUhVjXhOKsYqd3x'
# this is the fossil fuel plant only view
view_id = 'viwCiVUfX5kemiT2z'
fields = ['Plant Code', 'Generators from 1982 or older', 'Ownership']

table = Table(api_key, base_id, table_id)

# read EIA data and US map
plants_location = "shapefiles/Plants/PowerPlants_US_202108.shp"
US_map_location = "shapefiles/US/cb_2018_us_nation_20m.shp"

# read files into data frames
plants = gpd.read_file(plants_location)
US_map = gpd.read_file(US_map_location)

# DATA MODIFICATION
# create new columns in EIA data frames to insert airtable data into
plants['old_generators'] = 0
plants['ownership'] = ""

# insert airtable data into EIA data frames
for page in table.iterate(view = view_id, fields = fields):
    for airtable_plant in page:
        # store field values from airtable data
        fields = airtable_plant['fields']
        plant_code = fields['Plant Code']
        old_generators = fields['Generators from 1982 or older']
        ownership = fields['Ownership']

        # locate matching record in EIA data and set old_generators to correct value
        plants.loc[plants['Plant_Code'] == plant_code, ['old_generators']] = old_generators
        plants.loc[plants['Plant_Code'] == plant_code, ['ownership']] = ownership

# filter out unwanted plants
fossil_fuel_plants = plants[plants.ownership != '']
solely_owned_plants = plants[plants.ownership == 'S']
old_generator_plants = solely_owned_plants[solely_owned_plants.old_generators > 0]

# normalize plant size
scale = 500
base = 10

largest_plant_size = old_generator_plants['Total_MW'].max()
smallest_plant_size = old_generator_plants['Total_MW'].min()
plant_size_range = largest_plant_size - smallest_plant_size
old_generator_plants['norm_plant_size'] = (old_generator_plants.Total_MW - smallest_plant_size) / plant_size_range * scale + base

# create color buckets
old_generator_plants['old_generator_bucket'] = ""

old_generator_plants.loc[(old_generator_plants['old_generators'] > 0) & (old_generator_plants['old_generators'] <= 4), ['old_generator_bucket']] = '0-4'
old_generator_plants.loc[(old_generator_plants['old_generators'] > 4) & (old_generator_plants['old_generators'] <= 8), ['old_generator_bucket']] = '4-8'
old_generator_plants.loc[(old_generator_plants['old_generators'] > 8) & (old_generator_plants['old_generators'] <= 12), ['old_generator_bucket']] = '8-12'
# using U+200B ZERO-WIDTH SPACE for sorting purposes
old_generator_plants.loc[(old_generator_plants['old_generators'] > 12) & (old_generator_plants['old_generators'] <= 20), ['old_generator_bucket']] = "\u200B12-16"

# # print the columns in terminal
# # code for debugging
# pd.set_option("display.max_rows", None, 'display.max_columns',None)
# print(solely_owned_plants.head())

# PLOTTING
# create plots, set sizes, and hide axes
xlim1 = -130
xlim2 = -65
ylim1 = 22
ylim2 = 52

fig, ax1 = plt.subplots(figsize=(12,8))
ax1.set(xlim=(xlim1, xlim2), ylim=(ylim1, ylim2))
plt.axis('off')

fig, ax2 = plt.subplots(figsize=(12,8))
ax2.set(xlim=(xlim1, xlim2), ylim=(ylim1, ylim2))
plt.axis('off')

fig, ax3 = plt.subplots(figsize=(12,8))
ax3.set(xlim=(xlim1, xlim2), ylim=(ylim1, ylim2))
plt.axis('off')

fig, ax4 = plt.subplots(figsize=(12,8))
ax4.set(xlim=(xlim1, xlim2), ylim=(ylim1, ylim2))
plt.axis('off')

fig, ax5 = plt.subplots(figsize=(12,8))
ax5.set(xlim=(xlim1, xlim2), ylim=(ylim1, ylim2))
plt.axis('off')

# plot all plants
US_map.plot(ax=ax1, color='#ffffff', edgecolor='#6a6a6a')
plants.plot(ax=ax1, color='#440154', alpha = 0.5)

# filter by solely owned plants
US_map.plot(ax=ax2, color='#ffffff', edgecolor='#6a6a6a')
fossil_fuel_plants.plot(ax=ax2, color='#440154', alpha = 0.5)

# filter by solely owned plants
US_map.plot(ax=ax3, color='#ffffff', edgecolor='#6a6a6a')
solely_owned_plants.plot(ax=ax3, color='#440154', alpha = 0.5)

# filter by plants with generators older than 30
US_map.plot(ax=ax4, color='#ffffff', edgecolor='#6a6a6a')
old_generator_plants.plot(ax=ax4, color='#440154', alpha = 0.5)

# plot interactive map
US_map.plot(ax=ax5, color='#ffffff', edgecolor='#6a6a6a')
old_generator_plants.plot(ax=ax5, column='old_generator_bucket', markersize=old_generator_plants['norm_plant_size'], cmap='viridis', alpha=0.5)

# generate plot
plt.show()