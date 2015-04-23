from clarifai.client import ClarifaiApi
from instagram.client import InstagramAPI
from bs4 import BeautifulSoup
import json, re, requests, logging, urllib2, random, unirest
from flask import Flask, Response, request, send_file
from flask.ext.cors import CORS

logging.captureWarnings(True)

creds = json.load(open('configuration.json'))

app = Flask(__name__)
cors = CORS(app)
app.config.from_object(__name__)
app.config['IMAGE_FOLDER'] = '/root/lexograd/static/assets/images'

api = ClarifaiApi() # Assumes environmental variables have been set

exclamation = re.compile('^(.*?)\!')
period = re.compile('^(.*?)\.')

def getInstagrams():
        ig_response = unirest.get("https://api.instagram.com/v1/users/self/media/liked",
                headers={
                    "Accept":"text/plain"
                    },
                params={
                    'access_token': creds['ig_token'],
                    'count': 100
                })

        links = []

        for d in ig_response.body['data']:
             links.append(d['images']['standard_resolution']['url'])

        return links

class Lexograd():
	def __init__(self, url):
		self.url = url
		self.tags = None
                self.logo = None

	def extractTags(self):
		# imgFiles = [open(SYSPATH+fn) for fn in filenames]
		data = api.tag_image_urls(self.url)

		# for f in imgFiles:
		# 	f.close()

		tags_probs = []
		for r in data['results']:
			try:
				obj = r['result']['tag']
				tags_probs.extend(zip(obj['classes'], obj['probs']))
			except KeyError:
				pass

		self.tags = sorted(tags_probs, key=lambda x: x[1])
                print self.tags

	def getAdCopy(self):
		for i in range(len(self.tags)):
			url = "https://www.google.com/search?q=" + str(self.tags[i][0])
			r = requests.get(url)
			data = r.text
			soup = BeautifulSoup(data)
                        ad = soup.find('span', 'ac')
                        if ad != None:
                                title = ad.find_previous('cite')
                                if title != None:
                                        title = str(title)
                                        title = title.replace('<cite>','')
                                        title = title.replace('</cite>','')
                                        title = title.replace('<b>','')
                                        title = title.replace('</b>','')
                                        title = title.split('.')
                                        self.title = title[1]
                                        print self.title
                                        try:
                                                logo_url = "http://www.brandsoftheworld.com/logo/" + str(self.title) + "?original=1"
                                                print logo_url
                                                r = requests.get(logo_url)
                                                logo_soup = BeautifulSoup(r.text)
                                                img = logo_soup.find('img', 'image')
                                                self.logo = img['src']
                                                print self.logo
                                        except:
                                                pass
                                ad = str(ad)
                                ad = ad.replace('<span class=\"ac\">','')
                                ad = ad.replace('</span>','')
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
                                        self.copy = match_exclamation.group(0)
                                        break
                                elif match_period:
                                        #print 'match period'
                                        self.copy = match_period.group(0)
                                        break
                                else:
                                        #print 'ad split'
                                        ad = ad.split(' ')
                                        short = ad[0]
                                        for a in ad[1:]:
                                            if len(short) < 70:
                                                short += ' ' + a
                                        self.copy = short
                                        break
@app.route("/")
def index():
    return send_file('static/index.html')
        
@app.route("/submit",methods=['GET','POST'])
def submit():
    urls = getInstagrams()
    valid_lexograds = []
    
    while 1:
        index = random.randint(0, len(urls) - 1)
        temp_lex = Lexograd(urls[index])
        temp_lex.extractTags()
        temp_lex.getAdCopy()
        if temp_lex.copy:
            print temp_lex.copy
            pick = temp_lex
            break

    #pick = valid_lexograds[random.randint(0,len(valid_lexograds)-1)] 
    
    res = []
    res.append(pick.url)
    res.append(pick.tags)
    res.append(pick.copy)
    res.append(pick.title)
    res.append(pick.logo)
    return json.dumps(res)

if __name__ == '__main__':
        app.run(port=8080, debug=True)
