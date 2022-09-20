import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from matplotlib.widgets import CheckButtons
from datetime import datetime, timedelta, date
import datetime
import pyodbc
from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL
from numpy import load

st.title('Perbandingan Data Parameter Periode Waktu (6H)')

files_id = pd.read_csv('id_stasiun.csv')

data_24 = load('jam_24.npy', allow_pickle = True)
df_nan = pd.read_csv('df_nan.csv')
index = np.arange(1,25)
df_test = pd.read_csv('testml.csv')

ID_choice = st.selectbox('Stasiun', files_id['CODE'])
ID = files_id[files_id['CODE']==ID_choice].index.values + 11


#import data from SQL Server
conn_str = 'DRIVER={SQL Server};server=DESKTOP-ELAQ9RU\SQLEXPRESS;Database=awlr_mondylia;Trusted_Connection=yes;'
con_url = URL.create('mssql+pyodbc', query={'odbc_connect': conn_str})
engine = create_engine(con_url)

query = f"""select pH, DO, Cond, Turb, Temp, NH4,NO3,ORP,COD,BOD,TSS,logTime as NH3_N,logDate, datepart(hour, logTime) as logTime 
from periodicdata where Station={int(ID)} order by logDate,logTime"""

df = pd.read_sql(query, engine, coerce_float=False)
df['logDate'] = pd.to_datetime(df['logDate']).dt.date


#drop today data
tgl = date.today()
df = df.loc[df['logDate'] != tgl]
df = df.loc[(df['logDate'] >= date.fromisoformat('2021-09-21'))]

tanggal = np.unique(df['logDate'].values)
j = len(tanggal)

#ID Stasiun KLHK

#array data daily
arr = []

for i in tanggal:
    df_tgl = df.loc[df['logDate'] == i]

    if not np.array_equiv(df_tgl['logTime'].values, data_24):
        df_clean = df_tgl.drop_duplicates(subset='logTime', keep='last')
        df_clean = pd.concat([df_clean, df_nan])
        df_clean = df_clean.sort_values(by=['logTime'])
        df_clean = df_clean.fillna(method='ffill').fillna(method='bfill')
        df_clean = df_clean.drop_duplicates(subset='logTime', keep='last')
        df_clean.drop(columns=df_clean.columns[-1], axis=1, inplace=True)
        arr_clean = df_clean.to_numpy()
        arr.append(arr_clean)

    else:
        arr_clean = df_tgl.to_numpy()
        arr.append(arr_clean)

arr = np.asarray(arr)

cols = df.columns.values.tolist()
len_arr = arr.shape[0]*arr.shape[1]

arr_df = arr.reshape(len_arr,14)
arr_df = pd.DataFrame(arr_df,  columns = cols)

time_ind = arr_df.logTime.astype(int).astype(str)
time_lis = []
for i in time_ind:
    if len(i) < 2:
        i = '0' + i
    time_lis.append(i)
    
df_index = pd.to_datetime(arr_df.logDate.astype(str) + ' ' + time_lis)    
arr_df.set_index(df_index, inplace=True)
arr_df = arr_df.asfreq(freq='H')
arr_df = arr_df.fillna(0)
data_arr = arr_df.to_numpy()

def charts(y_series, xval, alfa, title=' '):
    
    fig = plt.figure(figsize = (10,7))
      
    plt.plot(xval, y_series[0], 'c', alpha=alfa[0], label='subuh')
    plt.plot(xval, y_series[1], 'y', alpha=alfa[1], label='pagi')
    plt.plot(xval, y_series[2], 'r', alpha=alfa[2], label='siang')
    plt.plot(xval, y_series[3], color='green', alpha=alfa[3], label='malam')
    plt.title(title)
    plt.legend()
    return fig


alfa_val = [0,0,0,0]


col1, col2, col3 = st.columns([1,1,1])

with col1:
    d1 = st.date_input('Tanggal Awal', datetime.date(2021,9,21))
    d2 = st.date_input('Tanggal Akhir' , datetime.date(2021,9,22))
    d3=d2-d1
    d3=d3.days
    #st.write('d3', d3)
    
    
with col2:
    param = st.radio('Parameter:', ('pH', 'DO', 'COD', 'BOD', 'NH4', 'NO3', 'Temp'))
    arr_t = arr_df[param].to_numpy()
    arr_t = arr_t.reshape(int(data_arr.shape[0]/24),4,6)
    
    #asumsi tanggal awal : 01-08-2022
    ref = datetime.date(2021,9,21)
    ref_add = (d1 - ref).days
    
    i = ref_add + d3
    x1 = d1
    x2 = d2
    #st.write(ref_add)
    #st.write(i)
    subuh = arr_t[ref_add:i, 0, :].flatten()
    pagi = arr_t[ref_add:i, 1, :].flatten()
    siang = arr_t[ref_add:i, 2, :].flatten()
    malam = arr_t[ref_add:i, 3, :].flatten()
    
    #st.write(len(subuh))

    periode = [subuh,pagi,siang,malam]
    x = [x+1 for x in range(len(subuh))]

with col3:
    st.write('periode waktu')
    #checkbox periode
    st_subuh = st.checkbox('Subuh')
    st_pagi = st.checkbox('Pagi', key='pagi')
    st_siang = st.checkbox('Siang')
    st_malam = st.checkbox('Malam')
    status_periode = [st_subuh, st_pagi, st_siang, st_malam]
    

    if all(status_periode):
        for i in range(len(alfa_val)):
            alfa_val[i] = 1

    if any(status_periode):
        for i in range(len(alfa_val)):
            if status_periode[i] == 1:
                alfa_val[i] = 1
                
suhu = charts(periode, x, alfa_val, f'Grafik {param} Sungai')
st.write(suhu)    

    
    
    
    
    
    
    