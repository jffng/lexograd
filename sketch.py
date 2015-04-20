from clarifai.client import ClarifaiApi
from instagram.client import InstagramAPI
from bs4 import BeautifulSoup
import json, re, requests, logging, urllib2

# disable InsecureRequestWarning
# urllib3.disable_warnings()
logging.captureWarnings(True)

creds = json.load(open('configuration.json'))

# app = Flask(__name__)

# app.config['IMAGE_FOLDER'] = ''

api = ClarifaiApi() # Assumes environmental variables have been set

def getInstagrams(lex):
	access_token = creds['ig_token']
	ig_api = InstagramAPI(access_token=access_token)
	liked_media, next_ = ig_api.user_liked_media()

	imagedir = '~/Thesis/meditation/lexograd/static/assets/images/'

	for media in liked_media:
		try:
			url = re.sub('\Image:\s', '', str(media.images['standard_resolution']))
			print url
                        f = urllib2.urlopen(url)
			data = f.read()
			with open(media.id + '.jpg', 'wb') as code:
				code.write(data)
			lex.append(Lexograd(url, media.id))
		except AttributeError:
			continue

class Lexograd():
	def __init__(self, url, filename):
		self.filename = filename
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
			ad  = soup.find('span', 'ac')
			if ad != None:
				ad = str(ad)
				ad = ad.replace('<span class=\"ac\">','')
				ad = ad.replace('</span>','')
				ad = ad.replace('<b>','')
				ad = ad.replace('</b>','')
				ad = ad.replace('<br>','\n')
				ad = ad.replace('</br>','')
				ad = ad.replace('&amp;','')	
				self.copy = ad
                                break

lexograds = []

getInstagrams(lexograds)

for l in lexograds:
	l.extractTags()
	l.getAdCopy()

for l in lexograds:
	if l.copy:
		print l.copy

