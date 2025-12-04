import { selectUser, accountIsRegionalStaff } from './auth'

export const availableStts = (path) => {
  return (state) =>
    accountIsRegionalStaff(state)
      ? selectUser(state)
          .regions?.map((region) => region.stts)
          .flat()
          .filter((stt) => {
            if (path.includes('fra')) {
              return stt.type !== 'tribe'
            }
            return true
          })
          .sort((a, b) => a.name.localeCompare(b.name))
      : state?.stts?.sttList
}
