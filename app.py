from flask import Flask, render_template, request , flash
from flask_sqlalchemy import SQLAlchemy
import datetime
import math
import csv

import os
current_dir=os.path.abspath(os.path.dirname(__file__))

app=Flask('__name__')
app.secret_key='noone_knows'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir, "database.sqlite3")
UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER
db=SQLAlchemy()
db.init_app(app)
app.app_context().push()

class User(db.Model):
  __tablename__ ='user'
  username = db.Column(db.String ,primary_key = True, nullable= False)
  password = db.Column(db.String, nullable= False)
  user_deck = db.relationship("Deck" , cascade='all, delete-orphan',backref='user' )
  def __init__(self,username,password):
        self.username = username
        self.password = password

class Deck(db.Model):
    __tablename__ ='deck'
    d_id= db.Column(db.Integer, primary_key = True,nullable=False, autoincrement=True)
    deck_topic = db.Column(db.String , nullable= False)
    d_username = db.Column(db.String , db.ForeignKey('user.username'), nullable=False)
    last_reviewed=db.Column(db.String,default="")
    d_score=db.Column(db.Integer,default=0)
    deck_card = db.relationship("Card" ,cascade='all, delete-orphan', backref='deck')
    def __init__(self, d_username, deck_topic, last_reviewed, d_score):
      self.d_username = d_username
      self.deck_topic = deck_topic
      self.last_reviewed= last_reviewed
      self.d_score=d_score


class Card(db.Model):
    __tablename__ ='card'
    c_id= db.Column(db.Integer,primary_key=True, autoincrement=True)
    c_d_id= db.Column(db.Integer,db.ForeignKey('deck.d_id'))
    question = db.Column(db.String , nullable= False)
    answer = db.Column(db.String , nullable= False)
    score= db.Column(db.Integer, default=0)
    def __init__(self, c_d_id, question, answer, score):
          self.c_d_id=c_d_id
          self.question = question
          self.answer = answer
          self.score= score




@app.route("/" ,methods=["GET"])
def index():
    return render_template("first.html")

@app.route("/login" ,methods=["GET"])
def login():
    return render_template("login.html")
@app.route("/login" ,methods=["POST"])
def login_submit():
    username= request.form.get("uname")
    password= request.form.get("psw")
    if username and password:
        exists = User.query.filter_by(username=username).first()
        if exists:
            if exists.password == password:
                return dashboard(username)
            else:
                flash('You got the password wrong :(')
                return render_template('login.html')
        else:
            flash('This user does not exists. Try signing up!')
            return render_template('login.html')
    else:
        flash('Both username and password are mandatory fields!')
        return render_template('login.html')

@app.route("/signup" ,methods=["GET"])
def signup():
    return render_template("signup.html")
@app.route("/signup" ,methods=["POST"])
def signup_submit():
    username= request.form.get("uname")
    password= request.form.get("psw")
    if username and password:
        exists = User.query.filter_by(username=username).first()
        if exists:
            flash('This user already exists. Try a different username or signup!')
            return render_template('login.html')
        else:
            u= User(username, password)
            db.session.add(u)
            db.session.commit()
            return dashboard(username)
    else:
        flash('Both username and password are mandatory fields!')
        return render_template('login.html')

@app.route("/dashboard/<string:username>", methods=["GET"])
def dashboard(username):
    user=User.query.filter_by(username=username).first()
    decks=Deck.query.filter_by(d_username=username).all()
    return render_template("dashboard.html",username=username,decks=decks)

@app.route("/add_deck/<string:username>", methods=["GET"])
def add_deck(username):
    return render_template("adddeckform.html",username=username)
@app.route("/add_deck/<string:username>", methods=["POST"])
def add_deck_submit(username):
    deck_topic= request.form.get("decdes")
    user_has_deck= Deck.query.filter_by(d_username=username, deck_topic=deck_topic).first()
    print(user_has_deck)
    if user_has_deck:
        flash("You already have a deck named " + deck_topic + ". Try a different name!")
        return add_deck(username)
        print('goes to if')
    else :
        d= Deck(username, deck_topic,"",0)
        print(d)
        db.session.add(d)
        db.session.commit()
        return dashboard(username)

@app.route("/edit_deck/<string:username>/<string:deck_topic>", methods=["GET"])
def edit_deck(username, deck_topic):
    deck=Deck.query.filter_by(d_username=username, deck_topic=deck_topic).first()
    c_d_id=deck.d_id
    cards= Card.query.filter_by(c_d_id=c_d_id).all()
    return render_template("edit_deck.html", username=username, deck_topic=deck_topic, cards=cards)

@app.route("/edit_deck/<string:username>/<string:deck_topic>", methods=["POST"])
def add_card(username, deck_topic):
    question= request.form.get("question")
    answer= request.form.get("answer")
    deck=Deck.query.filter_by(d_username=username, deck_topic=deck_topic).first()
    c_d_id=deck.d_id
    c = Card(c_d_id,question,answer,0)
    db.session.add(c)
    db.session.commit()
    return edit_deck(username,deck_topic)

@app.route("/delete_card/<string:username>/<string:deck_topic>/<int:c_id>", methods=["GET","POST"])
def delete_card(username,deck_topic,c_id):
    c=Card.query.filter_by(c_id=c_id).first()
    db.session.delete(c)
    db.session.commit()
    return edit_deck(username,deck_topic)

@app.route("/delete_deck/<string:username>/<string:deck_topic>", methods=['GET','POST'])
def delete_deck(username, deck_topic):
    d= Deck.query.filter_by(d_username=username, deck_topic=deck_topic).first()
    db.session.delete(d)
    db.session.commit()
    return dashboard(username)

@app.route("/review/<string:username>/<string:deck_topic>", methods=['GET'])
def deck_review(username, deck_topic):
    deck=Deck.query.filter_by(d_username=username, deck_topic=deck_topic).first()
    data=Card.query.filter_by(c_d_id=deck.d_id).all()
    n=0
    if data:
        c=data[n]
        return render_template('review.html',c=c,n=n,username=username,deck_topic=deck_topic)
    else:
        return render_template('no_cards_review.html',username=username,deck_topic=deck_topic)

@app.route("/review/<string:username>/<string:deck_topic>/<int:loop_no>", methods=['POST'])
def deck_review_next(username, deck_topic,loop_no):
    deck=Deck.query.filter_by(d_username=username, deck_topic=deck_topic).first()
    c_d_id=deck.d_id
    data=Card.query.filter_by(c_d_id=c_d_id).all()
    i=int(loop_no)
    prev=data[i]
    prev.score=request.form.get('gridRadios')
    db.session.commit()
    n=i+1
    if n==len(data):
        dt=datetime.datetime.now()
        t=str(datetime.datetime.time(dt).hour) +":"+str(datetime.datetime.time(dt).minute) + "," +str(datetime.datetime.date(dt))
        s=0
        for x in data:
            s+=int(x.score)
        f=s/len(data)
        fs=math.ceil(f/6*100)
        deck.last_reviewed=t
        ls=deck.d_score
        if ls!=0:
            nsl=math.ceil((ls+fs)/2)
        else:
            nsl=fs
        deck.d_score= nsl
        db.session.commit()
        return render_template('success.html',fs=fs,nsl=nsl,username=username,deck_topic=deck_topic)
    else:
        c=data[n]
        return render_template('review.html',c=c,n=n,username=username,deck_topic=deck_topic)

@app.route("/edit_card/<string:username>/<string:deck_topic>/<int:c_id>" , methods =["POST"])
def edit_card(username,deck_topic,c_id):
    c=Card.query.filter_by(c_id=c_id).one()
    if c:
        c.question=request.form.get("question2")
        c.answer=request.form.get("answer2")
        db.session.commit()
        return edit_deck(username, deck_topic)

@app.route("/import_deck/<string:username>", methods=["POST"])
def import_deck_csv(username):
    # get the uploaded file
    uploaded_file = request.files['file_import']
    if uploaded_file.filename != '':
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
    # set the file path
    uploaded_file.save(file_path)
    csvfile=open(file_path, 'r')
    csvreader=csv.reader(csvfile)
    rows=[]
    for row in csvreader:
        rows.append(row)
    deck_topic=rows[0][1]
    d=Deck(username,deck_topic,"",0)
    db.session.add(d)
    parent=Deck.query.filter_by(d_username=username,deck_topic=deck_topic).first()
    pd_id=parent.d_id
    for i in range(2,len(rows)):
        c=Card(pd_id,rows[i][0],rows[i][1],0)
        db.session.add(c)
        db.session.commit()
    return dashboard(username)

from flask_restful import Api, Resource, reqparse, fields, marshal_with
api=Api(app)
resource_fields={'question': fields.String, 'answer': fields.String, 'score':fields.Integer}

class DeckAPI(Resource):
    @marshal_with(resource_fields)
    def get(self,username,deck_topic):
        d= Deck.query.filter_by(d_username=username, deck_topic=deck_topic).first()
        deck_id=d.d_id
        c_list= Card.query.filter_by(c_d_id=deck_id).all()
        return c_list

api.add_resource(DeckAPI,"/deckapi/<string:username>/<string:deck_topic>")

if __name__ == '__main__':
#run the flask app
    app.run(host='0.0.0.0', debug=True, port=8080)
