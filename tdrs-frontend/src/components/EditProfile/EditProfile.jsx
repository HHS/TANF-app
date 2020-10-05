import React, { useState, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { fetchStts } from '../../actions/stts'
import Button from '../Button'

function EditProfile() {
  const [profileInfo, setProfileInfo] = useState({
    firstName: '',
    lastName: '',
    stt: '',
  })
  const [errors, setErrors] = useState({})

  const sttsLoading = useSelector((state) => state.stts.loading)
  const stts = useSelector((state) => state.stts.stts)

  const dispatch = useDispatch()

  useEffect(() => {
    dispatch(fetchStts())
  }, [dispatch])

  const validateInputs = ({ name, value }) => {
    if (value.length < 1)
      return setErrors({
        ...errors,
        [name]: 'You need at least 1 character',
      })
    return setErrors({})
  }

  return (
    <div className="grid-container">
      <h1 className="request-access-header font-serif-2xl">Request Access</h1>
      <p className="request-access-secondary">
        We need to collect some information before an OFA Admin can grant you
        access
      </p>
      <form className="usa-form">
        <div
          className={`usa-form-group ${
            errors['first-name'] ? 'usa-form-group--error' : ''
          }`}
        >
          <label
            className={`usa-label ${
              errors['first-name'] ? 'usa-label--error' : ''
            }`}
            htmlFor="first-name"
          >
            First name
            {errors['first-name'] && (
              <span
                className="usa-error-message"
                id="input-error-message"
                role="alert"
              >
                {errors['first-name']}
              </span>
            )}
            <input
              className={`usa-input ${
                errors['first-name'] ? 'usa-input--error' : ''
              }`}
              id="first-name"
              name="first-name"
              type="text"
              required
              aria-required="true"
              value={profileInfo.firstName}
              onChange={({ target }) => {
                validateInputs(target)
                setProfileInfo({ ...profileInfo, firstName: target.value })
              }}
            />
          </label>
        </div>
        <div
          className={`usa-form-group ${
            errors['last-name'] ? 'usa-form-group--error' : ''
          }`}
        >
          <label
            className={`usa-label ${
              errors['last-name'] ? 'usa-label--error' : ''
            }`}
            htmlFor="last-name"
          >
            Last name
            {errors['last-name'] && (
              <span
                className="usa-error-message"
                id="input-error-message"
                role="alert"
              >
                {errors['last-name']}
              </span>
            )}
            <input
              className={`usa-input ${
                errors['last-name'] ? 'usa-input--error' : ''
              }`}
              id="last-name"
              name="last-name"
              type="text"
              required
              aria-required="true"
              value={profileInfo.lastName}
              onChange={({ target }) => {
                validateInputs(target)
                setProfileInfo({ ...profileInfo, lastName: target.value })
              }}
            />
          </label>
        </div>
        <div
          className={`usa-form-group ${
            errors.stt ? 'usa-form-group--error' : ''
          }`}
        >
          {/* I am disabling this rule here because the <Select> component does have an input with an id of 'stt'
            but only once it's rendered.
          */}
          {/* eslint-disable-next-line jsx-a11y/label-has-associated-control */}
          <label className="usa-label" htmlFor="stt">
            Associated State, Tribe, or Territory
            <div className="usa-combo-box">
              <select
                className="usa-select usa-combo-box__select"
                name="stt"
                id="fruit"
              >
                <option value>Select a fruit</option>
                <option value="apple">Apple</option>
                <option value="apricot">Apricot</option>
                <option value="avocado">Avocado</option>
                <option value="banana">Banana</option>
                <option value="blackberry">Blackberry</option>
                <option value="blood orange">Blood orange</option>
                <option value="blueberry">Blueberry</option>
                <option value="boysenberry">Boysenberry</option>
                <option value="breadfruit">Breadfruit</option>
                <option value="buddhas hand citron">
                  Buddha&apos;s hand citron
                </option>
                <option value="cantaloupe">Cantaloupe</option>
                <option value="clementine">Clementine</option>
                <option value="crab apple">Crab apple</option>
                <option value="currant">Currant</option>
                <option value="cherry">Cherry</option>
                <option value="custard apple">Custard apple</option>
                <option value="coconut">Coconut</option>
                <option value="cranberry">Cranberry</option>
                <option value="date">Date</option>
                <option value="dragonfruit">Dragonfruit</option>
                <option value="durian">Durian</option>
                <option value="elderberry">Elderberry</option>
                <option value="fig">Fig</option>
                <option value="gooseberry">Gooseberry</option>
                <option value="grape">Grape</option>
                <option value="grapefruit">Grapefruit</option>
                <option value="guava">Guava</option>
                <option value="honeydew melon">Honeydew melon</option>
                <option value="jackfruit">Jackfruit</option>
                <option value="kiwifruit">Kiwifruit</option>
                <option value="kumquat">Kumquat</option>
                <option value="lemon">Lemon</option>
                <option value="lime">Lime</option>
                <option value="lychee">Lychee</option>
                <option value="mandarine">Mandarine</option>
                <option value="mango">Mango</option>
                <option value="mangosteen">Mangosteen</option>
                <option value="marionberry">Marionberry</option>
                <option value="nectarine">Nectarine</option>
                <option value="orange">Orange</option>
                <option value="papaya">Papaya</option>
                <option value="passionfruit">Passionfruit</option>
                <option value="peach">Peach</option>
                <option value="pear">Pear</option>
                <option value="persimmon">Persimmon</option>
                <option value="plantain">Plantain</option>
                <option value="plum">Plum</option>
                <option value="pineapple">Pineapple</option>
                <option value="pluot">Pluot</option>
                <option value="pomegranate">Pomegranate</option>
                <option value="pomelo">Pomelo</option>
                <option value="quince">Quince</option>
                <option value="raspberry">Raspberry</option>
                <option value="rambutan">Rambutan</option>
                <option value="soursop">Soursop</option>
                <option value="starfruit">Starfruit</option>
                <option value="strawberry">Strawberry</option>
                <option value="tamarind">Tamarind</option>
                <option value="tangelo">Tangelo</option>
                <option value="tangerine">Tangerine</option>
                <option value="ugli fruit">Ugli fruit</option>
                <option value="watermelon">Watermelon</option>
                <option value="white currant">White currant</option>
                <option value="yuzu">Yuzu</option>
              </select>
            </div>
          </label>
        </div>
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
