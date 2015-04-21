from clarifai.client import ClarifaiApi
from instagram.client import InstagramAPI
from bs4 import BeautifulSoup
import json, re, requests, logging, urllib2, random
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

def getInstagrams(lex):
	access_token = creds['ig_token']
	ig_api = InstagramAPI(access_token=access_token)
	liked_media, next_ = ig_api.user_liked_media()

	imagedir = '/root/lexograd/photosynthesis/static/assets/images/'

        media = liked_media[random.randint(0, len(liked_media)-1)]
        try:
                url = re.sub('\Image:\s', '', str(media.images['standard_resolution']))
                print url
                # f = urllib2.urlopen(url)
                # data = f.read()
                # with open(imagedir + media.id + '.jpg', 'wb') as code:
                        # code.write(data)
                lex.append(Lexograd(url))
        except AttributeError:
                pass

class Lexograd():
	def __init__(self, url):
		self.url = url
		self.tags = None

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
			title = soup.find('cite')
                        if title != None:
                                title = str(title)
                                title = title.replace('<cite>','')
                                title = title.replace('</cite>','')
                                title = title.replace('<b>','')
                                title = title.replace('</b>','')
                                self.title = title

                        ad = soup.find('span', 'ac')

                        if ad != None:
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
                                            if len(short) < 55:
                                                short += ' ' + a
                                        self.copy = short
                                        break
@app.route("/")
def index():
    return send_file('static/index.html')
        
@app.route("/submit",methods=['GET','POST'])
def submit():
    media=[]
    getInstagrams(media)
    index=0

    lexograds=[]
    for m in media:
        m.extractTags()
        m.getAdCopy()
        if m.copy:
            print m.copy
            lexograds.append(m)

    pick = lexograds[random.randint(0,len(lexograds)-1)] 
    
    res = []
    res.append(pick.url)
    res.append(pick.tags)
    res.append(pick.copy)
    res.append(pick.title)
    return json.dumps(res)

if __name__ == '__main__':
        app.run(port=8080, debug=True)
