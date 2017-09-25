# Ozone  
Ozone is the OnlineJudge for **PDPM Indian Institute of Information Technology, Design and Manufacturing, Jabalpur** being developed in python3.6 and using django webframework version 1.11.3  

[![Build Status](https://api.travis-ci.org/Samy-33/Ozone.svg?branch=master)](https://travis-ci.org/Samy-33/Ozone)


## Requirements  
Python 3.6+  
Django==1.11.3+  
And additional requirements are in *requirements.txt*  

## How to run it?  

  * install virtualenv `$ sudo apt install python-virtualenv`  
  * create a virtual environment `$ virtualenv env -p python3.6`  
  * activate the `env`: `$ source env/bin/activate`  
  * Create a folder tmp/problems/ in root directory of the project.  
  * `$ python manage.py makemigrations inout`  
  * `$ python manage.py makemigrations contests`  
  * `$ python manage.py makemigrations practice`  
  * `$ python manage.py migrate`  
  * Edit a variable in settings.py `CODEDIR`, change it to the absolute path of the Ozone  
  * `$ python manage.py createsuperuser`  
  * Login using the credentials of superuser  

Or you can just register and to activate your account,  
I have left a print statement, so it prints out activation code in terminal when a user registers. So find it there.  

## Work to be done  
- [X] Create Contests, Add Problems.  
- [X] Submit Code and get the verdict  
- [X] List of all the contests  
- [X] Ranking System  
- [X] Edit Problems  
- [X] Add Practice Feature  
- [X] Add Timer  
- [ ] Better Look  
- [ ] Make it secure  
- [ ] Profile View  
- [ ] Increase Content...

## Contribution  
Open an issue if you want to contribute for something that's not already in *issues*  
Send a Pull Request anytime.  
