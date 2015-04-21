from bs4 import BeautifulSoup
import requests

url = "https://www.google.com/search?q=" + "travel"

r = requests.get(url)
data = r.text
soup = BeautifulSoup(data)
ad = soup.find('span', 'ac')
title = ad.find_previous('cite')
#print soup.prettify().encode('utf8')
print ad
print title

logo_url = "http://www.brandsoftheworld.com/logo/expedia?original=1"
r = requests.get(logo_url)
soup = BeautifulSoup(r.text)
img = soup.find('img', 'image')
print img['src']

#ad.find_parents('div')
#print title
