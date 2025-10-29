/* istanbul ignore file */
import React, { createContext, useContext, useState, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import {
  clearFileList,
  reinitializeSubmittedFiles,
  setStt,
} from '../../actions/reports'
import { openFeedbackWidget } from '../../reducers/feedbackWidget'

const ReportsContext = createContext()

export const useReportsContext = () => {
  const context = useContext(ReportsContext)
  if (!context) {
    throw new Error('useReportsContext must be used within ReportsProvider')
  }
  return context
}

export const ReportsProvider = ({ isFra = false, children }) => {
  const dispatch = useDispatch()

  // Form state
  const [yearInputValue, setYearInputValue] = useState('')
  const [quarterInputValue, setQuarterInputValue] = useState('')
  const [fileTypeInputValue, setFileTypeInputValue] = useState(
    isFra ? 'workOutcomesOfTanfExiters' : 'tanf'
  )
  const [sttInputValue, setSttInputValue] = useState('')
  const [pendingChange, setPendingChange] = useState({
    type: null,
    value: null,
  })

  // FRA-specific upload state
  const [fraSelectedFile, setFraSelectedFile] = useState(null)
  const [fraUploadError, setFraUploadError] = useState(null)

  // Modal state
  const [errorModalVisible, setErrorModalVisible] = useState(false)
  const [modalTriggerSource, setModalTriggerSource] = useState(null) // 'cancel' or 'input-change'
  const [reprocessedModalVisible, setReprocessedModalVisible] = useState(false)
  const [reprocessedDate, setReprocessedDate] = useState('')

  // Alert state
  const [localAlert, setLocalAlertState] = useState({
    active: false,
    type: null,
    message: null,
  })

  // Tab state
  const [selectedSubmissionTab, setSelectedSubmissionTab] = useState(1)

  // Refs
  const headerRef = useRef(null)
  const alertRef = useRef(null)

  // Redux selectors
  const files = useSelector((state) => state.reports.submittedFiles)
  const uploadedFiles = files?.filter((file) => file.fileName && !file.id)

  // FRA-specific derived state
  const fraHasUploadedFile = fraSelectedFile && !fraSelectedFile.id

  // Actions
  const handleClearAll = () => {
    // Clear everything including STT, year, quarter
    if (isFra) {
      setFraSelectedFile(null)
      setFraUploadError(null)
      setYearInputValue('')
      setQuarterInputValue('')
      setSttInputValue('')
    } else {
      dispatch(clearFileList({ fileType: fileTypeInputValue }))
      setYearInputValue('')
      setQuarterInputValue('')
    }
  }

  const handleClearFilesOnly = () => {
    // Clear only file inputs/previews, keep STT, year, quarter
    if (isFra) {
      setFraSelectedFile(null)
      setFraUploadError(null)
    } else {
      dispatch(clearFileList({ fileType: fileTypeInputValue }))
    }
    switch (pendingChange.type) {
      case 'fileType':
        setFileTypeInputValue(pendingChange.value)
        // Reset year if it's invalid for the new file type
        const minYear =
          pendingChange.value === 'program-integrity-audit' ? 2024 : 2021
        if (yearInputValue && parseInt(yearInputValue) < minYear) {
          setYearInputValue('')
        }
        break
      case 'year':
        setYearInputValue(pendingChange.value)
        break
      case 'quarter':
        setQuarterInputValue(pendingChange.value)
        break
      case 'stt':
        setSttInputValue(pendingChange.value)
        dispatch(setStt(pendingChange.value))
        // Check if current file type is valid for the new STT
        if (
          pendingChange.sttObject &&
          fileTypeInputValue === 'ssp-moe' &&
          !pendingChange.sttObject.ssp
        ) {
          setFileTypeInputValue('tanf')
          dispatch(clearFileList({ fileType: 'tanf' }))
          dispatch(reinitializeSubmittedFiles('tanf'))
        }
        break
    }
    setPendingChange({ type: null, value: null, sttObject: null })
  }

  const cancelPendingChange = () => {
    setPendingChange({ type: null, value: null })
  }

  const handleOpenFeedbackWidget = () => {
    dispatch(openFeedbackWidget({
          dataType: fileTypeInputValue,
          dataFiles: uploadedFiles,
          widgetId: `${fileTypeInputValue}-report-submission-feedback`,
    }))
  }

  const selectFileType = (value) => {
    if (uploadedFiles.length > 0 || fraHasUploadedFile) {
      setModalTriggerSource('input-change')
      setPendingChange({ type: 'fileType', value })
      setErrorModalVisible(true)
    } else {
      setFileTypeInputValue(value)
      setLocalAlertState({ active: false, type: null, message: null })
      dispatch(clearFileList({ fileType: value }))
      dispatch(reinitializeSubmittedFiles(value))
      setFraSelectedFile(null)

      // Reset year if it's invalid for the new file type
      // Program Integrity Audit starts at 2024, TANF/SSP/FRA start at 2021
      const minYear = value === 'program-integrity-audit' ? 2024 : 2021
      if (yearInputValue && parseInt(yearInputValue) < minYear) {
        setYearInputValue('')
      }
    }
  }

  const selectYear = ({ target: { value } }) => {
    if (uploadedFiles.length > 0 || fraHasUploadedFile) {
      setModalTriggerSource('input-change')
      setPendingChange({ type: 'year', value })
      setErrorModalVisible(true)
    } else {
      setYearInputValue(value)
      setLocalAlertState({ active: false, type: null, message: null })
      dispatch(clearFileList({ fileType: fileTypeInputValue }))
      setFraSelectedFile(null)
    }
  }

  const selectQuarter = ({ target: { value } }) => {
    if (uploadedFiles.length > 0 || fraHasUploadedFile) {
      setModalTriggerSource('input-change')
      setPendingChange({ type: 'quarter', value })
      setErrorModalVisible(true)
    } else {
      setQuarterInputValue(value)
      setLocalAlertState({ active: false, type: null, message: null })
      dispatch(clearFileList({ fileType: fileTypeInputValue }))
      setFraSelectedFile(null)
    }
  }

  const selectStt = (value, sttObject = null) => {
    if (uploadedFiles.length > 0 || fraHasUploadedFile) {
      setModalTriggerSource('input-change')
      setPendingChange({ type: 'stt', value, sttObject })
      setErrorModalVisible(true)
    } else {
      setSttInputValue(value)
      dispatch(setStt(value))
      setLocalAlertState({
        active: false,
        type: null,
        message: null,
      })

      // Check if current file type is valid for the new STT
      // If SSP is selected but new STT doesn't support SSP, reset to TANF
      if (sttObject && fileTypeInputValue === 'ssp-moe' && !sttObject.ssp) {
        setFileTypeInputValue('tanf')
        dispatch(clearFileList({ fileType: 'tanf' }))
        dispatch(reinitializeSubmittedFiles('tanf'))
      } else {
        dispatch(clearFileList({ fileType: fileTypeInputValue }))
      }

      setFraSelectedFile(null)
    }
  }

  const value = {
    // State
    sttInputValue,
    fileTypeInputValue,
    yearInputValue,
    quarterInputValue,
    errorModalVisible,
    setErrorModalVisible,
    modalTriggerSource,
    setModalTriggerSource,
    reprocessedModalVisible,
    setReprocessedModalVisible,
    reprocessedDate,
    setReprocessedDate,
    localAlert,
    setLocalAlertState,
    selectedSubmissionTab,
    setSelectedSubmissionTab,
    headerRef,
    alertRef,

    // FRA-specific state
    fraSelectedFile,
    setFraSelectedFile,
    fraUploadError,
    setFraUploadError,

    // Derived state
    uploadedFiles,
    fraHasUploadedFile,

    // Actions
    handleClearAll,
    handleClearFilesOnly,
    cancelPendingChange,
    handleOpenFeedbackWidget,
    selectFileType,
    selectYear,
    selectQuarter,
    selectStt,
  }

  return (
    <ReportsContext.Provider value={value}>{children}</ReportsContext.Provider>
  )
}
