# 🌐 Bridging the Gap: The Global Digital Divide (2000–2023)

An interactive data visualization dashboard built with **Python, Streamlit, and Altair** that explores the historical progression of global internet adoption. 

Despite the rapid expansion of the internet over the last two decades, a stark **Digital Divide** persists. This dashboard explores the three critical pillars of global connectivity:
1. **Access:** How much of the population is actually online?
2. **Affordability:** Can citizens afford mobile data based on their local GDP?
3. **Equality:** Is there a gap between male and female internet usage?

## 📊 Data Sources
The data powering this dashboard was aggregated and cleaned from two primary sources:
* **[World Bank Open Data](https://data.worldbank.org/):** Provided historical data on GDP per capita, overall internet usage, and gender-specific internet usage.
* **[Best Broadband Deals](https://bestbroadbanddeals.co.uk/):** Provided the 2023 global pricing data for 1GB of mobile data.

## 🛠️ Tech Stack
* **Language:** Python
* **Data Cleaning & Engineering:** Pandas, Jupyter Notebook
* **Dashboard Framework:** Streamlit
* **Visualizations:** Altair (Vega-Lite)
* **Geospatial & Country Data:** `pycountry`, `vega_datasets`

## 📁 Project Structure
```text
THE-DIGITAL-DIVIDE/
│
├── data/                               # Raw datasets from World Bank & Kaggle
│   ├── GDP per capita/
│   ├── Internet Usage (Men)/
│   ├── Internet Usage (Population)/
│   ├── Internet Usage (Women)/
│   └── worldwide_mobile_data_pricing_data.xlsx
│
└── script/
    ├── app.py                          # The main Streamlit dashboard application
    ├── data_cleaning.ipynb             # Jupyter Notebook detailing the data merging/cleaning 
    └── cleaned_dashboard_data.csv      # The final cleaned dataset used by the dashboard
```
## 🚀 How to Run the Dashboard Locally

Follow these steps to run the app on your own machine:

**1. Clone or download this repository**
Open your terminal and navigate to the main project folder:
```bash
cd THE-DIGITAL-DIVIDE
```
**2. Install the required Python packages**
Ensure you have Python installed, then run the following command to install the dependencies:
```bash
pip install streamlit pandas altair pycountry vega_datasets
```
**3. Install the required Python packages**
Because the app and the dataset live inside the script directory, you must move into that folder before launching the app:
```bash
cd script
```
**4. Launch the Streamlit App**
After running this, the dashboard will automatically open in your default web browser.
```bash
streamlit run app.py
```
