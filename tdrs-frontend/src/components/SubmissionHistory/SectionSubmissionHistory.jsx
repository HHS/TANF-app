import { fileUploadSections } from '../../reducers/reports'
import { CaseAggregatesTable } from './components/CaseAggregatesTable'
import { TotalAggregatesTable } from './components/TotalAggregatesTable'
import { PaginatedHistory } from './components/PaginatedHistory'
import KnowledgeCenterLink from './components/KnowledgeCenterLink'
import { useSubmissionHistory } from '../../hooks/useSubmissionHistory'

const SectionSubmissionHistory = ({ filterValues, reprocessedState }) => {
  const { files, loading } = useSubmissionHistory(filterValues)
  const num_sections = filterValues.stt.num_sections

  return (
    <>
      <KnowledgeCenterLink />
      <div>
        {fileUploadSections.slice(0, num_sections).map((section, index) => {
          const sectionNumber = index + 1
          const TableComponent =
            sectionNumber === 1 || sectionNumber === 2
              ? CaseAggregatesTable
              : TotalAggregatesTable

          return (
            <PaginatedHistory
              key={section}
              caption={`Section ${sectionNumber} - ${section}`}
              files={files.filter((f) => f.section.includes(section))}
              loading={loading}
              reprocessedState={reprocessedState}
              TableComponent={TableComponent}
            />
          )
        })}
      </div>
    </>
  )
}

export default SectionSubmissionHistory
