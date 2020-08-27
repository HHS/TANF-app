# Details in Regards to the Custom OIDC Logic

We are currently using a custom implementation of OIDC authentication due to the limitations of existing Django OIDC libraries. This decision was derived out of necessity due to existing libraries such as [mozilla-django-oidc](https://github.com/mozilla/mozilla-django-oidc/blob/master/mozilla_django_oidc/auth.py#L222-L230) providing no option to append the client_assertion needed in the call to [Login.gov/token](https://developers.login.gov/oidc/#token). Other libraries such as [drf-oidc-auth](https://github.com/ByteInternet/drf-oidc-auth) and [django-oidc-provider](https://github.com/juanifioren/django-oidc-provider) provide less options as they are more geared towards using less secure OpenID Connect protocols implemented by Google and Social Media Platforms. Login.gov diverges from these older patterns by leveraging a more secure method in respect to its user base. 


## Status

We are currently researching the use of the Django library [drf-oidc-auth](https://github.com/ByteInternet/drf-oidc-auth) which we might be able to leverage to replace some of the `id_token` verification logic we have created but still not a viable replacement for the Login.gov authentication process we have to implement as it will not facilitate flow from [login.gov/authorize](https://developers.login.gov/oidc/#authorization) to [login.gov/logout](https://developers.login.gov/oidc/#logout). 

Also, we are looking into  forking the open source Github repo [mozilla-django-oidc](https://github.com/mozilla/mozilla-django-oidc) and adjust their code base to suit our needs, however this brings us back to the added risk of writing our own custom code to handle this process. 

## Decision

Until an adequate alternative can be found, we will continue to use our custom code that is being thoroughly unit tested.


## Consequences

There is an added risk of needing to support our own OIDC authentication logic due to the development team being directly responsible for its maintenance. 