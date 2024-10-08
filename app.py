from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from geoip2.database import Reader
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

#Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Love1981@127.0.0.1/jobportal'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class UserSearchData(db.Model):
    # __tablename__   = 'user_search_data'
    id              = db.Column(db.Integer, primary_key=True)
    ip_address      = db.Column(db.String(45), nullable=False)
    browser         = db.Column(db.Text, nullable=False)
    city            = db.Column(db.String(100))
    country         = db.Column(db.String(100))
    search_role     = db.Column(db.String(100))
    search_location = db.Column(db.String(100))
    search_time     = db.Column(db.DateTime, default=db.func.current_timestamp())
geoip_reader = Reader('GeoLite2-City.mmdb') 

def save_user_search(ip, browser, city, country, job_role, location):
    new_search = UserSearchData(ip_address=ip, browser=browser, city=city, country=country, search_role=job_role, search_location=location)
    db.session.add(new_search)
    db.session.commit()
  
def scrape_linkedin_jobs(keyword, location):
    url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&location={location}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    jobs = []
    job_listings = soup.find_all('div', class_='base-card')
    
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
            'url': job_url,
            'source': 'LinkedIn'
        })
    
    return jobs

def scrape_jobstreet_jobs(keyword, location):
    url = f"https://id.jobstreet.com/id/{keyword}-jobs/in-{location}/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    jobs = []
    job_listings = soup.find_all('article', class_='z1s6m00')
    
    for job in job_listings:
        title_elem = job.find('a', id=lambda x: x and x.startswith('job-title-'))
        company_elem = job.find('a', {'data-automation': 'jobCompany'})
        location_elem = job.find('a', {'data-automation': 'jobLocation'})
        link_elem = job.find('a', id=lambda x: x and x.startswith('job-title-'))
        
        title = title_elem.text.strip() if title_elem else "N/A"
        company = company_elem.text.strip() if company_elem else "N/A"
        location = location_elem.text.strip() if location_elem else "N/A"
        job_url = link_elem['href'] if link_elem else "N/A"
        
        jobs.append({
            'title': title,
            'company': company,
            'location': location,
            'url': job_url,
            'source': 'JobStreet'
        })
    return jobs

def scrape_jobs(keyword, location, source):
    if source == 'linkedin':
        return scrape_linkedin_jobs(keyword, location)
    elif source == 'jobstreet':
        return scrape_jobstreet_jobs(keyword, location)
    else:  # 'all'
        linkedin_jobs = scrape_linkedin_jobs(keyword, location)
        jobstreet_jobs = scrape_jobstreet_jobs(keyword, location)
        return linkedin_jobs + jobstreet_jobs

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        keyword  = request.form['keyword']
        location = request.form['location']
        source   = request.form['source']

        #Get user's IP and browser information
        user_ip      = request.remote_addr
        user_browser = request.user_agent.string

        #Get location informaton using GeoLite2
        try:
            response = geoip_reader.city(user_ip)
            city     = response.city.name
            country  = response.country.name
        except Exception as e:
            city    = "Unknown"
            country = "Unknown"   
        
        # Save search info to database
        save_user_search(user_ip, user_browser, city, country, keyword, location)

        jobs = scrape_jobs(keyword, location, source)
        return render_template('results.html', jobs=jobs)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)