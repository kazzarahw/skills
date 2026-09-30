# Search strategy

Use whatever websearch and webfetch tools the agent has. Verify which tools exist before promising coverage, because tool names and quotas drift.

## Per sub-question loop

1. Run 2-3 keyword variations: synonyms and spelling variants, phrase quotes for exact concepts, `site:` and `filetype:` to force diversity (official, academic, press, data).
2. Mix general and news-focused queries; add angle terms like criticism, limitations, or alternative when results skew positive.
3. Triage hits fast, then deep-read only keepers in full. Snippets never count as sources.
4. Mine one good source's references to snowball to more; track executed queries and visited URLs to avoid re-searching ground.

## Fallbacks

- If search returns nothing, retry with simpler phrasing, then fetch known doc URLs directly (for example `<product>.ai/docs/<topic>`).
- If a page is JS-heavy or truncated, try its data endpoint (JSON, CSV, repo mirror) or a narrower in-page query instead of citing the snippet.
- If paywalled, pivot to public summaries, docs, or data rather than citing the teaser.

## Log template (keep running, not reconstructed)

| Query | Top hits | Fetched in full? | Confidence |
|---|---|---|---|
| ... | ... | yes / snippet-only | high / medium / low |
