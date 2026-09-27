<script lang="ts">
	import { onMount, onDestroy, tick } from 'svelte';
	import type { LabLevel, LabAttempt, Control } from '$lib/games/lab/types';
	import { compile, evaluateOutput, evaluateSeries, evaluateTrajectory } from '$lib/games/lab/evaluate';
	import { prepare, drawTrajectory, drawCurve, drawFill, drawMeter } from '$lib/games/lab/render';

	export let level: LabLevel;
	/** Where the level came from. Shown to the student so a sample is never passed off as generated. */
	export let source: 'generated' | 'cached' | 'sample' = 'sample';
	/** Optional line explaining why a sample is showing. */
	export let notice = '';
	/** Optional. Called from the completion panel. */
	export let onNewChapter: (() => void) | undefined = undefined;

	type Point = { x: number; y: number };

	let canvas: HTMLCanvasElement;
	let challengeEl: HTMLElement;
	let nextBtn: HTMLButtonElement;
	let si = 0;
	let values: Record<string, number> = {};
	let output = 0;
	let hit = false;
	let ran = false;
	/** Sticky per stage: once cleared, the student can keep exploring other routes. */
	let cleared = false;
	let allDone = false;
	let attempts: LabAttempt[] = [];
	let hintsShown = 0;
	let statusText = '';
	let pastCurves: Point[][] = [];
	let pastValues: number[] = [];
	let pastShots: Point[][] = [];
	let shot: Point[] = [];
	let animFrame = 0;

	$: stage = level.stages[si];
	$: lock = stage?.lock ?? null;
	// Referenced directly in the template: legacy-mode markup does not re-run a
	// helper function when state it reads internally changes.
	$: lockedKey = lock?.key ?? null;
	$: angleCtl = level.controls.find(isAngle) ?? level.controls[0];
	$: speedCtl = level.controls.find((c) => c !== angleCtl) ?? level.controls[1];

	const tags = {
		generated: 'Generated from your file',
		cached: 'Generated from your file · saved copy',
		sample: 'Sample level'
	};

	function isAngle(c: Control) {
		return /°|deg/i.test(c.unit) || /theta|angle/i.test(c.key);
	}

	function enterStage(i: number) {
		si = i;
		const st = level.stages[i];
		values = Object.fromEntries(level.controls.map((c) => [c.key, c.default]));
		if (st.lock) values[st.lock.key] = st.lock.value;
		hintsShown = 0;
		ran = false;
		hit = false;
		cleared = false;
		statusText = '';
		pastCurves = [];
		pastValues = [];
		pastShots = [];
		shot = [];
		draw();
	}

	function resetFor(_l: LabLevel) {
		attempts = [];
		allDone = false;
		enterStage(0);
	}

	$: if (level) resetFor(level);

	function run() {
		try {
			output = evaluateOutput(level, values);
		} catch {
			statusText = 'That combination could not be evaluated. Try different values.';
			return;
		}

		const { target } = stage;
		const delta = output - target.value;
		hit = Math.abs(delta) <= target.tolerance;
		ran = true;

		const dp = level.output.decimals;
		const deltaText = hit
			? 'Hit'
			: `${Math.abs(delta).toFixed(dp)} ${level.output.unit} ${delta < 0 ? 'under' : 'over'}`;

		attempts = [
			{ index: attempts.length + 1, stage: si + 1, values: { ...values }, output, hit, deltaText },
			...attempts
		];

		if (level.visualMode === 'curve') pastCurves = [...pastCurves, evaluateSeries(level, values)];
		pastValues = [...pastValues, output];

		const firstClear = hit && !cleared;
		const reading = `${level.output.label} is ${output.toFixed(dp)} ${level.output.unit}`;
		statusText = !hit
			? `${reading}. That is ${deltaText}.`
			: firstClear
				? `Stage ${si + 1} cleared. ${reading}.`
				: `Another route to the target. ${reading}.`;

		if (hit) cleared = true;
		if (cleared && si === level.stages.length - 1) allDone = true;

		if (level.visualMode === 'trajectory') fire();
		else draw();

		if (firstClear && !allDone) tick().then(() => nextBtn?.focus());
	}

	function nextStage() {
		enterStage(si + 1);
		tick().then(() => {
			challengeEl?.scrollIntoView({ behavior: 'smooth', block: 'center' });
			const free = level.controls.find((c) => c.key !== lockedKey);
			if (free) document.getElementById(`ctl-${free.key}`)?.focus({ preventScroll: true });
		});
	}

	/** Animate the ball along its arc. The arc is only revealed by firing. */
	function fire() {
		if (shot.length) pastShots = [...pastShots, shot];
		const g = level.constants.g ?? 9.81;
		const full = evaluateTrajectory(values[angleCtl.key], values[speedCtl.key], g);
		cancelAnimationFrame(animFrame);
		if (matchMedia('(prefers-reduced-motion: reduce)').matches) {
			shot = full;
			draw();
			return;
		}
		const start = performance.now();
		const duration = 1100;
		const step = (now: number) => {
			const t = Math.min(1, (now - start) / duration);
			shot = full.slice(0, Math.max(2, Math.ceil(full.length * t)));
			draw();
			if (t < 1) animFrame = requestAnimationFrame(step);
		};
		animFrame = requestAnimationFrame(step);
	}

	function trajectoryScale() {
		const target = stage.target.value;
		let xMax = target * 1.6;
		let yMax = target * 0.55;
		for (const run of [...pastShots, shot]) {
			for (const p of run) {
				xMax = Math.max(xMax, p.x * 1.05);
				yMax = Math.max(yMax, p.y * 1.15);
			}
		}
		return { xMax, yMax };
	}

	function draw() {
		if (!canvas || !stage) return;
		const f = prepare(canvas);
		const target = stage.target;
		const done = hit && ran;

		try {
			if (level.visualMode === 'curve') {
				drawCurve(f, evaluateSeries(level, values), pastCurves.slice(0, -1), level, target, done);
			} else if (level.visualMode === 'fill') {
				drawFill(f, evaluateOutput(level, values), level, target, done);
			} else if (level.visualMode === 'meter') {
				drawMeter(f, evaluateOutput(level, values), level, target, pastValues.slice(0, -1), done);
			} else {
				const { xMax, yMax } = trajectoryScale();
				drawTrajectory(f, shot, pastShots, target.value, target.tolerance, xMax, yMax, done, values[angleCtl.key]);
			}
		} catch {
			// a bad intermediate value should never blank the screen
		}
	}

	function onSlide() {
		// A moved slider means the last result no longer describes the screen.
		if (ran && !hit) statusText = '';
		draw();
	}

	let ro: ResizeObserver;
	onMount(async () => {
		await tick();
		draw();
		ro = new ResizeObserver(() => draw());
		ro.observe(canvas);
	});
	onDestroy(() => {
		ro?.disconnect();
		cancelAnimationFrame(animFrame);
	});

	function readoutValue(expression: string, decimals: number, values: Record<string, number>): string {
		try {
			const names = [...level.controls.map((c) => c.key), ...Object.keys(level.constants)];
			return compile(expression, names)({ ...level.constants, ...values }).toLocaleString(undefined, {
				minimumFractionDigits: decimals,
				maximumFractionDigits: decimals
			});
		} catch {
			return '—';
		}
	}

	function onKey(e: KeyboardEvent) {
		if (e.key !== 'Enter') return;
		const el = e.target as HTMLElement;
		if (el.matches('input[type=range]')) {
			e.preventDefault();
			run();
		}
	}
</script>

<section class="lab" aria-label="{level.concept} experiment">
	<!-- a div, not <header>: the site stylesheet gives every <header> a fixed 90px height -->
	<div class="lab-head">
		<div>
			<p class="eyebrow">{level.subject.toUpperCase()} · {level.courseLabel}</p>
			<h2>{level.concept}</h2>
			<p class="sub">{level.sourceSummary}</p>
		</div>
		<span class="tag" class:sample={source === 'sample'}>{tags[source]}</span>
	</div>

	{#if notice}
		<p class="notice" role="status">{notice}</p>
	{/if}

	<ol class="steps" aria-label="Challenges">
		{#each level.stages as st, i}
			<li class:current={i === si && !allDone} class:done={i < si || allDone} aria-current={i === si ? 'step' : undefined}>
				<span class="dot">{i < si || allDone ? '✓' : i + 1}</span>
				<span class="step-label">{st.teaches}</span>
			</li>
		{/each}
	</ol>

	<div class="challenge" bind:this={challengeEl}>
		<p class="stage-no">Challenge {si + 1} of {level.stages.length}</p>
		<h3>{stage.challenge}</h3>
		{#if lock}
			<span class="lockpill">🔒 {lock.note}</span>
		{/if}
	</div>

	<!-- svelte-ignore a11y-no-static-element-interactions -->
	<div class="controls" on:keydown={onKey}>
		{#each level.controls as c (c.key)}
			<div class="control" class:locked={c.key === lockedKey}>
				<label for="ctl-{c.key}">
					<span>{c.label}{c.key === lockedKey ? ' (fixed)' : ''}</span>
					<strong>{values[c.key]?.toFixed(c.decimals)} {c.unit}</strong>
				</label>
				<input
					id="ctl-{c.key}"
					type="range"
					min={c.min}
					max={c.max}
					step={c.step}
					bind:value={values[c.key]}
					on:input={onSlide}
					disabled={c.key === lockedKey}
					aria-label="{c.label} in {c.unit}{c.key === lockedKey ? ', fixed for this challenge' : ''}"
				/>
				<div class="ends"><span>{c.min}</span><span>{c.max}</span></div>
			</div>
		{/each}

		<button class="run" on:click={run}>
			{level.visualMode === 'trajectory' ? 'Launch →' : 'Run experiment →'}
		</button>
	</div>

	<div class="stage">
		<canvas bind:this={canvas} aria-label="Visual result of the experiment. {statusText}"></canvas>
		{#if ran}
			<div class="badge" class:good={hit}>
				{hit ? 'TARGET REACHED' : 'MISSED'} · {output.toFixed(level.output.decimals)} {level.output.unit}
			</div>
		{/if}
	</div>

	<p class="sr-only" aria-live="polite">{statusText}</p>

	<div class="footer">
		<div class="readouts">
			{#each level.readouts.slice(0, 3) as r (r.label)}
				<div class="readout">
					<span>{r.label}</span>
					<strong>{readoutValue(r.expression, r.decimals, values)} {r.unit}</strong>
				</div>
			{/each}
		</div>

		<div class="side">
			<div class="formula">
				<span>The chapter's formula</span>
				<code>{level.formula}</code>
			</div>

			{#if statusText}
				<p class="status" class:good={hit}>{statusText}</p>
			{/if}

			{#if cleared}
				<p class="debrief">{stage.debriefing}</p>
				{#if !allDone}
					<button class="run next" bind:this={nextBtn} on:click={nextStage}>Next challenge →</button>
				{/if}
			{:else}
				{#each stage.hints.slice(0, hintsShown) as h}
					<p class="hint">{h}</p>
				{/each}
				{#if hintsShown < stage.hints.length}
					<button class="hintbtn" on:click={() => (hintsShown += 1)}>
						Need a hint? ({stage.hints.length - hintsShown} left)
					</button>
				{/if}
			{/if}
		</div>
	</div>

	{#if allDone}
		<div class="done" role="status">
			<h3>Chapter complete</h3>
			<p>{level.completion}</p>
			{#if onNewChapter}
				<button class="run" on:click={onNewChapter}>Try another chapter →</button>
			{/if}
		</div>
	{/if}

	{#if attempts.length}
		<div class="attempts">
			<h3>Attempts <span>{attempts.length}</span></h3>
			<ul>
				{#each attempts.slice(0, 8) as a (a.index)}
					<li class:good={a.hit}>
						<span class="n">S{a.stage}·#{a.index}</span>
						<span class="v">
							{#each level.controls as c}{c.key} = {a.values[c.key].toFixed(c.decimals)}&nbsp;&nbsp;{/each}
						</span>
						<span class="d">{a.output.toFixed(level.output.decimals)} · {a.deltaText}</span>
					</li>
				{/each}
			</ul>
		</div>
	{/if}
</section>

<style>
	.lab {
		background: #fff;
		border: 1px solid #e6eaf2;
		border-radius: 18px;
		padding: 26px 28px 22px;
	}
	.lab-head {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 20px;
		margin-bottom: 18px;
	}
	.eyebrow {
		font-size: 11.5px;
		letter-spacing: 0.09em;
		font-weight: 700;
		color: #2563eb;
		margin: 0 0 6px;
	}
	h2 {
		font-size: 24px;
		margin: 0 0 6px;
		color: #101828;
		letter-spacing: -0.015em;
	}
	.sub {
		margin: 0;
		color: #667085;
		font-size: 13.5px;
		max-width: 62ch;
	}
	.tag {
		background: #e7f5ec;
		color: #0f7a45;
		font-size: 12px;
		font-weight: 600;
		padding: 6px 12px;
		border-radius: 999px;
		white-space: nowrap;
	}
	.tag.sample {
		background: #fef6e7;
		color: #8a5a00;
	}
	.notice {
		background: #fef6e7;
		border-left: 3px solid #f0a830;
		color: #7a5200;
		font-size: 13.5px;
		padding: 10px 14px;
		border-radius: 0 8px 8px 0;
		margin: 0 0 18px;
	}

	.steps {
		list-style: none;
		display: grid;
		grid-auto-flow: column;
		grid-auto-columns: 1fr;
		gap: 10px;
		margin: 0 0 18px;
		padding: 0;
	}
	.steps li {
		display: flex;
		align-items: center;
		gap: 9px;
		font-size: 12.5px;
		color: #98a2b3;
		background: #f7f9fc;
		border-radius: 10px;
		padding: 9px 12px;
	}
	.steps li.current {
		color: #1d4ed8;
		background: #eef4ff;
		font-weight: 600;
	}
	.steps li.done {
		color: #0f7a45;
	}
	.dot {
		flex: none;
		width: 22px;
		height: 22px;
		border-radius: 50%;
		display: grid;
		place-items: center;
		font-size: 11.5px;
		font-weight: 700;
		background: #e4e7ec;
		color: #475467;
	}
	.current .dot {
		background: #2563eb;
		color: #fff;
	}
	.done .dot {
		background: #0f9d58;
		color: #fff;
	}

	.challenge {
		margin-bottom: 18px;
	}
	.stage-no {
		margin: 0 0 4px;
		font-size: 12px;
		font-weight: 700;
		color: #667085;
		letter-spacing: 0.04em;
		text-transform: uppercase;
	}
	.challenge h3 {
		margin: 0 0 8px;
		font-size: 19px;
		color: #101828;
	}
	.lockpill {
		display: inline-block;
		font-size: 12.5px;
		font-weight: 600;
		color: #475467;
		background: #f2f4f7;
		border: 1px solid #e4e7ec;
		border-radius: 999px;
		padding: 5px 12px;
	}

	.controls {
		display: grid;
		grid-template-columns: 1fr 1fr auto;
		gap: 26px;
		align-items: end;
		padding-bottom: 20px;
		border-bottom: 1px solid #eef1f7;
	}
	.control label {
		display: flex;
		justify-content: space-between;
		font-size: 13.5px;
		font-weight: 600;
		color: #344054;
		margin-bottom: 8px;
	}
	.control label strong {
		color: #2563eb;
		font-variant-numeric: tabular-nums;
	}
	.control.locked label,
	.control.locked label strong {
		color: #98a2b3;
	}
	input[type='range'] {
		width: 100%;
		accent-color: #2563eb;
		height: 22px;
	}
	input[type='range']:disabled {
		accent-color: #98a2b3;
		cursor: not-allowed;
	}
	input[type='range']:focus-visible {
		outline: 3px solid #93c5fd;
		outline-offset: 3px;
		border-radius: 6px;
	}
	.ends {
		display: flex;
		justify-content: space-between;
		font-size: 11.5px;
		color: #98a2b3;
	}
	.run {
		background: #2563eb;
		color: #fff;
		border: 0;
		border-radius: 10px;
		padding: 15px 24px;
		font-size: 15px;
		font-weight: 700;
		cursor: pointer;
		white-space: nowrap;
	}
	.run:hover:not(:disabled) {
		background: #1d4ed8;
	}
	.run:disabled {
		opacity: 0.45;
		cursor: not-allowed;
	}
	.run:focus-visible {
		outline: 3px solid #93c5fd;
		outline-offset: 3px;
	}
	.run.next {
		margin-top: 12px;
		background: #0f9d58;
	}
	.run.next:hover {
		background: #0b8049;
	}

	.stage {
		position: relative;
		margin: 6px 0 4px;
	}
	canvas {
		width: 100%;
		height: 340px;
		display: block;
	}
	.badge {
		position: absolute;
		top: 12px;
		left: 12px;
		background: #fef6e7;
		color: #8a5a00;
		font-size: 12.5px;
		font-weight: 700;
		padding: 8px 14px;
		border-radius: 8px;
	}
	.badge.good {
		background: #e7f5ec;
		color: #0f7a45;
	}

	.footer {
		display: grid;
		grid-template-columns: minmax(240px, 0.85fr) 1.15fr;
		gap: 26px;
		padding-top: 18px;
		border-top: 1px solid #eef1f7;
	}
	.readouts {
		display: grid;
		gap: 10px;
		align-content: start;
	}
	.readout {
		background: #f7f9fc;
		border-radius: 10px;
		padding: 11px 14px;
		display: flex;
		justify-content: space-between;
		font-size: 13px;
	}
	.readout span {
		color: #667085;
	}
	.readout strong {
		color: #101828;
		font-variant-numeric: tabular-nums;
	}

	.formula {
		background: #f4f7ff;
		border: 1px solid #dde6fb;
		border-radius: 10px;
		padding: 11px 14px;
		margin-bottom: 12px;
	}
	.formula span {
		display: block;
		font-size: 11.5px;
		color: #667085;
		margin-bottom: 4px;
	}
	.formula code {
		font-size: 14.5px;
		color: #1d4ed8;
		font-weight: 600;
	}
	.status {
		background: #fef6e7;
		border-left: 3px solid #f0a830;
		padding: 11px 14px;
		border-radius: 0 8px 8px 0;
		font-size: 13.5px;
		color: #7a5200;
		margin: 0 0 10px;
	}
	.status.good {
		background: #e7f5ec;
		border-left-color: #0f9d58;
		color: #0f7a45;
	}
	.debrief {
		font-size: 13.5px;
		color: #344054;
		line-height: 1.55;
		margin: 0;
	}
	.hint {
		font-size: 13.5px;
		color: #344054;
		background: #f7f9fc;
		padding: 10px 14px;
		border-radius: 8px;
		margin: 0 0 8px;
	}
	.hintbtn {
		background: none;
		border: 0;
		color: #2563eb;
		font-weight: 600;
		font-size: 13.5px;
		cursor: pointer;
		padding: 4px 0;
	}
	.hintbtn:focus-visible {
		outline: 3px solid #93c5fd;
		outline-offset: 3px;
	}

	.done {
		margin-top: 20px;
		background: #e7f5ec;
		border: 1px solid #b7e2c7;
		border-radius: 14px;
		padding: 18px 20px;
	}
	.done h3 {
		margin: 0 0 6px;
		color: #0f7a45;
		font-size: 17px;
	}
	.done p {
		margin: 0 0 12px;
		color: #1e4d33;
		font-size: 14px;
		line-height: 1.55;
	}

	.attempts {
		margin-top: 20px;
		padding-top: 16px;
		border-top: 1px solid #eef1f7;
	}
	.attempts h3 {
		font-size: 13px;
		color: #344054;
		margin: 0 0 10px;
	}
	.attempts h3 span {
		color: #98a2b3;
		font-weight: 400;
	}
	.attempts ul {
		list-style: none;
		margin: 0;
		padding: 0;
		display: grid;
		gap: 5px;
		max-height: 150px;
		overflow-y: auto;
	}
	.attempts li {
		display: grid;
		grid-template-columns: 64px 1fr auto;
		gap: 12px;
		font-size: 12.5px;
		color: #475467;
		padding: 7px 10px;
		border-radius: 7px;
		background: #f9fafb;
		font-variant-numeric: tabular-nums;
	}
	.attempts li.good {
		background: #e7f5ec;
		color: #0f7a45;
		font-weight: 600;
	}
	.n {
		color: #98a2b3;
	}

	.sr-only {
		position: absolute;
		width: 1px;
		height: 1px;
		padding: 0;
		margin: -1px;
		overflow: hidden;
		clip: rect(0, 0, 0, 0);
		white-space: nowrap;
		border: 0;
	}

	@media (max-width: 860px) {
		.controls,
		.footer {
			grid-template-columns: 1fr;
		}
		.steps {
			grid-auto-flow: row;
		}
		.lab {
			padding: 20px 16px;
		}
		.lab-head {
			flex-direction: column;
		}
	}
</style>
