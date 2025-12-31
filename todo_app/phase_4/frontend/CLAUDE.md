# Frontend Guidelines

## Build & Run
- Package Manager: `npm`
- Run Dev Server: `npm run dev`
- Build: `npm run build`
- Lint: `npm run lint`

## Architecture
- Framework: Next.js 16+ (App Router)
- Language: TypeScript
- Styling: Tailwind CSS v4
- Components: Shadcn/UI
- Auth: Better Auth
- HTTP Client: Axios

## Directory Structure
```
src/
├── app/              # Next.js App Router pages
│   ├── layout.tsx    # Root layout with providers
│   ├── page.tsx      # Home page
│   ├── login/        # Login page
│   ├── register/     # Registration page
│   └── dashboard/    # Protected dashboard
├── components/       # Reusable UI components
│   └── ui/           # Shadcn/UI components
└── lib/              # Utilities and services
    ├── api.ts        # Axios API client
    ├── auth.ts       # Better Auth server config
    ├── auth-client.ts # Better Auth client
    ├── auth-provider.tsx # React auth context
    ├── types.ts      # TypeScript interfaces
    └── utils.ts      # Utility functions
```

## Code Style
- Use TypeScript strictly
- Prefer Server Components where possible
- Use 'use client' only when needed
- Follow Shadcn/UI patterns for components
