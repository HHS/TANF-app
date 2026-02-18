import { selectUser, accountIsRegionalStaff } from './auth'

export const availableStts = (path) => {
  return (state) => {
    const filterTribes = (stts = []) => {
      if (path.includes('fra')) {
        return stts.filter((stt) => stt.type !== 'tribe')
      }
      return stts
    }

    if (accountIsRegionalStaff(state)) {
      const regionalStts =
        selectUser(state)
          .regions?.map((region) => region.stts)
          .flat() || []
      return filterTribes(regionalStts).sort((a, b) =>
        a.name.localeCompare(b.name)
      )
    }

    return filterTribes(state?.stts?.sttList || [])
  }
}
