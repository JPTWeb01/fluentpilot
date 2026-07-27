# apps/mobile

Expo + React Native mobile client, sharing API/auth/coach-check logic with `apps/web` via
`@fluentpilot/shared`.

- **Routing**: [Expo Router](https://docs.expo.dev/router/introduction/) (file-based, see `app/`)
- **Styling**: [NativeWind](https://www.nativewind.dev/) (Tailwind classes on RN components)
- **Auth persistence**: `expo-secure-store`, wired into `@fluentpilot/shared`'s `createAuthStore`

## Setup

```bash
cp .env.example .env.local
npm install   # from repo root
npm run start --workspace=apps/mobile
```

## Scripts

- `npm run start --workspace=apps/mobile` — start the Expo dev server
- `npm run lint --workspace=apps/mobile` — ESLint (`eslint-config-expo`)
- `npx tsc --noEmit -p apps/mobile` — typecheck
