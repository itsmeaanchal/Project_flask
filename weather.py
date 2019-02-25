from flask import Flask , render_template , request
import requests

app = Flask(__name__)

# Index
@app.route('/')
def index():
    return render_template('index.html')

# tempr
@app.route('/tempr' , methods = ['POST'])
def tempr():
    zipcode = request.form['zip']
    r = requests.get('http://api.openweathermap.org/data/2.5/weather?zip='+zipcode+',in&appid=723a3148402bfe1852323f8320380ec4').json()
    temp_k = float(r['main']['temp'])
    name = str(r['name'])
    temp_c = (temp_k - 273.15)
    #return render_template('tempr.html' , weather = weather)
    return render_template('tempr.html' , name = name ,temp=temp_c )

if __name__ == '__main__':
    app.run(debug=True)