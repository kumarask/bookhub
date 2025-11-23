FROM python:3.11-slim
WORKDIR /app
# Copy only the service requirements then install
COPY services/reviews/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the service application and the shared library into the image
COPY services/reviews/app ./app
COPY services/shared ./shared

EXPOSE 8004
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]
