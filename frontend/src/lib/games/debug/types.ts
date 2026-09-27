// src/lib/games/debug/types.ts

export interface DebugTest {
	/** Shown to the student, e.g. "Handles all negative numbers" */
	name: string;
	/** Arguments passed to the function, in order */
	args: unknown[];
	/** Expected return value */
	expected: unknown;
	/** Shown only after this test fails, to point at the concept */
	failNote: string;
}

export interface DebugLevel {
	gameType: 'debug';

	/** "Off-by-one comparison", "Array index bounds" */
	concept: string;
	/** One sentence on what the source chapter covers */
	sourceSummary: string;

	/** Name of the function the student must fix */
	functionName: string;
	/** The broken code the student starts with */
	brokenCode: string;
	/** The correct code. Never shown to the student. Used for validation only. */
	referenceCode: string;

	/** "Return the largest number in the list." */
	expectedBehavior: string;
	/** The mission line shown on the device */
	mission: string;

	tests: DebugTest[];

	/** Progressive. hints[0] is vague, hints[n] is close to the answer. */
	hints: string[];

	/** Shown on the DEFUSED screen. Explains what they actually learned. */
	debriefing: string;

	/** Seconds on the countdown. 0 disables the timer. */
	timeLimit: number;

	difficulty: 'middle' | 'high' | 'college';
}

export interface TestResult {
	name: string;
	passed: boolean;
	actual?: string;
	expected: string;
	failNote?: string;
	error?: string;
}

export interface Attempt {
	index: number;
	passedCount: number;
	totalCount: number;
	timestamp: number;
}
