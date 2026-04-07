<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

# AGENTS.md - Frontend

**Purpose**: Next.js 14+ App Router frontend

## STRUCTURE
```
frontend/src/
├── app/           # Next.js App Router pages
├── pages/         # Legacy pages (jobs, analytics, auth, etc.)
├── components/    # Reusable components (UI, Common, Layout, Charts)
├── lib/
│   ├── hooks/     # Custom React hooks
│   ├── api/       # API client (axios)
│   ├── utils/     # Utilities
│   └── context/   # React context providers
├── styles/        # Tailwind + theme configs
└── types/         # TypeScript types
```

## CONVENTIONS

- **Framework**: Next.js 16.2.0 (App Router)
- **Styling**: Tailwind CSS + shadcn/ui components
- **State**: Zustand for global state, React Query for server state
- **Forms**: React Hook Form + Zod validation
- **Testing**: Jest + React Testing Library (devDependencies present)

## TESTING

- Jest configured but no test script in package.json
- Run tests manually: `npx jest` in frontend directory

## ANTI-PATTERNS

- NEVER use `@ts-ignore` or `as any`
- NEVER suppress TypeScript errors

## COMMANDS
```bash
cd frontend && npm run dev    # Start dev server
cd frontend && npm run build # Production build
cd frontend && npm run lint   # ESLint
```

## KEY FILES
| Task | Location |
|------|----------|
| Entry | `frontend/src/app/page.tsx` |
| API client | `frontend/src/lib/api/` |
| Auth | `frontend/src/pages/auth/` |
| State | `frontend/src/lib/context/` |
