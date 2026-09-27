// Exports the Relationship Lab prompt and verified levels for the backend and
// contracts/ so the Python service and the front end cannot drift apart.
//
//   cd frontend && npm run export:contracts
//
// Re-run after editing routing.ts, fewshot.ts, or levels.ts.

import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { LAB_SYSTEM_PROMPT, DIFFICULTY_GUIDE } from '../src/lib/games/routing';
import { fallbackLevels } from '../src/lib/games/lab/levels';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '../..');

function write(path: string, content: string) {
	const full = resolve(root, path);
	mkdirSync(dirname(full), { recursive: true });
	writeFileSync(full, content, 'utf-8');
	console.log(path);
}

const header = 'GENERATED from frontend/src/lib/games. Do not edit; run `npm run export:contracts`.';

write('backend/app/prompts/lab_system_prompt.txt', LAB_SYSTEM_PROMPT.trim() + '\n');
write(
	'backend/app/prompts/lab_difficulty_guide.json',
	JSON.stringify({ _generated: header, ...DIFFICULTY_GUIDE }, null, 2) + '\n'
);

for (const [subject, level] of Object.entries(fallbackLevels)) {
	const slug = subject.toLowerCase().replace(/[^a-z]+/g, '-');
	write(`contracts/examples/labs/${slug}.json`, JSON.stringify(level, null, 2) + '\n');
}
