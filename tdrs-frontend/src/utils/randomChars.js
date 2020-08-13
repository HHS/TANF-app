/**
 * Random bytes used for Nonce and State
 *  Source:
 *   https://gist.github.com/darrenmothersele/7cd24da0f35d450babd4745c7f208acf
 *  Description:
 *   https://medium.com/@dazcyril/generating-cryptographic-random-state-in-javascript-in-the-browser-c538b3daae50
 */
const randomChars = (length = 40) => {
  const validChars =
    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let array = new Uint8Array(length)
  window.crypto.getRandomValues(array)
  array = array.map((x) => validChars.charCodeAt(x % validChars.length))
  return String.fromCharCode.apply(null, array)
}

export default randomChars
