from flask import Flask, render_template, url_for, request, redirect
import os 
from flask_sqlalchemy import SQLAlchemy
import random
import string
app = Flask(__name__, static_url_path='/static')

app.config['SQLALCHEMY_DATABASE_URI'] ="sqlite:///urls.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.before_first_request
def create_tables():
    db.create_all()

class Urls(db.Model):
    id_ = db.Column("id_", db.Integer, primary_key=True)
    long = db.Column("long", db.String())
    short = db.Column("short", db.String(10))

    def __init__(self, long, short):
        self.long = long
        self.short = short


@app.route('/')
def index():
	return render_template('index.html')

def shorten_url():
	letters = string.ascii_lowercase + string.ascii_uppercase
	while True:
		rand_letters = random.choices(letters, k=3)
		rand_letters = "".join(rand_letters)
		short_url = Urls.query.filter_by(short=rand_letters).first()
		if not short_url:
			return rand_letters

@app.route('/url_process', methods=['POST', 'GET'])
def url_process():
	if request.method == 'POST':
		url_received = request.form["url_pro"]
		found_url = Urls.query.filter_by(long=url_received).first()
		if found_url:
			return redirect(url_for("display_short_url", url=found_url.short))
		else:
			short_url = shorten_url()
			print(short_url)
			new_url = Urls(url_received, short_url)
			db.session.add(new_url)
			db.session.commit()
			return redirect(url_for("display_short_url", url=short_url))
	else:
		return render_template('index.html')

@app.route('/display/<url>')
def display_short_url(url):
    return render_template('results.html', short_url_display=url)

@app.route('/<short_url>')
def redirection(short_url):
    long_url = Urls.query.filter_by(short=short_url).first()
    if long_url:
        return redirect(long_url.long)
    else:
        return f'<h1>Url doesnt exist</h1>'

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


@app.route('/all_url')
def display_all():
    return render_template('all.html', vals=Urls.query.all())

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                 endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

if __name__=='__main__':
	app.run(port=5000, debug=True)