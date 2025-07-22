import React, { useState } from 'react'
import Button from '../Button'
import { faSignOutAlt } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useSelector } from 'react-redux'
import signOut from '../../utils/signOut'

const UserAccessInfo = () => {
  const user = useSelector((state) => state.auth.user)
  const primaryRole = user?.roles?.[0]

  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    jurisdictionType: user?.jurisdictionType || '',
    reportingFRA: user?.reportingFRA || '',
  })
  const [originalData] = useState(formData)

  const exUser = {
    name: 'John Doe',
    userType: 'Developer',
    jurisdictionType: 'State',
    state: 'Alaska',
    reportingFRA: 'Yes',
  }

  const handleEdit = () => {
    alert('Edit Profile clicked!')
  }

  const getState = () => {
    return user?.stt?.name || 'Federal Government'
  }

  return (
    <div className="profile-container">
      <div className="profile-info">
        <div className="row">
          <span className="label text-bold margin-right-4">Name</span>
          <span id="full-name" className="value">
            {user?.first_name} {user?.last_name}
          </span>
        </div>
        <hr />
        <div className="row">
          <span className="label text-bold margin-right-4">User Type</span>
          <span className="value">{primaryRole?.name}</span>
        </div>
        <div className="row">
          <span className="label text-bold margin-right-4">
            Jurisdiction Type
          </span>
          <span className="value">{user.jurisdictionType}</span>
        </div>
        <div className="row">
          <span className="label text-bold margin-right-4">State</span>
          <span className="value">{getState()}</span>
        </div>
        <div className="row">
          <span className="label text-bold margin-right-4">Reporting FRA</span>
          <span className="value">{user.reportingFRA}</span>
        </div>
      </div>
      <div className="margin-top-5">
        <div
          className="buttons"
          style={{
            display: 'flex',
            gap: '10px',
            justifyContent: 'space-between',
            marginTop: '10px',
          }}
        >
          {!isEditing ? (
            <>
              <Button type="button" onClick={handleEdit}>
                Edit Profile Information
              </Button>
              <Button type="button" onClick={signOut}>
                <FontAwesomeIcon
                  className="margin-right-1"
                  icon={faSignOutAlt}
                />
                Sign Out
              </Button>
            </>
          ) : (
            <>
              <Button type="button" onClick={handleEdit}>
                Request Access
              </Button>
              <Button type="button" onClick={signOut}>
                <FontAwesomeIcon
                  className="margin-right-1"
                  icon={faSignOutAlt}
                />
                Cancel
              </Button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default UserAccessInfo
