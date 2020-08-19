# Authentication
For clients to authenticate, they have to authenticate with Login.gov via the backend service. Upon successful authentication the backend service will create an [httpOnly cookie](https://owasp.org/www-community/HttpOnly). 

 This will allow the backend to identify the browser which requested access and authorize them based on the cookie they provide in their API calls. 

 The secured portion of this authorization is due to the httpOnly cookie being in accessible to the clients local browser. 