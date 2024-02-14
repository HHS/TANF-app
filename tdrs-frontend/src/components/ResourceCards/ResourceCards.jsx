import Button from '../Button'

function Card({ title, body, buttonId, link, linkText }) {
  return (
    <div className="usa-card__container">
      <header className="usa-card__header">
        <h3 className="usa-card__heading"> {title} </h3>
      </header>
      <div className="usa-card__body">
        <p>{body}</p>
      </div>
      <div className="usa-card__footer">
        <Button type="button" class="usa-button" id={buttonId} href={link}>
          {linkText}
        </Button>
      </div>
    </div>
  )
}

function ResourceCards() {
  return (
    <section className="padding-top-4 usa-section">
      <div className="grid-row">
        <div className="mobile:grid-container desktop:padding-0 desktop:grid-col-3">
          <h2 className="resources-header font-heading-2xl margin-top-0 margin-bottom-0">
            Featured TANF Resources
          </h2>
          <div>
            <p>Questions about TANF data?</p>
            <p>
              Email:{' '}
              <a className="usa-link" href="mailto: tanfdata@acf.hhs.gov">
                tanfdata@acf.hhs.gov
              </a>
            </p>
          </div>
        </div>
        <div className="desktop:grid-col-9">
          <ul className="grid-row usa-card-group mobile:margin-0">
            <li className="usa-card--header-first padding-bottom-4 desktop:padding-right-2 desktop:grid-col-6 mobile:grid-col-12">
              <Card
                buttonId="viewKnowledgeCenterButton"
                title="TDP Knowledge Center"
                body="The knowledge center contains resources on all things TDP from account creation to data submission."
                link="http://tdp-project-updates.app.cloud.gov/knowledge-center/"
                linkText="View Knowledge Center"
              />
            </li>
            <li className="usa-card--header-first padding-bottom-4 desktop:grid-col-6 mobile:grid-col-12">
              <Card
                buttonId="viewLayoutsButton"
                title="Transmission File Layouts & Edits"
                body="All transmission file layouts and edits (i.e. error codes) for TANF and SSP-MOE data reporting."
                link="https://www.acf.hhs.gov/ofa/policy-guidance/final-tanf-ssp-moe-data-reporting-system-transmission-files-layouts-and-edits"
                linkText="View Layouts & Edits"
              />
            </li>
            <li className="usa-card--header-first desktop:padding-right-2 desktop:padding-bottom-0 desktop:grid-col-6 mobile:grid-col-12 mobile:padding-bottom-4">
              <Card
                buttonId="viewTribalCodingInstructions"
                title="Tribal TANF Data Coding Instructions"
                body="File coding instructions addressing each data point that Tribal TANF grantees are required to report upon."
                link="https://www.acf.hhs.gov/ofa/policy-guidance/tribal-tanf-data-coding-instructions"
                linkText="View Tribal TANF Coding Instructions"
              />
            </li>
            <li className="usa-card--header-first desktop:grid-col-6 mobile:grid-col-12">
              <Card
                buttonId="viewACFFormInstructions"
                title="ACF-199 and ACF-209 Instructions"
                body="Instructions and definitions for completion of forms ACF-199 (TANF Data Report) and ACF-209 (SSP-MOE Data Report)."
                link="https://www.acf.hhs.gov/ofa/policy-guidance/acf-ofa-pi-23-04"
                linkText="View ACF Form Instructions"
              />
            </li>
          </ul>
        </div>
      </div>
    </section>
  )
}

export default ResourceCards
