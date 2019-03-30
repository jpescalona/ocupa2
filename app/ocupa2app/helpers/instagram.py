import requests

class Instagram():

    BASE_URL = 'http://hackathon.ocupa2.com/instagram/'

    def __init__(self,user_id, token=None):
        self.token = token
        self.user_id = user_id
        self.hashtag_cache = dict()
        self.user_cache = dict()
        self.media_cache = dict()

    def get_token(self):
        if not self.user_id:
            raise KeyError("You must specify the user_id")
        url = Instagram.BASE_URL + 'get/key'
        d = requests.get(url, {'email': self.user_id})
        self.token = d.json()['key']
        return self.token

    # TODO Memoize in database
    def get_hashtag(self, hashtag):
        if hashtag not in self.hashtag_cache:
            url = Instagram.BASE_URL + 'ig_hashtag_search'
            params = {'q': hashtag, 'user_id': self.user_id }
            d = requests.get(url, params)
            j = d.json()
            if 'id' not in j:
                return None
            self.hashtag_cache[hashtag] = j['id']
        return self.hashtag_cache[hashtag]

    def get_recent_posts(self, hashtag_id):
        url = Instagram.BASE_URL + '{id}/recent_media'.format(id=hashtag_id)
        params = {'user_id': self.user_id}
        d = requests.get(url, params)
        try:
            return d.json()['data']
        except:
            return []
    
    def get_top_posts(self, hashtag_id):
        url = Instagram.BASE_URL + '{id}/top_media'.format(id=hashtag_id)
        params = {'user_id': self.user_id}
        d = requests.get(url, params)
        try:
            return d.json()['data']
        except:
            return []

    def get_media(self, media_id):
        if media_id not in self.media_cache:
            url = Instagram.BASE_URL + 'media/{id}'.format(id=media_id)
            params = {'fields': 'id,comments_count,like_count,media_type,username'}
            d = requests.get(url, params)
            self.media_cache[media_id] = d.json()
        return self.media_cache[media_id]

    def get_user(self, user_id):
        if user_id not in self.user_cache:     
            url = Instagram.BASE_URL + '{id}'.format(id=user_id)
            params = {'fields': 'id,username,media_count,follower_count'}
            d = requests.get(url, params)
            self.user_cache[user_id] = d
        return self.user_cache[user_id]

    def extend_posts(self, posts):
        """ Adds to each post the username field added to the posts """
        for post in posts:
            media = self.get_media(post['id'])
            post['username'] = media[0]['userId']

        