import pandas as pd
import datetime
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components
import pyodbc
from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL

files_id = pd.read_csv('id_stasiun.csv')

conn_str = 'DRIVER={SQL Server};server=DESKTOP-ELAQ9RU\SQLEXPRESS;Database=awlr_mondylia;Trusted_Connection=yes;'
con_url = URL.create('mssql+pyodbc', query={'odbc_connect': conn_str})
engine = create_engine(con_url)

id_list = files_id['CODE'].tolist()


for df in id_list:
    ID = files_id[files_id['CODE'] == df].index.values + 11
    globals() [f'query_{df}'] = f"""select pH, DO, Cond, Turb, Temp, NH4,NO3,ORP,COD,BOD,TSS,logTime as NH3_N,logDate, datepart(hour, logTime) as logTime from periodicdata where Station={int(ID)} order by logDate,logTime"""
    globals() [f'{df}'] = pd.read_sql(globals() [f'query_{df}'], engine)
    globals() [f"{df}['logDate']"] = pd.to_datetime(globals() [f'{df}']['logDate']).dt.date
    
    globals() [f'pH_{df}'] = [x for x in globals()[f'{df}'][-24:]['pH']]
    globals() [f'ab_pH_{df}'] = sum(map(lambda x : x<5 and x>9, globals()[f'pH_{df}']))
    globals() [f'DO_{df}'] = [x for x in globals()[f'{df}'][-24:]['DO']]
    globals() [f'ab_DO_{df}'] = sum(map(lambda x : x<1, globals()[f'DO_{df}']))
    globals() [f'NH4_{df}'] = [x for x in globals()[f'{df}'][-24:]['NH4']]
    globals() [f'ab_NH4_{df}'] = sum(map(lambda x : x>100, globals()[f'NH4_{df}']))
    globals() [f'NO3_{df}'] = [x for x in globals()[f'{df}'][-24:]['NO3']]
    globals() [f'ab_NO3_{df}'] = sum(map(lambda x : x>100, globals()[f'NO3_{df}']))
    globals() [f'tgl_{df}'] = globals()[f'{df}']['logDate'].max()


st.title('Status Stasiun ONLIMO')

def status_onlimo(id_ol):
    st.header(id_ol)
    globals()[f'header_a_{id_ol}'], globals()[f'header_b_{id_ol}'] = st.columns(2)
    

    if globals()[f'{id_ol}']['logDate'].max() == datetime.today().strftime('%Y-%m-%d'): 
        globals()[f'header_a_{id_ol}'].button(globals() [f'tgl_{id_ol}'], key=f'{id_ol}_a')
        globals()[f'header_b_{id_ol}'].success('ONLINE')

    elif datetime.strptime(globals() [f'tgl_{id_ol}'], '%Y-%m-%d') < datetime.today(): 
        globals()[f'header_a_{id_ol}'].button(globals() [f'tgl_{id_ol}'], key=f'{id_ol}_b')
        globals()[f'header_b_{id_ol}'].warning('OFFLINE')

    else:
        globals()[f'header_a_{id_ol}'].button(globals() [f'tgl_{id_ol}'], key=f'{id_ol}_b')                  
        globals()[f'header_b_{id_ol}'].error('ERROR')   

    col1, col2, col3, col4 = st.columns(4)
    col1.metric('pH', globals() [f'ab_pH_{id_ol}'], '{0:.2f}'. format(globals() [f'pH_{id_ol}'][-1]))
    col2.metric('DO', globals() [f'ab_DO_{id_ol}'], '{0:.2f}'. format(globals() [f'DO_{id_ol}'][-1]))
    col3.metric('NH', globals() [f'ab_NH4_{id_ol}'], '{0:.2f}'. format(globals() [f'NH4_{id_ol}'][-1]))
    col4.metric('NO', globals() [f'ab_NO3_{id_ol}'], '{0:.2f}'. format(globals() [f'NO3_{id_ol}'][-1]))

    st.markdown("""<hr style="height:5px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
    
    
    
for i in id_list:
    status_onlimo(i)