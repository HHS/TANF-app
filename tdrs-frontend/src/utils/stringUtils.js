export const toTitleCase = (str) =>
  str &&
  str.replace(
    /\w\S*/g,
    (txt) => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
  )

export const objectToUrlParams = (obj) => {
  const arr = []
  Object.keys(obj).forEach((key) => {
    arr.push(`${key}=${obj[key]}`)
  })
  return `${arr.join('&')}`
}
