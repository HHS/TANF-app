import ProfileRow from './ProfileRow'

const JurisdictionLocationInfo = ({
  jurisdictionType,
  locationName,
  formType,
}) => {
  let label = 'State'
  if (jurisdictionType === 'territory') label = 'Territory'
  else if (jurisdictionType === 'tribe') label = 'Tribe'

  if (formType === 'access request') {
    return (
      <div className="read-only-row">
        <div className="label">{label}</div>
        <div className="value">{locationName}</div>
      </div>
    )
  } else {
    return <ProfileRow label={label} value={locationName} />
  }
}

export default JurisdictionLocationInfo
