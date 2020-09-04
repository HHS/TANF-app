import React, { useState } from 'react'
// // import './Header.scss'

import logoImg from '../../matt-wang-eNwx-kYd6fM-unsplash.jpg'
import circleImg from '../../matt-wang-eNwx-kYd6fM-unsplash.jpg'

import { 
  GridContainer,
  Grid, 
  FooterNav,
  Logo, 
  NavMenuButton, 
  Menu, 
  Header, 
  PrimaryNav,
  Title,
  ExtendedNav,
  Search,
  SocialLinks,
  Address,
  Footer 
} from '@trussworks/react-uswds'

// // function HeaderComp() {
// //   return <Header className="header">TDP</Header>
// // }

// function HeaderComp() {
//   const [expanded, setExpanded] = useState(false)
// const onClick = () => setExpanded((prvExpanded) => !prvExpanded)
// const [isOpen, setIsOpen] = useState([false])

// const testMenuItems = [
//   <a href="#linkOne" key="one">
//     Simple link one
//   </a>,
//   <a href="#linkTwo" key="two">
//     Simple link two
//   </a>,
// ]

// const testItemsMenu = [
//   <>
//     <Menu
//       key="one"
//       items={testMenuItems}
//       isOpen={isOpen[0]}
//       id="testDropDownOne"
//     />
//   </>,
//   <a href="#two" key="two" className="usa-nav__link">
//     <span>Welcome</span>
//   </a>
// ]

//   return (
//     <>
//       <div className={`usa-overlay ${expanded ? 'is-visible' : ''}`}></div>
//       <Header extended={true}>
//         <div className="usa-navbar">
//           <Title>Project Title</Title>
//           <NavMenuButton onClick={onClick} label="Menu" />
//         </div>
//         <ExtendedNav
//           primaryItems={testItemsMenu}
//           secondaryItems={[]}
//           mobileExpanded={expanded}
//           onToggleMobileNav={onClick}>
//           {/* <Search small onSubmit={() => {}} /> */}
//         </ExtendedNav>
//       </Header>
//     </>
//   )
// }


// const HeaderComp = () => {
//   const [expanded, setExpanded] = useState(false)
//   const onClick = () => setExpanded((prvExpanded) => !prvExpanded)

//   const testMenuItems = [
//     <a href="#linkOne" key="one">
//       Current link
//     </a>,
//     <a href="#linkTwo" key="two">
//       Simple link Two
//     </a>,
//   ]

//   const [isOpen, setIsOpen] = useState([false, false])

//   const onToggle = (index) => {
//     setIsOpen((prevIsOpen) => {
//       const newIsOpen = [false, false]
      
//       newIsOpen[index] = !prevIsOpen[index]
//       return newIsOpen
//     })
//   }

//   const testItemsMenu = [
//     <>
//       <Menu
//         key="one"
//         items={testMenuItems}
//         isOpen={isOpen[0]}
//         id="testDropDownOne"
//       />
//     </>,
//     <a href="#two" key="two" className="usa-nav__link">
//       <span>Parent link</span>
//     </a>,
//     <a href="#three" key="three" className="usa-nav__link">
//       <span>Parent link</span>
//     </a>,
//   ]

//   return (
//     <>
//       <div className={`usa-overlay ${expanded ? 'is-visible' : ''}`}></div>
//       <Header basic={true}>
//         <div className="usa-nav-container">
//           <div className="usa-navbar">
//             <Title>TANF Data Portal</Title>
//             <NavMenuButton onClick={onClick} label="Menu" />
//           </div>
//           <PrimaryNav
//             items={testItemsMenu}
//             mobileExpanded={expanded}
//             onToggleMobileNav={onClick}>
//           </PrimaryNav>
//         </div>
//       </Header>
//     </>
//   )
// }

function HeaderComp() {
  const [mobileNavOpen, setMobileNavOpen] = useState(false)

  const toggleMobileNav = () => {
    setMobileNavOpen((prevOpen) => !prevOpen)
  }

  const returnToTop = (
    <GridContainer className="usa-footer__return-to-top">
      <a href="#">Return to top</a>
    </GridContainer>
  )

  const footerPrimary = (
    <FooterNav
      aria-label="Footer navigation"
      size="medium"
      links={Array(5).fill(
        <a href="javascript:void(0)" className="usa-footer__primary-link">
          Primary link
        </a>
      )}
    />
  )

  const footerSecondary = (
    <>
      <Grid row gap>
        <Logo
          medium
          image={<img className="usa-footer__logo-img" src={logoImg} alt="" />}
          heading={<h3 className="usa-footer__logo-heading">Name of Agency</h3>}
        />
        <Grid className="usa-footer__contact-links" mobileLg={{ col: 6 }}>
          <SocialLinks
            links={[
              <a
                key="facebook"
                className="usa-social-link usa-social-link--facebook"
                href="javascript:void(0);">
                <span>Facebook</span>
              </a>,
              <a
                key="twitter"
                className="usa-social-link usa-social-link--twitter"
                href="javascript:void(0);">
                <span>Twitter</span>
              </a>,
              <a
                key="youtube"
                className="usa-social-link usa-social-link--youtube"
                href="javascript:void(0);">
                <span>YouTube</span>
              </a>,
              <a
                key="rss"
                className="usa-social-link usa-social-link--rss"
                href="javascript:void(0);">
                <span>RSS</span>
              </a>,
            ]}
          />
          <h3 className="usa-footer__contact-heading">Agency Contact Center</h3>
          <Address
            medium
            items={[
              <a key="telephone" href="tel:1-800-555-5555">
                (800) CALL-GOVT
              </a>,
              <a key="email" href="mailto:info@agency.gov">
                info@agency.gov
              </a>,
            ]}
          />
        </Grid>
      </Grid>
    </>
  )

  return (
    <>
      <a className="usa-skipnav" href="#main-content">
        Skip to main content
      </a>
      <div className={`usa-overlay ${mobileNavOpen ? 'is-visible' : ''}`}></div>
      <Header extended>
        <div className="usa-navbar">
          <Title id="extended-logo">
            <a href="/" title="Home" aria-label="Home">
              TANF Data Portal
            </a>
          </Title>
          <NavMenuButton
            label="Menu"
            onClick={toggleMobileNav}
            className="usa-menu-btn"
          />
        </div>
      </Header>

      <main id="main-content">
        <section className="usa-hero" aria-label="Introduction">
          <GridContainer>
            <div className="usa-hero__callout">
              <h1 className="usa-hero__heading">
                <span className="usa-hero__heading--alt">Sign into TANF Data Portal</span>
              </h1>
              <p>
                Our vision is to build a new, secure, web based data reporting system to improve 
                the federal reporting experience for TANF grantees and federal staff. 
                The new system will allow grantees to easily submit accurate data and be confident 
                that they have fulfilled their reporting requirements.
              </p>
              <a className="usa-button" href="javascript:void(0)">
                Sign in with LOGIN.GOV
              </a>
            </div>
          </GridContainer>
        </section>

        <section className="grid-container usa-section">
          <Grid row gap>
            <Grid tablet={{ col: 4 }}>
              <h2 className="font-heading-xl margin-top-0 tablet:margin-bottom-0">
                A tagline highlights your approach
              </h2>
            </Grid>
            <Grid tablet={{ col: 8 }} className="usa-prose">
              <p>
                The tagline should inspire confidence and interest, focusing on
                the value that your overall approach offers to your audience.
                Use a heading typeface and keep your tagline to just a few
                words, and don’t confuse or mystify.
              </p>
              <p>
                Use the right side of the grid to explain the tagline a bit
                more. What are your goals? How do you do your work? Write in the
                present tense, and stay brief here. People who are interested
                can find details on internal pages.
              </p>
            </Grid>
          </Grid>
        </section>

        <section className="usa-graphic-list usa-section usa-section--dark">
          <GridContainer>
            <Grid row gap className="usa-graphic-list__row">
              <Grid tablet={{ col: true }} className="usa-media-block">
                <img
                  className="usa-media-block__img"
                  src={circleImg}
                  alt="Alt text"
                />
                <div className="usa-media-block__body">
                  <h2 className="usa-graphic-list__heading">
                    Graphic headings can vary.
                  </h2>
                  <p>
                    Graphic headings can be used a few different ways, depending
                    on what your landing page is for. Highlight your values,
                    specific program areas, or results.
                  </p>
                </div>
              </Grid>
              <Grid tablet={{ col: true }} className="usa-media-block">
                <img
                  className="usa-media-block__img"
                  src={circleImg}
                  alt="Alt text"
                />
                <div className="usa-media-block__body">
                  <h2 className="usa-graphic-list__heading">
                    Stick to 6 or fewer words.
                  </h2>
                  <p>
                    Keep body text to about 30 words. They can be shorter, but
                    try to be somewhat balanced across all four. It creates a
                    clean appearance with good spacing.
                  </p>
                </div>
              </Grid>
            </Grid>
            <Grid row gap className="usa-graphic-list__row">
              <Grid tablet={{ col: true }} className="usa-media-block">
                <img
                  className="usa-media-block__img"
                  src={circleImg}
                  alt="Alt text"
                />
                <div className="usa-media-block__body">
                  <h2 className="usa-graphic-list__heading">
                    Never highlight anything without a goal.
                  </h2>
                  <p>
                    For anything you want to highlight here, understand what
                    your users know now, and what activity or impression you
                    want from them after they see it.
                  </p>
                </div>
              </Grid>
              <Grid tablet={{ col: true }} className="usa-media-block">
                <img
                  className="usa-media-block__img"
                  src={circleImg}
                  alt="Alt text"
                />
                <div className="usa-media-block__body">
                  <h2 className="usa-graphic-list__heading">
                    Could also have 2 or 6.
                  </h2>
                  <p>
                    In addition to your goal, find out your users’ goals. What
                    do they want to know or do that supports your mission? Use
                    these headings to show these.
                  </p>
                </div>
              </Grid>
            </Grid>
          </GridContainer>
        </section>

        <section id="test-section-id" className="usa-section">
          <GridContainer>
            <h2 className="font-heading-xl margin-y-0">Section heading</h2>
            <p className="usa-intro">
              Everything up to this point should help people understand your
              agency or project: who you are, your goal or mission, and how you
              approach it. Use this section to encourage them to act. Describe
              why they should get in touch here, and use an active verb on the
              button below. “Get in touch,” “Learn more,” and so on.
            </p>
            <a href="#" className="usa-button usa-button--big">
              Call to action
            </a>
          </GridContainer>
        </section>
      </main>

      <Footer
        returnToTop={returnToTop}
        primary={footerPrimary}
        secondary={footerSecondary}
      />
    </>
  )
}

export default HeaderComp