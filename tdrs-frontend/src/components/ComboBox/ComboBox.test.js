import React from 'react'
import { shallow } from 'enzyme'

import ComboBox from './ComboBox'

describe('ComboBox', () => {
  it('should call handleBlur on change of selection in combo box', () => {
    const props = {
      handleBlur: jest.fn(),
      setStt: jest.fn(),
      sttList: [
        {
          id: 1,
          type: 'state',
          code: 'AL',
          name: 'Alabama',
        },
        {
          id: 2,
          type: 'state',
          code: 'AK',
          name: 'Alaska',
        },
        {
          id: 140,
          type: 'tribe',
          code: 'AK',
          name: 'Aleutian/Pribilof Islands Association, Inc.',
        },
        {
          id: 52,
          type: 'territory',
          code: 'AS',
          name: 'American Samoa',
        },
        {
          id: 3,
          type: 'state',
          code: 'AZ',
          name: 'Arizona',
        },
        {
          id: 4,
          type: 'state',
          code: 'AR',
          name: 'Arkansas',
        },
      ],
    }

    const wrapper = shallow(<ComboBox {...props} />)

    const select = wrapper.find('.usa-select')

    select.simulate('change', {
      target: {
        name: 'stt',
        value: 'alaska',
      },
    })

    expect(props.handleBlur).toHaveBeenCalledTimes(1)
    expect(props.setStt).toHaveBeenCalledTimes(1)
    expect(props.setStt).toHaveBeenCalledWith('alaska')
  })
})
