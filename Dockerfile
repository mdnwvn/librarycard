FROM python:3.11
ENTRYPOINT [ "python" ]
CMD [ "librarycard.py" ]
WORKDIR /app
RUN mkdir -p /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
