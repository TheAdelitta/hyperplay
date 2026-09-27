// src/lib/games/lab/types.ts
//
// One engine, four visual modes, an ordered sequence of stages per upload.
// The model fills this in from the uploaded chapter. The front end renders it.
// The model never writes code.

export type VisualMode = 'trajectory' | 'curve' | 'fill' | 'meter';

export interface Control {
	/** Short symbol used inside expressions. Example: "r", "P", "T" */
	key: string;
	/** Shown to the student. Example: "Intrinsic growth rate" */
	label: string;
	/** Example: "per year", "kPa", "%" */
	unit: string;
	min: number;
	max: number;
	step: number;
	default: number;
	/** Decimal places to show next to the slider */
	decimals: number;
}

export interface Readout {
	label: string;
	/** Expression over control keys and constants */
	expression: string;
	unit: string;
	decimals: number;
}

export interface SeriesSpec {
	/** Variable that sweeps along the x axis. Almost always "t". */
	variable: string;
	label: string;
	unit: string;
	min: number;
	max: number;
	/** Number of sample points. 120 is smooth and cheap. */
	steps: number;
	/** Expression over the sweep variable, control keys, and constants */
	expression: string;
	/**
	 * Optional. The x value the target is scored at, drawn as a vertical
	 * marker. Defaults to max. Use this when the curve saturates before the
	 * end of the sweep, so both controls still matter.
	 */
	markAt?: number;
}

/**
 * One challenge in the sequence. Stages are worked in order, because a student
 * cannot sensibly jump between concepts they have not met yet.
 *
 * The ladder that teaches best:
 *   stage 1  lock one control, so a single relationship is visible on its own
 *   stage 2  lock the other, so the second relationship is visible on its own
 *   stage 3  unlock both, and pick a target reachable more than one way
 */
export interface Stage {
	/** "Hold the temperature at 300 K and reach 18.0 L." */
	challenge: string;
	/** One line on what this stage is teaching. Shown under the challenge. */
	teaches: string;

	target: {
		value: number;
		/** Absolute tolerance in output units. A hit is |actual - value| <= tolerance. */
		tolerance: number;
	};

	/**
	 * Optional. Freezes one control at a value so the student can only move the
	 * other. The frozen slider is disabled and labelled with the note.
	 */
	lock?: {
		key: string;
		value: number;
		note: string;
	};

	hints: string[];
	/** Shown after this stage is cleared. Explains what just happened. */
	debriefing: string;
}

export interface LabLevel {
	gameType: 'lab';
	/** The subject the model judged the uploaded material to be, which may differ from the student's pick. */
	detectedSubject?: string;
	visualMode: VisualMode;

	concept: string;
	sourceSummary: string;

	/** Human readable, shown on screen so the student can check the model */
	formula: string;
	/**
	 * Machine readable version of the same formula, evaluated by the app.
	 * May use control keys, constant keys, the series variable, and Math
	 * functions written bare: exp, log, sin, cos, sqrt, pow, abs, PI, E.
	 */
	expression: string;

	/** Exactly two. The engine draws exactly two sliders. */
	controls: [Control, Control];

	/** Fixed values referenced by expressions. Example: { R: 8.314, n: 1 } */
	constants: Record<string, number>;

	output: {
		label: string;
		unit: string;
		decimals: number;
		/** Used to scale the visual. Set generously. */
		min: number;
		max: number;
	};

	/** Ordered. Two to four. The model decides how many the chapter needs. */
	stages: Stage[];

	/** Required for visualMode 'curve'. Ignored otherwise. */
	series?: SeriesSpec;

	/** Up to three secondary numbers shown under the visual */
	readouts: Readout[];

	/** Shown once every stage is cleared. What the whole chapter taught. */
	completion: string;

	difficulty: 'middle' | 'high' | 'college';
	subject: string;
	courseLabel: string;
}

/**
 * Returned instead of a LabLevel when the chapter has no two-variable
 * quantitative relationship. Narrative history, anatomy, literary analysis.
 */
export interface UnfittableResult {
	gameType: 'unfittable';
	reason: string;
	suggestion: string;
}

export interface LabAttempt {
	index: number;
	stage: number;
	values: Record<string, number>;
	output: number;
	hit: boolean;
	deltaText: string;
}
