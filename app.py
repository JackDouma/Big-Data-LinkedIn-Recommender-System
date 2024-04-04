from flask import Flask, render_template, request
import csv

app = Flask(__name__)

# get job data
jobData = []
with open('data.csv', 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        jobData.append(row)

# index page
@app.route('/')
def index():
    return render_template('index.html')

# search page
@app.route('/search', methods=['POST'])
def search():
    # search keywords
    title_skills_keyword = request.form['skills'].lower()
    city_keyword = request.form['city'].lower()
    company_keyword = request.form['company'].lower()

    results = []
    
    # go through job data and return matches
    for job in jobData:
        title_skills_match = title_skills_keyword in job['job_skills'].lower() or title_skills_keyword in job['job_title'].lower()
        city_match = city_keyword in job['job_location'].lower()
        company_match = company_keyword in job['company'].lower()

        if title_skills_match and city_match and company_match:
            results.append(job)

    return render_template('search.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)