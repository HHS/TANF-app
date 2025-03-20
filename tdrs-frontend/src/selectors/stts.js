import { selectUser, accountIsRegionalStaff } from './auth'

export const availableStts = (state) =>
  accountIsRegionalStaff(state)
    ? selectUser(state)
        .regions?.map((region) => region.stts)
        .flat()
        .sort((a, b) => a.name.localeCompare(b.name))
    : state?.stts?.sttList
