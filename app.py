from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def scrape_jobs(keyword, location):
    url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&location={location}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print(f"URL: {url}")
    print(f"Response status code: {response.status_code}")
    print(f"Page title: {soup.title.string if soup.title else 'No title found'}")
    
    jobs = []
    job_listings = soup.find_all('div', class_='base-card')
    
    if not job_listings:
        print("No job listings found. The page structure might have changed.")
        return jobs

    for job in job_listings:
        title_elem = job.find('h3', class_='base-search-card__title')
        company_elem = job.find('h4', class_='base-search-card__subtitle')
        location_elem = job.find('span', class_='job-search-card__location')
        link_elem = job.find('a', class_='base-card__full-link')
        
        title = title_elem.text.strip() if title_elem else "N/A"
        company = company_elem.text.strip() if company_elem else "N/A"
        location = location_elem.text.strip() if location_elem else "N/A"
        job_url = link_elem['href'] if link_elem else "N/A"
        
        jobs.append({
            'title': title,
            'company': company,
            'location': location,
            'url': job_url
        })
    
    return jobs
 
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        keyword = request.form['keyword']
        location = request.form['location']
        jobs = scrape_jobs(keyword, location)
        return render_template('results.html', jobs=jobs)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)  