import React, { useEffect, useRef, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import classNames from 'classnames'

import { clearFileList } from '../../actions/reports'
import FileUploadForm from '../FileUploadForm'
import STTComboBox from '../STTComboBox'
import { fetchSttList } from '../../actions/sttList'
import Modal from '../Modal'
import SegmentedControl from '../SegmentedControl'
import SubmissionHistory from '../SubmissionHistory'
import ReprocessedModal from '../SubmissionHistory/ReprocessedModal'
import {
  selectPrimaryUserRole,
  accountIsRegionalStaff,
} from '../../selectors/auth'
import { quarters, constructYearOptions } from './utils'
import { openFeedbackWidget } from '../../reducers/feedbackWidget'
import RadioSelect from '../Form/RadioSelect'

const FiscalQuarterExplainer = () => (
  <table className="usa-table usa-table--striped margin-top-4 desktop:width-tablet mobile:width-full">
    <caption>TANF/SSP Data Reporting Guidelines</caption>
    <thead>
      <tr>
        <th>Fiscal Year (FY) &amp; Quarter (Q)</th>
        <th>Calendar Period</th>
        <th>Due Date</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>FY Q1</td>
        <td>Oct 1 - Dec 31</td>
        <td>February 14</td>
      </tr>
      <tr>
        <td>FY Q2</td>
        <td>Jan 1 - Mar 31</td>
        <td>May 15</td>
      </tr>
      <tr>
        <td>FY Q3</td>
        <td>Apr 1 - Jun 30</td>
        <td>August 14</td>
      </tr>
      <tr>
        <td>FY Q4</td>
        <td>Jul 1 - Sep 30</td>
        <td>November 14</td>
      </tr>
    </tbody>
  </table>
)

const ProgramIntegrityAuditExplainer = () => {
  const currentYear = new Date().getFullYear()
  return (
    <>
      <div className="mobile:grid-container desktop:padding-0 desktop:grid-col-fill">
        <div className="usa-alert usa-alert--slim usa-alert--info">
          <div className="usa-alert__body" role="alert">
            <p className="usa-alert__text">
              For Additional guidance please refer to the Program Instruction
              for this new reporting requirement.
            </p>
          </div>
        </div>
      </div>
      <table className="usa-table usa-table--striped">
        <caption>Audit Reporting</caption>
        <thead>
          <tr>
            <th>Fiscal Year (FY)</th>
            <th>Due Date</th>
          </tr>
        </thead>
        <tbody>
          {Array.from({ length: currentYear - 2024 }).map((_, index) => (
            <tr key={index}>
              <td>FY {currentYear - (index + 1)}</td>
              <td>November 14, {currentYear - index}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  )
}

/**
 * Reports is the home page for users to file a report.
 * The user can select a year
 * for the report that they would like to upload and then click on
 * `Search` to begin uploading files for that year.
 */
function Reports() {
  const [yearInputValue, setYearInputValue] = useState('')
  const [quarterInputValue, setQuarterInputValue] = useState('')
  const [fileTypeInputValue, setFileTypeInputValue] = useState('tanf')

  // The selected stt in the dropdown tied to our redux `reports` state
  const selectedStt = useSelector((state) => state.reports.stt)
  const [sttInputValue, setSttInputValue] = useState(selectedStt)

  // The logged in user saved in our redux `auth` state object
  const user = useSelector((state) => {
    return state.auth.user
  })
  const isOFAAdmin = useSelector(selectPrimaryUserRole)?.name === 'OFA Admin'
  const isDIGITTeam = useSelector(selectPrimaryUserRole)?.name === 'DIGIT Team'
  const isSystemAdmin =
    useSelector(selectPrimaryUserRole)?.name === 'OFA System Admin'
  const isRegionalStaff = useSelector(accountIsRegionalStaff)
  const canSelectSTT =
    isOFAAdmin || isDIGITTeam || isSystemAdmin || isRegionalStaff

  const sttList = useSelector((state) => state?.stts?.sttList)

  const [errorModalVisible, setErrorModalVisible] = useState(false)
  const files = useSelector((state) => state.reports.submittedFiles)
  const uploadedFiles = files?.filter((file) => file.fileName && !file.id)

  const userProfileStt = user?.stt?.name

  const dispatch = useDispatch()
  const [isUploadReportToggled, setIsToggled] = useState(false)

  const [reprocessedModalVisible, setReprocessedModalVisible] = useState(false)
  const [reprocessedDate, setReprocessedDate] = useState('')

  const currentStt =
    isOFAAdmin || isDIGITTeam || isSystemAdmin || isRegionalStaff
      ? selectedStt
      : userProfileStt

  const stt = sttList?.find((stt) => stt?.name === currentStt)

  const fileTypeStt = stt
    ? stt
    : sttList?.find((fileTypeStt) => fileTypeStt?.name === sttInputValue)

  const missingStt =
    (!isOFAAdmin &&
      !isDIGITTeam &&
      !isSystemAdmin &&
      !isRegionalStaff &&
      !currentStt) ||
    (isRegionalStaff && user?.regions?.length === 0)

  // Ensure newly rendered header is focused,
  // else it won't be read be screen readers.
  const headerRef = useRef(null)
  useEffect(() => {
    if (headerRef && headerRef.current) {
      headerRef.current.focus()
    }
  }, [])

  const [selectedSubmissionTab, setSelectedSubmissionTab] = useState(1)

  // Non-OFA Admin users will be unable to select an STT
  // prefer => `auth.user.stt`

  const handleOpenFeedbackWidget = () => {
    dispatch(openFeedbackWidget(fileTypeInputValue))
  }

  useEffect(() => {
    if (sttList.length === 0) {
      dispatch(fetchSttList())
    }
  }, [dispatch, sttList])

  const radio_options = [
    { label: 'TANF', value: 'tanf' },
    ...(fileTypeStt?.ssp ? [{ label: 'SSP-MOE', value: 'ssp-moe' }] : []),
    {
      label: 'Program Integrity Audit',
      value: 'program-integrity-audit',
    },
  ]

  const handleClear = () => {
    setIsToggled(false)
    dispatch(clearFileList())
    setYearInputValue('')
    setQuarterInputValue('')
  }

  const [localAlert, setLocalAlertState] = useState({
    active: false,
    type: null,
    message: null,
  })

  const selectFileType = (value) => {
    setFileTypeInputValue(value)
    if (value === 'program-integrity-audit') {
      setQuarterInputValue('')
    }
  }

  const selectYear = ({ target: { value } }) => {
    setYearInputValue(value)
    setLocalAlertState({
      active: false,
      type: null,
      message: null,
    })
    dispatch(clearFileList())
  }

  const selectQuarter = ({ target: { value } }) => {
    setQuarterInputValue(value)
    setLocalAlertState({
      active: false,
      type: null,
      message: null,
    })
    dispatch(clearFileList())
  }

  const selectStt = (value) => {
    setSttInputValue(value)
    setLocalAlertState({
      active: false,
      type: null,
      message: null,
    })
    clearFileList()
    dispatch(clearFileList())
  }

  return (
    <div className="page-container" style={{ position: 'relative' }}>
      <div
        className={classNames({
          'border-bottom': isUploadReportToggled,
        })}
      >
        {missingStt && (
          <div className="margin-top-4 usa-error-message" role="alert">
            An STT is not set for this user.
          </div>
        )}
        <p className="margin-top-5 margin-bottom-0">
          Fields marked with an asterisk (*) are required.
        </p>
        <div className="grid-row grid-gap">
          <div className="mobile:grid-container desktop:padding-0 desktop:grid-col-fill">
            {canSelectSTT && (
              <div
                className={classNames(
                  'usa-form-group maxw-mobile margin-top-4'
                )}
              >
                <STTComboBox
                  selectedStt={sttInputValue}
                  selectStt={selectStt}
                  error={false}
                />
              </div>
            )}
            <RadioSelect
              label="File Type"
              fieldName="reportType"
              setValue={selectFileType}
              options={radio_options}
              classes="margin-top-4"
            />
          </div>
        </div>
        <div className="grid-row grid-gap">
          <div className="mobile:grid-container desktop:padding-0 desktop:grid-col-auto">
            <div
              className={classNames('usa-form-group maxw-mobile margin-top-4')}
            >
              <label
                className="usa-label text-bold margin-top-4"
                htmlFor="reportingYears"
              >
                Fiscal Year (October - September)*
                <select
                  className={classNames('usa-select maxw-mobile')}
                  name="reportingYears"
                  id="reportingYears"
                  onChange={selectYear}
                  value={yearInputValue}
                  aria-describedby="years-error-alert"
                >
                  <option value="" disabled hidden>
                    - Select Fiscal Year -
                  </option>
                  {constructYearOptions()}
                </select>
              </label>
            </div>
            {fileTypeInputValue !== 'program-integrity-audit' && (
              <div
                className={classNames(
                  'usa-form-group maxw-mobile margin-top-4'
                )}
              >
                <label
                  className="usa-label text-bold margin-top-4"
                  htmlFor="quarter"
                >
                  Fiscal Quarter*
                  <select
                    className={classNames('usa-select maxw-mobile')}
                    name="quarter"
                    id="quarter"
                    onChange={selectQuarter}
                    value={quarterInputValue}
                    aria-describedby="quarter-error-alert"
                  >
                    <option value="" disabled hidden>
                      - Select Quarter -
                    </option>
                    {Object.entries(quarters).map(
                      ([quarter, quarterDescription]) => (
                        <option value={quarter} key={quarter}>
                          {quarterDescription}
                        </option>
                      )
                    )}
                  </select>
                </label>
              </div>
            )}
          </div>
          <div className="mobile:grid-container desktop:padding-0 desktop:grid-col-fill">
            {fileTypeInputValue === 'program-integrity-audit' ? (
              <ProgramIntegrityAuditExplainer />
            ) : (
              <FiscalQuarterExplainer />
            )}
          </div>
        </div>
      </div>
      {fileTypeInputValue &&
        yearInputValue &&
        (quarterInputValue ||
          fileTypeInputValue === 'program-integrity-audit') &&
        (canSelectSTT ? stt : true) && (
          <>
            <hr />
            <h2
              ref={headerRef}
              className="font-serif-xl margin-top-5 margin-bottom-0 text-normal"
              tabIndex="-1"
            >
              {`${currentStt} - ${fileTypeInputValue.toUpperCase()} - Fiscal Year ${yearInputValue} - ${
                quarters[quarterInputValue]
              }`}
            </h2>

            {isRegionalStaff ? (
              <h3 className="font-sans-lg margin-top-5 margin-bottom-2 text-bold">
                Submission History
              </h3>
            ) : (
              <SegmentedControl
                buttons={[
                  {
                    id: 1,
                    label: 'Current Submission',
                    onSelect: () => setSelectedSubmissionTab(1),
                  },
                  {
                    id: 2,
                    label: 'Submission History',
                    onSelect: () => setSelectedSubmissionTab(2),
                  },
                ]}
                selected={selectedSubmissionTab}
              />
            )}

            {!isRegionalStaff && selectedSubmissionTab === 1 && (
              <FileUploadForm
                stt={stt}
                year={yearInputValue}
                quarter={quarterInputValue}
                fileType={fileTypeInputValue}
                handleCancel={() => {
                  if (uploadedFiles.length > 0) {
                    setErrorModalVisible(true)
                  } else {
                    handleClear()
                  }
                }}
                openWidget={handleOpenFeedbackWidget}
                localAlert={localAlert}
                setLocalAlertState={setLocalAlertState}
              />
            )}

            {(isRegionalStaff || selectedSubmissionTab === 2) && (
              <SubmissionHistory
                filterValues={{
                  quarter: quarterInputValue,
                  year: yearInputValue,
                  stt: stt,
                  file_type: fileTypeInputValue,
                }}
                reprocessedState={{
                  setModalVisible: setReprocessedModalVisible,
                  setDate: setReprocessedDate,
                }}
              />
            )}
          </>
        )}
      <Modal
        title="Files Not Submitted"
        message="Your uploaded files have not been submitted. Clicking 'OK' will discard your changes and remove any uploaded files."
        isVisible={errorModalVisible}
        buttons={[
          {
            key: '1',
            text: 'Cancel',
            onClick: () => {
              setErrorModalVisible(false)
            },
          },
          {
            key: '2',
            text: 'OK',
            onClick: () => {
              setErrorModalVisible(false)
              handleClear()
            },
          },
        ]}
      />
      <ReprocessedModal
        date={reprocessedDate}
        isVisible={reprocessedModalVisible}
        setModalVisible={setReprocessedModalVisible}
      />
    </div>
  )
}

export default Reports
