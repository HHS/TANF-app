import axios from 'axios'

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
