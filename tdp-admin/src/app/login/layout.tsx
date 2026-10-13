import type { ReactNode } from "react";
import { AdminRoot } from "@/components/admin-root";

export default function LoginLayout({ children }: { children: ReactNode }) {
  return <AdminRoot>{children}</AdminRoot>;
}
