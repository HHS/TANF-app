"use client";

import NextLink from "next/link";

export default function UsersError({ reset }: { reset: () => void }) {
  return (
    <div className="admin-loading" role="alert">
      <h1>Could not load user accounts</h1>
      <p>Please try again.</p>
      <button className="usa-button" onClick={reset}>
        Try again
      </button>
      <p>
        <NextLink href="/users">Return to user accounts</NextLink>
      </p>
    </div>
  );
}
