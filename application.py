from flask import Flask, url_for, render_template, request, session, escape, redirect
from flaskext.mongoalchemy import MongoAlchemy
import time

app = Flask(__name__)

# Define the database configuration and get an instance of the database
app.config['MONGOALCHEMY_DATABASE'] = 'library'
db = MongoAlchemy(app)

# Create classes to represent objects to store in the database:
class User(db.Document):
    name = db.StringField()
    password = db.StringField()
    id = db.IntField()

# If root requested:
#
# If the user is logged in, display a message
# Else, display a link inviting user to login.
@app.route("/")
def index():
    if 'id' in session:
        user = User.query.filter(User.id == session['id']).first()
        return 'Logged %s with id %d' % (user.name, session['id'])
    return '<h1>You are not logged in</h1>Login <a href="login">here</a>'
    
# If /register/ requested:
#
# If method for requesting this URL is POST, then the variables are extracted 
# and checked and then stored in the database (using User class) and redirect to login
# page.
# If method is GET (i.e. standard HTTP request), then show the registration form.
@app.route('/register/', methods=['POST', 'GET'])
def register():
    myError = None
    if request.method == 'POST':
            if request.form['password1'] == request.form['password2']:
                person = User.query.filter(User.name == request.form['username']).first()
                if person == None:
                    uName = request.form['username']
                    uPassword = request.form['password1']
                    uId = int(round(time.time() * 1000))
                    user = User(name=uName, password=uPassword, id=uId)
                    user.save()
                    return redirect(url_for('login'))
                else:
                    myError = 'That username is taken'
            else:
                myError = 'Passwords do not match'
    return render_template('register.html', error=myError)

# If /login/ requested:
#
# If request method is POST, get username and password. Check these in the database
# (by getting any User objects that exist with that username) and then verify the 
# password. If correct, add user to sessions and redirect to the URL for index page. 
# If wrong, return an error.
# If request method is GET (standard HTTP request), display the login page.
@app.route('/login/', methods=['POST', 'GET'])
def login():
    myError = None
    if request.method == 'POST':
        person = User.query.filter(User.name == request.form['username']).first()
        if not person == None:
            if person.password == request.form['password']:
                session['id'] = person.id;
                return redirect(url_for('index'))
            else:
                myError = 'Wrong password'
        else:
            myError = 'User doesn\'t exist'
    return render_template('login.html', error=myError)

# If /logout/ requested:
#
# Remove id from session and redirect to URL for the index page (i.e. "/")
@app.route('/logout/')
def logout():
    session.pop('id', None)
    return redirect(url_for('index'))
  
# If /upload/ requested:
#
# This route only supports POST (if you try and visit localhost:5000/upload directly,
# an error will occur).
# Method gets the filename from the form and saves it in the same directory as this 
# script.
@app.route('/upload/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['the_file']
        f.save(f.filename)
        return "Upload successful"


# If 404 error
#
# Load standard error page and insert appropriate error.
@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', error="Error 404: Page not found"), 404

    
# Main code
app.debug = True # set to true and server will display any errors to the page
app.secret_key = "supsersecretkey" # for sessions
app.run() # start the server

