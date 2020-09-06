import React from 'react'

import footerSvg from '../../footer.svg'

import { GridContainer, Grid } from '@trussworks/react-uswds'

function Footer() {
  return (
    <div style={{ backgroundColor: '#E2EFF7'}}>
      <GridContainer>
        <Grid>
          <img alt="Office of Family Assistance Logo" src={footerSvg} />
        </Grid>
      </GridContainer>
    </div>
  )
}

export default Footer