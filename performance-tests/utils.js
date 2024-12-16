import http from 'k6/http';

export const login = (username = 'cypress-admin@teamraft.com') => {
  let url = `${__ENV.BASE_URL}/v1/login/cypress`
  let body = {
    username,
    token: __ENV.CYPRESS_TOKEN
  };

  // Using a JSON string as body
  let res = http.post(
    url,
    JSON.stringify(body),
    { headers: { 'Content-Type': 'application/json' } },
  );
}

export const attachAuthCookiesToBrowser = (context) => {
  const httpCookies = http.cookieJar().cookiesForURL(__ENV.BASE_URL)
  const keys = Object.keys(httpCookies)

  let browserCookies = []
  for (let i = 0; i < keys.length; i++) {
    const name = keys[i]
    const value = httpCookies[name]
    browserCookies.push({
      name,
      value,
      sameSite: 'Strict',
      url: __ENV.BASE_URL,
      httpOnly: true,
      secure: true
    })
  }

  context.addCookies(browserCookies)
  return context
}