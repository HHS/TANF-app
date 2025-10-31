import React, { useEffect, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import classNames from 'classnames'

import STTComboBox from '../STTComboBox'
import { fetchSttList } from '../../actions/sttList'
import Modal from '../Modal'
import ReprocessedModal from '../SubmissionHistory/ReprocessedModal'
import {
  selectPrimaryUserRole,
  accountIsRegionalStaff,
} from '../../selectors/auth'
import RadioSelect from '../Form/RadioSelect'
import TanfSspReports from './tdr/TanfSspReports'
import ProgramIntegrityAuditReports from './pia/ProgramIntegrityAuditReports'
import { ReportsProvider, useReportsContext } from './ReportsContext'

function ReportsContent() {
  const {
    fileTypeInputValue,
    sttInputValue,
    errorModalVisible,
    setErrorModalVisible,
    modalTriggerSource,
    reprocessedModalVisible,
    setReprocessedModalVisible,
    reprocessedDate,
    handleClearAll,
    handleClearFilesOnly,
    cancelPendingChange,
    selectFileType,
    selectStt,
    getSttError,
    getFileTypeError,
  } = useReportsContext()

  const dispatch = useDispatch()
  const user = useSelector((state) => state.auth.user)
  const isOFAAdmin = useSelector(selectPrimaryUserRole)?.name === 'OFA Admin'
  const isDIGITTeam = useSelector(selectPrimaryUserRole)?.name === 'DIGIT Team'
  const isSystemAdmin =
    useSelector(selectPrimaryUserRole)?.name === 'OFA System Admin'
  const isRegionalStaff = useSelector(accountIsRegionalStaff)
  const canSelectSTT =
    isOFAAdmin || isDIGITTeam || isSystemAdmin || isRegionalStaff

  const sttList = useSelector((state) => state?.stts?.sttList)

  const userProfileStt = user?.stt?.name

  const headerRef = useRef(null)
  useEffect(() => {
    if (headerRef && headerRef.current) {
      headerRef.current.focus()
    }
  }, [])

  useEffect(() => {
    if (sttList.length === 0) {
      dispatch(fetchSttList())
    }
  }, [dispatch, sttList])

  const redux_stt = useSelector((state) => state.reports.stt)

  const currentStt =
    isOFAAdmin || isDIGITTeam || isSystemAdmin || isRegionalStaff
      ? redux_stt
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

  const radio_options = [
    { label: 'TANF', value: 'tanf' },
    ...(fileTypeStt?.ssp ? [{ label: 'SSP-MOE', value: 'ssp-moe' }] : []),
    {
      label: 'Program Integrity Audit',
      value: 'program-integrity-audit',
    },
  ]

  return (
    <div className="page-container" style={{ position: 'relative' }}>
      <div>
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
                  selectStt={(value) => {
                    const selectedSttObject = sttList?.find(
                      (s) => s?.name === value
                    )
                    selectStt(value, selectedSttObject)
                  }}
                  error={getSttError()}
                />
              </div>
            )}
            <RadioSelect
              label="File Type*"
              fieldName="reportType"
              setValue={selectFileType}
              options={radio_options}
              classes="margin-top-4"
              selectedValue={fileTypeInputValue}
              error={getFileTypeError()}
              errorMessage="A file type selection is required"
            />
          </div>
        </div>

        {fileTypeInputValue === 'program-integrity-audit' ? (
          <ProgramIntegrityAuditReports
            stt={stt ? stt : fileTypeStt}
            isRegionalStaff={isRegionalStaff}
          />
        ) : (
          <TanfSspReports
            stt={stt ? stt : fileTypeStt}
            isRegionalStaff={isRegionalStaff}
          />
        )}
      </div>

      <Modal
        title="Files Not Submitted"
        message="Your uploaded files have not been submitted. Clicking 'OK' will discard your changes and remove any uploaded files."
        isVisible={errorModalVisible}
        buttons={[
          {
            key: '1',
            text: 'Cancel',
            onClick: () => {
              cancelPendingChange()
              setErrorModalVisible(false)
            },
          },
          {
            key: '2',
            text: 'OK',
            onClick: () => {
              setErrorModalVisible(false)
              if (modalTriggerSource === 'cancel') {
                handleClearAll()
              } else {
                handleClearFilesOnly()
              }
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

function Reports() {
  return (
    <ReportsProvider>
      <ReportsContent />
    </ReportsProvider>
  )
}

export default Reports
