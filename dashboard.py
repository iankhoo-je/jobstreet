import sqlite3
import plotly.express as px
import streamlit as st
import pandas as pd
import re
import streamlit as st
# from streamlit_tags import st_tags, st_tags_sidebar



database_file = 'jobss'

conn = sqlite3.connect(f'C:/Users/Ian/project_jobstreet/{database_file}.db')
c = conn.cursor()

df = pd.read_sql_query(f"SELECT * FROM jobss", conn)


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

data_col_1, data_col_2, data_col_3 = st.columns((.2, 7.1, .2))
with data_col_2:
    st.markdown("")
    see_data = st.expander('Click here to see all job postings')
    with see_data:
        st.dataframe(data=df_selection.reset_index(drop=True))
st.text('')


filter_number = 5

max_postings = df_selection['company'].value_counts().nlargest(filter_number)
max_comp_lst = max_postings.index.tolist()
max_comp_ind_lst = max_postings.tolist()

######################### Companies with Most Job Postings #############################
st.header(f'Top {filter_number} Companies with the Most Job Postings')
column1, column2 = st.columns((3,3))
with column1:
    for i in range(filter_number):
        st.markdown(f'{max_comp_lst[i]}')
with column2:
    for i in range(filter_number):
        st.markdown(f'{max_comp_ind_lst[i]}')

st.text("")
st.text("")

title_col1, title_col2 = st.columns((1,3))
with title_col1:
    st.subheader('Skills Chart for Job Postings')



skills_selections = []

# ------------------- Bar Chart-------------------------------
# language_dict = {'Language':['Python','Javascript','Java','MATLAB','Ruby','PHP','Perl','Swift','R language'], 'Results':[]}
# database_dict = {'Technology':['SQL','Database','MongoDB','NoSQL','Postgres','Sqlite3','Mysql'], 'Results':[]}
# cloud_dict = {'Cloud':['AWS','Cloud','Azure'], 'Results':[]}
# ml_dict = {'ML':['Jupyter','pandas','tensorflow','keras','python','Machine Learning','scikit'], 'Results':[]}
# data_science_dict = {'DS':['Python','REST API','API','Git','Linux','Jupyter'], 'Results':[]}
# spoken_lang_dict = {'SL':['English','Chinese','Malay','French'], 'Results':[]}
# data_vis_dict = {'Tool':['Power BI','Tableau','Excel','Plotly'],'Results':[]}


skills_lst = [{'Programming Languages':['Python','Javascript','Java','MATLAB','Ruby','PHP','Perl','Swift','R language'], 'Results':[]}, 
                {'Technology':['SQL','Database','MongoDB','NoSQL','Postgres','Sqlite3','Mysql'], 'Results':[]},
                {'Cloud Technologies':['AWS','Cloud','Azure'], 'Results':[]},
                {'Machine Learning':['Jupyter','Pandas','Tensorflow','Keras','Python','Machine Learning','Scikit'], 'Results':[]},
                {'Data Science':['Python','REST API','API','Git','Linux','Jupyter'], 'Results':[]},
                {'Spoken Languages':['English','Chinese','Malay','French', 'Cantonese', 'Mandarin', 'Hokkien'], 'Results':[]},]



for skill_dict in skills_lst:
    skill = list(skill_dict.keys())[0]
    skills_selections.append(skill)
    for idx in skill_dict[skill]:
        total = len(df_selection.loc[df_selection['jobdescription'].str.contains(f'{idx.lower()}', flags=re.I,regex=True)])
        skill_dict['Results'].append(total)


chart_col_1, chart_col_2 = st.columns((0.5,2))
with chart_col_1:
    st.title('')
    st.markdown('Choose skill/language(s) most desired by companies.')
    skill_select = st.selectbox('Select a skill', skills_selections, key = 'selection_plot')

with chart_col_2:
    for index in skills_lst:
        if skill_select in index:
            skills_bar_chart = px.bar(
                    index,
                    x =  skill_select,
                    y = 'Results',
                    title= f'Frequency of {skill_select.upper()} keywords in job postings',
                    orientation = 'v',
                    template ='plotly_white'
                )
            st.plotly_chart(skills_bar_chart)
                
            

with open('C:/Users/Ian/project_jobstreet/streamlit_csv.xlsx', 'rb') as my_file:
    st.download_button(label = 'Download excel file (add emoji)', 
            data = my_file, file_name = 'jobs.xlsx', mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') 
    


st.markdown('---')




