FROM python:3.10.5

ADD dinning-hall.py .
ADD Menu.py .
ADD Tables.py .
ADD Waiters.py .
# dependencies
RUN pip install requests flask
# expose port
EXPOSE 80
# run app
CMD ["python","-u","dinning-hall.py"]