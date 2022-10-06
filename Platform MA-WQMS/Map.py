import streamlit as st
import streamlit_folium as st_folium
import folium 
import pandas as pd

df = pd.read_csv('coor.csv')

st.map(df)