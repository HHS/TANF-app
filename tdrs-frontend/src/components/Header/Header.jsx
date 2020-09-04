import React, { useState } from 'react'
// // import './Header.scss'

import { 
  // GridContainer,
  // Grid, 
  // FooterNav,
  // Logo, 
  NavMenuButton, 
  Menu, 
  Header, 
  // PrimaryNav,
  Title,
  ExtendedNav,
  // Search,
  // SocialLinks,
  // Address,
  // Footer 
} from '@trussworks/react-uswds'

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
//         </ExtendedNav>
//       </Header>
//     </>
//   )
// }

function HeaderComp() {
  const [expanded, setExpanded] = useState(false)
  const onClick = () => setExpanded((prvExpanded) => !prvExpanded)
  const [isOpen] = useState([false])
  const [mobileNavOpen, setMobileNavOpen] = useState(false)

  const toggleMobileNav = () => {
    setMobileNavOpen((prevOpen) => !prevOpen)
  }

  const testMenuItems = [
    <a href="#linkOne" key="one">
      Simple link one
    </a>,
    <a href="#linkTwo" key="two">
      Simple link two
    </a>,
  ]

  const testItemsMenu = [
    <>
      <Menu
        key="one"
        items={testMenuItems}
        isOpen={isOpen[0]}
        id="testDropDownOne"
      />
    </>,
    <a href="#two" key="two" className="usa-nav__link">
      <span>Welcome</span>
    </a>
  ]


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
          <ExtendedNav
            primaryItems={testItemsMenu}
            secondaryItems={[]}
            mobileExpanded={expanded}
            onToggleMobileNav={onClick}>
          </ExtendedNav>
        </div>
      </Header>
    </>
  )
}

export default HeaderComp