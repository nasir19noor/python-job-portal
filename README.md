https://ai.belajarlagi.id/dash/c/9f986127-4ae8-4e73-a8c2-e35147df047b

mkdir job_portal

cd job_portal

python -m venv venv

source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

pip install flask requests beautifulsoup4 psycopg2-binary Flask-SQLAlchemy


CREATE TABLE user_searches (
    id SERIAL PRIMARY KEY,
    ip VARCHAR(50),
    browser VARCHAR(255),
    country VARCHAR(100),
    job_role VARCHAR(255),
    job_location VARCHAR(255)
);