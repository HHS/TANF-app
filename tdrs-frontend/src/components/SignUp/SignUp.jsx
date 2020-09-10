import React from 'react'
import {
  GridContainer,
  Form,
  Label,
  TextInput,
  Button,
} from '@trussworks/react-uswds'

/**
 * This component renders when a user logs in for the first time
 * and needs to finish setting up their account. The user will
 * submit their first and last name along with their state, tribe or territory.
 */

function SignUp() {
  return (
    <GridContainer>
      <h1>Request Access</h1>
      <p>
        We need to collect some information before an OFA Admin can grant you
        access
      </p>
      <Form>
        <Label htmlFor="first-name">First name</Label>
        <TextInput id="first-name" name="first-name" type="text" />
        <Label htmlFor="last-name">Last name</Label>
        <TextInput id="last-name" name="last-name" type="text" />
        <Button className="usa-button--big" type="submit">
          Request Access
        </Button>
      </Form>
    </GridContainer>
  )
}

export default SignUp
