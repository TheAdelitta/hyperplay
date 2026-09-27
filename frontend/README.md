# HyperPlay Frontend

This frontend is a standalone, browser-only learning flow. It is ready to run and review while the API integration is in progress. It does not currently request `GET /api/v1/simulations/demo` or `POST /api/v1/simulations/generate`.

Run locally:

```bash
npm install
npm run dev
```

Validate and build:

```bash
npm run check
npm run build
```

The app uses Svelte components in `src/lib/`:

- `ExampleCarousel.svelte`: three examples, manual arrows, pause, and seven-second rotation. Only projectile motion is labeled playable; the other two are concept previews.
- `ProjectileChallenge.svelte`: visible launch direction while adjusting the angle, the range rule beside the question, target at 50 m, animated run, persistent trajectories and attempt trail, hit/miss feedback, and a contextual reasoning hint.
- `App.svelte`: navigation, landing sections, profile, and browser-local file selection.

`src/app.css` contains the shared visual system. The provided logo reference is optimized as `public/assets/reference.webp`.

The upload flow currently selects and validates a local file; it does not upload or process it. Connect it to the team's backend only after agreeing on the request/response contract. The physics sample is deterministic client-side UI and remains available if that service is unavailable. The simulation assumes constant gravity, no air resistance, and equal launch and landing heights. The target counts as hit within 1 m.

## Integration decisions for the team

- The root README still describes a React frontend, but this UI is Svelte. Update the root architecture and team boundary language once the team confirms Svelte as the chosen frontend.
- `../contracts/examples/projectile-motion.json` uses the generic `relationship_lab` template and a 35–45 m target. This UI is a dedicated projectile challenge with a 50 m target and its own physics. Decide whether to adapt the UI to the generic `SimulationSpec` or add a reviewed projectile template to the contract. Do not claim uploaded lessons are rendered from the spec before this is implemented.
- The current backend accepts a text field or a PDF file, with a default 10 MB upload limit. This UI selector also allows slides, Word files, and text files up to 50 MB. Align the accepted formats and limit with the deployed API before enabling upload.
- With backend running at `http://127.0.0.1:8000`, CORS already allows Vite's default `http://localhost:5173`. If the frontend is served on another origin, update `FRONTEND_ORIGINS` in backend configuration.

The built site lives in `dist/` after `npm run build`. This prototype is separate from the team's GitHub repository, so copy the `src/`, `public/`, `index.html`, `package.json`, `package-lock.json`, `vite.config.js`, and `jsconfig.json` files into the team's Svelte app or port these two components.

UI revision: the launcher previews the selected angle before `Run experiment`. The rule and variable meanings are visible with the question. The calculated trajectory and measurements remain hidden until a run. Prior shots remain visible in an integrated attempt sidebar. Each carousel example animates during its seven-second interval; Pause freezes both movement and progress. The first profile step has a Back to home action.
