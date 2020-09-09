import React from 'react'
import { GridContainer, Grid } from '@trussworks/react-uswds'

import footerSvg from '../../assets/ACFLogo.svg'

function Footer() {
  return (
    <div style={{ backgroundColor: '#E2EFF7' }}>
      <GridContainer>
        <Grid>
          <img alt="Office of Family Assistance Logo" src={footerSvg} />
        </Grid>
      </GridContainer>
    </div>
  )
}

export default Footer
