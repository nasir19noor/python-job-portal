# Use an official Python runtime as a parent image
FROM python:3.9-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000

ENV FLASK_ENV=production

CMD ["python", "app.py"]

# COPY entrypoint.sh /app/entrypoint.sh
# # Make the entrypoint script executable
# RUN chmod +x entrypoint.sh

# # Use the entrypoint script
# ENTRYPOINT ["/app/entrypoint.sh"]
