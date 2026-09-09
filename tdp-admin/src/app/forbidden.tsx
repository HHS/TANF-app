import { GridContainer } from "@trussworks/react-uswds";
import NextLink from "next/link";

export default function ForbiddenPage() {
  return (
    <main className="admin-login-page" id="main-content">
      <section className="admin-success" aria-label="Access denied">
        <GridContainer className="grid-container-widescreen admin-success__shell">
          <div className="admin-success__panel">
            <p className="admin-console__eyebrow">Access denied</p>
            <h1>Admin access required</h1>
            <p className="admin-success__lede">
              Your account is authenticated, but it is not authorized for the
              TANF Data Portal admin console.
            </p>
            <div className="admin-success__actions">
              <NextLink className="usa-button usa-button--outline" href="/logout">
                Sign out
              </NextLink>
            </div>
          </div>
        </GridContainer>
      </section>
    </main>
  );
}
