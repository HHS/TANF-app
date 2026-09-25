import NextLink from "next/link";

type AdminRootProps = {
  children: React.ReactNode;
};

export function AdminRoot({ children }: AdminRootProps) {
  return (
    <>
      <a className="usa-skipnav" href="#main-content">
        Skip to main content
      </a>
      <main className="admin-login-page" id="main-content">
        <section className="admin-gov-banner" aria-label="Official government website">
          <div className="grid-container-widescreen admin-gov-banner__inner">
            <p>A Demo website of the United States government</p>
            <p>Here&apos;s how you know</p>
          </div>
        </section>

        <header className="usa-header usa-header--extended admin-header">
          <div className="grid-container-widescreen usa-nav__wide desktop:padding-left-4 desktop:border-bottom-0 mobile:border-bottom-1px mobile:padding-left-0 mobile:padding-right-0">
            <div className="usa-logo" id="extended-logo">
              <em className="usa-logo__text">
                <NextLink href="/" aria-label="TANF Data Portal Admin Home">
                  TANF Data Portal Admin
                </NextLink>
              </em>
            </div>
          </div>
        </header>

        {children}
      </main>
    </>
  );
}
