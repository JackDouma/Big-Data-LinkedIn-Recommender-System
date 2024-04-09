from flask import Flask, render_template, request, redirect
import csv
import webbrowser
import math

app = Flask(__name__)
app.secret_key = '1234'

appliedJobs = []
mostRecentSearchTerms = ["","",""]

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
    job_link = request.form['link']
    job_company = request.form['company']
    appliedJobs.append([job_title,job_link,job_company])

    webbrowser.open_new_tab(request.form['link'])
    return redirect('/')

# index page
@app.route('/')
def index():
    # You might also like... recommendations logic
    # Recommends jobs matching one of the previous search params, but NOT the other two
    title_skills_match_recommendations = []
    city_match_recommendations = []
    company_match_recommendations = []
    recommendations = []
    max_recommendations_count = 6

    for job in jobData:
        title_skills_match = (mostRecentSearchTerms[0].lower() in job['job_skills'].lower() or mostRecentSearchTerms[0] in job['job_title'].lower()) and mostRecentSearchTerms[0] != ""
        city_match = mostRecentSearchTerms[1].lower() in job['job_location'].lower() and mostRecentSearchTerms[1] != ""
        company_match = mostRecentSearchTerms[2].lower() in job['company'].lower() and mostRecentSearchTerms[2] != ""

        if (title_skills_match and not city_match and not company_match):
            title_skills_match_recommendations.append([job,"Because you searched for \""+mostRecentSearchTerms[0]+"\"."])

        elif (city_match and not title_skills_match and not company_match):
            city_match_recommendations.append([job,"Because you searched for jobs in "+mostRecentSearchTerms[1]+"."])
        
        elif (company_match and not title_skills_match and not city_match):
            company_match_recommendations.append([job,"Because you searched for jobs at "+mostRecentSearchTerms[2]+"."])
        
        if len(title_skills_match_recommendations) > max_recommendations_count and len(city_match_recommendations) > max_recommendations_count and len(company_match_recommendations) > max_recommendations_count:
            break

    # Curate the list of You might also like... recommendations
    for i in range(max_recommendations_count):
        if i < len(title_skills_match_recommendations):
            recommendations.append(title_skills_match_recommendations[i])
            if len(recommendations) == max_recommendations_count:
                break
        if i < len(city_match_recommendations):
            recommendations.append(city_match_recommendations[i])
            if len(recommendations) == max_recommendations_count:
                break
        if i < len(company_match_recommendations):
            recommendations.append(company_match_recommendations[i])
            if len(recommendations) == max_recommendations_count:
                break

    return render_template('index.html', recommendations=recommendations, appliedJobs=appliedJobs)

# search page
@app.route('/search', methods=['POST'])
def search():
    global mostRecentSearchTerms

    mostRecentSearchTerms = [request.form['title'], request.form['skills'], request.form['city'], request.form['company']]
    # search keywords
    title_keyword = mostRecentSearchTerms[0].lower()
    skills_keyword = mostRecentSearchTerms[1].lower()
    city_keyword = mostRecentSearchTerms[2].lower()
    company_keyword = mostRecentSearchTerms[3].lower()
    page = int(request.form['page'])

    results = []

    i = page * 50
    j = 0
    
    # go through job data and return matches
    for job in jobData:
        title_match = title_keyword in job['job_title'].lower()
        skills_match = skills_keyword in job['job_skills'].lower()
        city_match = city_keyword in job['job_location'].lower()
        company_match = company_keyword in job['company'].lower()

        if title_match and skills_match and city_match and company_match:
            j += 1
            if j <= i + 50 and j > i:
                results.append(job)

    return render_template('search.html', results=results, title=title_keyword, skills=skills_keyword, city=city_keyword, company=company_keyword, page=page, total_pages=math.ceil(j/50))

if __name__ == '__main__':
    app.run(debug=True)
