import unirest, json

creds = json.load(open('configuration.json'))

def getInstagrams():
        ig_response = unirest.get("https://api.instagram.com/v1/users/self/media/liked",
                headers={
                    "Accept":"text/plain"
                    },
                params={
                    'access_token': creds['ig_token'],
                    'count': 100
                })
        links=[]

        for d in ig_response.body['data']:
             links.append(d['images']['standard_resolution'])

        return links

getInstagrams()
