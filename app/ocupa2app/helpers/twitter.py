import requests

class Twitter():

    BASE_URL = 'http://hackathon.ocupa2.com/twitter/1.1/'

    def __init__(self,user_id, token=None):
        self.token = token
        self.user_id = user_id
        self.cache = dict()

    def get_token(self):
        if not self.user_id:
            raise KeyError("You must specify the user_id")
        url = Twitter.BASE_URL + 'get/key'
        d = requests.get(url, {'email': self.user_id})
        self.token = d.json()['key']
        return self.token

    def get_posts_by_hashtag(self, hashtag):
        url = Twitter.BASE_URL + 'search/tweets.json'
        params = {'hashtag': hashtag}
        d = requests.get(url, params)
        return d.json()
    
    def get_top_posts(self, hashtag_id):
        url = Twitter.BASE_URL + '{id}/top_media'.format(id=hashtag_id)
        params = {'user_id': self.user_id}
        d = requests.get(url, params)
        try:
            return d.json()
        except:
            return []

    def get_media(self, media_id):
        url = Twitter.BASE_URL + 'media/{id}'.format(id=media_id)
        params = {'fields': 'id,comments_count,like_count,media_type,username'}
        d = requests.get(url, params)
        return d.json()

    def get_user(self, user_id):
        url = Twitter.BASE_URL + '{id}'.format(id=user_id)
        params = {'fields': 'id,username,media_count,follower_count'}
        d = requests.get(url, params)
        return d

        