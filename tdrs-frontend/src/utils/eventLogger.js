import { useSelector } from 'react-redux'
import axiosInstance from '../axios-instance'

class EventLogger {
  constructor(logEvents) {
    this.logEvents = logEvents
  }

  error(message) {
    return this.logEvents(message, 'error')
  }

  alert(message) {
    return this.logEvents(message, 'alert')
  }
}

function sendDataToBackend(data) {
  axiosInstance.post(`${process.env.REACT_APP_BACKEND_URL}/logs/`, data, {
    withCredentials: true,
  })
}

export default function useEventLogger() {
  const user = useSelector((state) => state.auth.user)

  return new EventLogger((message, type) => {
    sendDataToBackend({
      message,
      type,
      username: user.email,
      timestamp: new Date().toISOString(),
    })
  })
}
