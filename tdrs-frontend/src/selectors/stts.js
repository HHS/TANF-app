import { selectUser, accountIsRegionalStaff } from './auth'

export const availableStts = (state) =>
  accountIsRegionalStaff(state)
    ? selectUser(state)
        .regions?.map((region) => region.stts)
        .flat()
    : state?.stts?.sttList
