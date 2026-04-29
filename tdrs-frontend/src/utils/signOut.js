const signOut = (e) => {
  e.preventDefault()
  window.location.href = `${process.env.REACT_APP_AUTH_URL || process.env.REACT_APP_BACKEND_URL}/logout/oidc`
}

export default signOut
