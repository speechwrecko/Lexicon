from flask import Flask, render_template, request, redirect, url_for, make_response
from werkzeug import secure_filename
from wtforms import Form, StringField, validators
from compute import compute
from database import InsertRow, ExportCSV
import sqlite3
import time
import csv
import os
#import string
import re

# !/usr/bin/env python

UPLOAD_FOLDER_NT = './'
UPLOAD_FOLDER_POSIX = ''
ALLOWED_EXTENSIONS = set(['csv'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER_NT


# Setup a class for form fields and validators
class InputForm(Form):
    r = StringField('r', validators=[validators.optional()])
    w = StringField('w', validators=[validators.required()])
    p = StringField('p', validators=[validators.required()])


# Function for loading the lexicon
def LoadLexicon(Path):
    return sqlite3.connect(Path)

# Function to check if an inputed file is of the proper type
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# View fucntion for the download link in the UI
@app.route('/download/')
def download():
    # Check if it is a windows machine for correct path
    if os.name == 'nt':
        db = LoadLexicon('DB\lexicon_3_28_17.db')
    # Otherwise assume linux
    else:
        db = LoadLexicon('DB/lexicon_3_28_17.db')

    # Export any user added entries to lexicon
    ExportCSV(db)
    db.close()

    # Create a response out of the CSV string
    response = make_response(open('lexicon_update.csv').read())

    # Set header of respond for downloaded
    response.headers["Content-Disposition"] = "attachment; filename=lexicon_update.csv"

    redirect(url_for('index', ))
    return response


# View function for teh main form
@app.route('/lexicon', methods=['GET', 'POST'])
def index():

    # Initialize variables and load DB
    missing_words = []
    if os.name == 'nt':
        db = LoadLexicon('DB\lexicon_3_28_17.db')
    else:
        db = LoadLexicon('DB/lexicon_3_28_17.db')

    form = InputForm(request.form)
    if request.method == 'POST':  # and form.validate():
        s = None

        # Check is search button was pusehd
        if request.form['btn'] == 'search':
            w = p = g = None

            #read in form data and send SQLITE For query
            r = form.r.data
            s = compute(r, db)

        #check if add button was pushed
        elif request.form['btn'] == 'add' and form.validate():
            r = s =g = None

            #readin form data and add to database
            w = form.w.data
            p = form.p.data
            date = time.strftime("%m/%d/%Y")
            source = 'user'
            row = (w, p, date, source)
            InsertRow(db, row)

        #check if upload button was pusehd
        elif request.form['btn'] == 'Upload':  # and form.validate():
            r = w = p = s = None
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if os.name == 'nt':
                with open(filepath, 'r', newline='') as f:
                    reader = csv.reader(f, dialect=csv.excel_tab)
                    file_list = list(reader)
                    f.close()
            else:
                with open(filepath, 'r') as f:
                    reader = csv.reader(f, dialect=csv.excel_tab)
                    file_list = list(reader)
                    f.close()

            for files in file_list:
                words = ' '.join(files).split(' ')
                for word in words:
                    word = word.lower()
                    word = word.strip()
                    #translator = str.maketrans('', '', string.punctuation)
                    #word = word.translate(translator)
                    word = re.sub("[^\w^\s^\'^\-]+",'',word)
                    out = compute(word, db)
                    if len(out) == 0:
                        missing_words.append(word)
            if os.name == 'nt':
                with open('outofvocabulary.csv', 'w', newline='') as csvfile:
                    spamwriter = csv.writer(csvfile, dialect=csv.excel_tab)
                    missing_words = (set(missing_words))
                    #spamwriter.writerows(missing_words)
                    for item in missing_words:
                        spamwriter.writerow([item])
                    csvfile.close()
            else:
                with open('outofvocabulary.csv', 'w') as csvfile:
                    spamwriter = csv.writer(csvfile, dialect=csv.excel_tab)
                    missing_words = (set(missing_words))
                    #spamwriter.writerows(missing_words)
                    for item in missing_words:
                        spamwriter.writerow([item])
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
