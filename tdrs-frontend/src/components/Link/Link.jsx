import { Link } from 'react-router-dom'

function Anchor({ to, children, ...props }) {
  return (
    <a href={to} {...props}>
      {children}
    </a>
  )
}

function LinkComponent({ to, key, target, children, ...props }) {
  const LinkComponent = !to.startsWith('/') ? Anchor : Link
  return (
    <LinkComponent to={to} key={key} target={target} {...props}>
      {children}
    </LinkComponent>
  )
}

export default LinkComponent
