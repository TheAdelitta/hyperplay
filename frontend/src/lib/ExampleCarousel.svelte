<script>
  import { onMount, onDestroy } from 'svelte';

  // Plot area inside the 440 x 210 viewBox.
  const X0 = 58, X1 = 420, Y0 = 162, Y1 = 22;

  const examples = [
    {
      title: 'Projectile motion',
      subtitle: 'Physics',
      caption: 'At 45°, a ball launched at 20 m/s lands about 41 m away.',
      color: '#1375e6',
      xLabel: 'Distance (m)', yLabel: 'Height (m)',
      xMax: 45, yMax: 12,
      // y = x·tan45° − g·x² / (2·v²·cos²45°), v = 20 m/s, g = 9.8
      f: (x) => x - (9.8 * x * x) / (2 * 400 * 0.5),
      xEnd: 40.8
    },
    {
      title: 'Compound interest',
      subtitle: 'Mathematics',
      caption: 'At 7% a year, $1,000 grows to about $7,600 in 30 years.',
      color: '#cc8622',
      xLabel: 'Years', yLabel: 'Balance ($)',
      xMax: 30, yMax: 8000,
      f: (t) => 1000 * Math.pow(1.07, t),
      xEnd: 30
    },
    {
      title: 'Population growth',
      subtitle: 'Biology',
      caption: 'Growth slows as the population nears its carrying capacity of 500.',
      color: '#189368',
      xLabel: 'Years', yLabel: 'Population',
      xMax: 30, yMax: 550,
      // logistic: K = 500, r = 0.3, N0 = 20
      f: (t) => 500 / (1 + 24 * Math.exp(-0.3 * t)),
      xEnd: 30
    }
  ];

  let current = 0, progress = 1, frame, reduced = false;
  $: item = examples[current];
  $: points = sample(item);
  $: shown = points.slice(0, Math.max(2, Math.ceil(points.length * progress)));
  $: path = shown.map((p, i) => (i ? 'L' : 'M') + p.x.toFixed(1) + ' ' + p.y.toFixed(1)).join(' ');
  $: dot = shown[shown.length - 1];

  function px(x, e) { return X0 + (x / e.xMax) * (X1 - X0); }
  function py(y, e) { return Y0 - (Math.max(0, y) / e.yMax) * (Y0 - Y1); }
  function sample(e) {
    return Array.from({ length: 81 }, (_, i) => {
      const x = (e.xEnd * i) / 80;
      return { x: px(x, e), y: py(e.f(x), e) };
    });
  }
  function fmt(v) { return v >= 1000 ? v.toLocaleString() : String(v); }

  // Draw the curve once (about 2.5 s) each time a card is shown, then stop.
  function play() {
    cancelAnimationFrame(frame);
    if (reduced) { progress = 1; return; }
    progress = 0;
    const start = performance.now();
    const tick = (now) => {
      progress = Math.min(1, (now - start) / 2500);
      if (progress < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
  }
  function step(n) { current = (current + n + examples.length) % examples.length; play(); }

  onMount(() => { reduced = matchMedia('(prefers-reduced-motion: reduce)').matches; play(); });
  onDestroy(() => cancelAnimationFrame(frame));
</script>

<div class="hero-visual" role="group" aria-roledescription="carousel" aria-label="Sample learning moments">
  <div class="small-label">
    <span>A SAMPLE LEARNING MOMENT</span>
    <span class="carousel-controls">
      <button type="button" on:click={() => step(-1)} aria-label="Previous example">‹</button>
      <span aria-live="polite">{current + 1}/{examples.length}</span>
      <button type="button" on:click={() => step(1)} aria-label="Next example">›</button>
    </span>
  </div>
  <div class="paper-head">
    <span class="paper-icon" aria-hidden="true">📄</span>
    <div><strong>{item.title}</strong><small>{item.subtitle}</small></div>
  </div>
  <div class="mini-graph">
    <svg viewBox="0 0 440 210" role="img" aria-label="{item.title}: {item.yLabel} against {item.xLabel}. {item.caption}">
      {#each [0.25, 0.5, 0.75, 1] as g}
        <line x1={X0} x2={X1} y1={Y0 - g * (Y0 - Y1)} y2={Y0 - g * (Y0 - Y1)} class="grid" />
      {/each}
      <line x1={X0} x2={X1} y1={Y0} y2={Y0} class="axis" />
      <line x1={X0} x2={X0} y1={Y1} y2={Y0} class="axis" />
      <text x={X0 - 8} y={Y0 + 4} class="tick" text-anchor="end">0</text>
      <text x={X0 - 8} y={Y1 + 4} class="tick" text-anchor="end">{fmt(item.yMax)}</text>
      <text x={X1} y={Y0 + 18} class="tick" text-anchor="end">{item.xMax}</text>
      <text x={(X0 + X1) / 2} y={Y0 + 36} class="axis-label" text-anchor="middle">{item.xLabel}</text>
      <text x="16" y={(Y0 + Y1) / 2} class="axis-label" text-anchor="middle" transform="rotate(-90 16 {(Y0 + Y1) / 2})">{item.yLabel}</text>
      <path d={path} fill="none" stroke={item.color} stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />
      {#if dot}<circle cx={dot.x} cy={dot.y} r="7" fill={item.color} />{/if}
    </svg>
  </div>
  <p class="mini-caption-text">{item.caption}</p>
</div>

<style>
  .mini-graph {
    border: 1px solid #d8e9f7;
    border-radius: 13px;
    background: linear-gradient(#f7fbff, #eef6fd);
    padding: 6px 8px 0;
  }
  svg { width: 100%; height: auto; display: block; }
  .grid { stroke: #dceaf7; stroke-width: 1; }
  .axis { stroke: #89b0d7; stroke-width: 2; }
  .tick { font-size: 11px; fill: #6a83a1; }
  .axis-label { font-size: 12px; font-weight: 700; fill: #506e91; }
  .mini-caption-text { margin: 12px 2px 0; font-size: 14px; color: #506e91; line-height: 1.45; }
</style>
