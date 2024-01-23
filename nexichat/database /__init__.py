from pymongo import MongoClient

import config

DAXXdb = MongoClient(config.MONGO_URL)
DAXX = DAXXdb["VIPDB"]["VIP"]


from .chats import *
from .users import *
