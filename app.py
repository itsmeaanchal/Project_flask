from flask import Flask , render_template,flash, redirect, url_for, session,logging,request
import pymysql
from flask_wtf import Form
from wtforms import TextField
from wtforms import StringField,TextAreaField,PasswordField ,validators
from passlib.hash import sha256_crypt
import data
from functools import wraps


app = Flask(__name__)
Articles = data.articles
app.debug = True

#config file
app.config["mysql_host"] = 'localhost'
app.config["mysql_user"] = 'root'
app.config["mysql_password"] = ''
app.config["mysql_db"] = 'myflaskapp'

mysql = pymysql.connect(app)


#home_page
@app.route('/')
def index():
    return render_template('home.html')

#about_page
@app.route('/about')
def about():
    return render_template('about.html')

#Articles..........
@app.route('/articles')
def articles():
    return render_template('articles.html', articles = Articles)

#single article
@app.route('/article/<string:id>/')
def article(id):
    return render_template('Article.html', id = id)

#Register_Form......
class RegisterForm(Form):
    name = StringField(u'Name', validators=[validators.length(min=1,max=5)])
    username  = StringField(u'UserName', validators=[validators.length(min=4,max=25)])
    email  = StringField(u'Email', validators=[validators.length(min=6,max=50)])
    password  = PasswordField(u'Password', validators=[validators.DataRequired(),validators.EqualTo('Confirm',message='Passwords do not match')])

    Confirm = PasswordField('Confirm Password') 


#route register
@app.route('/register.html')
def register():
    mysql = pymysql.connect(app)
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username =  form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

    #create cursor
    cur = mysql.connection.cursor()
    sql = "INSERT INTO users (%s) VALUES %r;" % (name,email,username,password)
    cur.execute(sql)

    #commit to db 
    mysql.connection.commit()
    #close conn
    cur.close()
    #flask flash msg
    flash('You are now registered and can log in','Successs')
#redirect
redirect(url_for('login'))

#route LOGIN
@app.route('/login.html',method = ['GET', 'POST'])
def login():
    mysql = pymysql.connect(app)
    
    if request.method == 'POST' :
        username =  request.form['username']
        password_c =  request.form['password']

    #create cursor
    cur = mysql.connection.cursor()

    #Get user by username
    sql = "SELECT * FROM users WHERE username = %", [username]
    result = cur.execute(sql)
    if result > 0:
        #Get Stored hash
        data = cur.fetchone()
        password = data['password']

        #compare password
        if sha256_crypt.verify(password_c, password):
            #passed
            session['logged_in'] = True
            session['username'] = username
            flash('You are now logged in','success')
            return redirect(url_for('dashboard'))
        else:
            #app.logger.info("PASSWORD NOT MATCHED")
            error = 'INVALID LOGIN'
            return render_template('login.html',error=error)
    else:
        #app.logger.info('NO USER')
        error='USERNAME NOT FOUND'
        return render_template('login.html',error=error)
    return render_template('login.html')

    #commit to db 
    mysql.connection.commit()
    #close conn
    cur.close()
    #flask flash msg
    flash('You have logged in','Successs')
#redirect
redirect(url_for('login'))


# wrapper 
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized , Please Login','danger')
            return redirect(url_for('login'))
    return wrap

#create logout route
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out ', 'Success')
    return redirect(url_for('login'))

#create dashboard route
@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')



if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run()