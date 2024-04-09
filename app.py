from flask import Flask, render_template, request, redirect
import csv
import webbrowser
import math
import random

app = Flask(__name__)
app.secret_key = '1234'

appliedJobs = []
recommendations = []
mostRecentSearchTerms = ["","","",""]
fromRecommendations = ["","","",""]

refreshRecs = False

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
            'location': random.choice(['New York', 'Boston', 'Toronto', 'Edmonton', 'Ottawa', 'Tampa', 'Vancouver']),
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
        
    if profile['location'].lower() in job['job_location'].lower():
        count += 1
        
    if profile['company'].lower() in job['company'].lower():
        count += 1
        
    return count
    
# route for applying to jobs        
@app.route('/apply', methods=['POST'])
def apply():
    global jobData, refreshRecs, fromRecommendations

    job_title = request.form['job_title']
    job_link = request.form['link']
    job_company = request.form['company']
    job_location = request.form['location']
    job_skills = request.form['skills']

    if request.form['recommended'] == "true":
        fromRecommendations = [job_title, job_skills, job_location, job_company]
    else:
        fromRecommendations = ["", "", "", ""]

    appliedJobs.append([job_title, job_link, job_company, job_location, job_skills])

    for i in range(len(jobData)):
        if jobData[i]['job_link'] == job_link:
            del jobData[i]
            break

    webbrowser.open_new_tab(request.form['link'])
    refreshRecs = True
    return redirect('/')

# index page
@app.route('/')
def index():
    global refreshRecs, recommendations
    # You might also like... recommendations logic
    # Recommends jobs matching one of the previous search params, but NOT the other two
    
    title_match_recommendations = []
    skills_match_recommendations = []
    location_match_recommendations = []
    company_match_recommendations = []
    max_recommendations_count = 6

    if refreshRecs:
        for job in jobData:
            title_match = mostRecentSearchTerms[0].lower() in job['job_title'].lower() and mostRecentSearchTerms[0] != ""
            skills_match = mostRecentSearchTerms[1].lower() in job['job_skills'].lower() and mostRecentSearchTerms[1] != ""
            location_match = mostRecentSearchTerms[2].lower() in job['job_location'].lower() and mostRecentSearchTerms[2] != ""
            company_match = mostRecentSearchTerms[3].lower() in job['company'].lower() and mostRecentSearchTerms[3] != ""

            if (title_match and not skills_match and not location_match and not company_match):
                title_match_recommendations.append([job,"Because you searched for \""+mostRecentSearchTerms[0]+"\"."])

            elif (skills_match and not title_match and not location_match and not company_match):
                skills_match_recommendations.append([job,"Because you searched for jobs that required \""+mostRecentSearchTerms[1]+"\"."])

            elif (location_match and not title_match and not skills_match and not company_match):
                location_match_recommendations.append([job,"Because you searched for jobs in "+mostRecentSearchTerms[2]+"."])
            
            elif (company_match and not title_match and not skills_match and not location_match):
                company_match_recommendations.append([job,"Because you searched for jobs at "+mostRecentSearchTerms[3]+"."])
            
            if len(title_match_recommendations) > max_recommendations_count and len(skills_match_recommendations) > max_recommendations_count and len(location_match_recommendations) > max_recommendations_count and len(company_match_recommendations) > max_recommendations_count:
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
            if i < len(location_match_recommendations):
                recommendations.append(location_match_recommendations[i])
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
        refreshRecs = False

    return render_template('index.html', recommendations=recommendations, appliedJobs=appliedJobs)

# search page
@app.route('/search', methods=['POST'])
def search():
    global mostRecentSearchTerms

    mostRecentSearchTerms = [request.form['title'], request.form['skills'], request.form['location'], request.form['company']]
    # search keywords
    title_keyword = mostRecentSearchTerms[0].lower()
    skills_keyword = mostRecentSearchTerms[1].lower()
    location_keyword = mostRecentSearchTerms[2].lower()
    company_keyword = mostRecentSearchTerms[3].lower()
    page = int(request.form['page'])

    results = []

    i = page * 50
    j = 0
    
    # go through job data and return matches
    for job in jobData:
        title_match = title_keyword in job['job_title'].lower()
        skills_match = skills_keyword in job['job_skills'].lower()
        location_match = location_keyword in job['job_location'].lower()
        company_match = company_keyword in job['company'].lower()

        if title_match and skills_match and location_match and company_match:
            j += 1
            if j <= i + 50 and j > i:
                results.append(job)

    return render_template('search.html', results=results, title=title_keyword, skills=skills_keyword, location=location_keyword, company=company_keyword, page=page, total_pages=math.ceil(j/50))

if __name__ == '__main__':
    app.run(debug=True)
