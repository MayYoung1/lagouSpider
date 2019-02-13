"""
Created by Young on 2019/1/23 10:25
"""
import pymongo
from selenium import webdriver
from lxml import etree
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import re

driver = webdriver.Chrome()
wait = WebDriverWait(driver,10)
url = 'https://www.lagou.com/jobs/list_python%E7%88%AC%E8%99%AB?oquery=python%E5%90%8E%E7%AB%AF&fromSearch=true&labelWords=relative'


client = pymongo.MongoClient('localhost',27017)
lagou = client['lagou']
meishi_info = lagou['lagou_job']

def job_link(url):

    driver.get(url)
    while True:
        source = driver.page_source
        time.sleep(2)
        page_list(source)
        next_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#s_position_list > div.item_con_pager > div > span.pager_next')))
        if 'pager_next pager_next_disabled' in next_btn.get_attribute('class'):
            break
        else:
            next_btn.click()
            time.sleep(2)

def page_list(source):
    html = etree.HTML(source)
    links = html.xpath('//a[@class="position_link"]/@href')
    for link in links:
        request_detail(link)


def request_detail(url):

    driver.execute_script("window.open('%s')" % url)
    driver.switch_to_window(driver.window_handles[1])
    source = driver.page_source
    time.sleep(2)
    job_detail(source)
    driver.close()
    driver.switch_to_window(driver.window_handles[0])

def job_detail(source):
    try:
        datas = []
        html = etree.HTML(source)
        company = html.xpath('//div[@class="company"]/text()')[0]
        position_name = html.xpath('//span[@class="name"]/text()')[0]
        job_request_span = html.xpath('//dd[@class="job_request"]//span')
        salary = job_request_span[0].xpath('.//text()')[0].strip()
        address = job_request_span[1].xpath('.//text()')[0].strip()
        address = re.sub(r'[\s/]', '', address)
        work_years = job_request_span[2].xpath('.//text()')[0].strip()
        work_years = re.sub(r'[\s/]', '', work_years)
        education = job_request_span[3].xpath('.//text()')[0].strip()
        education = re.sub(r'[\s/]','',education)
        work_time = job_request_span[4].xpath('.//text()')[0].strip()
        work_time = re.sub(r'[\s/]','',work_time)
        advantage = html.xpath('//dd[@class="job-advantage"]/p/text()')
        desc = ''.join(html.xpath('//dd[@class="job_bt"]//text()')).strip()
        desc = re.sub(r"职位描述：\n        \n       ",'',desc)
        data = {
            '【公司名】': company ,
            '【职位】': position_name,
            '【薪资】': salary,
            '【工作地点】': address,
            '【经验】': work_years,
            '【教育水平】': education,
            '【工作类型】': work_time,
            '【职位诱惑】' : advantage,
            '【职位描述】' : desc
        }
        datas.append(data)
        print(datas)
        print('**' * 30)
        save_to_mongo(data)
    except TimeoutException:
        return print('超时')

def save_to_mongo(result):
    if lagou['lagou_job'].insert(result):
        print('-----------------------------成功存储到MongoDB-------------------------------------\n', result)
        print('**************************************************************************************')
        return True
    return False

def main():
    job_link(url)

if __name__ == '__main__':
    main()
