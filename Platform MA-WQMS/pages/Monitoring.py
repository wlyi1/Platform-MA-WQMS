import pandas as pd
import datetime
from datetime import datetime as dt
import streamlit as st
import streamlit.components.v1 as components
import pyodbc
from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL
import matplotlib.pyplot as plt

def chart(ylabel, xlabel, yvalues, xvalues, title=''):
    #create new graph
    
    fig = plt.figure(figsize = (10,7))
    plt.plot(xvalues, yvalues)
    plt.title(title, fontsize = 20, fontweight = 'bold')
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    return fig

st.title('Data 24 HRS')

files_id = pd.read_csv('id_stasiun.csv')

ID_choice = st.selectbox('Stasiun', files_id['CODE'])
ID = files_id[files_id['CODE']==ID_choice].index.values + 11


#import data from SQL Server
conn_str = 'DRIVER={SQL Server};server=DESKTOP-ELAQ9RU\SQLEXPRESS;Database=awlr_mondylia;Trusted_Connection=yes;'
con_url = URL.create('mssql+pyodbc', query={'odbc_connect': conn_str})
engine = create_engine(con_url)

query = f"""select pH, DO, Cond, Turb, Temp, NH4,NO3,ORP,COD,BOD,TSS,logTime as NH3_N,logDate, datepart(hour, logTime) as logTime 
from periodicdata where Station={int(ID)} order by logDate,logTime"""

df = pd.read_sql(query, engine, coerce_float=False)
#f['logDate'] = pd.to_datetime(df['logDate']).dt.date


df['tgl'] = pd.to_datetime(df['logDate'] + ' ' + df['NH3_N'])
#st.write(df[-24:])

result_DO = [x for x in df[-24:]['DO']]
result_pH = [x for x in df[-24:]['pH']]
result_SUHU = [x for x in df[-24:]['Temp']]
result_NH = [x for x in df[-24:]['NH4']]
result_NO = [x for x in df[-24:]['NO3']]

st.title('Grafik Parameter 24 Jam Terakhir')
option = st.selectbox('Parameter untuk dilihat data dan grafiknya', ('pH', 'DO', 'NH4', 'NO3'))


#empty chart
c1, c2 = st.columns(2)
with c1:
    if 'space_initial' not in st.session_state:
        st.session_state.space_initial = st.empty()
with c2:
    if 'space_initial_2' not in st.session_state:
        st.session_state.space_initial_2 = st.empty()

#chart parameter
pH = chart('pH', 'Date', df[-24:]['pH'], df[-24:]['tgl'], title= 'Grafik pH')
DO = chart('DO', 'Date', df[-24:]['DO'], df[-24:]['tgl'], title= 'Grafik DO')
suhu = chart('Suhu', 'Date', df[-24:]['Temp'], df[-24:]['tgl'], title= 'Grafik Suhu')
NH = chart('NH', 'Date', df[-24:]['NH4'], df[-24:]['tgl'], title= 'Grafik NH')
NO = chart('NO', 'Date', df[-24:]['NO3'], df[-24:]['tgl'], title= 'Grafik NO')

#dataframe parameter
data_pH = df[-24:][['tgl', 'pH']]
data_DO = df[-24:][['tgl', 'DO']]
data_NH = df[-24:][['tgl', 'NH4']]
data_NO = df[-24:][['tgl', 'NO3']]
data_T0 = df[-24:][['tgl', 'Temp']]

#chart column
    
if option == 'pH':
    st.session_state.space_initial.write(pH)
    st.session_state.space_initial_2.write(data_pH)
elif option == 'DO':
    st.session_state.space_initial.write(DO)
    st.session_state.space_initial_2.write(data_DO)
elif option == 'NH4':
    st.session_state.space_initial.write(NH)
    st.session_state.space_initial_2.write(data_NH)
elif option == 'NO3':
    st.session_state.space_initial.write(NO)
    st.session_state.space_initial_2.write(data_NO)
    
st.markdown("""<hr style="height:5px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
st.title('Take Action !')

#input action from PJ
@st.cache(allow_output_mutation=True)
def get_data_input():
    return[]

@st.cache(allow_output_mutation=True)
def get_data_output():
    return[]

emoji = st.markdown(':smiley:')

aksi = st.radio(f'Hallo Iqbal, apa yang sudah dilakukan untuk data anomali ini ?', ('Kalibrasi ulang', 'Mencelupkan sensor ke air bersih','Membersihkan sensor', 'reset logger'))

tgl_aksi = datetime.datetime.now()

if st.button('add input'):
    get_data_input().append({'Tanggal Aksi': tgl_aksi, 'Aksi':aksi})
    input_41 = pd.DataFrame(get_data_input())
    input_41.tail(1).to_csv(f'log_{ID_choice}.csv', mode='a', index = False, header = False)

kasus = st.text_input(f'Apakah ada kasus di KLHK 41?')

if st.button('add'):
    get_data_input().append({'Tanggal Aksi': tgl_aksi, 'Aksi':kasus})
    input_41 = pd.DataFrame(get_data_input())
    input_41.tail(1).to_csv(f'log_{ID_choice}.csv', mode='a', index = False, header = False)

    
hasil = st.radio('Bagaimana hasilnya?', ('Pembacaan sensor normal', 'Pembacaan sensor masih anomali', 'Logger online kembali'))
tgl_hasil = datetime.datetime.now()

if st.button('add output'):
    get_data_output().append({'Tanggal Hasil': tgl_hasil, 'Hasil':hasil})
    hasil_41 = pd.DataFrame(get_data_output())
    hasil_41.tail(1).to_csv(f'log_hasil_{ID_choice}.csv', mode='a', index=False, header=False)

report_input = pd.read_csv(f'log_{ID_choice}.csv', names=['Tanggal', 'Aksi'])
report_output = pd.read_csv(f'log_hasil_{ID_choice}.csv', names=['Tanggal', 'Hasil'])

    
st.subheader('Datalog Aksi')
st.write(report_input)

st.subheader('Datalog Hasil')
st.write(report_output)

