# Ozone  
```
 django.__version__ == 1.9  
 ```  
 Python2.7  
Online Judge for IIITDMJ. 
Work in progress.  
Use your own gmail address in settings.py to get activation code, or you could do following in "./manage.py shell"  
```
from django.contrib.auth.models import User
activation = User.objects.get(username="Your username").profile.activation_code
```  
Or if you are going the other way i.e. adding your gmail as mailserver to send activation code then you also need to uncomment, the code in *inout/views.py*, in function which sends a mail to specifies mail address while user registration, called register to get an activation code, on your mail. :)  
and use it to activate your account.  
Requirements are in **requirements.txt**  
Will update ASAP

