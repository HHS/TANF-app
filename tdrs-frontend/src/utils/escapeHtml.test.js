import escapeHtml from './escapeHtml'

describe('escapeHtml', () => {
  it.each([
    ['>', '&gt;'],
    ['<', '&lt;'],
    ['"', '&quot;'],
    ["'", '&#039;'],
    [
      '<img src="" onload=alert("hello")/>',
      '&lt;img src=&quot;&quot; onload=alert(&quot;hello&quot;)/&gt;',
    ],
    ['', ''],
    [null, null],
  ])('Replaces HTML special chars and returns string', (original, expected) => {
    expect(escapeHtml(original)).toEqual(expected)
  })
})
