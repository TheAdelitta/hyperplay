<script>
  import { onMount } from 'svelte';
  const examples = [
    {title:'Projectile motion',subtitle:'Physics · playable sample',caption:'Watch how a change in angle affects the arc.',color:'#1375e6',tag:'Explore'},
    {title:'Free fall',subtitle:'Physics · concept preview',caption:'Watch distance grow faster with each second.',color:'#189368',tag:'Observe'},
    {title:'Quadratic equations',subtitle:'Algebra · concept preview',caption:'Watch a changing coefficient reshape the curve.',color:'#cc8622',tag:'Visualize'}
  ];
  let current=0,progress=0,paused=false,reduced=false,frame,last=0;
  $: item=examples[current];
  $: curve=current===0?'M30 152 Q190 0 410 152':current===1?'M95 30 Q100 68 140 152':`M30 32 Q220 ${165+55*Math.sin(progress*2*Math.PI)} 410 32`;
  function position(index,t){
    const control=index===0?[[30,152],[190,0],[410,152]]:index===1?[[95,30],[100,68],[140,152]]:[[30,32],[220,165+55*Math.sin(t*2*Math.PI)],[410,32]];
    const k=1-t;
    return {x:k*k*control[0][0]+2*k*t*control[1][0]+t*t*control[2][0],y:k*k*control[0][1]+2*k*t*control[1][1]+t*t*control[2][1]};
  }
  $: dot=position(current,progress);
  function step(n){current=(current+n+examples.length)%examples.length;progress=0;last=0}
  function tick(now){
    if(!last)last=now;
    const delta=Math.min(now-last,100);last=now;
    if(!paused&&!reduced&&!document.hidden){progress+=delta/7000;if(progress>=1){progress-=1;current=(current+1)%examples.length}}
    frame=requestAnimationFrame(tick);
  }
  onMount(()=>{reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;if(!reduced)frame=requestAnimationFrame(tick);return()=>cancelAnimationFrame(frame)});
</script>
<div class="hero-visual" role="group" aria-label="Learning examples">
  <div class="small-label"><span>A SAMPLE LEARNING MOMENT</span><span class="carousel-controls"><button type="button" on:click={()=>step(-1)} aria-label="Previous example">‹</button><span>{current+1}/3</span><button type="button" on:click={()=>step(1)} aria-label="Next example">›</button></span></div>
  <div class="paper-head"><span class="paper-icon">📄</span><div><strong>{item.title}</strong><small>{item.subtitle}</small></div><span class="mini-arrow">→</span></div>
  <div class="mini-play"><svg viewBox="0 0 440 190" role="img" aria-label={item.title+' animated concept preview'}><path d="M20 152H420 M20 115H420 M20 78H420" stroke="#dceaf7" stroke-width="1"/><path d={curve} fill="none" stroke={item.color} stroke-width="4" stroke-linecap="round"/><circle cx={dot.x} cy={dot.y} r="9" fill={item.color}/></svg><span class="mini-caption">{item.caption}</span></div>
  <div class="paper-foot"><span class="chip blue">{item.tag}</span><span class="carousel-progress" aria-hidden="true"><i style:transform={'scaleX('+progress+')'}></i></span><button type="button" class="carousel-pause" on:click={()=>paused=!paused} aria-label={paused?'Resume animated examples':'Pause animated examples'}>{paused?'Play':'Pause'}</button></div>
</div>
