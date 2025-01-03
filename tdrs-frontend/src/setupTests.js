// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom'
import 'jest-enzyme'
import Enzyme from 'enzyme'
import Adapter from '@cfaester/enzyme-adapter-react-18'
import startMirage from './mirage'

Enzyme.configure({ adapter: new Adapter() })

let server

global.beforeEach(() => {
  server = startMirage({ environment: 'test' })
  global.mirageServer = server
})

global.afterEach(() => {
  server.shutdown()
})
