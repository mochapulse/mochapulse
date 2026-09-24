# mochapulse — portfolio

A bilingual (EN/ES), responsive portfolio site for the **mochapulse** GitHub
account: self-hosted infrastructure, embedded firmware, and local AI projects.

Built with Vite + React + TypeScript, Tailwind CSS v4, and shadcn-style UI
components. Content is data-driven from `src/data/` and `src/i18n/locales/`.

## Develop

```sh
pnpm install
pnpm dev
```

## Build

```sh
pnpm build      # tsc -b && vite build  ->  dist/
pnpm preview
```

`vite.config.ts` sets `base: '/mochapulse/'` for a project-page deploy at
`https://mochapulse.github.io/mochapulse/`. Change it if you host elsewhere.

## Where things live

- `src/data/cv-data.ts` — identity, education, experience, skills.
- `src/data/projects-data.ts` — the project cards (mochapulse repos).
- `src/i18n/locales/{en,es}.json` — all UI copy in both languages.
- `src/components/sections/` — Hero, About, Experience, Projects, Skills, Contact.
