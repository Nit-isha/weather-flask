import requests
import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
load_dotenv('.env')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cityName = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return '<Task %r>' %self.id


def get_weather_data(city):
    url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric'
    response = requests.get(url.format(city, os.environ.get('APIid'))).json()
    return response
        

@app.route('/', methods=['GET'])
def index_get():
    cities = City.query.all()
    weather_data = []
    for city in cities:
        response = get_weather_data(city.cityName)

        weather = {
            'id' : city.id,
            'city' : city.cityName,
            'temprature' : response['main']['temp'],
            'desc' : response['weather'][0]['description'],
            'icon' : response['weather'][0]['icon']
        }
        
        weather_data.append(weather)

    return render_template('index.html', weather_data=weather_data)


@app.route('/', methods=['POST'])
def index_post():
    msg = ''
    status = 1
    new_city = request.form.get('city')
    if new_city:
        existing_city = City.query.filter_by(cityName=new_city.lower()).first()
        
        if not existing_city:
            response = get_weather_data(new_city)
            if response['cod'] == 200:
                new_city_obj = City(cityName=new_city)
                db.session.add(new_city_obj)
                db.session.commit()
                msg = 'City added Successfully!'

            else:
                msg = 'City does not exist in the world.'
                status = 0

        else:
            msg = 'City already exists in the database. '
            status = 0
    

    cities = City.query.all()
    weather_data = []

    for city in cities:
        response = get_weather_data(city.cityName)

        weather = {
            'id' : city.id,
            'city' : city.cityName,
            'temprature' : response['main']['temp'],
            'desc' : response['weather'][0]['description'],
            'icon' : response['weather'][0]['icon']
        }
        
        weather_data.append(weather)

    return render_template('index.html', msg=msg, status=status, weather_data=weather_data)


def errormessage(err_msg):
    print(err_msg)
    return render_template('index.html', err_msg=err_msg)

        
@app.route('/delete/<int:id>')
def delete(id):
    city_to_delete = City.query.get_or_404(id)
    try:
        db.session.delete(city_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was problem deleting that task.'

if __name__ == "__main__":
    app.config['APIid'] = os.environ.get('APIid')
    app.run(debug=True)