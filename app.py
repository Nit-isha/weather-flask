import requests
import os
from flask import Flask, render_template, request, redirect
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

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        new_city = request.form.get('city')
        if new_city:
            new_city_obj = City(cityName=new_city)
            db.session.add(new_city_obj)
            db.session.commit()
            return redirect('/')


    else:
        cities = City.query.all()
        url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric'
        
        weather_data = []
        for city in cities:
            response = requests.get(url.format(city.cityName, app.config['APIid'])).json()
            
            weather = {
                'id' : city.id,
                'city' : city.cityName,
                'temprature' : response['main']['temp'],
                'desc' : response['weather'][0]['description'],
                'icon' : response['weather'][0]['icon']
            }
            
            weather_data.append(weather)

        return render_template('index.html', weather_data=weather_data)

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
    #dotenvi
    app.run(debug=True)