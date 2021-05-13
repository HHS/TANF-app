
import { useLocation } from 'react-router-dom'

/** This component renders a message signaling to the user that this
 * page does not exist.
 */
export default function NoMatch() {
  let location = useLocation()

  return (
    <div>
      <h3>
        No match for <code>{location.pathname}</code>
      </h3>
    </div>
  )
}
