from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import time
from pandas import ExcelWriter 
from tkinter import *
import threading 
from datetime import datetime
import sys
import sqlite3

conn = sqlite3.connect('C:/Users/Ian/Desktop/jobstreet/software_jobs_database.db')
c = conn.cursor()
c.execute('''CREATE TABLE jobs
            (role TEXT, company TEXT, location TEXT, area TEXT, salary TEXT, 
            keywords TEXT, description TEXT, date TEXT) ''')

class App:
    HEIGHT = 300
    WIDTH = 600
    def __init__(self, parent):
         # Text and input for job field
        self.parent = parent
        self.parent.title('Jobstreet Search Tool v3.0')
        self.label_field = Label(self.parent, text='Enter Job Field')
        self.label_field.pack()
        self.entry_field = Entry(self.parent, width=50, bg='white',fg='black')
        self.entry_field.pack()

        # Text and input for job location
        self.label_location = Label(self.parent, text='Enter Job Location')
        self.label_location.pack()
        self.entry_location = Entry(self.parent, width=50, bg='white',fg='black')
        self.entry_location.pack()

        # Text and dropdown menu for number of pages
        self.menu = StringVar()
        self.menu.set('Select pages')
        self.drop = OptionMenu(self.parent, self.menu, '1','2','3','4','5','6','7','8')
        self.drop.pack()

        self.canvas = Canvas(self.parent, height=App.HEIGHT, width=App.WIDTH)
        self.button = Button(self.parent, text='Submit', command=threading.Thread(target=self.use_entry).start, activebackground='red', bg='white')

        self.button.pack()
        self.canvas.pack()

    def use_entry(self):
        App.field = self.entry_field.get()
        App.loc = self.entry_location.get()
        App.pages = self.menu.get()
        self.label_description = Label(self.parent, text=f'Searching for {App.field} jobs in {App.loc}...')
        self.label_description.pack()
        time.sleep(5)
        self.parent.destroy()


def general():
    root = Tk()
    app = App(root)
    root.mainloop()
    regex_clear_html = re.compile('<.*?>') 
    job_keyword = App.field
    location_keyword = App.loc
    page_input = App.pages
    xlsx_file_path = f'C:/Users/Ian/Documents/jobstreet-github/{job_keyword}_{location_keyword}.xlsx'
    base_url = 'https://www.jobstreet.com.sg/'
    search_query = 'en/job-search/'+ job_keyword + '-jobs-in-'+ location_keyword + '/' 
    search_url = base_url + search_query
    tag_regex = r'en/[^,"]*'
    a_tag_lst = []

    # For database insertion 
    role_lst=[]
    company_lst=[]
    location_lst=[]


    date_today = datetime.now()
    page_number = int(page_input) + 1
    print(f'Querying for {job_keyword} jobs in {location_keyword}, Searching through {page_input} pages...')
    search_all_pages = [(search_url + str(x)+"/?sort=createdAt") for x in range(1,page_number)]

    keywords = ['python','mechanical','scripting','Lean Six Sigma','entry','Masters','Mechanical Engineering', 'software','communication', 'CAD', 'Minitab','programming', 'excel','powerpoint', '1 year','fresh']
    keywords_lower = [word.lower() for word in keywords]

    data = {'Role':[], 'Company':[], 'Location': [], 'Area': [], 'Salary':[], 'Keywords Found':[], 'Job Description':[], 'Date Posted':[]}
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
        print(f"Obtaining job description for {data['Role'][idx]} from {data['Company'][idx]} ({idx})")
        time.sleep(1)
        details_lst=[]
        job_keyword =[]
        search_url = base_url + link
        link_html_text = requests.get(search_url).text
        soup_href = BeautifulSoup(link_html_text,'lxml')

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

        c.execute('''SELECT role FROM jobs WHERE role=?''',
                        (company_role,))
        result = c.fetchone()
        
        if result:
            print("FULLY UPDATED")
            break

        else:
            c.execute("INSERT INTO jobs VALUES (:role,:company,:location,:area,:salary,:keywords,:description,:date)", 
            {'role':company_role,'company':company_name,'location':location,'area':data['Area'][idx],'salary':data['Salary'][idx],
                    'keywords':data['Keywords Found'][idx],'description':data['Job Description'][idx],'date':data['Date Posted'][idx]})
            
            conn.commit()
            
    c.execute("SELECT COUNT(*) FROM jobs")
    result = c.fetchone()[0]
    print(result)
    conn.commit()
    df = pd.read_sql_query("SELECT * FROM jobs", conn)
    # c.execute('''SELECT * FROM jobs''')
    # print(c.fetchall())

    # pd.set_option("display.max_rows", None, "display.max_columns", None, "display.width", None, "display.max_colwidth", None) # constraints set to None for terminal to display the full dataframe
    # print(df)
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
    worksheet.write(0,0,f'Accessed Jobstreet search query at {date_today}. Search query: {job_keyword} jobs in {location_keyword}', italic_font)

    writer.save()

    sys.exit()
    


    
general()