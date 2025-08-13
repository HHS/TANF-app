// actions/mockUpdateUserRequest.js
export const updateUserRequest =
  ({ firstName, lastName, stt, regions, hasFRAAccess }) =>
  async (dispatch) => {
    const user = {
      first_name: firstName,
      last_name: lastName,
      stt: stt?.id,
      regions: regions ? [...regions] : [],
      has_fra_access: hasFRAAccess,
    }

    console.log('[Stubbed] updateUserRequest called with:', user)

    // simulate a delay like a real API call
    return new Promise((resolve) => {
      setTimeout(() => {
        dispatch({
          type: 'UPDATE_USER_REQUEST_SUCCESS',
          user, // this could be returned user data
        })
        resolve()
      }, 500)
    })
  }
