// Upload → level. Maps every backend response onto one of three outcomes:
//
//   file-error  the file itself is the problem; stay on the upload screen
//   unfit       the chapter has no two-variable relationship; say so honestly
//   level       a playable level, labelled generated, saved copy, or sample
//
// A sample level is only ever shown with a notice saying it is a sample.

import { validateLevel } from '$lib/games/lab/evaluate';
import { canonicalSubject, fallbackFor } from '$lib/games/lab/levels';
import type { LabLevel } from '$lib/games/lab/types';

export type LevelSource = 'generated' | 'cached' | 'sample';

export type Outcome =
	| { kind: 'level'; level: LabLevel; source: LevelSource; notice: string }
	| { kind: 'unfit'; reason: string; suggestion: string }
	| { kind: 'file-error'; message: string };

export const MAX_UPLOAD_MB = 10;
export const ACCEPTED_EXTENSIONS = ['pdf', 'txt'];

const GRADE_LEVELS: Record<string, 'middle' | 'high' | 'college'> = {
	'Middle school': 'middle',
	'High school': 'high',
	College: 'college'
};

/** Problems with the file itself. Anything else falls back to a labelled sample. */
const FILE_ERRORS = new Set([
	'UNSUPPORTED_FILE',
	'FILE_TOO_LARGE',
	'INVALID_DOCUMENT',
	'EMPTY_DOCUMENT',
	'MISSING_SOURCE'
]);

/**
 * True when the model judged the file to be a different subject from the one the student
 * picked, e.g. a chemistry chapter uploaded as History. "Other" never mismatches.
 */
export function subjectMismatch(chosen: string, outcome: Outcome): boolean {
	if (outcome.kind !== 'level' || outcome.source === 'sample') return false;
	const detected = outcome.level.detectedSubject;
	if (!detected || chosen === 'Other' || detected === 'Other') return false;
	return canonicalSubject(chosen).toLowerCase() !== canonicalSubject(detected).toLowerCase();
}

/** A built-in level, always labelled as a sample and never presented as generated. */
export function sample(subject: string, why: string): Outcome {
	const level = fallbackFor(subject);
	return {
		kind: 'level',
		level,
		source: 'sample',
		notice: `${why} Here’s a sample ${level.subject} level so you can still try the idea.`
	};
}

export async function generateLevel(opts: {
	file: File;
	subject: string;
	course: string;
	schoolLevel: string;
}): Promise<Outcome> {
	const subject = canonicalSubject(opts.subject);
	const body = new FormData();
	body.set('subject', subject);
	body.set('gradeLevel', GRADE_LEVELS[opts.schoolLevel] ?? 'high');
	body.set('course', opts.course.trim());
	if (opts.file.name.toLowerCase().endsWith('.txt')) body.set('text', await opts.file.text());
	else body.set('file', opts.file);

	let res: Response;
	try {
		res = await fetch('/api/v1/labs/generate', {
			method: 'POST',
			body,
			signal: AbortSignal.timeout(90_000)
		});
	} catch (err) {
		console.warn('[generate] request failed', err);
		return sample(subject, 'We couldn’t reach HyperPlay’s server just now.');
	}

	const data = await res.json().catch(() => null);

	if (res.ok && data?.gameType === 'unfittable') {
		return { kind: 'unfit', reason: data.reason, suggestion: data.suggestion };
	}

	if (res.ok && data?.gameType === 'lab') {
		// The server already validated this; checking again here costs nothing.
		const checked = validateLevel(data as LabLevel);
		if (checked.ok) {
			const source = res.headers.get('X-HyperPlay-Source') === 'cache' ? 'cached' : 'generated';
			return {
				kind: 'level',
				level: checked.level,
				source,
				notice:
					source === 'cached'
						? 'Live generation is unavailable, so this is the level HyperPlay built from this same file earlier.'
						: ''
			};
		}
		console.warn('[generate] level failed client validation', checked.problems);
		return sample(subject, 'The level built from your file didn’t pass our checks.');
	}

	const code: string | undefined = data?.error?.code;
	if (code && FILE_ERRORS.has(code)) {
		return { kind: 'file-error', message: data.error.message };
	}

	console.warn('[generate] generation unavailable', res.status, code);
	return sample(
		subject,
		code === 'AI_NOT_CONFIGURED'
			? 'Live generation isn’t switched on yet.'
			: 'We couldn’t build a level from your file right now.'
	);
}
