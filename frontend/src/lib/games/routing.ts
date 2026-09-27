// src/lib/games/routing.ts
//
// The subject dropdown on the upload screen already tells you which engine to
// use. Do not make the model choose. This removes a whole class of failure and
// costs one lookup.

import { FEWSHOT_EXAMPLES, UNFITTABLE_CLAUSE } from './lab/fewshot';

export type EngineId = 'lab' | 'debug' | 'sequence';

export const SUBJECT_TO_ENGINE: Record<string, EngineId> = {
	Physics: 'lab',
	Chemistry: 'lab',
	Mathematics: 'lab',
	Economics: 'lab',
	Biology: 'lab', // logistic growth is a relationship; swap to 'sequence' for pathways
	'Computer Science': 'debug',
	History: 'sequence'
};

export function engineFor(subject: string): EngineId {
	return SUBJECT_TO_ENGINE[subject] ?? 'lab';
}

/** Difficulty shaping passed into the prompt. Makes the profile screen mean something. */
export const DIFFICULTY_GUIDE: Record<'middle' | 'high' | 'college', string> = {
	middle:
		'Use whole numbers wherever possible. Keep slider ranges wide and the target tolerance generous, about 8 percent of the reachable span. Write all three hints in plain language and avoid symbols in the hint text.',
	high: 'Use one decimal place at most. Set the target tolerance to about 4 percent of the reachable span. Hints may reference the formula by name.',
	college:
		'Use the notation and units the chapter uses. Set the target tolerance to about 2 percent of the reachable span. Hints should point at the concept rather than the arithmetic.'
};

// ---------------------------------------------------------------------------
// The system prompt for the Relationship Lab engine.
// ---------------------------------------------------------------------------

const LAB_SCHEMA_PROMPT = `You convert a passage from an educational text into an ordered sequence of interactive challenges. You do not write code. You return one JSON object and nothing else. No prose, no markdown fences.

Read the passage and find the central quantitative relationship it teaches. Identify the two quantities a student would most usefully be able to change, and the single quantity that results from them. Then design a short sequence of challenges that walks the student through the concept.

Choose one visualMode:
- "curve" when the relationship unfolds over time, such as population growth, radioactive decay, or cooling. Requires a series object whose "variable" is NOT one of the two control keys. If time itself is one of the sliders, use "meter" instead.
- "fill" when the output is a physical amount contained in something, such as gas volume, tank level, or concentration.
- "meter" when the output is an accumulating total, such as money, distance covered, or mass produced.
- "trajectory" only for projectile motion through space. The two controls must be the launch angle in degrees (unit "°") and the launch speed in m/s, with gravity as the constant "g".

Return exactly this shape:

{
  "gameType": "lab",
  "visualMode": "curve" | "fill" | "meter" | "trajectory",
  "concept": string,
  "sourceSummary": string,
  "formula": string,
  "expression": string,
  "controls": [ControlA, ControlB],
  "constants": { "name": number },
  "output": { "label": string, "unit": string, "decimals": number, "min": number, "max": number },
  "stages": [Stage, ...],
  "series": { "variable": string, "label": string, "unit": string, "min": number, "max": number, "steps": 120, "expression": string, "markAt": number } | null,
  "readouts": [ { "label": string, "expression": string, "unit": string, "decimals": number } ],
  "completion": string,
  "difficulty": "middle" | "high" | "college",
  "subject": string,
  "courseLabel": string
}

Each control is:
{ "key": short symbol, "label": string, "unit": string, "min": number, "max": number, "step": number, "default": number, "decimals": number }

Each stage is:
{
  "challenge": string,
  "teaches": string,
  "target": { "value": number, "tolerance": number },
  "lock": { "key": string, "value": number, "note": string } | null,
  "hints": [string, string, string],
  "debriefing": string
}

THE STAGE LADDER. This is the most important part of your job.

Return three stages unless the chapter genuinely needs two or four. Never more than four. They are worked in order, because a student cannot jump between concepts they have not met yet. Build them like this:

- Stage 1 locks one control with "lock", so only the other can move. The student sees a single relationship on its own.
- Stage 2 locks the other control, so the second relationship is visible on its own.
- Stage 3 has "lock": null. Both move. Choose a target reachable by several different pairs, so the student discovers the trade off.

Write "teaches" as one short line naming what that stage isolates. Write "debriefing" to explain what just happened in the student's own experience, not to restate the formula. The final "completion" text says what the whole sequence taught.

Rules you must follow:

1. There are exactly two controls. Never more, never fewer.
2. "expression" is evaluated by the application. It may use only control keys, constant keys, the series variable, numbers, the operators + - * / ^ and parentheses, and these functions written bare: exp, log, sqrt, abs, pow, min, max, floor, round, sin, cos, tan (radians), PI, E. No other identifiers. No property access, no strings, no semicolons.
3. "formula" is the human readable version of the same relationship, written the way the passage writes it. It is shown on screen so the student can check your work.
4. EVERY stage target must be reachable. For a locked stage, sweep only the free control and confirm the output passes through the target. For an unlocked stage, sweep both. If a target is not reachable, change it.
5. A lock value must sit inside that control's range and land exactly on a step boundary.
6. A locked stage should have few solutions, because the student is solving for one value. The unlocked stage should have many.
7. Tolerance is an absolute value in output units, sized per the difficulty guidance given.
8. output.min and output.max must cover everything the controls can produce, because they scale the drawing.
9. Hints are ordered from vague to nearly explicit. The third hint may name specific values, and those values must actually win.
10. If the output saturates before the end of its range, use "markAt" to score earlier, where both controls still matter.
11. If the passage expresses a rate as a percentage, keep the slider in percent and divide inside the expression using a constant, so the student never types decimals.

Return only the JSON object.`;

/** The prompt actually sent. Schema, then the unfittable escape hatch, then two worked examples. */
export const LAB_SYSTEM_PROMPT = LAB_SCHEMA_PROMPT + UNFITTABLE_CLAUSE + FEWSHOT_EXAMPLES;

/** Build the user message. Keep the chapter text capped so latency stays low. */
export function buildLabUserMessage(opts: {
	chapterText: string;
	subject: string;
	courseLabel: string;
	difficulty: 'middle' | 'high' | 'college';
}): string {
	return [
		`Subject: ${opts.subject}`,
		`Course: ${opts.courseLabel}`,
		`Student level: ${opts.difficulty}`,
		`Difficulty guidance: ${DIFFICULTY_GUIDE[opts.difficulty]}`,
		'',
		'Passage:',
		opts.chapterText.slice(0, 6000)
	].join('\n');
}
