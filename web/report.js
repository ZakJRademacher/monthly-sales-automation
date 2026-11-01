'use strict';
const data=JSON.parse(document.getElementById('report-data').textContent);
const $=id=>document.getElementById(id);
const number=(v,places=2)=>v.toLocaleString('en-US',{minimumFractionDigits:places,maximumFractionDigits:places});
// Source money stays in integer ten-thousandths; display cents use half-up.
const money=units=>{const cents=Math.floor((Math.abs(units)+50)/100);return(units<0?'−':'')+Math.floor(cents/100).toLocaleString('en-US')+'.'+String(cents%100).padStart(2,'0');};
const percent=v=>(v<0?'−':'+')+number(Math.abs(v)*100,1)+'%';
const s=data.summary;
$('sales-value').textContent=money(s.current.sales_units);$('prior-sales').textContent=money(s.prior.sales_units);
$('sales-change').textContent=percent(s.sales_change_pct);$('order-value').textContent=number(s.current.orders,0);
$('order-change').textContent=percent(s.orders_change_pct);$('aov-value').textContent=number(s.current.average_order);$('aov-change').textContent=percent(s.average_order_change_pct);
const W=720,H=285,L=53,R=18,T=18,B=35,max=100000;
const x=day=>L+(day-1)/29*(W-L-R),y=units=>T+(1-units/10000/max)*(H-T-B);
const path=key=>data.trend.map((p,i)=>(i?'L':'M')+x(p.day).toFixed(2)+','+y(p[key]).toFixed(2)).join(' ');
const current=path('current'),prior=path('prior');
const grid=[0,25000,50000,75000,100000].map(v=>`<line class="grid-line" x1="${L}" x2="${W-R}" y1="${y(v*10000)}" y2="${y(v*10000)}"/><text class="axis-label" x="${L-12}" y="${y(v*10000)+4}" text-anchor="end">${v===0?'0':v/1000+'k'}</text>`).join('');
const ticks=[1,5,10,15,20,25,30].map(d=>`<text class="axis-label" x="${x(d)}" y="${H-10}" text-anchor="middle">${d===1?'01 Dec':d}</text>`).join('');
$('trend-chart').innerHTML=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Matched December 1–30 cumulative sales. Current 2018 ends at ${money(s.current.sales_units)}, prior 2017 at ${money(s.prior.sales_units)}. Exact selected-day values are shown below."><defs><linearGradient id="area-blue" x1="0" y1="0" x2="0" y2="1"><stop stop-color="var(--blue)" stop-opacity=".12"/><stop offset="1" stop-color="var(--blue)" stop-opacity="0"/></linearGradient></defs>${grid}${ticks}<path class="trend-fill" d="${current} L${x(30)},${y(0)} L${L},${y(0)} Z"/><path class="trend-prior trend-path" d="${prior}"/><path class="trend-current trend-path" d="${current}"/><line id="cursor" class="chart-cursor" y1="${T}" y2="${H-B}"/><circle id="prior-focus" class="focus-point" r="5" fill="var(--prior)"/><circle id="current-focus" class="focus-point" r="6" fill="var(--blue)"/></svg>`;
document.querySelectorAll('.trend-path').forEach(p=>p.style.setProperty('--path-length',p.getTotalLength()));
function selectDay(day){
  const p=data.trend[day-1];$('day-range').value=String(day);$('day-label').textContent=String(day).padStart(2,'0')+' DEC';
  $('day-current').textContent=money(p.current);$('day-prior').textContent=money(p.prior);
  const gap=p.current-p.prior;$('day-gap').textContent=(gap<0?'−':'+')+money(Math.abs(gap));$('day-gap').className=gap<0?'negative':'positive';
  $('cursor').setAttribute('x1',x(day));$('cursor').setAttribute('x2',x(day));
  for(const key of ['current','prior']){$(key+'-focus').setAttribute('cx',x(day));$(key+'-focus').setAttribute('cy',y(p[key]));}
}
$('day-range').addEventListener('input',e=>selectDay(Number(e.target.value)));
$('trend-chart').addEventListener('pointermove',e=>{if(e.pointerType==='touch')return;const rect=e.currentTarget.getBoundingClientRect();const chartX=(e.clientX-rect.left)/rect.width*W;selectDay(Math.max(1,Math.min(30,Math.round(1+(chartX-L)/(W-L-R)*29))));});
$('trend-chart').addEventListener('pointerleave',()=>selectDay(Number($('day-range').value)));
const maximum=Math.max(...Object.values(data.drivers).flat().map(r=>Math.abs(r.change_units)));
for(const scope of ['category','region']){
  $(scope+'-drivers').innerHTML=data.drivers[scope].map((r,i)=>{
    const negative=r.change_units<0,width=46*Math.abs(r.change_units)/maximum;
    const row=document.createElement('div');row.className='driver-row';row.tabIndex=0;
    const detail=`${r.member}: current ${money(r.current_sales_units)}, prior ${money(r.prior_sales_units)}, change ${percent(r.change_pct)}.`;
    row.setAttribute('aria-label',detail);row.title=detail;
    row.innerHTML=`<div class="driver-top"><span></span><strong class="${negative?'negative':'positive'}">${negative?'−':'+'}${money(Math.abs(r.change_units))}</strong></div><div class="driver-track" aria-hidden="true"><span class="${negative?'negative':'positive'}" style="left:${negative?50-width:50}%;width:${width}%;--delay:${i*.07}s"></span></div><div class="driver-meta">Current ${money(r.current_sales_units)} · Prior ${money(r.prior_sales_units)}</div>`;
    row.querySelector('.driver-top span').textContent=r.member;return row.outerHTML;
  }).join('');
}
function replay(){
  if(matchMedia('(prefers-reduced-motion: reduce)').matches)return;
  document.querySelectorAll('.trend-path,.driver-track>span').forEach(e=>{const animations=e.getAnimations();animations.forEach(a=>{a.cancel();a.play();});});
}
$('replay').addEventListener('click',replay);selectDay(30);

// Navigation follows the visible report section; no data state is changed.
document.querySelector(".contributions").id="contributions";document.querySelector(".decision").id="decision";
const sectionLinks=[...document.querySelectorAll(".studio-rail nav a")];
const sectionObserver=new IntersectionObserver(entries=>{for(const entry of entries){if(entry.isIntersecting){sectionLinks.forEach(a=>a.toggleAttribute("aria-current",a.hash==="#"+entry.target.id));}}},{rootMargin:"-10% 0px -60% 0px"});
for(const id of ["overview","contributions","decision"])sectionObserver.observe(document.getElementById(id));
