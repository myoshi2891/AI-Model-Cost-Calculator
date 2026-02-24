# Web (React Frontend)

This directory contains the React 19 frontend for the AI Model Pricing Calculator. It is designed to be built into a **single, portable HTML file** (`index.html`) using Vite and `vite-plugin-singlefile`.

## Technical Stack

- **Framework**: React 19 + TypeScript
- **Build Tool**: Vite 7 + Bun
- **Styling**: Tailwind CSS
- **Test Runner**: Vitest + `@testing-library/react` (Basic smoke testing implemented)

## Key Features

- **Single-File Output**: All CSS, JS, and data are inlined into a single HTML file during the build process (`assetsInlineLimit: 100_000_000`). This ensures maximum portability and no reliance on external assets.
- **Dynamic Pricing Data**: Evaluates and displays data fetched statically from `src/data/pricing.json`. This JSON is automatically copied over by the Python scraper process.
- **Common Header Integration**: The built application automatically resolves and injects `common-header.js` and `common-header.css` from the project root. This ensures that the primary calculator and statical specification files (like `claude_spec.html`) share identical and consistent responsive navigation.
- **Bilingual Interface**: Full support for English and Japanese text using a lightweight custom hook based on `src/i18n.ts`.

## Setup & Scripts

Make sure you have [Bun](https://bun.sh/) installed.

```bash
# Install dependencies
bun install

# Start development server
bun run dev

# Run unit tests and smoke tests
bun test

# Build for production (outputs to ../index.html via the root update.sh script)
bun run build

# Run ESLint validation
bun run lint
```
