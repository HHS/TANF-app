import { programIntegrityAuditLabels } from '../Reports/utils'
import { CaseAggregatesTable } from './components/CaseAggregatesTable'
import { PaginatedHistory } from './components/PaginatedHistory'
import KnowledgeCenterLink from './components/KnowledgeCenterLink'
import { useSubmissionHistory } from '../../hooks/useSubmissionHistory'

const QuarterSubmissionHistory = ({ filterValues, reprocessedState }) => {
  const { files } = useSubmissionHistory({ ...filterValues, quarter: null })

  return (
    <>
      <KnowledgeCenterLink />
      <div>
        {programIntegrityAuditLabels.map((quarterLabel, index) => {
          const quarterCode = `Q${index + 1}`
          const filteredFiles = files.filter((f) => f.quarter === quarterCode)

          return (
            <PaginatedHistory
              key={quarterLabel}
              caption={quarterLabel}
              files={filteredFiles}
              reprocessedState={reprocessedState}
              TableComponent={CaseAggregatesTable}
            />
          )
        })}
      </div>
    </>
  )
}

export default QuarterSubmissionHistory
