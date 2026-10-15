import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { getLoginDestination } from '../../utils/loginRedirect'

function PostLoginRedirect() {
  const location = useLocation()
  return <Navigate to={getLoginDestination(location.search)} replace />
}

export default PostLoginRedirect
