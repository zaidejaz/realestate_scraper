import io
from flask import Flask, render_template, request, send_file
import pandas as pd
import requests
import os

app = Flask(__name__)

cached_data = None

def fetch_data(address, location, api_key):
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
    if request.method == 'POST':
        address = request.form['address']
        location = request.form['location']
        api_key = request.form['api']
        data = fetch_data(address, location, api_key)
        if data:
            df = pd.DataFrame(data)
            df.to_excel('result.xlsx', index=False)  # Convert DataFrame to Excel file
            return render_template('results.html', tables=[pd.DataFrame(data).to_html(classes='data')], titles=pd.DataFrame(data).columns.values)
        else:
            return "Error: Unable to fetch data from the API."
    return render_template('index.html')

@app.route('/bulk', methods=['GET', 'POST'])
def bulk():
    if request.method == 'POST':
        api_key = request.form['api']
        all_data = []
        # Check if a CSV file is uploaded
        if 'file' in request.files:
            csv_file = request.files['file']
            if csv_file.filename.endswith('.csv'):
                df = pd.read_csv(csv_file)
                for index, row in df.iterrows():
                    # Check if the required keys exist in the row
                    if 'address' in row and 'location' in row:
                        address = row['address']
                        location = row['location']
                        print(f"Fetching data for {address}, {location}")
                        data = fetch_data(address, location, api_key)
                        print(f"Data: {data}")
                        if data:
                            all_data.extend(data)
                        print(f"\nData after this fetch\n")
                        print(f"All Data: {all_data}")
                        
                    else:
                        return "Error: CSV file does not contain 'address' or 'location' columns."
            if all_data:
                pd.set_option('display.max_rows', None)
                df = pd.DataFrame(all_data)
                print(f"Data Frame Converted: {df}")
                df.to_excel('result.xlsx', index=False)  # Convert DataFrame to Excel file
                return render_template('results.html', tables=[df.to_html(classes='data')], titles=df.columns.values)
            else:
                return "Error: Uploaded file is not a CSV."
    return render_template('bulk.html')

@app.route('/download')
def download():
    file_name = 'result.xlsx'
    root_directory = os.getcwd()  # Get the current working directory (root directory of the Flask application)
    file_path = os.path.join(root_directory, file_name)

    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "Error: File not found."

if __name__ == '__main__':
    app.run(debug=True)