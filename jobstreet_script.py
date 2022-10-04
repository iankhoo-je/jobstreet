########################################################################################################

from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import time
from pandas import ExcelWriter 
from datetime import datetime
import sqlite3


def general():
    ###########################################################################
    # User Configurable Variables
    job_query = 'software engineer'
    location_query = 'singapore'
    page_input = 4  
    xlsx_file_path = f'C:/Users/Ian/project_jobstreet/{job_query}_{location_query}_script.xlsx'
    db_table = 'software_jobs'
    db_file_path = f'C:/Users/Ian/project_jobstreet/{db_table}.db'
    ############################################################################

    conn = sqlite3.connect(db_file_path)
    c = conn.cursor()
    c.execute(f'''CREATE TABLE {db_table}
            (role TEXT, company TEXT, location TEXT, area TEXT, salary TEXT, years TEXT, 
            keywords TEXT, jobdescription TEXT, date TEXT, UNIQUE(company,jobdescription)) ''')

 

    regex_clear_html = re.compile('<.*?>') 
    base_url = 'https://www.jobstreet.com.sg/'
    search_query = 'en/job-search/'+ job_query + '-jobs-in-'+ location_query + '/' 
    search_url = base_url + search_query
    tag_regex = r'en/[^,"]*'
    a_tag_lst = []

    # For database insertion 
    role_lst=[]
    company_lst=[]
    location_lst=[]


    date_today = datetime.now()
    page_number = int(page_input) + 1
    print(f'Querying for {job_query} jobs in {location_query}, Searching through {page_input} page(s)...')
    search_all_pages = [(search_url + str(x)+"/?sort=createdAt") for x in range(1,page_number)]

    keywords = ['python','mechanical','scripting','Lean Six Sigma','entry','Masters','Mechanical Engineering', 'software','communication', 'CAD', 'Minitab','programming', 'excel','powerpoint', '1 year','fresh']
    keywords_lower = [word.lower() for word in keywords]

    data = {'Role':[], 'Company':[], 'Location': [], 'Area': [], 'Salary':[], 'Years of Experience':[], 'Keywords Found':[], 'Job Description':[], 'Date Posted':[]}
    for page in search_all_pages: 
        time.sleep(1)
        print(page)
        main_html_text = requests.get(page).text
        soup_page = BeautifulSoup(main_html_text,'lxml')
        jobs = soup_page.find_all('div', class_='sx2jih0 zcydq876 zcydq866 zcydq896 zcydq886 zcydq8n zcydq856 zcydq8f6 zcydq8eu') # for all jobs in one page
    
        for job in jobs: # loop through each job
            time.sleep(1)
            company_role = job.find('h1', class_='sx2jih0 zcydq84u _18qlyvc0 _18qlyvc1x _18qlyvc3 _18qlyvca').text

            try:
                company_name = job.find('span', class_='sx2jih0 zcydq84u _18qlyvc0 _18qlyvc1x _18qlyvc1 _18qlyvca').text
            except:
                company_name = 'Company Confidential'
            print(company_name)
            
            location = job.find('span', class_='sx2jih0 zcydq84u zcydq80 iwjz4h0').text 

            tag = job.find('h1',class_ ='sx2jih0 zcydq84u _18qlyvc0 _18qlyvc1x _18qlyvc3 _18qlyvca')
            regex_find = re.findall(tag_regex, str(tag)) # Regex search to find href tag for job description
            tag_formatted = ''.join([str(elem) for elem in regex_find])
            
            data['Role'].append(company_role)
            data['Company'].append(company_name)
            data['Location'].append(location)
            a_tag_lst.append(tag_formatted) # list of all href links
            role_lst.append(company_role)
            company_lst.append(company_name)
            location_lst.append(location)

    print('Accessing all job postings of this page to obtain further details...')

    # Using a-tag to access more details for each job
    for idx, link in enumerate(a_tag_lst):
        print(f"Obtaining job description for {data['Role'][idx]} from {data['Company'][idx]}({idx})")
        time.sleep(1)
        details_lst=[]
        job_keyword =[]
        search_url = base_url + link
        link_html_text = requests.get(search_url).text
        soup_href = BeautifulSoup(link_html_text,'lxml')
        
        career = soup_href.find_all('div', class_="sx2jih0 zcydq86q zcydq86v zcydq86w")
        career_level = career[0].find('span',class_="sx2jih0 zcydq84u _18qlyvc0 _18qlyvc1x _18qlyvc1 _1d0g9qk4 _18qlyvcb")
        cl_clear_tag = str(re.sub(regex_clear_html, '', str(career_level))).replace(u'\xa0', u' ')
        data['Years of Experience'].append(cl_clear_tag)  # Career level column

        description_raw = soup_href.find('div', class_='YCeva_0') # Retrieve job description
        description_clear_tag = str(description_raw).replace('</li>','\n').replace('</li>','\n')
        description = str(re.sub(regex_clear_html, '', str(description_clear_tag))).replace(u'\xa0', u' ')
        description_lower = description.lower()
        data['Job Description'].append(description)

        if any(keyword in description_lower for keyword in keywords_lower):
            for keyword in keywords_lower:
                if keyword in description_lower:
                    job_keyword.append(keyword)

            keyword_str = ','.join(job_keyword)
            data['Keywords Found'].append(keyword_str)
                    
        else:
            data['Keywords Found'].append('')


        all_info = soup_href.find_all('div',class_='sx2jih0 zcydq86a') # Retrieve salary,place..
        for info in all_info:
            info_raw = info.find('span',class_='sx2jih0 zcydq84u _18qlyvc0 _18qlyvc1x _18qlyvc1 _18qlyvca').text
            info_clean = str(re.sub(regex_clear_html, '', info_raw)).replace(u'\xa0', u' ')
            details_lst.append(info_clean)

        salary_counter = 0
        post_counter = 0
        location_counter = 0

        for detail in details_lst:
            currency_search = detail.find('SGD')
            post_search = detail.find('Posted')
            if 'SGD' in detail:
                salary_counter += 1
                salary = details_lst[details_lst.index(detail)]
            else:
                salary_counter

            if 'Posted' in detail:
                post_counter +=1
                post = details_lst[details_lst.index(detail)]
            else:
                post_counter

            if currency_search == -1 and post_search == -1:
                location_counter += 1
                loc = details_lst[details_lst.index(detail)]
            else:
                location_counter


        if salary_counter == 1:
            data['Salary'].append(salary)
        else:
            data['Salary'].append('')


        if post_counter == 1:
            data['Date Posted'].append(post)
        else:
            data['Date Posted'].append('No post shown')

        if location_counter == 1:
            data['Area'].append(loc)
        else:
            data['Area'].append('No location shown')

        company_role= role_lst[idx]
        company_name=company_lst[idx]
        location=location_lst[idx]
        print(description)
        c.execute(f'''SELECT jobdescription FROM {db_table} WHERE jobdescription=?''',
                        (description,))
       
        fetch_result = c.fetchall()
        
        if fetch_result:
            print("FULLY UPDATED")
            

        else:
            c.execute(f"INSERT INTO {db_table} VALUES (:role,:company,:location,:area,:salary,:years,:keywords,:jobdescription,:date)", 
            {'role':company_role,'company':company_name,'location':location,'area':data['Area'][idx],'salary':data['Salary'][idx], 'years':data['Years of Experience'][idx],
                    'keywords':data['Keywords Found'][idx],'jobdescription':data['Job Description'][idx],'date':data['Date Posted'][idx]})
            
            conn.commit()
   
        
    c.execute(f"SELECT COUNT(*) FROM {db_table}")
    result = c.fetchone()[0]
    print(result)
    conn.commit()
    df = pd.read_sql_query(f"SELECT * FROM {db_table}", conn)
  
    writer = pd.ExcelWriter(xlsx_file_path, engine='xlsxwriter')
    df.to_excel(writer, sheet_name= 'Jobstreet Search', startrow=1, header=False, index=False)

    # For Autofit Column Size
    for column in df:
        column_width = max(df[column].astype(str).map(len).max(),len(column))
        col_idx = df.columns.get_loc(column)
        writer.sheets['Jobstreet Search'].set_column(col_idx, col_idx, column_width)

    workbook = writer.book
    worksheet = writer.sheets['Jobstreet Search']

    (max_row, max_col) = df.shape
    column_settings = [{'header': column} for column in df.columns]

    worksheet.add_table(1, 0, max_row, max_col - 1, {'columns': column_settings})


    italic_font = workbook.add_format({'italic': True})
    worksheet.write(0,0,f'Accessed Jobstreet search query at {date_today}. Search query: {job_query} jobs in {location_query}', italic_font)

    writer.save() 
    
general()

def __