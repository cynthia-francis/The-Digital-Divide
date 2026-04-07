import streamlit as st
import pandas as pd
import altair as alt
import pycountry
from vega_datasets import data

# --- 1. SETUP & INTRO ---
st.set_page_config(page_title="The Digital Divide", layout="wide", initial_sidebar_state="expanded")

st.title("🌐 Bridging the Gap: The Global Digital Divide (2000–2023)")
st.markdown("""
Despite the rapid expansion of the internet over the last two decades, a stark **Digital Divide** persists. 
This interactive dashboard explores the three critical pillars of global connectivity: 
1. **Access** (Who is online?) 
2. **Affordability** (Who can afford the data?) 
3. **Equality** (Are men and women getting online at the same rate?)
""")
st.divider()

# --- 2. DATA LOADING & CLEANING ---
@st.cache_data
def load_and_prep_data():
    df = pd.read_csv('cleaned_dashboard_data.csv')
    
    valid_countries = []
    iso_numerics = []
    
    for code in df['Country Code']:
        country = pycountry.countries.get(alpha_3=code)
        if country:
            valid_countries.append(True)
            iso_numerics.append(int(country.numeric)) 
        else:
            valid_countries.append(False)
            iso_numerics.append(None)
            
    df['is_valid'] = valid_countries
    df['iso_numeric'] = iso_numerics
    
    df = df[df['is_valid'] == True].drop(columns=['is_valid'])
    return df

df = load_and_prep_data()

# --- 3. THE NEW & IMPROVED SIDEBAR ---
st.sidebar.title("⚙️ Dashboard Controls")
st.sidebar.markdown("Use the slider below to travel through time and watch the global digital landscape shift.")

min_year = int(df['Year'].min())
max_year = int(df['Year'].max())
selected_year = st.sidebar.slider("📅 Select Year", min_year, max_year, 2022)

st.sidebar.divider()

st.sidebar.markdown("### 💡 Quick Insights")
st.sidebar.info("""
- **Watch the Map:** See how rapidly the Global South comes online after 2010.
- **The UN Target:** The UN aims for 1GB of data to cost < 2% of monthly income. Watch regions drop below this line over time!
- **The Equality Line:** In the final chart, dots above the dashed line indicate women are outpacing men in internet usage.
""")

st.sidebar.divider()
st.sidebar.markdown("📊 **Data Sources:**")
st.sidebar.caption("- Internet & GDP Data: [World Bank Open Data](https://data.worldbank.org/)")
st.sidebar.caption("- Mobile Data Pricing: [Best Broadband Deals](https://bestbroadbanddeals.co.uk/)")

# Filter data for the selected year for the charts
df_year = df[df['Year'] == selected_year]


# --- 4. VIZ 1: CHOROPLETH MAP ---
st.subheader(f"🌍 1. Global Connectivity ({selected_year})")
st.markdown("This map shows the percentage of the total population using the internet. *Gray countries indicate missing data for the selected year.*")

world_map = alt.topo_feature(data.world_110m.url, 'countries')

all_countries = []
for c in pycountry.countries:
    if hasattr(c, 'numeric'):
        all_countries.append({'id': int(c.numeric), 'Country Name': c.name})
df_all_countries = pd.DataFrame(all_countries)

background = alt.Chart(world_map).mark_geoshape(
    fill='lightgray', stroke='white', strokeWidth=0.5
).transform_lookup(
    lookup='id', from_=alt.LookupData(df_all_countries, 'id', ['Country Name'])
).transform_calculate(
    Usage="'Not Available'"
).encode(
    tooltip=[alt.Tooltip('Country Name:N', title='Country'), alt.Tooltip('Usage:N', title='Internet Usage %')]
).project('naturalEarth1')

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
    lookup='id', from_=alt.LookupData(df_year, 'iso_numeric', ['Country Name', 'Internet_Usage_Pct'])
).project('naturalEarth1').properties(height=500)

st.altair_chart((background + map_chart), use_container_width=True)
st.divider()


# --- 5. VIZ 2: AFFORDABILITY SCATTER PLOT ---
st.subheader(f"💰 2. The Affordability Crisis ({selected_year})")
st.markdown("Is data affordable? The UN's broadband target dictates that 1GB of mobile data should cost **less than 2% of a citizen's monthly income**.")
st.markdown("*Click a region in the legend to highlight its countries. The size of the bubble represents the raw cost of 1GB in USD.*")

df_scatter = df_year.dropna(subset=['Affordability_Pct', 'GDP_Per_Capita', 'Cost_1GB_USD', 'Region']).copy()

if not df_scatter.empty:
    global_min_gdp = df['GDP_Per_Capita'].min()
    global_max_gdp = df['GDP_Per_Capita'].max()

    highlight = alt.selection_point(fields=['Region'], bind='legend')

    scatter = alt.Chart(df_scatter).mark_circle(stroke='white', strokeWidth=0.5).encode(
        x=alt.X('GDP_Per_Capita:Q', 
                scale=alt.Scale(type='log', domain=[global_min_gdp, global_max_gdp]), 
                axis=alt.Axis(tickCount=5, format='$,.0f'), 
                title="GDP per Capita (Log Scale, USD)"),
        y=alt.Y('Affordability_Pct:Q', 
                scale=alt.Scale(domain=[0, 15], clamp=True), 
                axis=alt.Axis(tickCount=5), 
                title="% of Monthly Income for 1GB"),
        size=alt.Size('Cost_1GB_USD:Q', title="Raw Cost of 1GB ($)", scale=alt.Scale(type='sqrt', range=[10, 250])), 
        color=alt.Color('Region:N', title="Region", scale=alt.Scale(scheme='category20')),
        opacity=alt.condition(highlight, alt.value(0.8), alt.value(0.1)), 
        tooltip=[
            alt.Tooltip('Country Name:N', title='Country'),
            alt.Tooltip('Region:N', title='Region'),
            alt.Tooltip('Cost_1GB_USD:Q', title='1GB Cost ($)', format='$.2f'),
            alt.Tooltip('Affordability_Pct:Q', title='Income %', format='.2f'),
            alt.Tooltip('GDP_Per_Capita:Q', title='GDP per Capita ($)', format=',.0f')
        ]
    ).add_params(highlight)

    target_line = alt.Chart(pd.DataFrame({'y': [2]})).mark_rule(
        color='red', strokeDash=[5, 5], size=2
    ).encode(y='y:Q')
    
    # Using your exact anchor code!
    target_label = alt.Chart(pd.DataFrame({'y': [2], 'x': [global_min_gdp]})).mark_text(
        align='right',      
        baseline='middle',  
        dx=-18,             
        color='red', 
        text='UN Affordability Target',   
        fontSize=11, 
        fontWeight='bold'
    ).encode(x='x:Q', y='y:Q')

    st.altair_chart((scatter + target_line + target_label).properties(height=500), use_container_width=True)
else:
    st.info(f"Not enough pricing data available for the year {selected_year}.")
st.divider()


# --- 6. VIZ 3: EQUALITY SCATTER PLOT ---
st.subheader(f"🚻 3. Male vs. Female Access ({selected_year})")
st.markdown("Does the digital divide affect genders equally? Compare average male and female internet usage by region.")
st.markdown("*Dots **below** the dashed line indicate men have more access. Dots **above** indicate women lead.*")

df_gender = df_year.dropna(subset=['Male_Usage_Pct', 'Female_Usage_Pct', 'Region']).copy()

if not df_gender.empty:
    df_grouped = df_gender.groupby('Region')[['Male_Usage_Pct', 'Female_Usage_Pct']].mean().reset_index()
    highlight_gender = alt.selection_point(fields=['Region'], bind='legend')

    scatter_gender = alt.Chart(df_grouped).mark_circle(size=250).encode(
        x=alt.X('Male_Usage_Pct:Q', scale=alt.Scale(domain=[0, 100]), axis=alt.Axis(tickCount=5), title="Average Male Internet Usage (%)"),
        y=alt.Y('Female_Usage_Pct:Q', scale=alt.Scale(domain=[0, 100]), axis=alt.Axis(tickCount=5), title="Average Female Internet Usage (%)"),
        color=alt.Color('Region:N', title="Region", scale=alt.Scale(scheme='category20')),
        opacity=alt.condition(highlight_gender, alt.value(0.9), alt.value(0.2)),
        tooltip=[
            alt.Tooltip('Region:N', title='Region'),
            alt.Tooltip('Male_Usage_Pct:Q', title='Avg Male Usage %', format='.1f'),
            alt.Tooltip('Female_Usage_Pct:Q', title='Avg Female Usage %', format='.1f')
        ]
    ).add_params(highlight_gender)

    line_df = pd.DataFrame({'x': [0, 100], 'y': [0, 100]})
    equality_line = alt.Chart(line_df).mark_line(
        color='gray', strokeDash=[5, 5], size=2, opacity=0.7
    ).encode(x='x:Q', y='y:Q')

    st.altair_chart((equality_line + scatter_gender).properties(height=550), use_container_width=True)
    st.caption("*Note: The dashed diagonal line represents perfect gender equality. If a region lands exactly on this line, male and female usage are identical.*")
else:
    st.info(f"Not enough gender data available for the year {selected_year}.")