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
 
# get fake
randomProfiles = [
    ['Software', 'Python', 'New York', 'Google'],
    ['Website', 'HTML', 'Boston', 'Microsoft'],
    ['Accountant', 'Finance', 'Edmonton', 'Apple'],
    ['Computer', 'Java', 'Chicago', 'Amazon'],
    ['Social Media', 'Marketing', 'Toronto', 'Amazon']
]


def countMatches(profile, job):
    matchCount = 0
    for i, (profile_attribute, job_attribute) in enumerate(zip(profile, job)):
        if i != 4 and profile_attribute.lower() in job_attribute.lower():
            matchCount += 1
        if i == 3:
            if matchCount >= 2:
                return profile
            else:
                matchCount = 0
                
    return None

        

# route for applying to jobs        
@app.route('/apply', methods=['POST'])
def apply():
    global jobData, refreshRecs, fromRecommendations

    job_title = request.form['job_title']
    job_link = request.form['link']
    job_company = request.form['company']
    job_location = request.form['location']
    job_skills = request.form['skills']

    # if the request was from a recommendation, add the info to a global variable, otherwise clear it
    if request.form['recommended'] == "true":
        fromRecommendations = [job_title, job_skills, job_location, job_company]
    else:
        fromRecommendations = ["", "", "", ""]

    appliedJobs.append([job_title, job_skills, job_location, job_company, job_link])

    # remove the selected job from the dataset and any current recommendations, so it cannot appear while searching, or through other forms of recommendations
    for i in range(len(jobData)):
        if jobData[i]['job_link'] == job_link:
            del jobData[i]
            break

    for i in range(len(recommendations)):
        if recommendations[i][0]['job_link'] == job_link:
           del recommendations[i]
           break

    # open link in a new tab, and set the refresh flag to True
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
    profile_recommendations = []
    max_recommendations_count = 6
    
    # if a new job was selected, then refresh and create new recommendations from it
    if refreshRecs:
        # if it came from a search term, then run below code
        if fromRecommendations[0] == "":

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

        # if it came from an existing recommendation, then run the below code
        else:
            title_matches = 0
            skills_matches = 0
            location_matches = 0
            # loop through the jobData, and select 2 recommendations based off name, 2 off skills, and 2 off location
            for job in jobData:
                title_match = ' '.join(fromRecommendations[0].split()[:2]).lower() in job['job_title'].lower()
                skills_match = fromRecommendations[1].split(', ')[0].lower() in job['job_skills'].lower() and fromRecommendations[1].split(', ')[1].lower() in job['job_skills'].lower() and fromRecommendations[1].split(', ')[2].lower() in job['job_skills'].lower()
                location_match = fromRecommendations[2].lower().split(', ')[0] in job['job_location'].lower()

                if title_match and title_matches < 2:
                    recommendations.append([job,"Because you showed interest in " + fromRecommendations[0] + "."])
                    title_matches += 1
                elif skills_match and skills_matches < 2:
                    recommendations.append([job,"Because " + fromRecommendations[0] + " at " + fromRecommendations[3] + " requires some similar skills."])
                    skills_match += 1
                elif location_match and location_matches < 2:
                    recommendations.append([job,"Because you showed interest in " + fromRecommendations[0] + " which is in " + fromRecommendations[2] + "."])
                    location_matches += 1
                
                if title_matches + skills_matches + location_matches >= max_recommendations_count:
                    break
         
        match = False        
        
        # find matching job
        for profile in randomProfiles:
            for job in appliedJobs:
                
                matchingJob = countMatches(profile, job)
                
                if matchingJob is not None:
                    match = True
                    break
            if match:
                break
            
        print(matchingJob)
        # if job found 
        if matchingJob is not None:
            matching_title, matching_skills, matching_location, matching_company = matchingJob
            
            # fill recommendations with matchingJob matches
            for job in jobData:
                if (job['job_title'].lower() in matching_title.lower() or
                    job['job_skills'].lower() in matching_skills.lower() and
                    job['job_location'].lower() in matching_location.lower() or
                    job['company'].lower() in matching_company.lower()):
                    profile_recommendations.append(job)

        # shuffle and select a maximum of max_recommendations_count recommendations
        random.shuffle(recommendations)
        random.shuffle(profile_recommendations)
        recommendations = recommendations[:max_recommendations_count]
        refreshRecs = False

    return render_template('index.html', recommendations=recommendations, appliedJobs=appliedJobs, profile_recommendations=profile_recommendations)

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
