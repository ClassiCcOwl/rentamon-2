import pandas as pd
import time
import requests as r
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from sqlite3 import connect, PARSE_COLNAMES

SCRIPT = """
function days() {
    var dis = []


document.querySelectorAll(".vuec-day.vuec-col.disabled:not([aria-hidden]) .calendar-range-day__date").forEach(
    d=>
    {
        var date =''
            console.log(date)
            date += d.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.previousElementSibling.previousElementSibling.querySelector(".range-calendar__name-of-month").textContent.replace("1402","").trim() 
        date += " "
            date+= d.textContent.trim() 
        dis.push(date) 
    
    console.log(d.textContent.trim(), d.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.previousElementSibling.previousElementSibling.querySelector(".range-calendar__name-of-month").textContent.trim())
})

return dis
}

return days()
"""
DOMAIN = "https://www.jabama.com"
CITY = "rasht"
ARGUMENTS = [
    '--headless=new',
    '--log-level=3',
    '--no-sandbox',
    '--disable-gpu'
]
SCHEMA = {
    "table_name": "jabama",
    "columns": [
        {"name": "url", "type": "TEXT", "primary_key": True},
        {"name": "rooms", "type": "INT"},
        {"name": "price", "type": "INT"},
        {"name": "blocked", "type": "TEXT"},
        {"name": "rate", "type": "REAL"}
    ]
}


def urlmaker(domain, city, page):
    return domain + "/city-" + city + "?page-number=" + str(page)


def contentCreator(URL: str, crawledContent: list):
    response = r.get(URL)
    soup = bs(response.content, 'html5lib')
    ul = soup.select_one('ul')
    lis = ul.find_all("li")
    for li in (lis):
        rooms = 0
        link = DOMAIN + li.find('a')['href']
        infos = li.select('span.product-card-info__item')
        for item in infos:
            if "اتاق" in item.text.strip():
                rooms = item.text.replace("اتاق", "").strip()
                try:
                    rooms = int(rooms)
                except:
                    pass
        price = int(li.select_one(
            ".pricing-main .text-bold").text.replace("تومان", "").replace(",", "").strip())
        content = {"link": link,
                   "rooms": rooms,
                   "price": price,
                   "blocked": None,
                   "rate": None}
        crawledContent.append(content)


def browserOptionsMaker(arguments=ARGUMENTS):
    browser_options = webdriver.ChromeOptions()
    for argument in arguments:
        browser_options.add_argument(argument)
    return browser_options


def db(data):
    try:
        connection = connect("rentamon.db")
        cursor = connection.cursor()
        table_columns = ", ".join(
            [f"{col['name']} {col['type']}" for col in SCHEMA['columns']])
        table_columns += ", PRIMARY KEY (url)"
        table_stmt = f"CREATE TABLE IF NOT EXISTS {SCHEMA['table_name']} ({table_columns})"
        cursor.execute(table_stmt)
        columns = [col['name'] for col in SCHEMA['columns']]
        placeholders = ", ".join(["?" for _ in columns])
        insert_stmt = f"INSERT OR REPLACE INTO {SCHEMA['table_name']} VALUES ({placeholders})"
        data = [tuple(x.values()) for x in data]
        cursor.executemany(insert_stmt, data)
        cursor.execute("COMMIT")
    except Exception as e:
        print('Something is wrong with db', e)
    finally:
        if connection:
            connection.close()


contents = []
for page in range(1, 5):
    url = urlmaker(DOMAIN, CITY, page)
    contentCreator(url, contents)
db(contents)
browser_options = browserOptionsMaker()
service = Service()
driver = webdriver.Chrome(options=browser_options, service=service)
driver.set_page_load_timeout(5)
driver.set_script_timeout(300)
for c in range(len(contents)):
    url = contents[c]['link']
    try:
        driver.get(url)
    except:
        ...
    blocked = driver.execute_script(SCRIPT)
    contents[c]['blocked'] = str(blocked)
    contents[c]['rate'] = len(blocked) / 30 * 100
    print(c, url, contents[c])
    print()
db(contents)


conn = connect("rentamon.db", isolation_level=None,
               detect_types=PARSE_COLNAMES)
db_df = pd.read_sql_query("SELECT * FROM jabama", conn)
db_df.to_csv('rentamon.csv', index=False, encoding='utf-8-sig')
