import sqlite3
import csv

def InsertRow(db, row):
    cursor2 = db.cursor()
    cursor2.execute('insert into lexicon values (?,?,?,?)', (row[0], row[1], row[2], row[3]))
    db.commit();
    return

def ExportCSV(db):
    csv_cursor = db.cursor()
    csv_cursor.execute('SELECT * FROM lexicon WHERE source = "user"')
    with open('lexicon_update.csv', 'w', newline='') as out_csv_file:
        csv_out = csv.writer(out_csv_file)
        # write header
        csv_out.writerow([d[0] for d in csv_cursor.description])
        # write data
        for result in csv_cursor:
            csv_out.writerow(result)

    out_csv_file.close()
    return out_csv_file
