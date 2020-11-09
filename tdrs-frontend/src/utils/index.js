import axios from 'axios'
import axiosCookieJarSupport from 'axios-cookiejar-support'
import tough from 'tough-cookie'


let memo = null

const exports = {
  get axiosInstance() {
    if (memo) return memo
    return (memo = axios.create({
      withCredentials: true,
      // httpsAgent: new https.Agent({
      //     rejectUnauthorized: false,
      //     requestCert: true,
      //     keepAlive: true
      // })
    }))
  },
}

export default exports

// example
// async function authLogin(name, pass) {
//     let jar = request.jar();
//     let instance = await axios.create({
//         headers: {
//             jar: jar,
//             json: true
//         },
//         httpsAgent: new https.Agent({
//             rejectUnauthorized: false,
//             requestCert: true,
//         })
//     }); //it seems that using instance is better than using config while request

//     //let res = await instance.get('https://172.16.220.133/api/config');

//     console.log(res.data.csrf_token); //got csrf token

//     instance.defaults.headers['x-csrf-token'] = res.data.csrf_token;
//     res = await instance.post('https://172.16.220.133/login', { username: name, password: pass });
//     console.log(res.statusCode); //failed with code 403 err
// }

// ///below with request is success:

// function login(name, pass) {
//     let jar = request.jar();
//     let res = request({
//         url: 'https://172.16.220.133/api/config',
//         json: true,
//         jar: jar,
//         rejectUnauthorized: false,
//         requestCert: true,
//         agent: false,
//     }, function (err, res, body) {
//         if (err) {
//             console.log(err);
//         }
//         request.post('https://172.16.220.133/login', {
//             form: {
//                 username: name,
//                 password: pass,
//             },
//             json: true,
//             jar: jar,
//             rejectUnauthorized: false,
//             requestCert: true,
//             agent: false,
//             headers: {
//                 'x-csrf-token': body.csrf_token,
//             },
//         }, function (err, res, body) {
//             try {
//                 console.log(body.header.user);
//             } catch (err) {
//                 console.log(err.code === Error.ERR_NAPI_TSFN_GET_UNDEFINED);
//             }
//             console.log(res.statusCode);
//         });
//     });
// }
