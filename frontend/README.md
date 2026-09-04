# Bhumi Praman — Frontend

React + TypeScript + Vite + Tailwind CSS v4. See the root `README.md` for full setup instructions.

Quick start (backend must already be running on :8000):
```
npm install
npm run dev
```
Opens on http://localhost:5173 — `/api/*` is proxied to the backend automatically (see `vite.config.ts`).

## Structure
- `src/pages/` — one component per route
- `src/components/` — shared UI (Sidebar, FieldCard, DocumentCanvas, badges)
- `src/services/api.ts` — typed API client (axios)
- `src/hooks/useAuth.tsx` — auth context
- `src/types/index.ts` — types mirroring the backend's Pydantic schemas
- `src/index.css` — design tokens (`@theme` block) lifted from the chosen UI design

`npm run build` runs the TypeScript compiler and production build.
