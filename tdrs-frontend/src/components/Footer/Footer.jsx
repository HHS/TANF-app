import React from 'react'

import footerSvg from '../../footer.svg'

import {
  GridContainer,
  FooterNav,
  Grid,
  Logo,
  SocialLinks,
  Address,
} from '@trussworks/react-uswds'

function Footer() {
  // const returnToTop = (
  //   <GridContainer className="usa-footer__return-to-top">
  //     <a href="#">Return to top</a>
  //   </GridContainer>
  // )

  // const footerPrimary = (
  //   <FooterNav
  //     aria-label="Footer navigation"
  //     size="medium"
  //     links={Array(5).fill(
  //       <a href="javascript:void(0)" className="usa-footer__primary-link">
  //         Primary link
  //       </a>
  //     )}
  //   />
  // )

  // const footerSecondary = (
  //   <>
  //     <Grid row gap>
  //       <Logo
  //         medium
  //         image={<img className="usa-footer__logo-img" src={logoImg} alt="" />}
  //         heading={<h3 className="usa-footer__logo-heading">Name of Agency</h3>}
  //       />
  //       <Grid className="usa-footer__contact-links" mobileLg={{ col: 6 }}>
  //         <SocialLinks
  //           links={[
  //             <a
  //               key="facebook"
  //               className="usa-social-link usa-social-link--facebook"
  //               href="javascript:void(0);">
  //               <span>Facebook</span>
  //             </a>,
  //             <a
  //               key="twitter"
  //               className="usa-social-link usa-social-link--twitter"
  //               href="javascript:void(0);">
  //               <span>Twitter</span>
  //             </a>,
  //             <a
  //               key="youtube"
  //               className="usa-social-link usa-social-link--youtube"
  //               href="javascript:void(0);">
  //               <span>YouTube</span>
  //             </a>,
  //             <a
  //               key="rss"
  //               className="usa-social-link usa-social-link--rss"
  //               href="javascript:void(0);">
  //               <span>RSS</span>
  //             </a>,
  //           ]}
  //         />
  //         <h3 className="usa-footer__contact-heading">Agency Contact Center</h3>
  //         <Address
  //           medium
  //           items={[
  //             <a key="telephone" href="tel:1-800-555-5555">
  //               (800) CALL-GOVT
  //             </a>,
  //             <a key="email" href="mailto:info@agency.gov">
  //               info@agency.gov
  //             </a>,
  //           ]}
  //         />
  //       </Grid>
  //     </Grid>
  //   </>
  // )

  return (
    <div style={{ backgroundColor: '#E2EFF7'}}>
      <img src={footerSvg} />
    </div>
  )
}

export default Footer