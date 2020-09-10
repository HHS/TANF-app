import React from 'react'
import {
  GridContainer,
  CardGroup,
  Card,
  Form,
  Fieldset,
  Label,
  TextInput,
  Button,
  CardHeader,
  CardBody,
} from '@trussworks/react-uswds'

function SignUp() {
  const mockSubmit = () => {
    console.log('triggered signup submit')
  }
  return (
    <GridContainer>
      <CardGroup>
        <Card gridLayout={{ col: 6 }}>
          <CardHeader>
            <h3 className="usa-card__heading">Request Access</h3>
            <p>
              We need to collect some information before an OFA Admin can grant
              you access
            </p>
          </CardHeader>
          <CardBody>
            <Form onSubmit={mockSubmit}>
              <Fieldset>
                <Label htmlFor="first-name">First name</Label>
                <TextInput id="first-name" name="first-name" type="text" />
                <Label htmlFor="last-name">Last name</Label>
                <TextInput id="last-name" name="last-name" type="text" />
                <Button className="usa-button--big" type="button">
                  Request Access
                </Button>
              </Fieldset>
            </Form>
          </CardBody>
        </Card>
      </CardGroup>
    </GridContainer>
  )
}

export default SignUp
