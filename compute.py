import math
import sqlite3

def compute(r, db):
    #db = sqlite3.connect('DB/lexicon_3-28_17.db')
    cursor = db.cursor()
    cursor.execute('''SELECT word, spelling FROM lexicon WHERE word like ?''',(r,))
    return cursor.fetchall()