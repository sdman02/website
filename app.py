from flask import Flask, render_template, url_for, request, redirect

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

import requests
import json
from key import api_key

app = Flask(__name__)

db_name = 'Classes.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
app.app_context().push()

#model
class Classes(db.Model):
    class_code = db.Column(db.String(50), nullable=False, primary_key=True)
    class_name = db.Column(db.String(200), nullable=False)
    class_credits = db.Column(db.Integer, nullable=False)
    class_school = db.Column(db.String(100), nullable=False)

    def __repr__(self) -> str:
        return '<Name %r>' % self.id

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data', methods = ['GET', 'POST'])
def data():

    if request.method == 'POST':
        className = request.form.get('className')
        classCode = request.form.get('classCode')
        classCredits = request.form.get('classCredits')
        classSchool = request.form.get('classSchool')
        new_class = Classes(class_name = className, class_code = classCode, class_credits= classCredits, class_school = classSchool)

        try:
            db.session.add(new_class)
            db.session.commit()
            return redirect('/data')
        except:
            return "Error adding Class"
    else:
        classList = Classes.query.order_by(Classes.class_code)
        return render_template('data.html', classList = classList)

@app.route('/delete/<string:code>')
def delete(code):
    item = Classes.query.get_or_404(code)

    try:
        db.session.delete(item)
        db.session.commit()
        return redirect('/data')
    except:
        return 'error deleting'

@app.route('/update/<string:code>', methods = ['GET', 'POST'])
def update(code):
    item = Classes.query.get_or_404(code)
    if request.method == 'POST':
        item.class_name = request.form.get('className')
        item.class_code = request.form.get('classCode')
        item.class_credits = request.form.get('classCredits')
        item.class_school = request.form.get('classSchool')

        try:
            db.session.commit()
            return redirect('/data')
        except:
            return 'Error updating item'
    else:
        return render_template('update.html', item=item)
    
@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/maps', methods = ['GET', 'POST'])
def maps():
    if request.method == 'POST':
        KEY = api_key()
        lat = request.form.get('lat')
        long = request.form.get('long')
        distance = request.form.get('range')
        entityType = request.form.get('services') 
        entityID = {'banks':'6000', 'schools':'8211', 'restaurants':'5800', 'airports':'4581'}
        base_url = 'http://spatial.virtualearth.net/REST/v1/data/Microsoft/PointsOfInterest'
        query = f"?spatialFilter=nearby({lat},{long},{distance})&$filter=EntityTypeID%20eq%20'{entityID[entityType]}'&$format=json&$select=DisplayName,Latitude,Longitude,AddressLine&key={KEY}"
        
        r = requests.get(base_url + query)
        data = r.json()

        itemData = list()

        for point in data['d']['results']:
            item = list()
            item.append(point['DisplayName'])
            item.append(point['AddressLine'])
            itemData.append(item)
        
        return render_template('maps.html', itemData=itemData)

    if request.method == 'GET':
        return render_template('maps.html')

if __name__ == "__main__":
    app.run(debug=True)
