import NextLink from "next/link";

export default function AdminDataLoadError({
  title,
  message,
  href,
  action = "Try again",
}: {
  title: string;
  message: string;
  href: string;
  action?: string;
}) {
  return (
    <div className="usa-alert usa-alert--warning" role="status">
      <div className="usa-alert__body">
        <h2 className="usa-alert__heading">{title}</h2>
        <p>{message}</p>
        <NextLink href={href} prefetch={false}>
          {action}
        </NextLink>
      </div>
    </div>
  );
}
