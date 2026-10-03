# Use a lightweight python runtime image
FROM python:3.12-slim

# Set container base directory
WORKDIR /app

# Copy deployment artifacts into working directory
COPY . .

# Ensure pip is up-to-date and then install dependency modules directly without caching
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

EXPOSE 7860

# Expose port and launch Gunicorn web server with 4 workers targeting the Flask instance
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:ProductStore_sales_revenue_api"]
