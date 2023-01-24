import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from htmldate import find_date
import requests
from webdriver_manager.chrome import ChromeDriverManager
import datetime
import pandas as pd
import os
from subprocess import Popen, PIPE, STDOUT

options = webdriver.ChromeOptions()
options.add_extension("I-don-t-care-about-cookies.crx")
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
SCROLL_PAUSE_TIME = 7
TEXT_FILENAME1 = 'text1.txt'
TEXT_FILENAME2 = 'text2.txt'
DATE_RANGE = 5 #DAYS

def get_topic(website):
    driver.get(website)
    headers = [header.text for header in driver.find_elements(By.TAG_NAME, 'h1')]
    return headers

def get_similar_websites(website):
    topic = get_topic(website)[0]
    base_link = 'https://www.google.com/search?q='
    topic_parameter = topic.replace(' ', '+')
    link = base_link+topic_parameter
    driver.get(link)
    similar_headers = driver.find_elements(By.TAG_NAME, 'h3')[:6]
    similar_links = [similar_header.find_element(By.XPATH, '..').get_attribute('href') for similar_header in similar_headers]
    for i in range(len(similar_links)):
        if similar_links[i] == website:
            similar_links.pop(i)
            break
    similar_headers_texts = [similar_header.text for similar_header in similar_headers]
    return similar_headers_texts, similar_links

def get_date(website):
    content = requests.get(website).content.decode('utf-8')
    date = find_date(content)
    return date

def get_text(website):
    driver.get(website)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # driver.execute_script("window.scrollTo(0, 100);")
    time.sleep(SCROLL_PAUSE_TIME)
    lines = [p_el.text for p_el in driver.find_elements(By.TAG_NAME, 'p')]+[p_el.text for p_el in driver.find_elements(By.TAG_NAME, 'span')]
    # with open(file_name, 'w') as file:
    #     for line in lines:
    #         file.write(line)
    return lines

def get_category(website):
    df = pd.read_csv("Zaacznik_1_-_lista_kategorii.XLSX - Arkusz1.csv", encoding='utf_8')
    lines = get_text(website)
    text = " ".join(lines)
    category = None
    for i, data in df.iterrows():
        if data['TEMATY'] in text:
            category = data['GRUPA']
            return category

def check_similarity_and_domain(websites, texts):
    lines1 = [websites[0]+"\n", " ".join(texts[0])]
    lines2 = [websites[1]+"\n", " ".join(texts[1])]
    with open("semantics_jar/"+TEXT_FILENAME1, 'wb') as file:
        file.write(" ".join(lines1).encode('utf-8'))
    with open("semantics_jar/"+TEXT_FILENAME2, 'wb') as file:
        file.write(" ".join(lines2).encode('utf-8'))
    cwd = os.getcwd()
    file_name1, file_name2 = os.path.join(cwd, TEXT_FILENAME1), os.path.join(cwd, TEXT_FILENAME2)
    os.chdir('semantics_jar')
    output = os.popen('java -jar semantics.jar').read()
    os.chdir('..')
    return float(output.split('\n')[0]), float(output.split('\n')[1]) 
    #p = Popen(['java', '-jar', 'semantics_jar/semantics.jar'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    #grep_stdout = p.communicate(input=f"{file_name1}\n".encode('utf-8'))[0]
    #print(grep_stdout)
    #grep_stdout = p.communicate(input=f"{file_name2}\n".encode('utf-8'))[0]
    #print(grep_stdout)

def check_fake(website):
    similar_headers, similar_links = get_similar_websites(website)
    dates = [get_date(link) for link in similar_links]
    website_date = get_date(website)
    y, m, d = map(int, website_date.split('-'))
    if website_date:
        datetime_late = datetime.datetime(y, m, d) - datetime.timedelta(days=DATE_RANGE/2)
        datetime_obj = datetime.datetime(y, m, d)
        datetime_recent = datetime.datetime(y, m, d) + datetime.timedelta(days=DATE_RANGE/2)
        dates_similar = []
        for i in range(len(dates)):
            y,m,d = map(int, dates[i].split('-'))
            date = datetime.datetime(y,m,d)
            if datetime_late<=date<=datetime_recent: dates_similar.append(True)
            else: dates_similar.append(False)

    else: dates_similar = [True, True, True, True, True]
    categories = [get_category(link) for link in similar_links]
    print(categories)
    print(dates_similar)
    website_text = get_text(website)
    similarities = []
    if any(dates_similar):
        for j in range(len(dates_similar)):
            if dates_similar[j]:
                similarities.append(check_similarity_and_domain([website, similar_links[j]], [website_text, get_text(similar_links[i])]))
    print(similarities)
    avg_sim = 0
    avg_dom = 0
    counter = 0
    for k in range(len(similarities)):
        if similarities[k][0] >= 0.5:
            avg_sim+=similarities[k][0]
            avg_dom+=similarities[k][1]
            counter+=1
    if counter:
        avg_sim/=counter
        avg_dom/=counter
    avg=(avg_dom+avg_sim)/2

    return 1-avg
    
def installJ():
    cmd = "java --version"
    output = os.system(cmd)
    if (output!=0):
        cmd = "start jdk-18.0.2.1_windows-x64_bin.exe"
