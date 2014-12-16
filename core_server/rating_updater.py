#!/usr/bin/python2.7
import pymongo
from datetime import datetime
from bson.objectid import ObjectId

class Updater:
    def _initDB(self):
        client = pymongo.MongoClient('localhost', 27017, w=1)
        self.db = client['p2dvin']

    def _updateAIRating(self):
        lastid = self.db.updater.find_one({'type': 'ai'})['id']
        nowid = lastid

        ratingList = dict()
        for ai in self.db.ais.find({}):
            ratingList[str(ai['_id'])] = ai['rating']

        for rec in self.db.records.find({'_id': {'$gt': lastid}}).sort('_id', 1):
            nowid = rec['_id']
            if rec['ids'][0] == rec['ids'][1]:
                continue
            ai0 = self.db.ais.find_one({'_id':rec['ids'][0]})
            ai1 = self.db.ais.find_one({'_id':rec['ids'][1]})
            R0 = ai0['rating']
            R1 = ai1['rating']
            E0 = 1 / (1 + 10**((R1 - R0)/400))
            E1 = 1 / (1 + 10**((R0 - R1)/400))
            if rec['result'] == 0:
                S0, S1 = 1, 0
            elif rec['result'] == 1:
                S0, S1 = 0, 1
            else:
                S0, S1 = 0.5, 0.5
            r0 = int(R0 + 42 * (S0 - E0))
            r1 = int(R1 + 42 * (S1 - E1))

            if r0 != R0:
                self.db.ais.update({'_id':rec['ids'][0]}, {'$set': {'rating':r0}})
            if r1 != R1:
                self.db.ais.update({'_id':rec['ids'][1]}, {'$set': {'rating':r1}})

        if nowid == lastid:
            return
        for ai in self.db.ais.find({}):
            if ai['rating'] != ratingList[str(ai['_id'])]:
                self.db.airatings.insert({'id': ai['_id'], 'rating': ai['rating'], 'date': datetime.utcnow()})
        self.db.updater.update({'type': 'ai'}, {'$set': {'id': nowid}})

    def _updateUserRating(self):
        lastid = self.db.updater.find_one({'type': 'user'})['id']
        nowid = lastid

        ratingList = dict()
        for user in self.db.users.find({}):
            ratingList[str(user['_id'])] = user['rating']

        for rec in self.db.records.find({'_id': {'$gt': lastid}}).sort('_id', 1):
            nowid = rec['_id']
            if rec['user0'] == rec['user1']:
                continue
            user0 = self.db.users.find_one({'name':rec['user0']})
            user1 = self.db.users.find_one({'name':rec['user1']})
            R0 = user0['rating']
            R1 = user1['rating']
            E0 = 1 / (1 + 10**((R1 - R0)/400))
            E1 = 1 / (1 + 10**((R0 - R1)/400))
            if rec['result'] == 0:
                S0, S1 = 1, 0
            elif rec['result'] == 1:
                S0, S1 = 0, 1
            else:
                S0, S1 = 0.5, 0.5
            r0 = int(R0 + 16 * (S0 - E0))
            r1 = int(R1 + 16 * (S1 - E1))

            if r0 != R0:
                self.db.users.update({'name':rec['user0']}, {'$set': {'rating':r0}})
            if r1 != R1:
                self.db.users.update({'name':rec['user1']}, {'$set': {'rating':r1}})

        if nowid == lastid:
            return
        for user in self.db.users.find({}):
            if user['rating'] != ratingList[str(user['_id'])]:
                self.db.userratings.insert({'id': user['_id'], 'rating': user['rating'], 'date': datetime.utcnow()})
        self.db.updater.update({'type': 'user'}, {'$set': {'id': nowid}})

    def Run(self):
        self._initDB()
        self._updateAIRating()
        self._updateUserRating()

updater = Updater()
updater.Run()
