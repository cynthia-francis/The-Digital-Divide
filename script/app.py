import streamlit as st
import pandas as pd
import altair as alt
import pycountry
from vega_datasets import data

# --- 1. SETUP ---
st.set_page_config(page_title="The Digital Divide Dashboard", layout="wide")
st.title("🌐 The Hidden Digital Divide (2000 - 2024)")
st.markdown("An interactive exploration of global internet adoption, affordability, and the gender gap.")

# --- 2. DATA LOADING & CLEANING ---
@st.cache_data
def load_and_prep_data():
    # Load your exact CSV
    df = pd.read_csv('cleaned_dashboard_data.csv')
    
    # 1. FILTER OUT AGGREGATES (Regions, Income Groups, etc.)
    # We only want real countries. Real countries have a 3-letter ISO code that pycountry recognizes.
    valid_countries = []
    iso_numerics = []
    
    for code in df['Country Code']:
        country = pycountry.countries.get(alpha_3=code)
        if country:
            valid_countries.append(True)
            iso_numerics.append(int(country.numeric)) # Altair's map requires this numeric ID
        else:
            valid_countries.append(False)
            iso_numerics.append(None)
            
    df['is_valid'] = valid_countries
    df['iso_numeric'] = iso_numerics
    
    # Keep only valid countries and drop the helper column
    df = df[df['is_valid'] == True].drop(columns=['is_valid'])
    
    # Create a Gender Gap column for sorting the dumbbell plot later
    df['Gender_Gap'] = df['Male_Usage_Pct'] - df['Female_Usage_Pct']
    
    return df

df = load_and_prep_data()

# --- 3. SIDEBAR CONTROLS ---
st.sidebar.header("Dashboard Controls")
# Get min and max year from data, default to 2022 since 2023/2024 are sparse
min_year = int(df['Year'].min())
max_year = int(df['Year'].max())
selected_year = st.sidebar.slider("Select Year", min_year, max_year, 2022)

# Filter data for the selected year
df_year = df[df['Year'] == selected_year]

st.markdown(f"### Data for **{selected_year}**")
st.divider()

# --- 4. ALTAIR VIZ 1: CHOROPLETH MAP ---
st.subheader("🌍 1. Global Connectivity Map")
st.markdown("Percentage of the population using the internet.")

# Load Altair's built-in world map topology
world_map = alt.topo_feature(data.world_110m.url, 'countries')

map_chart = alt.Chart(world_map).mark_geoshape(stroke='white', strokeWidth=0.5).encode(
    color=alt.Color('Internet_Usage_Pct:Q', 
                    scale=alt.Scale(scheme='teals', domain=[0, 100]), 
                    title="Internet Usage (%)",
                    legend=alt.Legend(orient='bottom', direction='horizontal', gradientLength=400)),
    tooltip=[
        alt.Tooltip('Country Name:N', title='Country'),
        alt.Tooltip('Internet_Usage_Pct:Q', title='Internet Usage %', format='.1f')
    ]
).transform_lookup(
    lookup='id', # The numeric ID in the topojson map
    from_=alt.LookupData(df_year, 'iso_numeric', ['Country Name', 'Internet_Usage_Pct'])
).project(
    type='naturalEarth1' # A clean, modern map projection
).properties(
    height=500
)

# Add a background for missing data (gray)
background = alt.Chart(world_map).mark_geoshape(fill='lightgray', stroke='white').project('naturalEarth1')
st.altair_chart((background + map_chart), use_container_width=True)

st.divider()

# --- 5. ALTAIR VIZ 2: AFFORDABILITY SCATTER PLOT ---
st.subheader("💰 2. The Affordability Crisis")
st.markdown("The UN target is for 1GB of data to cost **less than 2%** of monthly GNI per capita.")

# Filter out rows missing the affordability data so the chart doesn't break
df_scatter = df_year.dropna(subset=['Affordability_Pct', 'GDP_Per_Capita', 'Cost_1GB_USD'])

if not df_scatter.empty:
    scatter = alt.Chart(df_scatter).mark_circle(opacity=0.7).encode(
        x=alt.X('GDP_Per_Capita:Q', scale=alt.Scale(type='log'), title="GDP per Capita (Log Scale, USD)"),
        y=alt.Y('Affordability_Pct:Q', scale=alt.Scale(domain=[0, 20], clamp=True), title="% of Monthly Income for 1GB"),
        size=alt.Size('Cost_1GB_USD:Q', title="Raw Cost of 1GB ($)", scale=alt.Scale(range=[20, 500])),
        color=alt.Color('Affordability_Pct:Q', scale=alt.Scale(scheme='redyellowblue', reverse=True), legend=None),
        tooltip=['Country Name', 'Cost_1GB_USD', 'Affordability_Pct', 'GDP_Per_Capita']
    )

    # Draw the UN 2% Threshold Line
    target_line = alt.Chart(pd.DataFrame({'y': [2]})).mark_rule(
        color='red', strokeDash=[5, 5]
    ).encode(y='y:Q')

    st.altair_chart((scatter + target_line).properties(height=450), use_container_width=True)
else:
    st.info(f"Not enough cost data available for the year {selected_year} to display this chart. Try selecting 2021 or 2022.")

st.divider()

# --- 6. ALTAIR VIZ 3: GENDER GAP DUMBBELL PLOT ---
st.subheader("🚻 3. The Hidden Divide: Male vs. Female Access")
st.markdown("Countries with the largest gap between male and female internet usage.")

# Filter and get top 20 countries with the largest gender gap
df_gender = df_year.dropna(subset=['Male_Usage_Pct', 'Female_Usage_Pct']).copy()

if not df_gender.empty:
    df_gender = df_gender.sort_values(by='Gender_Gap', ascending=False).head(20)

    # Melt the data specifically for the dumbbell plot
    df_melted = pd.melt(df_gender, id_vars=['Country Name', 'Gender_Gap'], 
                        value_vars=['Male_Usage_Pct', 'Female_Usage_Pct'], 
                        var_name='Gender', value_name='Usage')

    # The connecting line
    line = alt.Chart(df_melted).mark_line(color='lightgray', size=3).encode(
        x='Usage:Q',
        y=alt.Y('Country Name:N', sort=alt.EncodingSortField(field='Gender_Gap', order='descending'), title=""),
        detail='Country Name:N'
    )

    # The dots (Colored by Gender)
    points = alt.Chart(df_melted).mark_circle(size=150, opacity=1).encode(
        x=alt.X('Usage:Q', title="Internet Usage (%)"),
        y=alt.Y('Country Name:N', sort=alt.EncodingSortField(field='Gender_Gap', order='descending')),
        color=alt.Color('Gender:N', 
                        scale=alt.Scale(domain=['Male_Usage_Pct', 'Female_Usage_Pct'], range=['#1f77b4', '#ff7f0e']),
                        legend=alt.Legend(title="Demographic")),
        tooltip=[alt.Tooltip('Country Name:N'), alt.Tooltip('Gender:N'), alt.Tooltip('Usage:Q', format='.1f')]
    )

    st.altair_chart((line + points).properties(height=500), use_container_width=True)
else:
    st.info(f"Not enough gender data available for the year {selected_year} to display this chart.")