FROM python:3.10.5

COPY requisitos.txt ./

RUN pip install --upgrade pip 
RUN pip install -r requisitos.txt

COPY . .

