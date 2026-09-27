// src/lib/games/lab/render.ts
//
// One canvas, four modes. Every mode receives the same shape of data so the
// play component does not branch on mode except to call the right function.

import type { LabLevel, Stage } from './types';

type Target = Stage['target'];

export interface Palette {
	grid: string;
	axis: string;
	text: string;
	muted: string;
	accent: string;
	past: string;
	target: string;
	hit: string;
}

export const palette: Palette = {
	grid: '#e6eaf2',
	axis: '#9aa4b8',
	text: '#1f2a44',
	muted: '#7b869c',
	accent: '#2563eb',
	past: '#d9b382',
	target: '#0f9d58',
	hit: '#0f9d58'
};

export interface Frame {
	ctx: CanvasRenderingContext2D;
	w: number;
	h: number;
	pad: { l: number; r: number; t: number; b: number };
}

export function prepare(canvas: HTMLCanvasElement): Frame {
	const dpr = window.devicePixelRatio || 1;
	const rect = canvas.getBoundingClientRect();
	canvas.width = Math.round(rect.width * dpr);
	canvas.height = Math.round(rect.height * dpr);
	const ctx = canvas.getContext('2d')!;
	ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
	ctx.clearRect(0, 0, rect.width, rect.height);
	return { ctx, w: rect.width, h: rect.height, pad: { l: 58, r: 28, t: 22, b: 42 } };
}

function grid(f: Frame, cols = 10, rows = 6) {
	const { ctx, w, h, pad } = f;
	ctx.strokeStyle = palette.grid;
	ctx.lineWidth = 1;
	for (let i = 0; i <= cols; i++) {
		const x = pad.l + ((w - pad.l - pad.r) * i) / cols;
		ctx.beginPath();
		ctx.moveTo(x, pad.t);
		ctx.lineTo(x, h - pad.b);
		ctx.stroke();
	}
	for (let i = 0; i <= rows; i++) {
		const y = pad.t + ((h - pad.t - pad.b) * i) / rows;
		ctx.beginPath();
		ctx.moveTo(pad.l, y);
		ctx.lineTo(w - pad.r, y);
		ctx.stroke();
	}
}

function label(f: Frame, text: string, x: number, y: number, align: CanvasTextAlign = 'left', color = palette.muted, size = 12, weight = '500') {
	f.ctx.fillStyle = color;
	f.ctx.textAlign = align;
	f.ctx.font = `${weight} ${size}px -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif`;
	f.ctx.fillText(text, x, y);
}

// ---------------------------------------------------------------------------
// TRAJECTORY  ·  physics. Arc through space with past shots retained.
// ---------------------------------------------------------------------------

export function drawTrajectory(
	f: Frame,
	pts: { x: number; y: number }[],
	pastRuns: { x: number; y: number }[][],
	targetX: number,
	targetTol: number,
	xMax: number,
	yMax: number,
	hit: boolean,
	aimDeg?: number
) {
	const { ctx, w, h, pad } = f;
	grid(f);
	const px = (x: number) => pad.l + ((w - pad.l - pad.r) * x) / xMax;
	const py = (y: number) => h - pad.b - ((h - pad.t - pad.b) * y) / yMax;

	// launcher, aimed at the current angle before and after firing
	if (aimDeg !== undefined) {
		const a = (aimDeg * Math.PI) / 180;
		ctx.strokeStyle = palette.text;
		ctx.lineWidth = 7;
		ctx.lineCap = 'round';
		ctx.beginPath();
		ctx.moveTo(px(0), py(0));
		ctx.lineTo(px(0) + 34 * Math.cos(a), py(0) - 34 * Math.sin(a));
		ctx.stroke();
		ctx.lineCap = 'butt';
	}

	// ground
	ctx.strokeStyle = palette.axis;
	ctx.lineWidth = 2;
	ctx.beginPath();
	ctx.moveTo(pad.l, py(0));
	ctx.lineTo(w - pad.r, py(0));
	ctx.stroke();

	// past shots
	ctx.lineWidth = 2;
	ctx.strokeStyle = palette.past;
	for (const run of pastRuns.slice(-6)) {
		ctx.globalAlpha = 0.55;
		ctx.beginPath();
		run.forEach((p, i) => (i ? ctx.lineTo(px(p.x), py(p.y)) : ctx.moveTo(px(p.x), py(p.y))));
		ctx.stroke();
	}
	ctx.globalAlpha = 1;

	// target
	ctx.fillStyle = palette.target;
	ctx.fillRect(px(targetX - targetTol), py(0) - 14, Math.max(4, px(targetX + targetTol) - px(targetX - targetTol)), 14);
	label(f, `Target · ${targetX.toFixed(0)} m`, px(targetX), py(0) - 24, 'center', palette.target, 13, '700');

	// current shot
	ctx.strokeStyle = hit ? palette.hit : palette.accent;
	ctx.lineWidth = 3.5;
	ctx.beginPath();
	pts.forEach((p, i) => (i ? ctx.lineTo(px(p.x), py(p.y)) : ctx.moveTo(px(p.x), py(p.y))));
	ctx.stroke();

	const last = pts[pts.length - 1];
	if (last) {
		ctx.fillStyle = hit ? palette.hit : '#f0a830';
		ctx.beginPath();
		ctx.arc(px(last.x), py(last.y), 8, 0, Math.PI * 2);
		ctx.fill();
	}

	label(f, '0 m', pad.l, h - 14, 'left');
	label(f, `${xMax.toFixed(0)} m`, w - pad.r, h - 14, 'right');
}

// ---------------------------------------------------------------------------
// CURVE  ·  biology, anything over time. Sigmoid, decay, oscillation.
// ---------------------------------------------------------------------------

export function drawCurve(
	f: Frame,
	pts: { x: number; y: number }[],
	pastRuns: { x: number; y: number }[][],
	level: LabLevel,
	target: Target,
	hit: boolean
) {
	const { ctx, w, h, pad } = f;
	const s = level.series!;
	const yMax = level.output.max;
	grid(f);

	const px = (x: number) => pad.l + ((w - pad.l - pad.r) * (x - s.min)) / (s.max - s.min);
	const py = (y: number) => h - pad.b - ((h - pad.t - pad.b) * (y - level.output.min)) / (yMax - level.output.min);

	// y axis ticks
	for (let i = 0; i <= 5; i++) {
		const v = level.output.min + ((yMax - level.output.min) * i) / 5;
		label(f, v.toFixed(0), pad.l - 8, py(v) + 4, 'right');
	}

	// target band at the marker
	const at = s.markAt ?? s.max;
	ctx.strokeStyle = palette.target;
	ctx.setLineDash([5, 4]);
	ctx.lineWidth = 1.5;
	ctx.beginPath();
	ctx.moveTo(px(at), pad.t);
	ctx.lineTo(px(at), h - pad.b);
	ctx.stroke();
	ctx.setLineDash([]);

	ctx.fillStyle = 'rgba(15,157,88,0.16)';
	const bandTop = py(target.value + target.tolerance);
	const bandBot = py(target.value - target.tolerance);
	ctx.fillRect(pad.l, bandTop, w - pad.l - pad.r, Math.max(3, bandBot - bandTop));
	label(f, `Target · ${target.value}`, w - pad.r - 6, bandTop - 6, 'right', palette.target, 12, '700');

	// past curves
	ctx.lineWidth = 2;
	ctx.strokeStyle = palette.past;
	for (const run of pastRuns.slice(-5)) {
		ctx.globalAlpha = 0.5;
		ctx.beginPath();
		run.forEach((p, i) => (i ? ctx.lineTo(px(p.x), py(p.y)) : ctx.moveTo(px(p.x), py(p.y))));
		ctx.stroke();
	}
	ctx.globalAlpha = 1;

	// current curve
	ctx.strokeStyle = hit ? palette.hit : palette.accent;
	ctx.lineWidth = 3.5;
	ctx.beginPath();
	pts.forEach((p, i) => (i ? ctx.lineTo(px(p.x), py(p.y)) : ctx.moveTo(px(p.x), py(p.y))));
	ctx.stroke();

	// marker dot where it is scored
	const scored = pts.reduce((best, p) => (Math.abs(p.x - at) < Math.abs(best.x - at) ? p : best), pts[0]);
	if (scored) {
		ctx.fillStyle = hit ? palette.hit : '#f0a830';
		ctx.beginPath();
		ctx.arc(px(scored.x), py(scored.y), 8, 0, Math.PI * 2);
		ctx.fill();
	}

	label(f, `${s.label} →`, pad.l, h - 14, 'left');
	label(f, `${s.max}${s.unit}`, w - pad.r, h - 14, 'right');
}

// ---------------------------------------------------------------------------
// FILL  ·  chemistry. A piston in a cylinder, height set by the output.
// ---------------------------------------------------------------------------

export function drawFill(f: Frame, value: number, level: LabLevel, target: Target, hit: boolean) {
	const { ctx, w, h, pad } = f;
	const cw = Math.min(220, w * 0.34);
	const cx = w / 2 - cw / 2;
	const top = pad.t + 10;
	const bot = h - pad.b - 10;
	const ch = bot - top;

	const frac = Math.max(0.02, Math.min(1, (value - level.output.min) / (level.output.max - level.output.min)));
	const gasTop = bot - ch * frac;

	// cylinder walls
	ctx.strokeStyle = palette.axis;
	ctx.lineWidth = 3;
	ctx.strokeRect(cx, top, cw, ch);

	// gas
	const grad = ctx.createLinearGradient(0, gasTop, 0, bot);
	grad.addColorStop(0, hit ? 'rgba(15,157,88,0.35)' : 'rgba(37,99,235,0.30)');
	grad.addColorStop(1, hit ? 'rgba(15,157,88,0.12)' : 'rgba(37,99,235,0.10)');
	ctx.fillStyle = grad;
	ctx.fillRect(cx + 2, gasTop, cw - 4, bot - gasTop - 1);

	// particles, density and speed suggest temperature
	const count = 26;
	ctx.fillStyle = hit ? palette.hit : palette.accent;
	for (let i = 0; i < count; i++) {
		const rx = cx + 10 + ((i * 7919) % (cw - 20));
		const ry = gasTop + 8 + ((i * 6271) % Math.max(10, bot - gasTop - 16));
		ctx.globalAlpha = 0.5;
		ctx.beginPath();
		ctx.arc(rx, ry, 2.6, 0, Math.PI * 2);
		ctx.fill();
	}
	ctx.globalAlpha = 1;

	// piston head
	ctx.fillStyle = '#6b7280';
	ctx.fillRect(cx - 6, gasTop - 12, cw + 12, 12);
	ctx.fillRect(w / 2 - 7, top - 4, 14, Math.max(0, gasTop - 12 - top + 4));

	// target line
	const tFrac = (target.value - level.output.min) / (level.output.max - level.output.min);
	const ty = bot - ch * tFrac;
	ctx.strokeStyle = palette.target;
	ctx.setLineDash([6, 4]);
	ctx.lineWidth = 2;
	ctx.beginPath();
	ctx.moveTo(cx - 34, ty);
	ctx.lineTo(cx + cw + 34, ty);
	ctx.stroke();
	ctx.setLineDash([]);
	label(f, `Target ${target.value} ${level.output.unit}`, cx + cw + 38, ty + 4, 'left', palette.target, 12, '700');

	label(f, `${value.toFixed(level.output.decimals)} ${level.output.unit}`, w / 2, bot + 26, 'center', palette.text, 15, '700');
}

// ---------------------------------------------------------------------------
// METER  ·  math, finance. A bar climbing toward a goal line.
// ---------------------------------------------------------------------------

export function drawMeter(
	f: Frame,
	value: number,
	level: LabLevel,
	target: Target,
	past: number[],
	hit: boolean
) {
	const { ctx, w, h, pad } = f;
	const left = pad.l;
	const right = w - pad.r - 90;
	const track = right - left;
	const barH = 46;
	const y = pad.t + 46;

	const scaleMax = Math.max(target.value * 1.6, value * 1.1, level.output.min + 1);
	const fx = (v: number) => left + (track * Math.max(0, Math.min(v, scaleMax))) / scaleMax;

	// track
	ctx.fillStyle = '#eef1f7';
	ctx.beginPath();
	ctx.roundRect(left, y, track, barH, 10);
	ctx.fill();

	// past attempts as tick marks
	ctx.strokeStyle = palette.past;
	ctx.lineWidth = 2;
	for (const p of past.slice(-8)) {
		ctx.beginPath();
		ctx.moveTo(fx(p), y - 8);
		ctx.lineTo(fx(p), y + barH + 8);
		ctx.stroke();
	}

	// bar
	ctx.fillStyle = hit ? palette.hit : palette.accent;
	ctx.beginPath();
	ctx.roundRect(left, y, Math.max(6, fx(value) - left), barH, 10);
	ctx.fill();

	// goal line
	ctx.strokeStyle = palette.target;
	ctx.lineWidth = 3;
	ctx.beginPath();
	ctx.moveTo(fx(target.value), y - 18);
	ctx.lineTo(fx(target.value), y + barH + 18);
	ctx.stroke();
	label(f, `Goal ${target.value.toLocaleString()}`, fx(target.value), y - 26, 'center', palette.target, 12, '700');

	// value
	label(f, value.toLocaleString(undefined, { maximumFractionDigits: level.output.decimals }), right + 12, y + barH / 2 + 7, 'left', palette.text, 20, '700');
	label(f, level.output.label, left, y + barH + 40, 'left', palette.muted, 12);
}
