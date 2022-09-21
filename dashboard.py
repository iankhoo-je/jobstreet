import sqlite3
import plotly.express as px
import streamlit as st
import pandas as pd
import re
import streamlit as st
# from streamlit_tags import st_tags, st_tags_sidebar

conn = sqlite3.connect('C:/Users/Ian/Documents/jobstreet-github/test_data.db')
c = conn.cursor()

df = pd.read_sql_query("SELECT * FROM proper", conn)


st.set_page_config(page_title='Jobstreet Search',
                        page_icon = ':shell:',
                        layout='wide')

# --------------SIDEBAR-------------------
st.sidebar.header('Job Filter:')
location = st.sidebar.multiselect(
    'Select Job location',
    options=df['location'].unique(),
    default=df['location'].unique()
    
)

years = st.sidebar.multiselect(
    'Select Years of Experience',
    options=df['years'].unique(),
    default=df['years'].unique()
    
)


df_selection = df.query(
    'location == @location & years == @years'
)

# keyword = st_tags_sidebar(label='# Enter Keywords:',
#                         text='Press enter to add more',
#                         value=['Zero', 'One', 'Two'],
#                         suggestions=['five', 'six', 'seven', 'eight', 'nine', 'three', 'eleven', 'ten', 'four'],
#                         key="afrfae")

# st.sidebar.write((keyword))


# ---------------- Main Page ---------------
st.title(':bar_chart: Jobstreet Query')

st.markdown('##')

#----------------- Top Results------------------
postings = df_selection.groupby(['company']).count()
max_postings = max(postings['role']) # max postings of one company - NTU

python_keyword = len(df_selection.loc[df['keywords'].str.contains('python', flags=re.I,regex=True)]) # No. of postings with keyword Python


left_column, right_column = st.columns(2)

with left_column:
    st.subheader('Max Postings')
    st.subheader(f'Nanyang Technology University with {max_postings}')


with right_column:
    st.subheader('Keyword Search')
    st.subheader(f'Python keyword found in {python_keyword} job postings')

# ------------------- Bar Chart-------------------------------
language_dict = {'Language':['Python','Javascript','Java','MATLAB','Ruby','PHP','Perl','Swift','R language'], 'Results':[]}
database_dict = {'Technology':['SQL','Database','MongoDB','NoSQL','Postgres','Sqlite3','Mysql'], 'Results':[]}
cloud_dict = {'Cloud':['AWS','Cloud','Azure'], 'Results':[]}
ml_dict = {'ML':['Jupyter','pandas','tensorflow','keras','python','Machine Learning','scikit'], 'Results':[]}
data_science_dict = {'DS':['Python','REST API','API','Git','Linux','Jupyter'], 'Results':[]}
# spoken_lang_dict = {'SL':['English','Chinese','Malay','French'], 'Results':[]}
# data_vis_dict = {'Tool':['Power BI','Tableau','Excel','Plotly'],'Results':[]}



for idx in language_dict['Language']:
    total = len(df_selection.loc[df_selection['description'].str.contains(f'{idx.lower()}', flags=re.I,regex=True)])
    language_dict['Results'].append(total)
for idx in database_dict['Technology']:
    total = len(df_selection.loc[df_selection['description'].str.contains(f'{idx.lower()}', flags=re.I,regex=True)])
    database_dict['Results'].append(total)
for idx in cloud_dict['Cloud']:
    total = len(df_selection.loc[df_selection['description'].str.contains(f'{idx.lower()}', flags=re.I,regex=True)])
    cloud_dict['Results'].append(total)
for idx in ml_dict['ML']:
    total = len(df_selection.loc[df_selection['description'].str.contains(f'{idx.lower()}', flags=re.I,regex=True)])
    ml_dict['Results'].append(total)
for idx in data_science_dict['DS']:
    total = len(df_selection.loc[df_selection['description'].str.contains(f'{idx.lower()}', flags=re.I,regex=True)])
    data_science_dict['Results'].append(total)


language_bar_chart = px.bar(
    language_dict,
    x =  'Language',
    y = 'Results',
    title= 'Most Used Software Technologies',
    orientation = 'v',
    template ='plotly_white'
)
database_bar_chart = px.bar(
    database_dict,
    x =  'Technology',
    y = 'Results',
    title= 'Most Used Data Visualisation Tools',
    orientation = 'v',
    template ='plotly_white'
)
cloud_bar_chart = px.bar(
    cloud_dict,
    x =  'Cloud',
    y = 'Results',
    title= 'Most Used Cloud Softwares',
    orientation = 'v',
    template ='plotly_white'
)
ml_bar_chart = px.bar(
    ml_dict,
    x =  'ML',
    y = 'Results',
    title= 'Most Used Machine Learning Tools',
    orientation = 'v',
    template ='plotly_white'
)
data_science_bar_chart = px.bar(
    data_science_dict,
    x =  'DS',
    y = 'Results',
    title= 'Most Used Data Science Tools',
    orientation = 'v',
    template ='plotly_white'
)


st.plotly_chart(language_bar_chart)
st.plotly_chart(database_bar_chart)
st.plotly_chart(cloud_bar_chart)
st.plotly_chart(ml_bar_chart)
st.plotly_chart(data_science_bar_chart)












# dict = {'Language':['Python','Java','C++','Excel'],'Amount':[3,6,9,10]}
# df_2 = pd.DataFrame(data=dict)



# chart = px.bar(
#     df_2,
#     x =  'Language',
#     y = 'Amount',
#     orientation = 'v',
#     template ='plotly_white'
# )





st.markdown('---')




# st.dataframe(df_selection)