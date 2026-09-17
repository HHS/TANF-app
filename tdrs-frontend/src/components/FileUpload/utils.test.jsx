import { handlePreview } from './utils'

describe('handlePreview', () => {
  const targetClassName = '.usa-file-input__target input#active_case_data'

  beforeEach(() => {
    document.body.innerHTML = `
      <div class="usa-file-input__target">
        <input id="active_case_data" />
        <span class="usa-file-input__instructions">Choose a file</span>
        <div class="usa-file-input__preview">
          <img class="usa-file-input__preview-image is-loading" alt="" />
        </div>
      </div>
    `
  })

  it('leaves a USWDS preview in place while its FileReader is loading', () => {
    expect(handlePreview('report.txt', targetClassName)).toBe(false)
    expect(
      document.querySelector('.usa-file-input__preview-image.is-loading')
    ).not.toBeNull()
  })
})
