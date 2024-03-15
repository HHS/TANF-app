const escapeHtml = (unsafe) => {
  return unsafe
    ? unsafe
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;')
    : unsafe
}

export default escapeHtml
