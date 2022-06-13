FROM pypy:3
COPY . /src
WORKDIR /src
RUN ["pip", "install", "--no-cache-dir", "-r", "/src/requirements.txt"]
CMD ["python", "/src/run.py"]