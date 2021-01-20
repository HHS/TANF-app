import React, { useEffect } from 'react'
import PropTypes from 'prop-types'

/**
 * A layout for all pages that require an authenticated context.
 * Populates document title for a11y of authenticated views.
 * Wraps all pages in a container div to ensure a consistant experience between
 * authenticated views.
 * @param {Object} props - properties passed in to react component
 * @param props.title - Title added to page header and document title
 * @param {React.Component[]} children - the elements to be used in an
 * instance of this template
 * @returns {React.Component} A page to be used in an authenticacted context
 */
export default function PrivateTemplate({ title, children }) {
  useEffect(() => {
    document.title = `${title} - TDP - TANF Data Portal`
  })

  return (
    <div className="grid-container margin-top-3">
      <h1 className="font-serif-2xl margin-bottom-0 text-normal">{title}</h1>
      {children}
    </div>
  )
}

PrivateTemplate.propTypes = {
  title: PropTypes.node.isRequired,
  children: PropTypes.node.isRequired,
}
