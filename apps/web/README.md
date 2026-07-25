# apps/web

React + TypeScript + Vite web client.

## Local development

```bash
cd apps/web
npm install
copy .env.example .env
npm run dev
```

Requires the API running at the URL in `.env` (`VITE_API_URL`, defaults to
`http://localhost:8000/api/v1` — see `apps/api/README` for how to start it).

## Layout

```
src/
├── lib/           # api-client (fetch + 401 refresh-retry), cn() utility
├── stores/        # zustand: auth-store (tokens, current user)
├── features/auth/ # types, TanStack Query hooks, Login/Register pages
├── components/ui/ # shadcn-style primitives (Button, Input, Label, Card)
├── routes/        # router config, ProtectedRoute
└── pages/         # top-level routed pages (DashboardPage)
```

**Auth**: access + refresh tokens are held in a Zustand store persisted to
localStorage. The API client attaches `Authorization: Bearer <token>` and, on a
401, does one silent refresh-and-retry before forcing logout. This is a
pragmatic choice for a personal project — moving refresh tokens to an httpOnly
cookie is a backend change to revisit before any multi-tenant SaaS exposure.
