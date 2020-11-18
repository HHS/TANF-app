# Session Management

The requirement for this project is that users will be logged out of the system after 30 minutes of activity. This is our strategy to accomplish that.

### Backend
The backend will be the ultimate arbiter of session management. When the user logs in they will receive an HttpOnly cookie that is set to expire in 30 minutes. After that, with every interaction between the FE and BE, the BE will refresh the cookie, so it will extend the timeout time to another 30 minutes.

### Frontend
The frontend will also have a timer that it will set when the user logs in. It will monitor user activity and reset every time a user interacts with the page. That means when a form field is filled out or changed, the FE timer will reset. Because this is not dependent on interactions with the BE, the FE will call the /v1/authorization-check endpoint whenever it resets the timer. This will serve to verify the user is still authenticated on the BE as well as refresh the cookie.

When the FE timer reaches 20 minutes (?) it will alert the user that the session will time out soon and give them the option to either extend the session or logout of the system. If the user chooses to extend the session, the FE will call the /v1/authorization-check endpoint to refresh the session. If the user elects to log out of the system it will call the /v1/logout endpoint to clear the session and log the user out of the system. We will also employ a strategy of using `throttle` to mitigate the potential of sending too many requests to the backend.
