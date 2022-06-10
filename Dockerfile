FROM python:3.8
COPY . /src
WORKDIR /src
RUN ["pip", "install", "-r", "/src/requirements.txt"]
CMD ["python", "/src/run.py"]