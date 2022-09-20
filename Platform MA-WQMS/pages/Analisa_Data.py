import pyodbc
import pandas as pd
from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL
from datetime import date
import datetime as dt
import numpy as np
from datetime import datetime
from numpy import load
from sklearn.model_selection import train_test_split
import streamlit as st
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.metrics import accuracy_score   
from sklearn.model_selection import cross_val_score

st.title('Data Normal dan Anomali')

#list function
def data_anom():
    result_DO = [x for x in df_con['DO']]
    result_pH = [x for x in df_con['pH']]
    result_NH = [x for x in df_con['NH4']]
    result_NO = [x for x in df_con['NO3']]
    ab_pH = sum(map(lambda x : x<5 and x>9, result_pH))
    ab_DO = sum(map(lambda x : x<1, result_DO))
    ab_NH4 = sum(map(lambda x : x>100, result_NH))
    ab_NO3 = sum(map(lambda x : x>100, result_NO))
    
    locals_stored = list(locals())
    list_var = dict()
    for i in locals_stored:
        list_var[i] = eval(i)
    return list_var

def ml(data_input):
    #training machine learning model
    X = df_test.drop('Status', axis = 1)
    y = df_test['Status']

    test_size = 0.3
    seed = 7
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=seed)
    NN = KNeighborsClassifier(n_neighbors=5)
    NN.fit(X_train, y_train)
    y_pred = NN.predict(X_test)
    status = NN.predict(data_input)
    return status

def data(param):
    arr1 = param.reshape(j,4,6)
    

    mean = []
    std_data = []
    std_grad = []
    max_data = []
    min_data = []
    
    for x in range(j):
        y = arr1[x].flatten()
        y_g = np.gradient(arr1[x].flatten())
        x_mean = np.mean(y)
        x_std = np.std(y)
        x_g_std = np.std(y_g)
        x_max = np.max(y)
        x_min = np.min(y)
        mean.append(x_mean)
        std_data.append(x_std)
        std_grad.append(x_g_std)
        max_data.append(x_max)
        min_data.append(x_min)

    df_ml = pd.DataFrame(list(zip(mean, max_data, min_data, std_data, std_grad)), columns = ['Mean', 'Max', 'Min', 'Std_Data', 'Std_Gradient'])
    arr_ml = df_ml.to_numpy()
        
    df_ml['TGL'] = df['logDate'].unique()
    #st.write(df_ml)
    df_ml['TGL'] = df_ml['TGL'].apply(lambda x: dt.datetime.strftime(x, '%Y-%m-%d'))

    df_ml = df_ml.set_index(pd.DatetimeIndex(df_ml['TGL']))
    df_ml.index = df_ml.index.strftime('%Y-%m-%d')
    
    return arr, df_ml, arr_ml

#import pre data
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

df = pd.read_sql(query, engine)
df['logDate'] = pd.to_datetime(df['logDate']).dt.date



#drop today data
tgl = date.today()
df = df.loc[df['logDate'] != tgl]
tanggal = np.unique(df['logDate'].values)
j = len(tanggal)
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
x_arr = arr[:,:,6].flatten()   

#input tanggal user
tgl = st.date_input('Tanggal' , dt.date(2022,1,2))

#return 1 dataframe date
cols = df.columns.values.tolist()
len_arr = arr.shape[0]*arr.shape[1]

arr_df = arr.reshape(len_arr,14)
df_con = pd.DataFrame(arr_df, columns = cols)

df_con = df_con.set_index(df_con['logDate'])
df_con = df_con.loc[tgl]       
#st.write(df_con)
   

tab1, tab2, tab3, tab4 = st.tabs(['pH', 'DO', 'NH4', 'NO3'])
name_param = ['pH', 'DO', 'NH4', 'NO3']
stat_data = data_anom()
posisi_param = [0,1,5,6]



l_tab = [tab1, tab2, tab3, tab4]
for i1,j2,z in zip(l_tab, name_param, posisi_param):
    with i1:
        col_an1, col_an2 = st.columns(2)
        col_an1.metric(label = 'Baku Mutu', value=24 - stat_data[f'ab_{j2}'])
        col_an2.metric(label = 'Tidak Baku Mutu', value=stat_data[f'ab_{j2}'])
        st.header(f'Analisis Anomali Sensor {j2}')
        st.text('Analisis menggunakan algoritma machine learning KNN')
        
        par_arr = arr[:,:,z].flatten()
        
        globals() [f'data_{j2}'] = data(par_arr)
        status = ml(globals() [f'data_{j2}'][2])
        globals() [f'data_{j2}'][1]['Status'] = status
        #d1 = st.date_input('Pilih Tanggal', dt.date(2022,1,2))  
        d1 = tgl.strftime('%Y-%m-%d') 
        #st.write(data_no3[1])
        stt = globals() [f'data_{j2}'][1]['Status'].loc[d1]
        #st.write(stt)

        stats = globals() [f'data_{j2}'][1]['Status'].loc[d1]

        if stats == 'Normal':
            st.success(f'Sensor {j2} Normal')
        else:
            st.error(f'Sensor {j2} Anomali')
        
        st.header(f'Jumlah Hari Anomali {j2}')
        globals() [f'{j2}_arr'] = arr[:,:,z].flatten()
        globals() [f'df_{j2}'] = data(globals() [f'{j2}_arr'])
        globals() [f'status_{j2}'] = ml(globals() [f'df_{j2}'][2])

        globals() [f'df_{j2}'][1]['Status'] = globals() [f'status_{j2}']
        globals() [f'df_{j2}_st'] = globals() [f'df_{j2}'][1]['Status'].value_counts()
        st.write(globals() [f'df_{j2}_st'])
        st.subheader('Tanggal Data Sensor Anomali')
        st.write(globals() [f'df_{j2}'][1]['TGL'].loc[globals() [f'df_{j2}'][1]['Status'] == 'Anomali'])


        
st.write(":heavy_minus_sign:" * 32)






