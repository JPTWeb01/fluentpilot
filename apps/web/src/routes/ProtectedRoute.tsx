import type { PropsWithChildren } from "react";
import { Navigate } from "react-router";

import { useAuthStore } from "@/stores/auth-store";

export function ProtectedRoute({ children }: PropsWithChildren) {
  const accessToken = useAuthStore((s) => s.accessToken);

  if (!accessToken) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
