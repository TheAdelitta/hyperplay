// src/lib/games/lab/fewshot.ts
//
// You cannot fine-tune an Azure model during a hackathon. You do not need to.
// Showing the model two complete, verified examples inside the prompt makes its
// output on unseen chapters far more consistent than describing the schema
// alone. This is the cheapest accuracy win available.
//
// The examples are serialised from the verified levels in levels.ts at import
// time, so they cannot drift away from what the code actually plays.
//
// Key order matters: a model writes JSON top to bottom, so "controls" comes
// before "visualMode". It commits to its two sliders before it picks a view.
// When the view came first, gpt-4.1-mini chose "curve" for compound interest
// and then reused its time axis "t" as a slider in 6 of 6 runs. Example 3
// shows that case done right.

import { biologyLogisticGrowth, chemistryGasLaws, mathCompoundInterest } from './levels';
import type { LabLevel } from './types';

/** The order the model should write fields in: controls before visualMode. */
const KEY_ORDER: (keyof LabLevel)[] = [
	'gameType',
	'concept',
	'sourceSummary',
	'formula',
	'controls',
	'constants',
	'visualMode',
	'series',
	'expression',
	'output',
	'stages',
	'readouts',
	'completion',
	'difficulty',
	'subject',
	'courseLabel'
];

function example(level: LabLevel): string {
	const ordered: Record<string, unknown> = {};
	for (const key of KEY_ORDER) ordered[key] = level[key] ?? null;
	ordered.stages = level.stages.map((st) => ({ ...st, lock: st.lock ?? null }));
	return JSON.stringify(ordered, null, 2);
}

export const FEWSHOT_EXAMPLES = `
Here are three complete, correct outputs. Match this level of specificity, and
copy the stage ladder exactly: lock one control, lock the other, then unlock both.

EXAMPLE 1
Passage: a chapter deriving PV = nRT and rearranging it to solve for volume,
noting that pressure and temperature push volume in opposite directions.
Subject: Chemistry. Level: high.

${example(chemistryGasLaws)}

EXAMPLE 2
Passage: a chapter contrasting exponential and logistic growth, stressing that
the intrinsic rate of increase sets the steepness while the carrying capacity
sets the ceiling.
Subject: Biology. Level: college.

${example(biologyLogisticGrowth)}

EXAMPLE 3
Passage: a chapter developing A = P(1 + r)^t for annual compounding, showing
that the rate sits in the base while time sits in the exponent.
Subject: Mathematics. Level: high.

${example(mathCompoundInterest)}

Note five things about these examples.

First, the stage ladder. Stage 1 freezes one control so a single relationship is
visible alone. Stage 2 freezes the other. Stage 3 unlocks both and picks a target
that several different pairs can reach. That ordering is what teaches.

Second, the locked stages have narrow answers and the unlocked stage has many.
That is correct. With one slider fixed, the student is solving for one value.

Third, example 2 uses "markAt". The logistic curve saturates well before year 30,
so scoring at year 30 would make the carrying capacity the only slider that
matters. Scoring at year 15 keeps both meaningful. Apply the same reasoning
whenever an output flattens before the end of its range.

Fourth, compare examples 2 and 3. Both describe growth over time. In example 2
time is NOT a slider: the controls are r and K, and time runs along the x axis
as the series variable, so it is "curve". In example 3 time IS a slider ("t",
years invested), so it is "meter", with no series, and the output is read at the
number of years the slider sets. A control key is never also the series variable.

Fifth, every specific value named in a third hint actually wins. Check yours.
`;

/**
 * If the passage has no two-variable quantitative relationship, the model
 * should say so rather than inventing one. Appended to the system prompt and
 * handled in the backend.
 */
export const UNFITTABLE_CLAUSE = `
If the passage contains no quantitative relationship between two adjustable
quantities, for example a narrative history chapter or a descriptive chapter
on anatomy, do not invent one. Return exactly this instead:

{ "gameType": "unfittable", "reason": "<one sentence on what the chapter covers>", "suggestion": "<one sentence naming the kind of chapter that would work>" }
`;
