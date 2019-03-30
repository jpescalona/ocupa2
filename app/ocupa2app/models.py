from datetime import datetime
from django_neomodel import DjangoNode
from neomodel import StringProperty, DateTimeProperty, UniqueIdProperty, IntegerProperty, \
    RelationshipTo, RelationshipFrom

class SocialNetwork(DjangoNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True)
    user = RelationshipFrom('User', 'HAS_ACCOUNT')


class User(DjangoNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True)
    created = DateTimeProperty(default=datetime.utcnow)
    refreshed = DateTimeProperty(default=datetime.utcnow)
    social_network = RelationshipTo(SocialNetwork, 'HAS_ACCOUNT')
    post = RelationshipFrom('Post', 'BELONGS_TO')

class InstagramPost(DjangoNode):
    uid = UniqueIdProperty()
    like_count = IntegerProperty()
    created = DateTimeProperty(default=datetime.utcnow)
    user = RelationshipTo(User, 'BELONGS_TO')

    comment_count = IntegerProperty()
    media_type = StringProperty()

class TweeterPost(DjangoNode):
    uid = UniqueIdProperty()
    like_count = IntegerProperty()
    created = DateTimeProperty(default=datetime.utcnow)
    user = RelationshipTo(User, 'BELONGS_TO')

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

