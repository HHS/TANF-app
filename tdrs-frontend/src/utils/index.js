import axios from 'axios'
import axiosCookieJarSupport from 'axios-cookiejar-support'
import tough from 'tough-cookie'


let memo = null

const exports = {
  get axiosInstance() {
    if (memo) return memo
    memo = axios.create({
      withCredentials: true,
    })
    return memo
  },
}

export default exports
