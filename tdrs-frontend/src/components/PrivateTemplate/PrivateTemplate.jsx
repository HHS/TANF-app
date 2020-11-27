import React, { useEffect } from 'react'
import PropTypes from 'prop-types'


export default function PrivateTemplate({ title, children }) {

    useEffect(() => {
        document.title = `${title} - TDP - TANF Data Portal`
    })

    return (
        <div className="grid-container margin-top-3" >
          <h1 className="font-serif-2xl margin-bottom-0 text-normal">{title}</h1>
            {children}
        </div>
    )
}

PrivateTemplate.propTypes = {
    children : PropTypes.node.isRequired
}
