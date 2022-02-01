import React from 'react'
import thunk from 'redux-thunk'
import { mount } from 'enzyme'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import { fireEvent, render } from '@testing-library/react'

import { MemoryRouter, Redirect } from 'react-router-dom'
import Profile, { validation } from './Profile'

describe('Profile', () => {})
