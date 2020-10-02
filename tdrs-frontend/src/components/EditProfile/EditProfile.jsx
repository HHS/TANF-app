import React, { useEffect } from 'react'
import { Select } from 'antd'
import { useDispatch, useSelector } from 'react-redux'
import { fetchStts } from '../../actions/stts'
import Button from '../Button'

const { Option } = Select

function EditProfile() {
  const sttsLoading = useSelector((state) => state.stts.loading)
  const stts = useSelector((state) => state.stts.stts)
  const dispatch = useDispatch()

  useEffect(() => {
    dispatch(fetchStts())
  }, [dispatch])

  function onChange(value) {
    console.log(`selected ${value}`)
  }

  function onBlur() {
    console.log('blur')
  }

  function onFocus() {
    console.log('focus')
  }

  function onSearch(val) {
    console.log('search:', val)
  }

  return (
    <div className="grid-container">
      <h1 className="request-access-header font-serif-2xl">Request Access</h1>
      <p className="request-access-secondary">
        We need to collect some information before an OFA Admin can grant you
        access
      </p>
      <form className="usa-form">
        <label className="usa-label" htmlFor="first-name">
          First name
          <input
            className="usa-input"
            id="first-name"
            name="first-name"
            type="text"
            required
            aria-required="true"
          />
        </label>

        <label className="usa-label" htmlFor="last-name">
          Last name
          <input
            className="usa-input"
            id="last-name"
            name="last-name"
            type="text"
            required
            aria-required="true"
          />
        </label>
        {/* I am disabling this rule here because the <Select> component does have an input with an id of 'stt'
            but only once it's rendered.
        */}
        {/* eslint-disable-next-line jsx-a11y/label-has-associated-control */}
        <label className="usa-label" htmlFor="stt">
          Associated State, Tribe, or Territory
          <Select
            showSearch
            allowClear
            style={{ width: 320 }}
            placeholder="Select a person"
            onChange={onChange}
            onFocus={onFocus}
            onBlur={onBlur}
            onSearch={onSearch}
            loading={sttsLoading}
            filterOption={(input, option) =>
              option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
            }
          >
            {stts.map((stt) => (
              <Option
                key={stt.id}
                label={stt.name}
                value={stt.name.toLowerCase()}
              >
                {stt.name}
              </Option>
            ))}
          </Select>
        </label>
        <Button
          type="submit"
          disabled
          size="big"
          className="request-access-button"
        >
          Request Access
        </Button>
      </form>
    </div>
  )
}

export default EditProfile
