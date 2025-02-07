export const quarters = {
  Q1: 'Quarter 1 (October - December)',
  Q2: 'Quarter 2 (January - March)',
  Q3: 'Quarter 3 (April - June)',
  Q4: 'Quarter 4 (July - September)',
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

export const constructYearOptions = () => {
  const years = []
  const today = new Date(Date.now())

  const fiscalYear =
    today.getMonth() > 8 ? today.getFullYear() + 1 : today.getFullYear()

  for (let i = fiscalYear; i >= 2021; i--) {
    const option = (
      <option key={i} data-testid={i} value={i}>
        {i}
      </option>
    )
    years.push(option)
  }
  return years
}
