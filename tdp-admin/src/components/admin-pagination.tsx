import NextLink from "next/link";

export default function AdminPagination({
  count,
  page,
  pageSize,
  href,
}: {
  count: number;
  page: number;
  pageSize: number;
  href: (page: number) => string;
}) {
  const pages = Math.max(1, Math.ceil(count / pageSize));
  const previousLabel = (
    <>
      <span aria-hidden="true">←</span> Previous
    </>
  );
  const nextLabel = (
    <>
      Next <span aria-hidden="true">→</span>
    </>
  );
  return (
    <nav className="admin-pagination" aria-label="Pagination">
      {page > 1 ? (
        <NextLink
          className="admin-pagination__button"
          href={href(page - 1)}
          prefetch={false}
          rel="prev"
        >
          {previousLabel}
        </NextLink>
      ) : (
        <span className="admin-pagination__button" aria-disabled="true">
          {previousLabel}
        </span>
      )}
      <span className="admin-pagination__current" aria-current="page">
        Page {page} of {pages}
      </span>
      {page < pages ? (
        <NextLink
          className="admin-pagination__button"
          href={href(page + 1)}
          prefetch={false}
          rel="next"
        >
          {nextLabel}
        </NextLink>
      ) : (
        <span className="admin-pagination__button" aria-disabled="true">
          {nextLabel}
        </span>
      )}
    </nav>
  );
}
