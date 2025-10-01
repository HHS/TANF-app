import React, { createContext, useContext, useState, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import {
  clearFileList,
  reinitializeSubmittedFiles,
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

export const ReportsProvider = ({ children }) => {
  const dispatch = useDispatch()

  // Form state
  const [yearInputValue, setYearInputValue] = useState('')
  const [quarterInputValue, setQuarterInputValue] = useState('')
  const [fileTypeInputValue, setFileTypeInputValue] = useState('tanf')
  const [sttInputValue, setSttInputValue] = useState('')

  // Modal state
  const [errorModalVisible, setErrorModalVisible] = useState(false)
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

  // Redux selectors
  const files = useSelector((state) => state.reports.submittedFiles)
  const uploadedFiles = files?.filter((file) => file.fileName && !file.id)

  // Actions
  const handleClear = () => {
    dispatch(clearFileList({ fileType: fileTypeInputValue }))
    setYearInputValue('')
    setQuarterInputValue('')
  }

  const handleOpenFeedbackWidget = () => {
    dispatch(openFeedbackWidget(fileTypeInputValue))
  }

  const selectFileType = (value) => {
    setFileTypeInputValue(value)
    setYearInputValue('')
    setQuarterInputValue('')
    dispatch(clearFileList({ fileType: value }))
    dispatch(reinitializeSubmittedFiles(value))
  }

  const value = {
    // State
    yearInputValue,
    setYearInputValue,
    quarterInputValue,
    setQuarterInputValue,
    fileTypeInputValue,
    setFileTypeInputValue,
    sttInputValue,
    setSttInputValue,
    errorModalVisible,
    setErrorModalVisible,
    reprocessedModalVisible,
    setReprocessedModalVisible,
    reprocessedDate,
    setReprocessedDate,
    localAlert,
    setLocalAlertState,
    selectedSubmissionTab,
    setSelectedSubmissionTab,
    headerRef,

    // Derived state
    uploadedFiles,

    // Actions
    handleClear,
    handleOpenFeedbackWidget,
    selectFileType,
  }

  return (
    <ReportsContext.Provider value={value}>{children}</ReportsContext.Provider>
  )
}
