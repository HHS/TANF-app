import type { SVGProps } from "react";

export type AdminNavIconProps = SVGProps<SVGSVGElement>;

function AdminNavIconBase({ children, ...props }: AdminNavIconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="1.8"
      {...props}
    >
      {children}
    </svg>
  );
}

export function AdminNavAppearanceIcon(props: AdminNavIconProps) {
  return (
    <AdminNavIconBase {...props}>
      <path d="M12 3a9 9 0 1 0 0 18h1.25a1.75 1.75 0 0 0 .4-3.45l-.9-.2a1.3 1.3 0 0 1 .3-2.57H15a6 6 0 0 0 0-12h-3Z" />
      <path d="M7.7 10.4h.1M9.9 7.4h.1M13.2 7.1h.1M16 9.4h.1" />
    </AdminNavIconBase>
  );
}

export function AdminNavApprovalIcon(props: AdminNavIconProps) {
  return (
    <AdminNavIconBase {...props}>
      <path d="M6 4h9l3 3v13H6z" />
      <path d="M14 4v4h4M9 14l2 2 4-5" />
    </AdminNavIconBase>
  );
}

export function AdminNavCollapseIcon(props: AdminNavIconProps) {
  return (
    <AdminNavIconBase {...props}>
      <path d="M4 5h16v14H4zM9 5v14" />
      <path d="m15 9-3 3 3 3" />
    </AdminNavIconBase>
  );
}

export function AdminNavDashboardIcon(props: AdminNavIconProps) {
  return (
    <AdminNavIconBase {...props}>
      <path d="M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z" />
    </AdminNavIconBase>
  );
}

export function AdminNavDataFilesIcon(props: AdminNavIconProps) {
  return (
    <AdminNavIconBase {...props}>
      <path d="M3.5 6.5h6l1.75 2H20.5v9.5a1.5 1.5 0 0 1-1.5 1.5H5a1.5 1.5 0 0 1-1.5-1.5z" />
      <path d="M3.5 8.5V6A1.5 1.5 0 0 1 5 4.5h4.25l1.75 2" />
    </AdminNavIconBase>
  );
}

export function AdminNavEtlIcon(props: AdminNavIconProps) {
  return (
    <AdminNavIconBase {...props}>
      <path d="M4 7h10M10 3l4 4-4 4" />
      <path d="M20 17H10M14 13l-4 4 4 4" />
    </AdminNavIconBase>
  );
}

export function AdminNavFeatureFlagsIcon(props: AdminNavIconProps) {
  return (
    <AdminNavIconBase {...props}>
      <path d="M6 20V4" />
      <path d="M6 5h11l-1.5 3L17 11H6" />
    </AdminNavIconBase>
  );
}

export function AdminNavFeedbackIcon(props: AdminNavIconProps) {
  return (
    <AdminNavIconBase {...props}>
      <path d="M5 5h14v10H9l-4 4z" />
      <path d="M8.5 8.5h7M8.5 11.5h4" />
    </AdminNavIconBase>
  );
}

export function AdminNavHomeIcon(props: AdminNavIconProps) {
  return (
    <AdminNavIconBase {...props}>
      <path d="m3 10.5 9-7 9 7" />
      <path d="M5.5 9.5V20h13V9.5" />
      <path d="M9.5 20v-6h5v6" />
    </AdminNavIconBase>
  );
}

export function AdminNavLogEntriesIcon(props: AdminNavIconProps) {
  return (
    <AdminNavIconBase {...props}>
      <path d="M6 4h9l3 3v13H6z" />
      <path d="M14.5 4v4h3.5M9 12h6M9 15h6M9 18h3" />
    </AdminNavIconBase>
  );
}

export function AdminNavParsersIcon(props: AdminNavIconProps) {
  return (
    <AdminNavIconBase {...props}>
      <path d="M8 5 4 12l4 7M16 5l4 7-4 7" />
      <path d="m13.5 6.5-3 11" />
    </AdminNavIconBase>
  );
}

export function AdminNavPeriodicTasksIcon(props: AdminNavIconProps) {
  return (
    <AdminNavIconBase {...props}>
      <path d="M6 5h12a2 2 0 0 1 2 2v11H4V7a2 2 0 0 1 2-2Z" />
      <path d="M8 3v4M16 3v4M4 10h16M8 15l2 2 4-4" />
    </AdminNavIconBase>
  );
}

export function AdminNavReportsIcon(props: AdminNavIconProps) {
  return (
    <AdminNavIconBase {...props}>
      <path d="M5 20V4h14v16z" />
      <path d="M9 16v-4M12 16V8M15 16v-6" />
    </AdminNavIconBase>
  );
}

export function AdminNavSearchIcon(props: AdminNavIconProps) {
  return (
    <AdminNavIconBase {...props}>
      <path d="M11 18a7 7 0 1 1 0-14 7 7 0 0 1 0 14Z" />
      <path d="m16.5 16.5 3.5 3.5" />
    </AdminNavIconBase>
  );
}

export function AdminNavSearchIndexesIcon(props: AdminNavIconProps) {
  return (
    <AdminNavIconBase {...props}>
      <path d="M5 4h8l4 4v5" />
      <path d="M13 4v5h4M7.5 12h4" />
      <path d="M13.5 17.5a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0Z" />
      <path d="m19.5 20.5 1.5 1.5" />
    </AdminNavIconBase>
  );
}

export function AdminNavSecurityIcon(props: AdminNavIconProps) {
  return (
    <AdminNavIconBase {...props}>
      <path d="M12 3 5 6v5c0 4.25 2.75 7.5 7 10 4.25-2.5 7-5.75 7-10V6z" />
      <path d="m9 12 2 2 4-5" />
    </AdminNavIconBase>
  );
}

export function AdminNavSttsIcon(props: AdminNavIconProps) {
  return (
    <AdminNavIconBase {...props}>
      <circle cx="6.5" cy="7" r="2.5" />
      <circle cx="17.5" cy="7" r="2.5" />
      <circle cx="12" cy="17" r="2.5" />
      <path d="m8 9 2.75 5M16 9l-2.75 5M9 17h-1" />
    </AdminNavIconBase>
  );
}

export function AdminNavUsersIcon(props: AdminNavIconProps) {
  return (
    <AdminNavIconBase {...props}>
      <path d="M8.5 11a3.25 3.25 0 1 0 0-6.5 3.25 3.25 0 0 0 0 6.5Z" />
      <path d="M3.5 20a5 5 0 0 1 10 0" />
      <path d="M16 10.5a2.75 2.75 0 1 0 0-5.5" />
      <path d="M16 14.5a4 4 0 0 1 4 4" />
    </AdminNavIconBase>
  );
}
