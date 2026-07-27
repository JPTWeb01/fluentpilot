import { useMe } from "@fluentpilot/shared";
import { Link } from "react-router";

import { AppShell } from "@/components/layout/AppShell";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
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
        <CardContent className="flex items-center justify-between text-sm text-muted-foreground">
          Ready to practice speaking English out loud?
          <div className="flex gap-2">
            <Link
              to="/practice"
              className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:opacity-90"
            >
              Start practicing
            </Link>
            <Link
              to="/interview"
              className="inline-flex h-10 items-center justify-center rounded-md border border-input bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground"
            >
              Try a mock interview
            </Link>
          </div>
        </CardContent>
      </Card>
    </AppShell>
  );
}
