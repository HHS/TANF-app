import { useEffect, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { getAvailableFileList } from '../actions/reports'
import { useReportsContext } from '../components/Reports/ReportsContext'

/**
 * Custom hook that encapsulates shared submission history logic
 * Used by both QuarterSubmissionHistory and SectionSubmissionHistory
 *
 * @param {Object} filterValues - Filter values for fetching files
 * @returns {Object} Files and fetch state
 */
export const useSubmissionHistory = (filterValues) => {
  const dispatch = useDispatch()
  const { files, loading } = useSelector((state) => state.reports)
  const prevFilterValuesRef = useRef()
  const { isDonePolling } = useReportsContext()

  useEffect(() => {
    // Serialize filterValues for comparison
    const currentFilters = JSON.stringify(filterValues)
    const prevFilters = prevFilterValuesRef.current

    // Fetch if this is the first render or if filterValues have changed
    // if (!prevFilters && !isDonePolling()) {
    //   return
    // } else
    if (!prevFilters || currentFilters !== prevFilters) {
      dispatch(getAvailableFileList(filterValues))
      prevFilterValuesRef.current = currentFilters
    }
  }, [dispatch, filterValues, isDonePolling])

  return {
    files,
    loading,
  }
}
