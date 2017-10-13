from flask import Flask, render_template, request, redirect, url_for, make_response
from wtforms import Form, StringField, validators
from compute import compute
from database import InsertRow, ExportCSV
import sqlite3
import time
import csv

#!/usr/bin/env python

app = Flask(__name__)

# Model
class InputForm(Form):
    r = StringField('r', validators=[validators.optional()])
    w = StringField('w', validators=[validators.required()])
    p = StringField('p', validators=[validators.required()])
    #, validators.length(min=1), validators.InputRequired()



# Lexicon
def LoadLexicon(Path):
    return sqlite3.connect(Path)

@app.route('/download/')
def download():
    db = LoadLexicon('DB\lexicon_3_28_17.db')
    ExportCSV(db)
    db.close()

    # We need to modify the response, so the first thing we
    # need to do is create a response out of the CSV string
    response = make_response(open('lexicon_update.csv').read())
    # This is the key: Set the right header for the response
    # to be downloaded, instead of just printed on the browser
    response.headers["Content-Disposition"] = "attachment; filename=lexicon_update.csv"
    redirect(url_for('index', ))
    return response

# View
@app.route('/lexicon', methods=['GET', 'POST'])
def index():
    db = LoadLexicon('DB\lexicon_3_28_17.db')
    form = InputForm(request.form)
    if request.method == 'POST':# and form.validate():
        s = None
        if request.form['btn'] == 'search':
            w = None
            p = None
            r = form.r.data
            s = compute(r, db)
        elif request.form['btn'] == 'add' and form.validate():
            r= None
            s = None
            w = form.w.data
            p = form.p.data
            date = time.strftime("%m/%d/%Y")
            source = 'user'
            row = (w,p,date,source)
            InsertRow(db, row)

    else:
        r = None
        s = None
        w = None
        p = None

    db.close()

    form.w.data = form.p.data = form.r.data = None
    return render_template("view.html", form=form, s=s)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
