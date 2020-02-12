from flask import Flask, render_template, make_response, request
import requests, json, unicodedata
from flask_restful import Resource, Api
from wtforms import Form, StringField, SelectField
from forms import SearchForm
from torreuserdata import Data

#Initiate Flask Framework
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = '2.71828182845904523536028747135266249775724709369'

#Create App route for our homepage and results page
@app.route('/', methods=['GET', 'POST'])
def homepage():
    if request.method=='POST':
        username = request.form['username']
        data = Data(username)
        all_summaries = data.find_summary()
        info = json.dumps(all_summaries)
        info = json.loads(info)
        return render_template('usermetrics.html', info=info)

    return render_template('index.html')

#Main function
if __name__ == '__main__':
 app.run(debug=True)
