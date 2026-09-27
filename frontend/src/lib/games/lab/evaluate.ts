// src/lib/games/lab/evaluate.ts

import type { LabLevel } from './types';

const ALLOWED = /^[0-9a-zA-Z_+\-*/^().,\s]*$/;

const MATH_SCOPE = {
	exp: Math.exp,
	log: Math.log,
	ln: Math.log,
	log10: Math.log10,
	sin: Math.sin,
	cos: Math.cos,
	tan: Math.tan,
	sqrt: Math.sqrt,
	abs: Math.abs,
	pow: Math.pow,
	min: Math.min,
	max: Math.max,
	floor: Math.floor,
	round: Math.round,
	PI: Math.PI,
	E: Math.E
};

/**
 * Compile an expression string into a function of a variable map.
 * Rejects anything containing characters outside the safe set, which blocks
 * property access, string literals, and statement separators.
 */
export function compile(expression: string, varNames: string[]): (vars: Record<string, number>) => number {
	if (!ALLOWED.test(expression)) {
		throw new Error('Expression contains disallowed characters');
	}

	// ^ is exponentiation in textbook notation, ** in JavaScript
	const js = expression.replace(/\^/g, '**');

	const scopeKeys = Object.keys(MATH_SCOPE);
	const allKeys = [...new Set([...varNames, ...scopeKeys])];

	// eslint-disable-next-line no-new-func
	const fn = new Function(...allKeys, `"use strict"; return (${js});`) as (
		...args: unknown[]
	) => number;

	return (vars: Record<string, number>) => {
		const args = allKeys.map((k) =>
			k in vars ? vars[k] : (MATH_SCOPE as Record<string, unknown>)[k]
		);
		const result = fn(...args);
		if (typeof result !== 'number' || !Number.isFinite(result)) {
			throw new Error('Expression did not produce a finite number');
		}
		return result;
	};
}

function varNamesFor(level: LabLevel): string[] {
	const names = [
		...level.controls.map((c) => c.key),
		...Object.keys(level.constants)
	];
	if (level.series) names.push(level.series.variable);
	return names;
}

/** Evaluate the main output for a given pair of slider values. */
export function evaluateOutput(level: LabLevel, values: Record<string, number>): number {
	const vars = { ...level.constants, ...values };

	if (level.visualMode === 'curve' && level.series) {
		// Output is the series value at the marker, or the end of the sweep
		const f = compile(level.series.expression, varNamesFor(level));
		const at = level.series.markAt ?? level.series.max;
		return f({ ...vars, [level.series.variable]: at });
	}

	const f = compile(level.expression, varNamesFor(level));
	return f(vars);
}

/** Generate the points for curve mode. */
export function evaluateSeries(
	level: LabLevel,
	values: Record<string, number>
): { x: number; y: number }[] {
	if (!level.series) return [];
	const f = compile(level.series.expression, varNamesFor(level));
	const vars = { ...level.constants, ...values };
	const pts: { x: number; y: number }[] = [];
	const span = level.series.max - level.series.min;

	for (let i = 0; i <= level.series.steps; i++) {
		const x = level.series.min + (span * i) / level.series.steps;
		try {
			pts.push({ x, y: f({ ...vars, [level.series.variable]: x }) });
		} catch {
			// skip an undefined point rather than killing the whole curve
		}
	}
	return pts;
}

/** Generate the arc for trajectory mode. Physics is fixed, not model supplied. */
export function evaluateTrajectory(
	angleDeg: number,
	speed: number,
	gravity: number
): { x: number; y: number }[] {
	const rad = (angleDeg * Math.PI) / 180;
	const vx = speed * Math.cos(rad);
	const vy = speed * Math.sin(rad);
	const pts: { x: number; y: number }[] = [];
	const dt = 1 / 60;

	for (let t = 0; t < 30; t += dt) {
		const y = vy * t - 0.5 * gravity * t * t;
		if (y < 0 && t > 0) {
			// interpolate the landing point
			const prev = pts[pts.length - 1];
			const frac = prev.y / (prev.y - y);
			pts.push({ x: prev.x + (vx * dt) * frac, y: 0 });
			break;
		}
		pts.push({ x: vx * t, y: Math.max(0, y) });
	}
	return pts;
}

export interface ValidationResult {
	ok: boolean;
	level: LabLevel;
	problems: string[];
}

/**
 * Never trust model output. Sweep a grid over both controls, then check EVERY
 * stage independently. A locked stage is swept only along its free control,
 * because that is all the student can move.
 *
 * Unreachable targets are clamped into range rather than rejected. A stage
 * that still cannot be solved after clamping is dropped. If nothing survives,
 * the whole level is rejected and the caller loads the fallback.
 */
export function validateLevel(input: LabLevel): ValidationResult {
	const problems: string[] = [];
	const level: LabLevel = JSON.parse(JSON.stringify(input));

	if (!level.controls || level.controls.length !== 2) {
		return { ok: false, level, problems: ['Level does not define exactly two controls'] };
	}
	if (!level.stages?.length) {
		return { ok: false, level, problems: ['Level defines no stages'] };
	}

	for (const c of level.controls) {
		if (!(c.max > c.min)) problems.push(`Control ${c.key} has an empty range`);
		if (c.default < c.min || c.default > c.max) c.default = (c.min + c.max) / 2;
		if (!(c.step > 0)) c.step = (c.max - c.min) / 100;
	}
	if (problems.length) return { ok: false, level, problems };

	const [a, b] = level.controls;
	const N = 40;

	/** Reachable outputs, optionally with one control frozen. */
	function sweep(lock?: { key: string; value: number }) {
		let lo = Infinity;
		let hi = -Infinity;
		let nearestTo = (v: number) => Infinity;
		const outs: number[] = [];
		let failures = 0;

		// A locked stage leaves one slider free: check every position the student can
		// actually reach, as the backend validator does. Otherwise sample a grid.
		const positions = (c: typeof a) => {
			const count = Math.floor((c.max - c.min) / c.step + 1e-9);
			if (lock && count <= 2000) return Array.from({ length: count + 1 }, (_, k) => c.min + k * c.step);
			return Array.from({ length: N + 1 }, (_, i) => c.min + ((c.max - c.min) * i) / N);
		};
		const aValues = lock?.key === a.key ? [lock.value] : positions(a);
		const bValues = lock?.key === b.key ? [lock.value] : positions(b);

		for (const va of aValues) {
			for (const vb of bValues) {
				try {
					const out = evaluateOutput(level, { [a.key]: va, [b.key]: vb });
					lo = Math.min(lo, out);
					hi = Math.max(hi, out);
					outs.push(out);
				} catch {
					failures++;
				}
			}
		}
		nearestTo = (v: number) => outs.reduce((m, o) => Math.min(m, Math.abs(o - v)), Infinity);
		return { lo, hi, nearestTo, failures, count: outs.length };
	}

	const full = sweep();
	if (full.failures > (N + 1) * (N + 1) * 0.2) {
		return { ok: false, level, problems: ['Expression failed across too much of the range'] };
	}

	// Output scale drives the drawing, so make sure it covers what can happen
	if (!(level.output.max > level.output.min)) {
		level.output.min = Math.min(0, full.lo);
		level.output.max = full.hi * 1.1;
		problems.push('Output scale was invalid, derived from the reachable range');
	}

	const kept: typeof level.stages = [];

	level.stages.forEach((stage, idx) => {
		const n = idx + 1;

		// A lock must name a real control and sit inside its range
		if (stage.lock) {
			const ctl = level.controls.find((c) => c.key === stage.lock!.key);
			if (!ctl) {
				problems.push(`Stage ${n} locks an unknown control, lock removed`);
				delete stage.lock;
			} else {
				stage.lock.value = Math.min(Math.max(stage.lock.value, ctl.min), ctl.max);
			}
		}

		const s = stage.lock ? sweep(stage.lock) : full;
		const span = s.hi - s.lo;

		if (!Number.isFinite(span) || span <= 0) {
			problems.push(`Stage ${n} has no reachable range, dropped`);
			return;
		}

		if (!(stage.target.tolerance > 0) || stage.target.tolerance > span * 0.25) {
			stage.target.tolerance = Math.max(span * 0.03, 1e-6);
			problems.push(`Stage ${n} tolerance was missing or too loose, tightened`);
		}

		if (s.nearestTo(stage.target.value) > stage.target.tolerance) {
			const clamped = Math.min(
				Math.max(stage.target.value, s.lo + span * 0.15),
				s.hi - span * 0.15
			);
			stage.target.value = Number(clamped.toFixed(level.output.decimals));
			problems.push(`Stage ${n} target was unreachable, clamped into range`);

			if (s.nearestTo(stage.target.value) > stage.target.tolerance) {
				problems.push(`Stage ${n} still unsolvable after clamping, dropped`);
				return;
			}
		}

		if (!stage.hints?.length) {
			stage.hints = ['Change one slider at a time and watch which way the result moves.'];
		}
		kept.push(stage);
	});

	if (!kept.length) {
		return { ok: false, level, problems: [...problems, 'No stage survived validation'] };
	}

	level.stages = kept;
	if (!level.completion) level.completion = 'You worked through every challenge in this chapter.';

	return { ok: true, level, problems };
}
