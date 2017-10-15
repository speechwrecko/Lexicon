from flask import Flask, render_template, request, redirect, url_for, make_response
from werkzeug import secure_filename
from wtforms import Form, StringField, validators
from compute import compute
from database import InsertRow, ExportCSV
import sqlite3
import time
import csv
import os

# !/usr/bin/env python

UPLOAD_FOLDER = './'
ALLOWED_EXTENSIONS = set(['csv'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Model
class InputForm(Form):
    r = StringField('r', validators=[validators.optional()])
    w = StringField('w', validators=[validators.required()])
    p = StringField('p', validators=[validators.required()])
    g = StringField('g', validators=[validators.required()])


# Lexicon
def LoadLexicon(Path):
    return sqlite3.connect(Path)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


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
    missing_words = []
    db = LoadLexicon('DB\lexicon_3_28_17.db')
    form = InputForm(request.form)
    if request.method == 'POST':  # and form.validate():
        s = None
        if request.form['btn'] == 'search':
            w = None
            p = None
            g = None
            r = form.r.data
            s = compute(r, db)
        elif request.form['btn'] == 'add' and form.validate():
            r = None
            s = None
            g = None
            w = form.w.data
            p = form.p.data
            date = time.strftime("%m/%d/%Y")
            source = 'user'
            row = (w, p, date, source)
            InsertRow(db, row)
        elif request.form['btn'] == 'Upload':  # and form.validate():
            r = None
            w = None
            p = None
            s = None
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            with open(filepath, 'r', newline='') as f:
                reader = csv.reader(f, dialect=csv.excel_tab)
                file_list = list(reader)
                f.close()
            for files in file_list:
                words = ' '.join(files).split(' ')
                for word in words:
                    out = compute(word, db)
                    if len(out) == 0:
                        missing_words.append(word)
            with open('outofvocabulary.csv', 'w', newline='') as csvfile:
                spamwriter = csv.writer(csvfile, dialect=csv.excel_tab)
                spamwriter.writerows(missing_words)
                csvfile.close()
                # We need to modify the response, so the first thing we
                # need to do is create a response out of the CSV string
                response = make_response(open('outofvocabulary.csv').read())
                # This is the key: Set the right header for the response
                # to be downloaded, instead of just printed on the browser
                response.headers["Content-Disposition"] = "attachment; filename=outofvocabulary.csv"
                redirect(url_for('index', ))
                return response

    else:
        r = None
        g = None
        w = None
        p = None
        s = None

    db.close()

    form.w.data = form.p.data = form.r.data = None
    return render_template("view.html", form=form, s=s)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
