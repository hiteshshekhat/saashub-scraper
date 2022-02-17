import requests
import random
import requests_cache
from bs4 import BeautifulSoup
import time
from selenium import webdriver
import json


requests_cache.install_cache(expire_after=18000, allowable_methods=('GET', 'POST'))

base_url = "https://www.saashub.com/compare/sitemap/"

alpha_list = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

with open('proxies_ip.txt', "r") as f:
    proxies=f.read().splitlines()



def send_request(url, proxies):
    while True:
        proxy = proxies[random.randint(0, len(proxies)-1)]
        try:
            # proxies = {"http": 'http://' + proxies(proxy), "https": 'https://' + proxies(proxy)}
            response = requests.get(url, timeout=10, proxies={"http": 'http://' + proxy, "https": 'https://' + proxy})
            print(response.status_code)
            print("Proxy currently being used")
            break
        except:
            print("Error, looking for another proxy")
    return response




def get_comparison_links(letter):
    url = base_url + letter
    print(url)
    r = send_request(url, proxies)
    # r = requests.get(url, headers=headers)
    print(r.request.headers)
    html_soup = BeautifulSoup(r.text, "html.parser")
    a_tags = html_soup.select('.is-one-third-tablet a')
    comparison_links = ['https://www.saashub.com/' + a['href'] for a in a_tags]
    return comparison_links


def get_company_links(url):
    r = send_request(url, proxies)
    html_soup = BeautifulSoup(r.text, "html.parser")
    div = html_soup.find('div', attrs={'class':'columns mt-6'})
    a_tags = div.select('.is-5 a')
    company_links = ['https://www.saashub.com' + a['href'] for a in a_tags]
    return company_links
# print(get_comparision_links(alpha_list[0]))

def get_company_info(url):
    company_dict = {'company_url':url}
    r = send_request(url, proxies)
    html_soup = BeautifulSoup(r.text, "html.parser")
    company_info_div = html_soup.select('.hero-body .columns .column')
    for div in company_info_div:
        if company_info_div.index(div) == 1:
            name = div.find('h2').get_text(strip=True)
            print(name)
            company_dict['name'] = name
            try:
                review_count = div.select_one('.underlined-links .service-rating a').get_text(strip=True)
                review_count = int(review_count.split(' ')[0].replace('(',''))
                print(review_count)
                company_dict['review_count'] = review_count
            except AttributeError:
                company_dict['review_count'] = "No review"
            
            
        if company_info_div.index(div) == 3:
            a_tags = div.select('.column a')
            company_dict['website'] = 'No website'
            company_dict['twitter'] = 'No twitter'
            for a in a_tags:
                print(a.get_text(strip=True))
                if a.get_text(strip=True) == 'Visit Website':
                    company_dict['website'] = a['href']
                if 'twitter' in a['href']:
                    company_dict['twitter'] = a['href']
                    
            # if len(a_tags) > 1:
            #     website = a_tags[0]['href']
            #     twiter = a_tags[2]['href']
            #     print(website)
            #     print(twiter)
            #     company_dict['website'] = website
            #     company_dict['twiter'] = twiter
            # else:
            #     company_dict['website'] = 'No website'
            #     company_dict['twiter'] = 'No twiter'
    alt_info_div = html_soup.find('div', attrs={'id':'main_list'})
    a_tags = alt_info_div.select('li .is-4 a')
    alternatives = ['https://www.saashub.com' + a['href'] for a in a_tags]
    # print(alternatives)
    company_dict['alternatives'] = alternatives
    return company_dict


def write_data_to_json(data):
    with open('company_info.jl', 'a') as f:
        json.dump(data, f)
        f.write('\n')



if __name__ == '__main__':
    comparison_links = get_comparison_links(alpha_list)
    print(comparison_links)
    print(len(comparison_links))
    for url in comparison_links:
        company_links = get_company_links(url)
        print(company_links)
        for url in company_links:
            d = get_company_info(url)
            print(d)
            write_data_to_json(d)
            
                    

        

