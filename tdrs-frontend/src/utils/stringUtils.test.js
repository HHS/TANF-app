import { toTitleCase } from './stringUtils'

describe('toTitleCase', () => {
  it.each([
    ['test me', 'Test Me'],
    ['tribe', 'Tribe'],
    [' i like peanuts ', ' I Like Peanuts '],
    ['jeffrey wuz 123here', 'Jeffrey Wuz 123here'],
    ['', ''],
    [null, null],
  ])('Capitalizes first char of each word', (original, expected) => {
    expect(toTitleCase(original)).toEqual(expected)
  })
})
