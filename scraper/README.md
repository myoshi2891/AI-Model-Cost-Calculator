# Scraper (Python Backend)

This directory contains the Python-based data extraction engine for the LLM Studies Calculator. It employs Playwright to regularly fetch current pricing data from various AI providers.

## Technical Stack

- **Environment**: Python 3.12+
- **Package Manager**: [uv](https://github.com/astral-sh/uv)
- **Scraping Engine**: Playwright (Headless Chromium) + httpx
- **Validation**: Pydantic v2
- **Testing**: pytest (Basic smoke and import tests implemented)

## Responsibilities

1. **Extraction**: Programmatically visits official pricing pages of providers (like OpenAI, Anthropic, Google) and extracts token or subscription costs using reliable RegEx parsing.
2. **Fallback Logic**: Implements a robust 3-tier fallback strategy (Successful Scrape -> Previous Data in `pricing.json` -> Hardcoded Defaults) to guarantee generation success even if a UI changes.
3. **Currency Conversion**: Fetches the latest USD to JPY exchange rate utilizing the Frankfurter API to enable accurate yen cost display.
4. **Data Contract**: Outputs `pricing.json`. This is synchronized structurally with the TypeScript types present in the `web` directory, enabling strictly typed frontend rendering.

## Directory Structure

- `src/scraper/providers/`: Scripts for programmatic API endpoints (e.g., Anthropic, Azure, DeepSeek).
- `src/scraper/tools/`: Scripts for subscription services (e.g., Cursor, GitHub Copilot).
- `src/scraper/models.py`: Defines the `ApiModel` and `SubTool` schemas which must stay synchronized with `web/src/types/pricing.ts`.

## Setup & Scripts

Make sure you have [uv](https://docs.astral.sh/uv/) installed.

```bash
# Install dependencies and sync virtual environment
uv sync

# Install standard Playwright chromium browser locally
uv run playwright install chromium

# Run the complete scraper pipeline manually
uv run scraper --output ../pricing.json

# Run unit tests and smoke tests
uv run pytest
```
