## Ozone  
Ozone is the OnlineJudge for **PDPM Indian Institute of Information Technology, Design and Manufacturing Jabalpur** being developed in python2.7 and using django webframework version 1.9  

## Requirements  
Python2.7  
Django==1.11  
And additional requirements are in *requirments.txt*  

## How to run it?  
I have not added the database. So *makemigrations* and *migrate* the database.  
Create a *superuser* and login using the credentials. Or you can just register and to activate your account, you can find the *activation_code* in `User.objects.get(username="your username").profile.activation_code` and get started.  
I have left a print statement, so it prints out activation code in terminal when a user registers. So find it there.  
  
## Work to be done  
- [X] Create Contests, Add Problems.  
- [X] Submit Code and get the verdict  
- [X] List of all the contests  
- [X] Ranking System  
- [ ] Better Look  
- [ ] Edit Problems
- [ ] Make it secure  
- [ ] Add Practice Feature  
- [ ] Profile View  
- [ ] Increase Content...
