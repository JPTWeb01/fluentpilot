import { AppShell } from "@/components/layout/AppShell";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useMe } from "@/features/auth/api";
import { useAuthStore } from "@/stores/auth-store";

export function DashboardPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const { data: user, isLoading } = useMe(!!accessToken);

  return (
    <AppShell>
      <Card>
        <CardHeader>
          <CardTitle>Welcome{user?.full_name ? `, ${user.full_name}` : ""}</CardTitle>
          <CardDescription>
            {isLoading ? "Loading your profile..." : `Signed in as ${user?.email}`}
          </CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          Practice sessions aren't available yet — the voice coach is coming in a later phase.
        </CardContent>
      </Card>
    </AppShell>
  );
}
