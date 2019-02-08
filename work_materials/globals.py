from telegram.ext import Updater
from config import ProductionToken, request_kwargs, psql_creditals

import psycopg2

castles = ['🍆', '🍁', '☘', '🌹', '🐢', '🦇', '🖤']
classes_list = ['⚗️Alchemist', '⚒Blacksmith', '📦Collector', '🏹Ranger', '⚔️Knight', '🛡Sentinel']

processing = 1

conn = psycopg2.connect("dbname={0} user={1} password={2}".format(psql_creditals['dbname'], psql_creditals['user'], psql_creditals['pass']))
conn.set_session(autocommit = True)
cursor = conn.cursor()

updater = Updater(token=ProductionToken, request_kwargs=request_kwargs)

dispatcher = updater.dispatcher
job = updater.job_queue
