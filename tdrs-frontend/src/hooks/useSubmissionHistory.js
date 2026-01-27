import { useEffect, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import {
  getAvailableFileList,
  getTanfSubmissionStatus,
  SET_TANF_SUBMISSION_STATUS,
} from '../actions/reports'
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
  const { isPolling, startPolling } = useReportsContext()

  useEffect(() => {
    // Serialize filterValues for comparison
    const currentFilters = JSON.stringify(filterValues)
    const prevFilters = prevFilterValuesRef.current

    // Fetch if this is the first render or if filterValues have changed
    if (!prevFilters && Object.keys(isPolling).some((k) => !isPolling[k])) {
      return
    } else if (!prevFilters || currentFilters !== prevFilters) {
      dispatch(getAvailableFileList(filterValues))
      prevFilterValuesRef.current = currentFilters
    }
  }, [dispatch, filterValues, isPolling])

  // Restart polling for any pending files when history is loaded (e.g., after navigation)
  useEffect(() => {
    files
      ?.filter((file) => file?.summary?.status === 'Pending')
      ?.forEach((file) => {
        if (isPolling[file.id]) return

        startPolling(
          `${file.id}`,
          () => getTanfSubmissionStatus(file.id),
          (response) => {
            const status = response?.data?.summary?.status
            return status && status !== 'Pending'
          },
          (response) => {
            dispatch({
              type: SET_TANF_SUBMISSION_STATUS,
              payload: {
                datafile_id: file.id,
                datafile: response?.data,
              },
            })
          },
          () => {
            // Silent failure to avoid noisy alerts on navigation-driven polling
          },
          () => {
            // Timed out; leave status as-is and let user refresh manually
          }
        )
      })
  }, [dispatch, files, isPolling, startPolling])

  return {
    files,
    loading,
  }
}
