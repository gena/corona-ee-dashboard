import requests
import pandas as pd
import geopandas as gpd
import matplotlib.pylab as plt
import datetime as dt

from dateutil.parser import parse
import pytz

import sys

if len(sys.argv) != 2:
    print('Usage: <script> USE_NRT_FLAG')
    print('USE_NRT_FLAG - True or False')
    sys.exit(1)

use_nrt = sys.argv[1]

print('Reading and converting cases from JHU GitHub ...')

df_confirmed = pd.read_csv('../data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv')
df_deaths = pd.read_csv('../data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv')
df_recovered = pd.read_csv('../data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv')

dates = df_confirmed.columns[4:]

items = []
for i in range(len(df_confirmed)):
    for date in dates:
        t = parse(date)
        t = t.replace(tzinfo=pytz.UTC)
        o = {
            'province': df_confirmed.iloc[i]['Province/State'],
            'country': df_confirmed.iloc[i]['Country/Region'],
            'lon': df_confirmed.iloc[i]['Long'],
            'lat': df_confirmed.iloc[i]['Lat'],
            't': int(t.timestamp() * 1000),
            'confirmed': df_confirmed.iloc[i][date],
            'recovered': df_recovered.iloc[i][date],
            'deaths': df_deaths.iloc[i][date]
        }
        
        items.append(o)

df = pd.DataFrame(items)

# geopandas
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat))

gdf['dt'] = pd.to_datetime(gdf.t, unit='ms')
gdf['dt'] = gdf['dt'].apply(lambda x: dt.datetime.strftime(x, '%Y-%m-%d'))

if use_nrt == 'True':
    # update NRT data
    print('Fetching recent updates ...')

    # read recent
    url = r'https://services1.arcgis.com/0MSEUqKaxRlEPj5g/arcgis/rest/services/Coronavirus_2019_nCoV_Cases/FeatureServer/1/query?where=Deaths+%3E+-100&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&resultType=standard&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&outFields=*&returnGeometry=true&featureEncoding=esriDefault&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&returnZ=false&returnM=false&returnExceededLimitFeatures=true&quantizationParameters=&sqlFormat=none&f=pgeojson&token='

    r = requests.get(url)

    open('../data/covid19_recent.geojson', 'w').write(r.text)
    gdf_cases_recent = gpd.read_file('../data/covid19_recent.geojson')

    mapping = {'Province_State': 'province', 'Country_Region': 'country', 'Long_': 'lon', 'Lat': 'lat', 
               'Last_Update': 't', 'Confirmed': 'confirmed', 'Recovered': 'recovered', 'Deaths': 'deaths'}

    gdf_cases_recent = gdf_cases_recent.rename(columns=mapping)
                                            
    cols = list(mapping.values()) + ['geometry']
    gdf_cases_recent = gdf_cases_recent[cols]

    # merge
    gdf_cases_recent['dt'] = pd.to_datetime(gdf_cases_recent.t, unit='ms')
    gdf_cases_recent['dt'] = gdf_cases_recent['dt'].apply(lambda x: dt.datetime.strftime(x, '%Y-%m-%d'))

    t_cases_last = list(gdf.sort_values('dt').dt.unique())[-1]
    print('Last date in data from GitHub: ', t_cases_last)

    t_cases_last_recent = list(gdf_cases_recent.sort_values('dt').dt.unique())[-1]
    print('Last date in data from ArcGIS: ', t_cases_last_recent)

    gdf_cases_prev_day=gdf[gdf.dt == t_cases_last].copy()
    merged = pd.concat([gdf_cases_prev_day, gdf_cases_recent])
    merged['country'].fillna(value='none', inplace=True)
    merged['province'].fillna(value='none', inplace=True)
    merged['country_province'] = merged['country'] + merged['province']

    merged_unique = merged.groupby(['country_province']).max()
    rows = []
    for i, row in merged_unique.iterrows():
        row['geometry'] = merged[merged.country_province == row.name].iloc[0]['geometry']
        rows.append(row)
    merged_unique = pd.DataFrame(rows)
    merged_unique['dt_reported'] = merged_unique['dt']
    merged_unique['dt'] = t_cases_last_recent

    gdf_recent = gpd.GeoDataFrame(merged_unique)

    # gdf_recent.to_file("../data/covid19_recent.geojson", driver='GeoJSON')
    # merged_unique.to_csv("../data/covid19_recent.csv")
    # gdf_recent.to_file('../data/covid19_recent') # shp

    gdf = pd.concat([gdf, gdf_recent])

print('Saving to geojson and shp ...')

gdf.to_file("../data/covid19.geojson", driver='GeoJSON')
gdf.to_csv("../data/covid19.csv")
gdf.to_file('../data/covid19') # shp

print('Generating aggregated ...')

# aggregated
agg = gdf.groupby(['dt']).sum()[['confirmed', 'recovered', 'deaths']]
agg.to_json('../data/covid19_aggregated.json')

