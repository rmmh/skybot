import os
import sqlite3


def get_db_connection(server, name='skybot.%s.db'):
    "returns an sqlite3 connection to a persistent database"
    filename = os.path.join(bot.persist_dir, name % server)
    return sqlite3.connect(filename, timeout=10)

bot.get_db_connection = get_db_connection
