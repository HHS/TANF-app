import React from 'react'
import { Switch, Route } from 'react-router-dom'
import Welcome from '../Welcome'

const Routes = () => {
  return (
    <Switch>
      <>
        <Route path="/">
          <Welcome />
        </Route>
      </>
    </Switch>
  )
}

export default Routes
