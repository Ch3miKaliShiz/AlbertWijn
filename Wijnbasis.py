# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 15:52:12 2022

@author: rkatw
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as BS
from urllib.request import urlopen
import numpy as np
import time
import pandas as pd

#chrome beta 104 ipv 103 gebruiken
options = webdriver.ChromeOptions()
options.binary_location = "C:/Program Files/Google/Chrome/Application/chrome.exe"
driver = webdriver.Chrome('C:/chrome_driver104/chromedriver',options=options)

"""Albert heijn gedeelte"""
#"specify url to go to"
search_url = 'https://www.ah.nl/zoeken?query=witte%20wijn&page=12'
driver.get(search_url)

#remove cookie screen
driver.find_element_by_xpath('//*[@id="accept-cookies" ]').click()

#beautiful soup AH pagina
usock = urlopen(search_url)
data = usock.read()
usock.close()
soup = BS(data)

#Lege lists voor prijs onderdelen
integer_list = []
fractional_list = []
volume_list = []

# creer resultset van alle huidige prijzen
find_class = soup.find_all('div', {'class':'price-amount_highlight__3WjBM'})
find_class_volume = soup.find_all('span', {'class':'price_unitSize__8gRVX'})

#Append alle huidige prijzen
for osdorp in find_class:
    integer = osdorp.find('span', {'class':'price-amount_integer__1cJgL'})
    fractional = osdorp.find('span', {'class':'price-amount_fractional__2wVIK'})
    integer_list.append(integer.string)
    fractional_list.append(fractional.string)
    
#remove '' from price elements
integer_clean = list(map(int, integer_list))
fractional_clean = list(map(int, fractional_list))

#divide fractional element of price by 100 to match actual price
actual_fractional = np.array(fractional_clean)/100

#Lege lists voor prijs en naam
price = []
names = []

#Add integer and fractional elements of price in to 1 float
for k in range(0, len(integer_list)):
    price.append(integer_clean[k] + actual_fractional[k])

#Get names from wines
for link in soup.find_all('a', {'class' : 'link_root__65rmW product-card-portrait_link__1ROKP' }):
    names.append(link.get('title'))

"""Vivino gedeelte"""
#specify search url
search_url2 = 'http://www.vivino.com'
#Go to Vivino and click cookie button
driver.get(search_url2)
driver.implicitly_wait(1000)
driver.find_element_by_xpath("//*[@class='jss18']").click()
#MuiButtonBase-root MuiButton-root jss1 MuiButton-outlined jss3 MuiButton-outlinedSecondary jss4 MuiButton-disableElevation MuiButton-fullWidth'
#wijnscore lijst
wijnscore = []

#enter wijnnaam in vivino
m = 0
while m < len(names):
    search_bar = driver.find_element_by_name('q') #find searchbar
    search_bar.clear()
    zoekopdracht = names[0+m]
    search_bar.send_keys(zoekopdracht)
    search_bar.send_keys(Keys.RETURN)
    time.sleep(5)  # wait for page to fully load before getting html
    soup_url = driver.current_url # pak html code van current page
    usock2 = urlopen(soup_url)
    data2 = usock2.read()
    usock2.close()
    soup2 = BS(data2)  # maak soupp van current html
    score = soup2.find('div',{'class' : 'text-inline-block light average__number'})
    if score is None :
        wijnscore.append(0)
        m += 1
        continue
    else:
        score_string = score.string
        score_string1 =  score_string.replace(',', '.')  # clean up score from useless elements
        score_clean1 = score_string1.replace('\n', '')
        score_clean2 = score_clean1.replace('\n', '')
        score_clean3 = score_clean2.replace("'", "")
        wijnscore.append(float(score_clean3))
        time.sleep(6.5) ## mandatory waiting time to not overload vivino site
        m += 1

# Dataframe maken van dictionary met alle informatie
d = { "Naam" : names, " Prijs": price ,"Score": wijnscore}  # make dictionary of names, price and score
df = pd.DataFrame(d)

df.to_excel('wijnschoon.xls')