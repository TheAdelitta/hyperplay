<script>
  import { onDestroy } from 'svelte';
  const G=9.81,X=7,Y=5.2,target=50;
  let angle=45,speed=20,shots=[],progress=0,frame;
  function physics(a,v){const rad=a*Math.PI/180;return {rad,v,range:v*v*Math.sin(2*rad)/G,height:v*v*Math.sin(rad)**2/(2*G),time:2*v*Math.sin(rad)/G}}
  function point(f,p){const x=p.range*f,y=x*Math.tan(p.rad)-G*x*x/(2*p.v*p.v*Math.cos(p.rad)**2);return {x:30+x*X,y:238-Math.max(0,y)*Y}}
  function trajectory(p){return Array.from({length:61},(_,i)=>{const q=point(i/60,p);return(i?'L':'M')+q.x.toFixed(1)+' '+q.y.toFixed(1)}).join(' ')}
  $: latest=shots.length?shots[shots.length-1]:null;
  $: ball=latest?point(progress,latest.physics):null;
  $: previewRadians=Number(angle)*Math.PI/180;
  $: barrelX=30+39*Math.cos(previewRadians);
  $: barrelY=236-39*Math.sin(previewRadians);
  $: arcX=30+53*Math.cos(previewRadians);
  $: arcY=236-53*Math.sin(previewRadians);
  $: labelX=30+72*Math.cos(previewRadians/2);
  $: labelY=236-72*Math.sin(previewRadians/2);
  function run(){
    if(frame)cancelAnimationFrame(frame);
    const p=physics(Number(angle),Number(speed)),delta=p.range-target;
    shots=[...shots,{number:shots.length+1,angle:Number(angle),speed:Number(speed),physics:p,hit:Math.abs(delta)<=1,difference:Math.abs(delta),direction:delta<0?'short':'past the target'}];
    progress=0;
    if(matchMedia('(prefers-reduced-motion: reduce)').matches){progress=1;return}
    const start=performance.now();
    function tick(now){progress=Math.min(1,(now-start)/1150);if(progress<1)frame=requestAnimationFrame(tick);else frame=null}
    frame=requestAnimationFrame(tick);
  }
  function reset(){if(frame)cancelAnimationFrame(frame);shots=[];progress=0}
  onDestroy(()=>{if(frame)cancelAnimationFrame(frame)});
</script>
<div class="experiment-board">
  <div class="experiment-heading"><div><div class="eyebrow">YOUR EXPERIMENT</div><h3>Can you land the ball at 50 meters?</h3><p>Use the rule below to choose an angle and speed. Watch the launcher tilt as you adjust it, then run a shot to test your prediction.</p></div><span class="sim-tag">INTERACTIVE SAMPLE</span></div>
  <div class="concept-rule"><div><span class="concept-rule-label">THE RULE YOU CAN USE</span><strong class="formula">R = v² sin(2θ) / g</strong></div><p><b>R</b> is landing distance, <b>v</b> is launch speed, <b>θ</b> is the angle, and <b>g</b> is gravity (9.81 m/s²). Try to make <b>R = 50 m</b>.</p></div>
  <div class="experiment-toolbar"><div class="slider-row"><label for="angle">Launch angle <output>{angle}°</output></label><input id="angle" type="range" min="10" max="80" bind:value={angle}/><div class="slider-ends"><span>10°</span><span>80°</span></div></div><div class="slider-row"><label for="speed">Initial speed <output>{speed} m/s</output></label><input id="speed" type="range" min="10" max="28" bind:value={speed}/><div class="slider-ends"><span>10 m/s</span><span>28 m/s</span></div></div><button class="primary run-button" type="button" on:click={run}>Run experiment →</button></div>
  <div class="experiment-stage"><div class="sim-field"><svg viewBox="0 0 640 280" role="img" aria-label="Projectile graph with previous shots and target at 50 meters"><defs><pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M 40 0 L 0 0 0 40" fill="none" stroke="#dceaf7" stroke-width="1"/></pattern></defs><rect width="640" height="280" fill="url(#grid)"/><line x1="30" y1="238" x2="610" y2="238" stroke="#819fbd" stroke-width="2"/>
    {#each shots.slice(0,-1) as shot (shot.number)}<path d={trajectory(shot.physics)} fill="none" stroke="#d39436" stroke-width="2.5" opacity=".48"/><circle cx={30+shot.physics.range*X} cy="238" r="4" fill="#d39436"/>{/each}
    <line x1="380" y1="206" x2="380" y2="242" stroke="#168657" stroke-width="2" stroke-dasharray="4 3"/><rect x="374" y="231" width="12" height="7" rx="2" fill="#168657"/><text x="380" y="198" text-anchor="middle" fill="#167b55" font-size="14" font-weight="700">Target · 50 m</text>
    {#if latest}<path d={trajectory(latest.physics)} fill="none" stroke="#1375e6" stroke-width="4" stroke-linecap="round"/><circle cx={ball.x} cy={ball.y} r="9" fill="#f2a62b"/>{/if}
    <line x1="30" y1="236" x2="87" y2="236" stroke="#6d99c8" stroke-width="1.5" stroke-dasharray="3 3"/><path d="M 83 236 A 53 53 0 0 0 {arcX} {arcY}" fill="none" stroke="#ee9a24" stroke-width="2"/><text x={labelX} y={labelY} text-anchor="middle" fill="#a86010" font-size="13" font-weight="800">{angle}°</text><line x1="30" y1="236" x2={barrelX} y2={barrelY} stroke="#153d75" stroke-width="9" stroke-linecap="round"/><circle cx="30" cy="236" r="8" fill="#153d75"/><circle cx={barrelX} cy={barrelY} r="6" fill="#f2a62b"/><text x="29" y="262" fill="#7088a2" font-size="12">0 m</text><text x="590" y="262" fill="#7088a2" font-size="12">80 m</text></svg>
    {#if latest}<div class:hit={latest.hit} class="result-overlay" aria-live="polite">{latest.hit?'HIT':'MISSED'} · Landed at {latest.physics.range.toFixed(1)} m{latest.hit?'':' · '+latest.difference.toFixed(1)+' m '+latest.direction}</div>{:else}<div class="graph-instruction">Run the experiment to reveal the trajectory.</div>{/if}</div>
    <aside class="shot-history" aria-label="Previous experiments"><div class="shot-history-title"><strong>Attempts</strong><span>{shots.length}</span></div>{#if !shots.length}<p>Your results will appear here after the first run.</p>{:else}<ol>{#each [...shots].reverse() as shot (shot.number)}<li><span>#{shot.number} · {shot.angle}° · {shot.speed} m/s</span><strong class:correct={shot.hit} class:try-again={!shot.hit}>{shot.physics.range.toFixed(1)} m · {shot.hit?'Hit':'Miss'}</strong></li>{/each}</ol>{/if}</aside></div>
  <div class="experiment-bottom"><div class="sim-stats"><div><small>Range</small><strong>{latest?latest.physics.range.toFixed(1)+' m':'—'}</strong></div><div><small>Max height</small><strong>{latest?latest.physics.height.toFixed(1)+' m':'—'}</strong></div><div><small>Time in air</small><strong>{latest?latest.physics.time.toFixed(1)+' s':'—'}</strong></div></div><div class="experiment-feedback"><p class:success={latest?.hit} class="challenge-feedback" aria-live="polite">{#if !latest}Choose your launch direction and speed, then test your prediction.{:else if latest.hit}Excellent! You hit the target after {shots.length} {shots.length===1?'run':'runs'}. Compare your previous paths to see what changed.{:else}You landed {latest.difference.toFixed(1)} m {latest.direction}. Adjust a slider and try again.{/if}</p><details class="hint"><summary>Need a hint?</summary>{#if Number(speed)*Number(speed)/G<49}<p>At {speed} m/s, even a 45° launch can travel only {(Number(speed)*Number(speed)/G).toFixed(1)} m. What happens if you raise the speed?</p>{:else if latest?.direction==='past the target'}<p>Your last shot went too far. Try a little less speed, or move the angle away from 45°, where range is greatest.</p>{:else if latest}<p>Your last shot fell short. Try more speed, or move the angle closer to 45°, where range is greatest.</p>{:else}<p>At a fixed speed, 45° gives the greatest range in this ideal model. Speed has a squared effect, so a small speed change can make a big difference.</p>{/if}</details></div></div>
  <div class="experiment-foot"><span>Ideal model · g = 9.81 m/s² · no air resistance · equal launch and landing heights</span>{#if shots.length}<button class="reset-challenge" type="button" on:click={reset}>Clear attempts</button>{/if}</div>
</div>
