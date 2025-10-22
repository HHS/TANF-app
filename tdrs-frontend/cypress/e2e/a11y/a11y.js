describe('Accessibility checks', () => {
  beforeEach(() => {
    cy.visit('/home')
    cy.injectAxe() // ✅ Inject axe-core
  })

  // Define at the top of the spec file or just import it
  function terminalLog(violations) {
    cy.task(
      'log',
      `${violations.length} accessibility violation${
        violations.length === 1 ? '' : 's'
      } ${violations.length === 1 ? 'was' : 'were'} detected`
    )
    // pluck specific keys to keep the table readable
    const violationData = violations.map(
      ({ id, impact, description, nodes }) => ({
        id,
        impact,
        description,
        nodes: nodes.length
      })
    )

    cy.task('table', violationData)
  }

  // TODO: Enable this test after fixing the a11y issues
  //it('Has no detectable a11y violations on load', () => {
  //cy.checkA11y(null, null, terminalLog); // ✅ Run axe check
  //})
})