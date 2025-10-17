import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { getAvailableFileList } from '../actions/reports'

/**
 * Custom hook that encapsulates shared submission history logic
 * Used by both QuarterSubmissionHistory and SectionSubmissionHistory
 *
 * @param {Object} filterValues - Filter values for fetching files
 * @returns {Object} Files and fetch state
 */
export const useSubmissionHistory = (filterValues) => {
  const dispatch = useDispatch()
  const [hasFetchedFiles, setHasFetchedFiles] = useState(false)
  const { files } = useSelector((state) => state.reports)

  useEffect(() => {
    if (!hasFetchedFiles) {
      dispatch(getAvailableFileList(filterValues))
      setHasFetchedFiles(true)
    }
  }, [hasFetchedFiles, files, dispatch, filterValues])

  return {
    files,
    hasFetchedFiles,
  }
}
