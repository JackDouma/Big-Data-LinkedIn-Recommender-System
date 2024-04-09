from flask import Flask, render_template, request, redirect
import csv
import webbrowser
import math
import random

app = Flask(__name__)
app.secret_key = '1234'

appliedJobs = []
mostRecentSearchTerms = ["","","",""]

# get job data
jobData = []
with open('data.csv', 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        jobData.append(row)
 
def generateFakeProfiles(numberOfProfiles):
    profiles = []
    for x in range(numberOfProfiles):
        profile = {
            'title': random.choice(['Computer', 'Cashier', 'Janitor', 'Marketing', 'Doctor', 'Accountant', 'Software', 'Entry Level', 'Website', 'PSW']),
            'skills': random.choice(['HTML', 'Java', 'Python', 'Cleaning', 'Zoom', 'Customer Service', 'Sales', 'Communication', 'Organizational', 'Time Management']),
            'city': random.choice(['New York', 'Boston', 'Toronto', 'Edmonton', 'Ottawa', 'Tampa', 'Vancouver']),
            'company': random.choice(['Google', 'Microsoft', 'Apple', 'Amazon', 'Facebook', 'ScotiaBank', 'IBM', 'Walmart'])
        }
        profiles.append(profile)
    return profiles

randomProfiles = generateFakeProfiles(10)

def countMatches(profile, job):
    count = 0
    
    if profile['title'].lower() in job['job_title'].lower():
        count += 1
        
    if profile['skills'].lower() in job['job_skills'].lower():
        count += 1
        
    if profile['city'].lower() in job['job_location'].lower():
        count += 1
        
    if profile['company'].lower() in job['company'].lower():
        count += 1
        
    return count
    
# route for applying to jobs        
@app.route('/apply', methods=['POST'])
def apply():
    job_title = request.form['job_title']
    job_link = request.form['link']
    job_company = request.form['company']
    job_location = request.form['location'] 
    job_skills = request.form['skills']    

    appliedJobs.append([job_title, job_link, job_company, job_location, job_skills])

    webbrowser.open_new_tab(request.form['link'])
    return redirect('/')

# index page
@app.route('/')
def index():
    # You might also like... recommendations logic
    # Recommends jobs matching one of the previous search params, but NOT the other two
    title_match_recommendations = []
    skills_match_recommendations = []
    city_match_recommendations = []
    company_match_recommendations = []
    recommendations = []
    max_recommendations_count = 6

    for job in jobData:
        title_match = mostRecentSearchTerms[0] in job['job_title'].lower() and mostRecentSearchTerms[0] != ""
        skills_match = mostRecentSearchTerms[1].lower() in job['job_skills'].lower() and mostRecentSearchTerms[1] != ""
        city_match = mostRecentSearchTerms[2].lower() in job['job_location'].lower() and mostRecentSearchTerms[2] != ""
        company_match = mostRecentSearchTerms[3].lower() in job['company'].lower() and mostRecentSearchTerms[3] != ""

        if (title_match and not skills_match and not city_match and not company_match):
            title_match_recommendations.append([job,"Because you searched for \""+mostRecentSearchTerms[0]+"\"."])

        elif (skills_match and not title_match and not city_match and not company_match):
            skills_match_recommendations.append([job,"Because you searched for jobs that required \""+mostRecentSearchTerms[1]+"\"."])

        elif (city_match and not title_match and not skills_match and not company_match):
            city_match_recommendations.append([job,"Because you searched for jobs in "+mostRecentSearchTerms[2]+"."])
        
        elif (company_match and not title_match and not skills_match and not city_match):
            company_match_recommendations.append([job,"Because you searched for jobs at "+mostRecentSearchTerms[3]+"."])
        
        if len(title_match_recommendations) > max_recommendations_count and len(skills_match_recommendations) > max_recommendations_count and len(city_match_recommendations) > max_recommendations_count and len(company_match_recommendations) > max_recommendations_count:
            break

    # Curate the list of You might also like... recommendations
    for i in range(max_recommendations_count):
        if i < len(title_match_recommendations):
            recommendations.append(title_match_recommendations[i])
            if len(recommendations) == max_recommendations_count:
                break
        if i < len(skills_match_recommendations):
            recommendations.append(skills_match_recommendations[i])
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
            
    for profile in randomProfiles:
        profile_recommendations = []
        for viewedJob in appliedJobs:
            for job in jobData:
                # count the number of matching attributes between the profile and the viewed job
                matchCount = countMatches(profile, job)
                # if at least 2 out of 4 attributes match, recommend the job
                if matchCount >= 2 and job['job_title'] == viewedJob[0]:
                    profile_recommendations.append(job)
        recommendations.extend(profile_recommendations)

    # shuffle and select a maximum of max_recommendations_count recommendations
    random.shuffle(recommendations)
    recommendations = recommendations[:max_recommendations_count]

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
