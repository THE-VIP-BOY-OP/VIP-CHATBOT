from pymongo import MongoClient

import config

DAXXdb = MongoClient(config.MONGO_URL)
DAXX = DAXXdb["DAXXDb"]["DAXX"]


from .chats import *
from .users import *
