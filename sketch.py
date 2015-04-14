from clarifai.client import ClarifaiApi
from instagram.client import InstagramAPI
from bs4 import BeautifulSoup
import json, re, requests

creds = json.load(open('configuration.json'))

api = ClarifaiApi() # Assumes environmental variables have been set

def getInstagrams():
	access_token = creds['ig_token']
	ig_api = InstagramAPI(access_token=access_token)
	liked_media, next_ = ig_api.user_liked_media()

	urls = []

	for media in liked_media:
		try:
			url = re.sub('\Image:\s', '', str(media.images['standard_resolution']))
			urls.append(url)
		except AttributeError:
			continue

	return urls

def extractTags(image_urls):
	# imgFiles = [open(SYSPATH+fn) for fn in filenames]
	data = api.tag_image_urls(image_urls[8])

	# for f in imgFiles:
	# 	f.close()

	tags_probs = []
	for r in data['results']:
		try:
			obj = r['result']['tag']
			tags_probs.extend(zip(obj['classes'], obj['probs']))
		except KeyError:
			pass

	return sorted(tags_probs, key=lambda x: x[1])

urls = getInstagrams()
sorted_tags = extractTags(urls)

copy = []

for i in range(len(sorted_tags)):
	# url = "https://www.google.com/search?q=travel"
	url = "https://www.google.com/search?q=" + str(sorted_tags[i][0])
	r = requests.get(url)
	data = r.text
	soup = BeautifulSoup(data)
	ad = soup.find('span', 'ac')
	if ad != None:
		copy.append(ad)

print copy