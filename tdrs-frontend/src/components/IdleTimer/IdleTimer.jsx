import React, { useRef, useState, useEffect } from 'react'
import { useIdleTimer } from 'react-idle-timer'
import { useDispatch } from 'react-redux'
import Button from '../Button'
import { fetchAuth } from '../../actions/auth'

/**
 * IdleTimer uses the `react-idle-timer` package to watch for user inactivity.
 * There are environment variables set for the timeout time (how long before the
 * inactivity modal pops up) and the time between when the modal pops up and the
 * user is automatically logged out.
 * There is a second variable for the debounce time to minimize calls to
 * `/v1/auth_check` on user activity.
 */
function IdleTimer() {
  const [isModalVisible, setIsModalVisible] = useState(false)
  const dispatch = useDispatch()

  useEffect(() => {
    function keyListener(e) {
      const listener = keyListenersMap.get(e.keyCode)
      return listener && listener(e)
    }
    document.addEventListener('keydown', keyListener)

    return () => document.removeEventListener('keydown', keyListener)
  })

  useEffect(() => {
    let timer
    if (isModalVisible) {
      headerRef.current.focus()
      timer = setTimeout(onSignOut, process.env.REACT_APP_LOGOUT_TIME)
    }

    return () => clearTimeout(timer)
  })

  const onSignOut = () => {
    window.location.href = `${process.env.REACT_APP_BACKEND_URL}/logout/oidc`
  }

  const onRenewSession = () => {
    dispatch(fetchAuth())
    setIsModalVisible(false)
  }

  const modalRef = useRef()
  const headerRef = useRef()
  const handleTabKey = (e) => {
    if (isModalVisible) {
      const focusableModalElements = modalRef.current.querySelectorAll('button')
      const firstElement = focusableModalElements[0]
      const lastElement =
        focusableModalElements[focusableModalElements.length - 1]

      if (!e.shiftKey && document.activeElement !== firstElement) {
        firstElement.focus()
        return e.preventDefault()
      }

      if (e.shiftKey && document.activeElement !== lastElement) {
        lastElement.focus()
        e.preventDefault()
      }
    }

    return null
  }

  const keyListenersMap = new Map([
    [27, onRenewSession],
    [9, handleTabKey],
  ])

  useIdleTimer({
    timeout: process.env.REACT_APP_TIMEOUT_TIME,
    onIdle: () => {
      setIsModalVisible(true)
    },
    onAction: () => {
      if (!isModalVisible) {
        dispatch(fetchAuth())
      }
    },
    debounce: process.env.REACT_APP_DEBOUNCE_TIME,
  })

  return (
    <div
      id="myModal"
      className={`modal ${isModalVisible ? 'display-block' : 'display-none'}`}
    >
      <div className="modal-content" ref={modalRef}>
        <h1
          className="font-serif-xl margin-4 margin-bottom-0 text-normal"
          tabIndex="-1"
          ref={headerRef}
        >
          Your session is about to expire!
        </h1>
        <p className="margin-4 margin-top-1">
          You will be signed out due to inactivity in three minutes. Any unsaved
          data will be lost if you allow your session to expire.
        </p>
        <div className="margin-x-4 margin-bottom-4">
          <Button
            type="button"
            className="renew-session mobile:margin-bottom-1 mobile-lg:margin-bottom-0"
            onClick={onRenewSession}
          >
            Stay Signed In
          </Button>
          <Button type="button" className="sign-out" onClick={onSignOut}>
            Sign Out Now
          </Button>
        </div>
      </div>
    </div>
  )
}

export default IdleTimer
