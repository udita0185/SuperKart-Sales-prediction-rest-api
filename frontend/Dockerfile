# Set container base layout and work directories for frontend deployment
FROM python:3.12-slim

WORKDIR /app

# Copy frontend deployment structures inside active directory
COPY . .

# Install required UI dependencies
RUN pip install -r requirements.txt

EXPOSE 8501

# Launch the app and listen on port 8501 while disabling cross-site script validation
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableXsrfProtection=false"]
