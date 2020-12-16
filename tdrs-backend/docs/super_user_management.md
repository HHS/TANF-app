# Superuser Creation

**Description**

There are endpoints provided by the TDRS Backend service which require users to have the role of Superuser. This guide will provide instructions on how to define them in local and deployed environments. 


**Local Development**
	
1.) After following the instructions in the README.md for the TDRS Frontend and Backend services, you will now be able to login via Login.gov which will result in your account being generated and stored in the local database.

2.) With the backend instance running execute the following commands from the `tdrs-backend` directory:

  
   ```bash
   docker-compose run web sh -c "python manage.py shell"
   ```
   This will open up a shell prompt that will allow you to execute commands directly to the TDRS Backend Django application.
   
   To update your user, edit the sample script below to reflect your Login.gov email associated with your login process and press enter.  After this you may exit the shell and resume using the application with the updated Superuser role. 
   
   ```
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username="test@example.com")
user.is_staff = True
user.is_admin = True
user.is_superuser = True
user.save()
```
 
 
 **Deployed Evironment**
	
1.) Users targeted for Superuser creation will have to be manually elevated by system administrators with access to the intended Cloud.gov environment. 

2.) Admins with access will have to ssh into the environment via the following command 

 ```bash
   cf ssh tdp-backend
```

3.) After moving into the `tdpapp` directory, the admin will then have to set the alias for the python executable if it has not been set and execute the shell script to promote the existing user.

Commands to move to the correct directory and make python available 
```bash
cd ../tdpaspp
alias pytemp='/usr/local/bin/python3.7'
pytemp manage.py shell
```

Python script to promote the targer user: 

```
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username="test@example.com")
user.is_staff = True
user.is_admin = True
user.is_superuser = True
user.save()
```