import ProfileRow from './ProfileRow'
import { FORM_TYPES } from '../../utils/formHelpers'

export const JURISDICTION_TYPES = {
  STATE: 'state',
  TRIBE: 'tribe',
  TERRITORY: 'territory',
}

const JurisdictionLocationInfo = ({
  jurisdictionType,
  locationName,
  formType,
}) => {
  let label = 'State'
  if (jurisdictionType === JURISDICTION_TYPES.TERRITORY) label = 'Territory'
  else if (jurisdictionType === JURISDICTION_TYPES.TRIBE) label = 'Tribe'

  if (formType === FORM_TYPES.ACCESS_REQUEST) {
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
