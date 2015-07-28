import re, requests
from bs4 import BeautifulSoup

exclamation = re.compile('^(.*?)\!')
period = re.compile('^(.*?)\.')

url = "https://www.google.com/search?q=" + "travel"
r = requests.get(url)
data = r.text
soup = BeautifulSoup(data)

title = soup.find('cite')
if title != None:
        title = str(title)
        title = title.replace('<cite>','')
        title = title.replace('</cite>','')
        title = title.replace('<b>','')
        title = title.replace('</b>','')
        print title

ad = soup.find('span', 'ac')
print str(ad)

ad = soup.find('div', 'ads-creative')
print str(ad)

if ad != None:
	ad = str(ad)
	ad = ad.replace('<div class=\"ads-creative\">','')
	ad = ad.replace('</div>','')
	ad = ad.replace('<b>','')
	ad = ad.replace('</b>','')
	ad = ad.replace('<br>',' ')
	ad = ad.replace('</br>','')
	ad = ad.replace('&amp;','')
        if ad[-1] == '.' or ad[-1] == '!':
            ad = ad[0:-1]
	match_exclamation = re.match(exclamation, ad)
	match_period = re.match(period, ad)
        if match_exclamation:
                #print 'match excl'
		print match_exclamation.group(0)
        elif match_period:
                #print 'match period'
		print match_period.group(0)
        else:
                #print 'ad split'
                ad = ad.split(' ')
                short = ad[0]
                for a in ad[1:]:
                    if len(short) < 35:
                        short += ' ' + a
                print short

