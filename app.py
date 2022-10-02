import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from gapminder import gapminder

#######
# Data loading
#######

df = gapminder
year_values = (int(df["year"].min()), int(df["year"].max()))
metrics = ["lifeExp", "pop", "gdpPercap"]
dimension = ["country", "continent", "year"]

#######
# Helper functions
#######
def get_filtered_data(
    continents="All", 
    countries="All",
    min_year=year_values[0],
    max_year=year_values[1],
):
    if isinstance(continents, str) and continents != "All":
        mask_continent = df["continent"] == continents
    else:
        mask_continent = df["continent"].isin(continents)
    if isinstance(countries, str) and countries != "All":
        mask_country = df["country"] == countries
    else:
        mask_country = df["country"].isin(countries)
    mask_year = ((df["year"] >= min_year) & (df["year"] <= max_year))
    return df[mask_continent & mask_country & mask_year]
        
def box_plot(df, x, y):
    fig = px.box(
        df, x=x, y=y, hover_data=df[dimension + [x]],
        points="all", color=x)
    return fig

def scatter_plot(df, x, y, hue):
    fig = px.scatter(
        df, x=x, y=y, 
        color=hue, symbol=hue)
    return fig


def line_plot(df, y_axis, label, highlighted):
    fig = go.Figure()
    if label=="continent":
        df = df.groupby(["continent", "year"]).agg({
            "lifeExp": "mean", 
            "pop": "sum",
            "gdpPercap": "mean",
        }).reset_index()
    
    for i in df[label].unique():
        if i == highlighted:
            continue
        data = df[df[label]==i]
        x = data["year"]
        y = data[y_axis]
        fig.add_trace(go.Scatter(x=x, y=y, 
            hovertext=[
                f"{label}: {i}<br>year: {year}<br>{y_axis}: {value}"
                for year, value in zip(x,y)
            ],
            hoverinfo="text",
            mode='lines',
            line = dict(color='gray', width=1),
            # name=i
        ))
    
    data = df[df[label]==highlighted]
    x = data["year"]
    y = data[y_axis]
    fig.add_trace(go.Scatter(x=x, y=y, 
        hovertext=[
            f"{label}: {highlighted}<br>year: {year}<br>{y_axis}: {value}"
            for year, value in zip(x,y)
        ],
        hoverinfo="text",
        mode='lines',
        line = dict(color='orange', width=10),
        # name=highlighted
    ))
    
    fig.update_layout(showlegend=False)
    return fig

#######
# Streamlit app code
#######

st.title('[Gapminder] Exploratory Data Analysis')

st.markdown("## Gapminder Table")
selected_continents = st.multiselect("Select Continents:", df["continent"].unique(), key="table_continent")
selected_countries = st.multiselect("Select Countries:", df.loc[df["continent"].isin(selected_continents), "country"].unique(), key="table_country")
min_year, max_year = st.slider("Select Year:", year_values[0], year_values[1], year_values, key="table_year")
st.dataframe(get_filtered_data(selected_continents, selected_countries, min_year, max_year))

st.markdown("## Gapminder Boxplot")
col1, col2 = st.columns(2)
with col1:
    x = st.selectbox("Select x Axis", dimension, "continent", key="boxplot_x")
with col2:
    y = st.selectbox("Select y Axis", metrics, key="boxplot_y")
st.plotly_chart(box_plot(df, x, y))

st.markdown('## Gapminder Lineplot')
col1, col2, col3 = st.columns(3)
with col3:
    label = st.radio("Select label", ["country", "continent"], key="lineplot_label")
with col1:
    highlighted = st.selectbox("Select value to hightlight", df[label].unique(), key="lineplot_highlighting")
with col2:
    y = st.selectbox("Select hue", metrics, key="lineplot_y")
st.plotly_chart(line_plot(df, y, label, highlighted))


st.markdown('## Gapminder Scatterplot')
col1, col2, col3 = st.columns(3)
with col1:
    x = st.selectbox("Select x Axis", metrics, key="scatterplot_x")
with col2:
    y = st.selectbox("Select y Axis", metrics, key="scatterplot_y")
with col3:
    hue = st.radio("Select hue", ["country", "continent"], key="scatterplot_hue")
st.plotly_chart(scatter_plot(df, x, y, hue))
