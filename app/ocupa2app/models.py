from datetime import datetime
from django_neomodel import DjangoNode
from neomodel import StringProperty, DateTimeProperty, UniqueIdProperty, IntegerProperty, \
    RelationshipTo, RelationshipFrom

class SocialNetwork(DjangoNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True)
    user = RelationshipFrom('User', 'HAS_ACCOUNT')


class User(DjangoNode):
    uid = StringProperty()
    name = StringProperty(unique_index=True)
    created = DateTimeProperty(default=datetime.utcnow)
    refreshed = DateTimeProperty(default=datetime.utcnow)
    social_network = RelationshipTo(SocialNetwork, 'HAS_ACCOUNT')
    media_count = IntegerProperty()
    follower_count = IntegerProperty()
    post = RelationshipTo('Post', 'BELONGS_TO')

class Post(DjangoNode):
    uid = StringProperty()
    created = DateTimeProperty(default=datetime.utcnow)
    user = RelationshipTo(User, 'BELONGS_TO')
    hashtags = RelationshipTo('HashTag', 'HAS_HASHTAG')
    like_count = IntegerProperty()

class InstagramPost(Post):
    comment_count = IntegerProperty()
    media_type = StringProperty()

class TwitterPost(Post):
    retweeted_count = IntegerProperty()
    reply_count = IntegerProperty()

class Category(DjangoNode):
    uid = UniqueIdProperty()
    name =  StringProperty(unique_index=True)
    hashtags = RelationshipFrom('HashTag', 'IS_FROM')

class HashTag(DjangoNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True)
    category = RelationshipTo(Category, 'IS_FROM')
    post = RelationshipFrom(Post, 'HAS_HASHTAG')
