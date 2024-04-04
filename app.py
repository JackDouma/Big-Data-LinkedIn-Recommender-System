from flask import Flask, render_template, request, redirect
import csv

app = Flask(__name__)
app.secret_key = '1234'

appliedJobs = []

# get job data
jobData = []
with open('data.csv', 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        jobData.append(row)
     
# route for applying to jobs        
@app.route('/apply', methods=['POST'])
def apply():
    job_title = request.form['job_title']
    appliedJobs.append(job_title)

    return redirect('/')

# index page
@app.route('/')
def index():
    return render_template('index.html', appliedJobs=appliedJobs)

# search page
@app.route('/search', methods=['POST'])
def search():
    # search keywords
    title_skills_keyword = request.form['skills'].lower()
    city_keyword = request.form['city'].lower()
    company_keyword = request.form['company'].lower()
    page = int(request.form['page'])

    results = []

    i = page * 50
    j = 0
    
    # go through job data and return matches
    for job in jobData:
        title_skills_match = title_skills_keyword in job['job_skills'].lower() or title_skills_keyword in job['job_title'].lower()
        city_match = city_keyword in job['job_location'].lower()
        company_match = company_keyword in job['company'].lower()

        if title_skills_match and city_match and company_match:
            j += 1
            if(j <= i + 50 and j > i):
                results.append(job)
            if(results.count == 50):
                break

    return render_template('search.html', results=results, title_skills=title_skills_keyword, city=city_keyword, company=company_keyword, page=page)

if __name__ == '__main__':
    app.run(debug=True)
