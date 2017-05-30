import pymongo

host = '106.14.177.41'
port = 27017
user_name = 'exam'
user_pwd = 'g9vn5Bevn2EKtG'
db_name = 'gisdb'
coll_name = 'test'
def conn_mongo_3():
    '''
    host:port
    client.authenticate(username, password)
    '''
    mongo_client = pymongo.MongoClient("%s:%d" % (host, port))
    mongo_client[db_name].authenticate(user_name, user_pwd, db_name, mechanism='SCRAM-SHA-1')
    mongo_db = mongo_client[db_name]
    mongo_coll = mongo_db[coll_name]
    print("conn_mongo_3 -- count: %d" % mongo_coll.count())

conn_mongo_3()