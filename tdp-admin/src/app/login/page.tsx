import AdminLoginPage from "@/components/admin-login-page";
import {
  getAdminLoginErrorMessage,
  type AdminLoginSearchParams,
} from "@/lib/admin-login-errors";

type LoginPageProps = {
  searchParams?: Promise<AdminLoginSearchParams>;
};

export default async function LoginPage({ searchParams }: LoginPageProps) {
  const resolvedSearchParams = searchParams ? await searchParams : undefined;

  return (
    <AdminLoginPage
      loginErrorMessage={getAdminLoginErrorMessage(resolvedSearchParams)}
    />
  );
}
