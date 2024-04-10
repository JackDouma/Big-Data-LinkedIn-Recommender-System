<h1>COMP-4311 Big Data Final Project</h1>
<h3>By: Michael Rosanelli, Jackson Douma and Chris Veilleux</h3>


<h3>Using the following dataset</h3>
https://www.kaggle.com/datasets/asaniczka/1-3m-linkedin-jobs-and-skills-2024

<h4>The following code was used to merge Job Posting and Job Skills into 1 dataset</h4>

```
import csv

def read_csv(filename, encoding='utf-8'):
    rows = []
    with open(filename, 'r', encoding=encoding) as file:
        reader = csv.reader(file)
        for row in reader:
            rows.append(row)
    return rows

def merge_csv(file1, file2, output_file):
    data_file1 = read_csv(file1)
    data_file2 = read_csv(file2)
    
    file2_dict = {row[0]: row[1:] for row in data_file2}

    merged_data = []
    for row in data_file1:
        record = row
        shared_record = file2_dict.get(row[0])
        if shared_record:
            record.extend(shared_record)
        merged_data.append(record)

    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(merged_data)

file1 = "job_skills.csv"
file2 = "linkedin_job_postings.csv"
output_file = "merged_output.csv"
merge_csv(file1, file2, output_file)
print("Merged data has been written to", output_file)
```

<h2>Abstract</h2>
Our project incorporated a large data set (886.216 MB) of recent job postings from the social media and job searching platform LinkedIn. With this data, we made a recommender system designed to help users find job postings on LinkedIn that are appropriate for them. The application utilizes HTML pages rendered dynamically through the Flask library in Python. Users begin by performing a search, with the ability to enter a job title, skills, location, and company, and are returned a list of job postings matching the criteria. Once a user ‘applies’ to a job, the recommender system begins building a profile of the user to make further recommendations. Recommendations are based on: previous search queries, suggesting jobs that match some but not all of the most recent search criteria; the jobs the user has applied to, suggesting jobs that have some similar elements; and a collaborative filtering approach, where users are shown jobs that other users are interested in who have a similar user profile. Upon selecting the apply button on a job after performing a search, the user is redirected to the homepage and sees all three types of recommendations. By using these three approaches to recommend jobs, the system can suggest relevant job postings to the user with a high degree of accuracy.

<h2>Introduction</h2>
It is a well-known fact that job searching is a time-consuming and arduous task. But before the rigours of the application process, interview, and contract negotiation, job-seekers must first find job postings that meet their own unique preferences, skills, and qualifications. While the internet is a great resource to find these postings, users need a way to sort through the mass amount that they will encounter to find ones they are interested in and are competitive for. LinkedIn is one such place where users can find job postings. According to recent research [1], 48% of hirers on LinkedIn explicitly use skills data to fill their roles, so it is of utmost importance that users find postings that match up with their own qualifications, skills included. Our project aims to leverage the verbose listing of qualifications on LinkedIn job postings to recommend only the most relevant jobs to users. Using a large CSV file of job posting data from LinkedIn, including job title, skills, location, and so on, we were able to build a recommender system to provide these job suggestions. Our recommender system will consider the search terms entered in past searches, what jobs the user has expressed interest in, and compare user profiles to collaboratively recommend jobs to ensure users can find the most relevant postings.

<h2>Methods</h2>

<h3>Data</h3>
The data for the recommender system was sourced from user ASANICZKA on Kaggle.com [2]. The data contains information from roughly 1.3 million job listings scraped from LinkedIn in 2024, including job titles, posting links, companies, locations, cities, and skills listed in the posting. Some initial processing had to be performed on the data before it was in a usable format for our recommender system. The data we wanted to work with was split into two CSV files, one containing the skills listed for each job posting, and another containing all of the other information about each posting, so a Python script was used to join these two files into one. The join was performed on the column containing the link to the posting, the only shared column between the two files. After the join operation was performed, the output file contained 1,296,381 rows and was properly formatted for the recommender system.
<h3>Previous Search Terms Recommender</h3>
Similar job postings based on previous search terms will be recommended after users perform a search, and then apply to a job (using the blue “Apply” button listed beside each job). When the apply button is clicked, the system performs another search on the dataset and returns 4 lists of job postings where one of either title, skills, location, or company from the previous search query matches, but not the other three. For example, if the previous search was for “Programmer”, with skills “Python”, in location “Canada”, at the company “Google”, a matching posting could be one with Python listed as a skill but without “Programmer” in the job title, not in Canada, and not at Google. The system then adds postings from each list to the main recommendation list, then the main list is shuffled and trimmed to six items. This produces a list of job posting recommendations that are similar to but not identical to the user’s previous search, helping them identify new opportunities they may be suited to but wouldn’t have otherwise known to search for. These recommendations appear underneath the “You might also like…” heading on the homepage, and each recommendation lists the job title, company, location, and the reason for the recommendation.

<h3>Similar Jobs Recommender</h3>
Similar job postings based on previously recommended jobs will be shown after users click on a job posting that has been recommended under the “You might also like…” or the “People like you viewed…” headings. When a job is selected from either of these lists, the system performs another search on the dataset and appends 2 new job postings with a similar job title, 2 postings with similar skills, and 2 postings in the same location to the list of recommendations, for a total of 6 new positions. The list of recommendations is then shuffled and trimmed back down to six items before it is shown underneath the “You might also like…” heading on the homepage. By recommending jobs based on other recommended jobs, the list of recommendations grows to include a broader variety of positions, exposing the user to a more diverse set of positions they could be interested in. As with the previous search terms recommender, each recommendation lists the job title, company, location, and the reason for the recommendation.

<h3>Collaborative Filtering Recommender</h3>
Job postings based on similar user profiles will be recommended after users either perform a search and apply for a job, or after clicking on one of the recommended postings in either of the recommended jobs lists. If the user’s profile matches any of the existing profiles coded into the system, the existing user profile will be used to search for jobs. When the user performs one of these actions, the system will take all of the jobs the user has previously applied to (listed under the “Jobs Viewed” heading on the homepage), and find a matching user profile by looping over all existing profile job views and determining them as a "collaborative fit" if a job has at least 2 attributes (title, skills, location, and company) matching a job of the main user. Once a profile has been identified for the user based on their previously viewed jobs, the system performs a search on the dataset of job postings and identifies jobs that have either a similar title and similar skills, or a similar location and similar company. These jobs are then appended to a list of recommendations (different from the list used in the previous two recommender approaches) which is then shuffled and shown underneath the “People like you viewed…” heading. By harnessing the power of collaborative filtering, users are exposed to jobs that they are likely to be interested in given that people similar to them are also interested in them.

<h2>Results</h2>
In testing, we found that the previous search terms recommender performed moderately well. Since it was a hard-coded search for jobs with search terms that users themselves had entered, we believed that the recommendations would have a reasonable chance of being something the user would be interested in. Only matching one of the four attributes (job title, skills, location, company) did lead to some unrelated recommendations, such as jobs that had completely different functions but were at the same company or general location. The similar job recommender performed marginally better. Recommendations based on jobs with similar titles or skills were almost always relevant, but again, recommendations for postings at the same location were often irrelevant. Recommending based on location could be good for a student in the area looking for a part-time job, but for those looking to enter the workforce full-time with a degree, these may not be the most optimal The collaborative filtering recommender performed reasonably well. By building a user profile based on two or more attributes listed in previously viewed jobs, the profile is representative of the user as a job-seeker. Matching the user profile to other profiles and suggesting jobs that suited other similar users generally produced relevant recommendations with fewer exceptions than the other two recommenders.
<h2>Discussion</h2>
Overall, we are satisfied with our recommender system as it was implemented as we designed it to be from the start, with three different recommendation methods and a user interface that easily allows users to access them, dynamically updating with each job viewed. Using three different approaches to recommendations was interesting as we could compare the methods to each other as searches were performed, and we benefited from a very large data set with all the information needed to provide accurate recommendations. An improvement to consider for our system would have been a more production-level implementation of collaborative filtering, with real-life users creating accounts. These accounts would be tied to user profiles based on job viewing history, which could have then been used in the collaborative filtering recommendations. Users could be able to add additional information that ties to them, like age for example. If a user shows they are a student, then we could show recommendations in a given area based on job selection and have good faith that those would be beneficial. With the addition of user accounts, we could also implement a user feedback system to gather data about how accurate recommendations are, allowing us to further improve the system. Another improvement we had initially considered as its own recommendation system was to utilize the summary of job postings. We could have calculated the similarity between job summaries using an approach like shingling to identify similar jobs to suggest to the user. A final improvement to consider is to scrape our own data from LinkedIn. The data sourced from Kaggle.com was quite North America-centric and underrepresented other regions of the world, making this system largely unhelpful for people in other countries. While completing this project, we discovered that collaborative filtering was the best solution based on the relevance of the job postings that our recommender was suggesting. While other approaches may yield better results at larger scales or with more complex algorithms, we found that using the pre-built user profiles to find relevant jobs consistently outperformed the other systems. We also discovered that there is more overlap between seemingly unrelated job postings than initially expected. For example, two completely different jobs may both list organization as a skill. For that reason, it would be wise to consider combining recommender systems to form a hybrid system to generate the most accurate results.
