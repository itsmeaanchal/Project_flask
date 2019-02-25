from flask import Flask , render_template,flash, redirect, url_for, session,logging,request
import pymysql
import pymysql.cursors
from flask_wtf import Form
from wtforms import TextField
from wtforms import StringField , TextAreaField , PasswordField ,validators
from passlib.hash import sha256_crypt
import data
from functools import wraps

# Global Variables
global __sql_cursor__
global __sql_db__

__sql_db__ = None

app = Flask(__name__)
Articles = data.articles
app.debug = True

#config file
app.config["mysql_host"] = 'localhost'
app.config["mysql_user"] = 'root'
app.config["mysql_password"] = ''
app.config["mysql_db"] = 'myflaskapp'
# Open database connection
__sql_db__ =  pymysql.connect(host="localhost",user="root",passwd="",database="myflaskapp",use_unicode=True, charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
__sql_cursor__ = __sql_db__.cursor()
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
    global __sql_cursor__
    global __sql_db__
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username =  form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        #create cursor
        sql = "INSERT INTO users(name,email,username,password) VALUES (%s,%s,%s,%s)",(name,email,username,password)
        __sql_cursor__.execute(sql)


        #commit to db 
        __sql_db__.commit()
        #close conn
        __sql_db__.close()
        #flask flash msg
        flash('You are now registered and can log in','Successs')
    #redirect
    redirect(url_for('login'))

#route LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    global __sql_cursor__
    global __sql_db__
    #mysql = pymysql.connect(app)
    
    if request.method == 'POST' :
        username =  request.form['username']
        password_c =  request.form['password']

    #Get user by username
    sql = "SELECT * FROM users WHERE username = %", [username]
    result = __sql_cursor__.execute(sql)
    if result > 0:
        #Get Stored hash
        data =__sql_cursor__.fetchone()
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
    __sql_db__.commit()
    #close conn
    __sql_db__.close()
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