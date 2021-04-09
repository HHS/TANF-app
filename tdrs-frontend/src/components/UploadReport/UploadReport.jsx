import React, { useEffect, useRef } from 'react'
import PropTypes from 'prop-types'
import { fileInput } from 'uswds/src/js/components'

import Button from '../Button'

import FileUpload from '../FileUpload'

function UploadReport({ handleCancel, header }) {
  // Ensure newly rendered header is focused, else it
  // won't be read be screen readers.
  const headerRef = useRef(null)

  useEffect(() => {
    headerRef.current.focus()
  }, [])

  useEffect(() => {
    // `init` for the uswds fileInput must be called on the
    // initial render for it to load properly
    fileInput.init()
  }, [])

  return (
    <>
      <h2
        ref={headerRef}
        className="font-serif-xl margin-top-5 margin-bottom-0 text-normal"
        tabIndex="-1"
      >
        {header}
      </h2>
      <form>
        <FileUpload section="1 - Active Case Data" />
        <FileUpload section="2 - Closed Case Data" />
        <FileUpload section="3 - Aggregate Data" />
        <FileUpload section="4 - Stratum Data" />

        <div className="buttonContainer margin-y-4">
          <Button className="card:margin-y-1" type="submit">
            Submit Data Files
          </Button>
          <Button className="cancel" type="button" onClick={handleCancel}>
            Cancel
          </Button>
        </div>
      </form>
    </>
  )
}

UploadReport.propTypes = {
  handleCancel: PropTypes.func.isRequired,
  header: PropTypes.string.isRequired,
}

export default UploadReport
