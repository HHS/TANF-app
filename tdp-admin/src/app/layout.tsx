import type { Metadata } from "next";
import "@uswds/uswds/css/uswds.min.css";
import "./globals.css";
import { AdminRoot } from "@/components/admin-root";

export const metadata: Metadata = {
  title: "TDP Admin",
  description: "Administrative sign-in for the TANF Data Portal.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AdminRoot>{children}</AdminRoot>
      </body>
    </html>
  );
}
