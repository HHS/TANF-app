# Back End Testing with Postman

In order to test the back end of our application we are using the API Client [Postman](https://www.postman.com) in combination with the [Google Chrome](https://www.google.com/chrome/) extension [Postman Interceptor](https://chrome.google.com/webstore/detail/postman-interceptor/aicmkgpgakddgnaphhhpliifpcfhicfo?hl=en).

We use these tools together because of the way we are handling authentication and authorization on the back end. Once a user is authenticated we use a secure cookie that is unreadable by the front end application that is automatically sent with any request the front end makes to the back end. Because of this, the only way to query the back end with an API client is to have that cookie attached. These tools offer us a fairly easy way to get that cookie.

## Instructions

1. Download the required software if you don't already have it
   * [Postman](https://www.postman.com)
   * [Google Chrome](https://www.google.com/chrome/)
   * [Postman Interceptor](https://chrome.google.com/webstore/detail/postman-interceptor/aicmkgpgakddgnaphhhpliifpcfhicfo?hl=en)
**Note:** As the Postman Interceptor is a Google Chrome Extension, you must use Chrome to follow the link above and install the extension
2. Open Postman
3. Click the Interceptor button on the top bar of Postman to access the Interceptor settings
4. Under `Requests` you will see two sources, `Proxy` and `Interceptor`. Click on each of these and then click the on/off toggle under `Capture Requests` to `on`.
5. Click `Cookies` in the top menu.
6. Under `Capture Cookies` click the on/off toggle to `on`.
7. Under `Domains` add the following domains
   * tdp-frontend.app.cloud.gov
   * tdp-backend.app.cloud.gov
   * idp.int.identitysandbox.gov
8. Open Google Chrome and navigate to the [development site](https://tdp-frontend.app.cloud.gov/).
9. Click the `Sign In` button on the home page and complete the login process through [login.gov](https://login.gov)
10. Once you are returned back to the development site, go back to Postman.


You will see a list of URLs in the left menu, and you should now have the cookie set in Postman. You can test it by pasting the following URL under `Untitled Request` `https://tdp-backend.app.cloud.gov/v1/auth_check`. Make sure the dropdown menu to the left is set to `GET`. You should see a response similar to the one below, except it will have the email you used to log in to login.gov.

```
{
    "authenticated": true,
    "user": {
        "email": "youremail@example.com",
        "first_name": "",
        "last_name": ""
    }
}
```
11. For subsequent calls to the API, there is one more step to take. If you click on `Untitled Request` `https://tdp-backend.app.cloud.gov/v1/auth_check` you will see a link titled `Cookies`. When you click that link you will see a list of cookies for that domain. Under `tdp-backend.app.cloud.gov` select the cookie named `csrftoken` and you will see something like this:

```
csrftoken=RNxMaASMvJzG0d35aMsVZ8YGGNj4y9doE5NyvHYz76YuKc8CiVlfmo5NqWIc7sSq; Path=/; Domain=.tdp-backend.app.cloud.gov;
```
Copy the part immediately following `csrftoken=` and the semicolon. In this example, the value would be `RNxMaASMvJzG0d35aMsVZ8YGGNj4y9doE5NyvHYz76YuKc8CiVlfmo5NqWIc7sSq`

12. At the top of the Postman screen, click the `+` button to create a new request. In the new request screen click the `Headers` button and add a new header. Under `Key` type in `X-CSRFToken` and under `Value` paste in the value you copied above.
13. Now you can add whatever endpoint you want to test and the system will recognize you as the authenticated user.
