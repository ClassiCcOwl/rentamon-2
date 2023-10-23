import requests as r
from bs4 import BeautifulSoup as bs

DOMAIN = "https://www.jabama.com"

CITY = "qom"


def urlmaker(domain, city, page):
    return domain + "/city-" + city + "?page-number="  + page


URL = urlmaker(DOMAIN, CITY)

print(URL)

def contentCreatpr(URL):
    response = r.get(URL)
    soup = bs(response.content, 'html5lib')
    ul = soup.select_one('ul')
    lis = ul.find_all("li")
    
    for li in(lis):
        rooms = 0
        link = DOMAIN + li.find('a')['href']

        infos = li.select('span.product-card-info__item')

        for item in infos:
            if "اتاق" in item.text.strip():
                rooms = int(item.text.replace("اتاق", "").strip())
                break

        price = int(li.select_one(
            ".pricing-main .text-bold").text.replace("تومان", "").replace(",", "").strip())
        
    
