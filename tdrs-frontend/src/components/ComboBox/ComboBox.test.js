import React from 'react'
import { shallow } from 'enzyme'
import { render } from '@testing-library/react'

import ComboBox from './ComboBox'

describe('ComboBox', () => {
  it('should call handleBlur on change of selection in combo box', () => {
    const props = {
      handleBlur: jest.fn(),
      handleSelect: jest.fn(),
      name: 'stt',
    }

    const stts = [
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
    ]

    const wrapper = shallow(
      <ComboBox {...props}>
        {stts.map((stt) => (
          <option
            className="sttOption"
            key={stt.id}
            value={stt.name.toLowerCase()}
          >
            {stt.name}
          </option>
        ))}
      </ComboBox>
    )

    const select = wrapper.find('.usa-select')

    select.simulate('change', {
      target: {
        name: 'stt',
        value: 'alaska',
      },
    })

    expect(props.handleBlur).toHaveBeenCalledTimes(1)
    expect(props.handleSelect).toHaveBeenCalledTimes(1)
    expect(props.handleSelect).toHaveBeenCalledWith('alaska')
  })

  it('should call handleSelect with selected value on change of selection in combo box', () => {
    const props = {
      handleBlur: jest.fn(),
      handleSelect: jest.fn(),
      name: 'stt',
    }

    const stts = [
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
    ]

    const wrapper = shallow(
      <ComboBox {...props}>
        {stts.map((stt) => (
          <option
            className="sttOption"
            key={stt.id}
            value={stt.name.toLowerCase()}
          >
            {stt.name}
          </option>
        ))}
      </ComboBox>
    )

    const select = wrapper.find('.usa-select')

    select.simulate('change', {
      target: {
        name: 'stt',
        value: 'alaska',
      },
    })

    expect(props.handleSelect).toHaveBeenCalledTimes(1)
    expect(props.handleSelect).toHaveBeenCalledWith('alaska')
  })

  it('should add class of `usa-combo-box__input--error` if error is passed to ComboBox', () => {
    const props = {
      handleBlur: jest.fn(),
      handleSelect: jest.fn(),
      error: 'There is an error',
      name: 'stt',
    }

    const stts = [
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
    ]

    const { container } = render(
      <ComboBox {...props}>
        {stts.map((stt) => (
          <option
            className="sttOption"
            key={stt.id}
            value={stt.name.toLowerCase()}
          >
            {stt.name}
          </option>
        ))}
      </ComboBox>
    )

    const input = container.querySelector('.usa-combo-box__input--error')

    expect(input).toBeInTheDocument()
  })

  it('should NOT add class of `usa-combo-box__input--error` if NO error is passed to ComboBox', () => {
    const props = {
      handleBlur: jest.fn(),
      handleSelect: jest.fn(),
      name: 'stt',
    }

    const stts = [
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
    ]

    const { container } = render(
      <ComboBox {...props}>
        {stts.map((stt) => (
          <option
            className="sttOption"
            key={stt.id}
            value={stt.name.toLowerCase()}
          >
            {stt.name}
          </option>
        ))}
      </ComboBox>
    )

    const input = container.querySelector('.usa-combo-box__input--error')

    expect(input).not.toBeInTheDocument()
  })
})
