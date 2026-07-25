import { render, screen } from "@testing-library/react";
import { createMemoryRouter, RouterProvider } from "react-router";
import { beforeEach, describe, expect, it } from "vitest";

import { useAuthStore } from "@/stores/auth-store";

import { ProtectedRoute } from "./ProtectedRoute";

function renderProtected() {
  const router = createMemoryRouter(
    [
      { path: "/", element: <ProtectedRoute>Secret content</ProtectedRoute> },
      { path: "/login", element: <>Login page</> },
    ],
    { initialEntries: ["/"] },
  );
  return render(<RouterProvider router={router} />);
}

describe("ProtectedRoute", () => {
  beforeEach(() => {
    useAuthStore.setState({ accessToken: null, refreshToken: null });
  });

  it("redirects to /login when there is no access token", async () => {
    renderProtected();

    expect(await screen.findByText("Login page")).toBeInTheDocument();
  });

  it("renders its children when an access token is present", async () => {
    useAuthStore.getState().setSession("token-1", "refresh-1");

    renderProtected();

    expect(await screen.findByText("Secret content")).toBeInTheDocument();
  });
});
