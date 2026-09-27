# HyperPlay Frontend

Svelte 5 + Vite. The upload flow posts the chapter to `POST /api/v1/labs/generate` and renders the returned level with `RelationshipLab`.

Run locally, with the backend on `http://127.0.0.1:8000` (Vite proxies `/api` to it):

```bash
npm install
npm run dev
```

Validate and build:

```bash
npm run check
npm run build
```

## Layout

- `src/App.svelte`: navigation, landing sections, profile, upload, and the lab and "doesn't fit" screens.
- `src/lib/generate.ts`: the upload request. It maps every response to a file error, a "doesn't fit" result, or a level labelled generated, saved copy, or sample.
- `src/lib/components/RelationshipLab.svelte`: the staged game. It covers locked sliders, hints, debriefs, Next challenge, the completion panel, and the attempt history. Clearing a stage stays sticky, so students can look for a second route.
- `src/lib/games/lab/`: the engine. `types.ts` is the contract, `evaluate.ts` holds the formula evaluator and winnability validator, `render.ts` draws the four canvas modes, and `levels.ts` holds four verified fallback levels (Physics, Chemistry, Biology, Mathematics).
- `src/lib/games/routing.ts` and `lab/fewshot.ts`: the Azure prompt. `npm run export:contracts` copies it into the backend.
- `src/lib/ProjectileChallenge.svelte` and `ExampleCarousel.svelte`: the landing-page demo, unchanged.
- `public/samples/`: three sample chapters for the "Try a sample" buttons. `scripts/regenerate-samples.py` rebuilds them.

The built site lives in `dist/` after `npm run build`.

UI revision: the launcher previews the selected angle before `Run experiment`. The rule and variable meanings are visible with the question. The calculated trajectory and measurements remain hidden until a run. Prior shots remain visible in an integrated attempt sidebar. Each carousel example animates during its seven-second interval; Pause freezes both movement and progress. The first profile step has a Back to home action.
