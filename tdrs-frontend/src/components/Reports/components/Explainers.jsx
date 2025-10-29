export const FiscalQuarterExplainer = () => (
  <table className="usa-table usa-table--striped margin-top-4 desktop:width-tablet mobile:width-full">
    <caption>TANF/SSP Data Reporting Guidelines</caption>
    <thead>
      <tr>
        <th>Fiscal Year (FY) &amp; Quarter (Q)</th>
        <th>Calendar Period</th>
        <th>Due Date</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>FY Q1</td>
        <td>Oct 1 - Dec 31</td>
        <td>February 14</td>
      </tr>
      <tr>
        <td>FY Q2</td>
        <td>Jan 1 - Mar 31</td>
        <td>May 15</td>
      </tr>
      <tr>
        <td>FY Q3</td>
        <td>Apr 1 - Jun 30</td>
        <td>August 14</td>
      </tr>
      <tr>
        <td>FY Q4</td>
        <td>Jul 1 - Sep 30</td>
        <td>November 14</td>
      </tr>
    </tbody>
  </table>
)

export const ProgramIntegrityAuditExplainer = () => {
  const currentYear = new Date().getFullYear()
  return (
    <>
      <div className="mobile:grid-container mobile:margin-top-4 mobile:padding-0 desktop:padding-0 desktop:grid-col-fill">
        <div className="usa-alert usa-alert--slim usa-alert--info">
          <div className="usa-alert__body" role="alert">
            <p className="usa-alert__text">
              For Additional guidance please refer to the Program Instruction
              for this new reporting requirement.
            </p>
          </div>
        </div>
      </div>
      <table className="usa-table usa-table--striped">
        <caption>Audit Reporting Guidelines</caption>
        <thead>
          <tr>
            <th>Fiscal Year (FY)</th>
            <th>Due Date</th>
          </tr>
        </thead>
        <tbody>
          {Array.from({ length: currentYear - 2024 }).map((_, index) => (
            <tr key={index}>
              <td>FY {currentYear - (index + 1)}</td>
              <td>November 14, {currentYear - index}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  )
}
