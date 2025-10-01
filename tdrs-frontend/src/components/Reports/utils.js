export const quarters = {
  Q1: 'Quarter 1 (October - December)',
  Q2: 'Quarter 2 (January - March)',
  Q3: 'Quarter 3 (April - June)',
  Q4: 'Quarter 4 (July - September)',
}

// Array of quarter labels for Program Integrity Audit file inputs
export const programIntegrityAuditLabels = [
  'Quarter 1 (October - December)',
  'Quarter 2 (January - March)',
  'Quarter 3 (April - June)',
  'Quarter 4 (July - September)',
]

export const PROGRAM_INTEGRITY_SECTION = 'Program Audit'

// Helper to map quarter index (0-3) to quarter code (Q1-Q4)
export const getQuarterFromIndex = (index) => {
  const quarterMap = ['Q1', 'Q2', 'Q3', 'Q4']
  return quarterMap[index] || 'Q1'
}

export const constructYears = () => {
  const years = []
  const today = new Date(Date.now())

  const fiscalYear =
    today.getMonth() > 8 ? today.getFullYear() + 1 : today.getFullYear()

  for (let i = fiscalYear; i >= 2021; i--) {
    years.push(i)
  }

  return years
}

export const constructYearOptions = (startYear = 2021) => {
  const years = []
  const today = new Date(Date.now())

  const fiscalYear =
    today.getMonth() > 8 ? today.getFullYear() + 1 : today.getFullYear()

  for (let i = fiscalYear; i >= startYear; i--) {
    const option = (
      <option key={i} data-testid={i} value={i}>
        {i}
      </option>
    )
    years.push(option)
  }
  return years
}
