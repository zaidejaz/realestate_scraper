from flask import Flask, render_template, request, send_file
import pandas as pd
import requests
import os

app = Flask(__name__)

cached_data = None

def fetch_data(address, location):
    api_key = request.form['api']
    api_url = "https://app.scrapeak.com/v1/scrapers/people_search/search"
    parameters = {
        "api_key": api_key,
        "search_by": "address",
        "address": address,
        "location": location
    }
    response = requests.get(api_url, params=parameters)
    if response.status_code == 200:
        data = response.json().get('data', [])
        return data
    else:
        return None

def generate_excel(file_name):
    global cached_data
    if cached_data:
        df = pd.DataFrame(cached_data)
        df.to_excel(file_name, index=False)  # Convert DataFrame to Excel file
        return file_name
    else:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    global cached_data
    if request.method == 'POST':
        address = request.form['address']
        location = request.form['location']
        cached_data = fetch_data(address, location)
        if cached_data:
            return render_template('results.html', tables=[pd.DataFrame(cached_data).to_html(classes='data')], titles=pd.DataFrame(cached_data).columns.values)
        else:
            return "Error: Unable to fetch data from the API."
    return render_template('index.html')

@app.route('/download')
def download():
    file_name = 'result.xlsx'
    if generate_excel(file_name):
        return send_file(file_name, as_attachment=True)
    else:
        return "Error: Unable to generate Excel file."

if __name__ == '__main__':
    app.run(debug=True)
