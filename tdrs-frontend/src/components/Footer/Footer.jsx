import React from 'react'

import footerSvg from '../../footer.svg'

import { GridContainer } from '@trussworks/react-uswds'

function Footer() {
  return (
    <div style={{ backgroundColor: '#E2EFF7'}}>
      <GridContainer>
        <img src={footerSvg} />
      </GridContainer>
    </div>
  )
}

export default Footer