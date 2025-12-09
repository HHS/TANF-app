/* istanbul ignore file */
import {
  createContext,
  useContext,
  useState,
  useRef,
  useEffect,
  useCallback,
  useMemo,
} from 'react'
import { useDispatch, useSelector } from 'react-redux'
import {
  clearFileList,
  reinitializeSubmittedFiles,
  setStt,
} from '../../actions/reports'
import { openFeedbackWidget } from '../../reducers/feedbackWidget'
import { useSearchParams } from 'react-router-dom'
import { accountCanSelectStt } from '../../selectors/auth'
import { getCurrentFiscalYear, quarters } from './utils'

const ReportsContext = createContext()

export const useReportsContext = () => {
  const context = useContext(ReportsContext)
  if (!context) {
    throw new Error('useReportsContext must be used within ReportsProvider')
  }
  return context
}

// Valid file types for each report mode
const VALID_FILE_TYPES = {
  reports: [
    'tanf',
    'ssp-moe',
    ...(process.env.REACT_APP_SHOW_PIA === 'true'
      ? ['program-integrity-audit']
      : []),
  ],
  fra: [
    'workOutcomesOfTanfExiters',
    // TODO: uncomment when we collect this data
    // 'secondarySchoolAttainment',
    // 'supplementalWorkOutcomes',
  ],
}

// Valid quarters
const VALID_QUARTERS = Object.keys(quarters) // ['Q1', 'Q2', 'Q3', 'Q4']

/**
 * Validates URL parameters for the report pages.
 * Invalid parameters are cleared individually, valid ones are kept.
 * @param {URLSearchParams} searchParams - URL search parameters
 * @param {boolean} isFra - Whether this is for FRA reports
 * @param {Array} sttList - List of valid STTs
 */
const validateUrlParams = (searchParams, isFra, sttList) => {
  const fiscalYear = searchParams.get('fy')
  const quarter = searchParams.get('q')
  const type = searchParams.get('type')
  const stt = searchParams.get('stt')
  const tab = searchParams.get('tab')

  const defaultType = isFra ? 'workOutcomesOfTanfExiters' : 'tanf'
  let validatedFy = ''
  let validatedQ = ''
  let validatedType = defaultType
  let validatedStt = ''
  let validatedTab = 1
  let hasInvalidParam = false

  // Validate fiscal year (must be a valid year between 2021 and current fiscal year)
  // For program-integrity-audit, only 2024 is allowed
  const year = parseInt(fiscalYear, 10)
  const currentFiscalYear = getCurrentFiscalYear()
  const minYear = type === 'program-integrity-audit' ? 2024 : 2021
  const maxYear = type === 'program-integrity-audit' ? 2024 : currentFiscalYear
  if (!isNaN(year) && year >= minYear && year <= maxYear) {
    validatedFy = fiscalYear
  } else {
    hasInvalidParam = true
  }

  // Validate quarter (must be Q1, Q2, Q3, or Q4)
  if (VALID_QUARTERS.includes(quarter)) {
    validatedQ = quarter
  } else {
    hasInvalidParam = true
  }

  // Validate file type
  const validTypes = isFra ? VALID_FILE_TYPES.fra : VALID_FILE_TYPES.reports
  if (validTypes.includes(type)) {
    validatedType = type
  } else {
    hasInvalidParam = true
  }

  // Validate STT (must exist in the STT list if provided)
  if (sttList && sttList.length > 0) {
    if (sttList.some((s) => s?.name === stt)) {
      validatedStt = stt
    } else {
      hasInvalidParam = true
    }
  } else {
    // STT list not loaded yet, keep the value for now
    validatedStt = stt
  }

  // Validate tab (must be 1 or 2)
  if (tab === '1' || tab === '2') {
    validatedTab = parseInt(tab, 10)
  } else {
    hasInvalidParam = true
  }

  return {
    fy: validatedFy,
    q: validatedQ,
    type: validatedType,
    stt: validatedStt,
    tab: validatedTab,
    wasInvalid: hasInvalidParam,
  }
}

export const ReportsProvider = ({ isFra = false, children }) => {
  const dispatch = useDispatch()
  const canSelectStt = useSelector(accountCanSelectStt)
  const sttList = useSelector((state) => state?.stts?.sttList)

  // Search params
  const [searchParams, setSearchParams] = useSearchParams()
  const [hasValidatedParams, setHasValidatedParams] = useState(false)

  // Get validated params (without STT validation since it will never be loaded since we have to wait for fetchSTTs to
  // run.
  const validatedParams = useMemo(
    () => validateUrlParams(searchParams, isFra, []),
    [searchParams, isFra]
  )

  // Form state
  const [yearInputValue, setYearInputValue] = useState(validatedParams.fy)
  const [quarterInputValue, setQuarterInputValue] = useState(validatedParams.q)
  const [fileTypeInputValue, setFileTypeInputValue] = useState(
    validatedParams.type
  )
  const [sttInputValue, setSttInputValue] = useState(validatedParams.stt)
  const [selectedSubmissionTab, setSelectedSubmissionTab] = useState(
    validatedParams.tab
  )

  // Re-validate when STT list becomes available (only validates STT param) since it might not be available yet
  useEffect(() => {
    if (sttList && sttList.length > 0 && !hasValidatedParams) {
      // Check if the STT from URL is valid
      const sttParam = searchParams.get('stt')
      if (sttParam && !sttList.some((s) => s?.name === sttParam)) {
        // Invalid STT in URL clear it
        setSttInputValue('')
      }
      setHasValidatedParams(true)
    }
  }, [sttList])

  const [pendingChange, setPendingChange] = useState({
    type: null,
    value: null,
  })

  useEffect(() => {
    const newParams = new URLSearchParams()
    if (yearInputValue) {
      newParams.set('fy', yearInputValue)
    }
    if (quarterInputValue) {
      newParams.set('q', quarterInputValue)
    }
    if (fileTypeInputValue) {
      newParams.set('type', fileTypeInputValue)
    }
    if (sttInputValue) {
      newParams.set('stt', sttInputValue)
    }
    if (selectedSubmissionTab) {
      newParams.set('tab', selectedSubmissionTab)
    }
    setSearchParams(newParams)
  }, [
    yearInputValue,
    quarterInputValue,
    fileTypeInputValue,
    sttInputValue,
    selectedSubmissionTab,
    setSearchParams,
  ])

  // Touched state for validation
  const [yearTouched, setYearTouched] = useState(false)
  const [quarterTouched, setQuarterTouched] = useState(false)
  const [fileTypeTouched, setFileTypeTouched] = useState(false)
  const [sttTouched, setSttTouched] = useState(false)

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

  // Refs
  const headerRef = useRef(null)
  const alertRef = useRef(null)

  // Redux selectors
  const files = useSelector((state) => state.reports.submittedFiles)
  const uploadedFiles = files?.filter((file) => file.fileName && !file.id)
  const submittedFiles = files?.filter((file) => file.fileName && file.id) || []

  // FRA-specific derived state
  const fraHasUploadedFile = !!fraSelectedFile && !fraSelectedFile.id

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

  const handleOpenFeedbackWidget = useCallback(() => {
    dispatch(
      openFeedbackWidget({
        dataType: fileTypeInputValue,
        dataFiles: submittedFiles,
        widgetId: `${fileTypeInputValue}-report-submission-feedback`,
      })
    )
  }, [dispatch, fileTypeInputValue, submittedFiles])

  const selectFileType = (value) => {
    setFileTypeTouched(true)
    handleFieldSelection('fileType')

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
    setYearTouched(true)
    handleFieldSelection('year')

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
    setQuarterTouched(true)
    handleFieldSelection('quarter')

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
    setSttTouched(true)
    handleFieldSelection('stt')

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

  const handleYearBlur = () => {
    setYearTouched(true)
  }

  const handleQuarterBlur = () => {
    setQuarterTouched(true)
  }

  // Helper to check if order is broken and mark all fields as touched
  const handleFieldSelection = (fieldName) => {
    // Define the correct order with field values
    const fieldOrder = [
      {
        name: 'stt',
        isTouched: () => sttTouched,
        hasValue: () => !canSelectStt || !!sttInputValue,
        isRequired: () => canSelectStt,
      },
      {
        name: 'fileType',
        isTouched: () => fileTypeTouched,
        hasValue: () => !!fileTypeInputValue,
        isRequired: () => true,
      },
      {
        name: 'year',
        isTouched: () => yearTouched,
        hasValue: () => !!yearInputValue,
        isRequired: () => true,
      },
      {
        name: 'quarter',
        isTouched: () => quarterTouched,
        hasValue: () => !!quarterInputValue,
        isRequired: () => true,
      },
    ]

    // Find the index of the current field
    const currentFieldIndex = fieldOrder.findIndex((f) => f.name === fieldName)

    // Check if any required previous fields are empty (regardless of touched state)
    // A field with a value is considered valid even if not explicitly touched
    let orderBroken = false
    for (let i = 0; i < currentFieldIndex; i++) {
      const field = fieldOrder[i]
      if (field.isRequired() && !field.hasValue()) {
        orderBroken = true
        break
      }
    }

    // If order is broken, mark all fields as touched
    if (orderBroken) {
      if (canSelectStt) setSttTouched(true)
      setFileTypeTouched(true)
      setYearTouched(true)
      setQuarterTouched(true)
    }
  }

  // Validation helpers with sequential order enforcement
  // Order: STT (if applicable) -> File Type -> Fiscal Year -> Fiscal Quarter

  const getSttError = () => {
    // Only show error if user can select STT and hasn't selected one
    if (!canSelectStt) return false
    return sttTouched && !sttInputValue
  }

  const getFileTypeError = () => {
    // Show error if:
    // 1. Field was touched and is empty, OR
    // 2. Previous required field (STT) is not filled AND this field was touched
    if (canSelectStt && !sttInputValue) {
      return fileTypeTouched && !fileTypeInputValue
    }
    return fileTypeTouched && !fileTypeInputValue
  }

  const getYearError = () => {
    // Only show error if the field is empty
    if (yearInputValue) return false

    // Show error if field was touched OR any previous required field is invalid
    if (!yearTouched) return false

    return true
  }

  const getQuarterError = () => {
    // Only show error if the field is empty
    if (quarterInputValue) return false

    // Show error if field was touched OR any previous required field is invalid
    if (!quarterTouched) return false

    return true
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

    // Validation state
    yearTouched,
    quarterTouched,
    fileTypeTouched,
    sttTouched,
    getYearError,
    getQuarterError,
    getFileTypeError,
    getSttError,

    // Actions
    handleClearAll,
    handleClearFilesOnly,
    cancelPendingChange,
    handleOpenFeedbackWidget,
    selectFileType,
    selectYear,
    selectQuarter,
    selectStt,
    handleYearBlur,
    handleQuarterBlur,
  }

  return (
    <ReportsContext.Provider value={value}>{children}</ReportsContext.Provider>
  )
}
