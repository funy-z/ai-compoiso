FROM python:3.12
WORKDIR /app
COPY ai_services/ /app
RUN chmod +x pip_requirements.sh
RUN ./pip_requirements.sh
RUN pip install --no-cache-dir -r pip_requirements.txt
EXPOSE 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
