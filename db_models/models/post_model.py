import mongoengine
import datetime
from .user_model import UserModel


class Posts(mongoengine.Document):
    """Main model"""
    post = mongoengine.BinaryField(required=True)
    """Original File"""
    date = mongoengine.DateTimeField(default=datetime.datetime.now)
    user = mongoengine.ReferenceField(UserModel, reverse_delete_rule=mongoengine.CASCADE, required=True)
    location = mongoengine.StringField(required=True)
    meta = {
        'db_alias': 'core',
        'collection': 'posts'
    }
