import ProfileRow from './ProfileRow'

const JurisdictionLocationInfo = ({ jurisdictionType, locationName }) => {
  let label = 'State'
  if (jurisdictionType === 'territory') label = 'Territory'
  else if (jurisdictionType === 'tribe') label = 'Tribe'

  return <ProfileRow label={label} value={locationName} />
}

export default JurisdictionLocationInfo
