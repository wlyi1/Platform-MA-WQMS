import pandas as pd
import numpy as np
from numpy import load
import pyodbc
from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL
import datetime
from statsmodels.tsa.stattools import adfuller
from datetime import datetime, timedelta, date
import matplotlib.pyplot as plt
import datetime
import streamlit as st

st.title('Analisis Timeseries')

def chart(datum, parameter):
    #create new graph
    fig = plt.figure(figsize = (20,5))
    datum.plot(figsize = (20,5))
    plt.title(f'Grafik {parameter} vs Times', size = 24)
    return fig

data_24 = load('jam_24.npy', allow_pickle = True)
df_nan = pd.read_csv('df_nan.csv')
index = np.arange(1,25)

#select stasiun
files_id = pd.read_csv('id_stasiun.csv')
ID_choice = st.selectbox('Stasiun', files_id['CODE'])
ID = files_id[files_id['CODE']==ID_choice].index.values + 11

#import data from SQL Server
conn_str = 'DRIVER={SQL Server};server=DESKTOP-ECB4MMH\SQLEXPRESS;Database=awrl;Trusted_Connection=yes;'
con_url = URL.create('mssql+pyodbc', query={'odbc_connect': conn_str})
engine = create_engine(con_url)

query = f"""select pH, DO, Cond, Turb, Temp, NH4,NO3,ORP,COD,BOD,TSS,logTime as NH3_N,logDate, datepart(hour, logTime) as logTime 
from data where Station={int(ID)} order by logDate,logTime"""

df = pd.read_sql(query, engine, coerce_float=False)
df['logDate'] = pd.to_datetime(df['logDate']).dt.date


#drop today data
tgl = date.today()
df = df.loc[df['logDate'] != tgl]
df = df.loc[(df['logDate'] >= date.fromisoformat('2021-09-21'))]

tanggal = np.unique(df['logDate'].values)
j = len(tanggal)

parameter = st.selectbox('Parameter untuk dilihat data dan grafiknya', ('pH', 'DO', 'NH4', 'NO3', 'COD', 'BOD', 'Temp'))

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

del arr_df['logDate']
del arr_df['logTime']
del arr_df['NH3_N']
col = arr_df.columns.values.tolist()
#mean each column
mean = arr_df.filter(col).mean()

arr_df[col] = arr_df[col].fillna(arr_df.mean().iloc[0])

data_arr = arr_df.to_numpy()

data = arr_df[f'{parameter}']

#create chart
for i in ['pH', 'DO', 'NH4', 'NO3', 'COD', 'BOD', 'Temp']:
    globals()[f'{i}'] = chart(data, i)

for i in ['pH', 'DO', 'NH4', 'NO3', 'COD', 'BOD', 'Temp']:
    if parameter == i:
        st.write(globals() [i])
    

X = data.values
result = adfuller(X)
st.write('ADF Statistic: %f' % result[0])
st.write('p-value: %f' % result[1])
st.write('Critical Values:')
for key, value in result[4].items():
    st.write('\t%s: %.3f' % (key, value))
    
st.write('--------') 
st.subheader('Test Stationarity')
if result[1] <= 0.05:
    st.write('Stationary')
else:
    st.write('Non-stationary')