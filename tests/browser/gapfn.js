(t)=>{const h=document.getElementById('hero-'+t);const hb=h.getBoundingClientRect().bottom;let sec=h.nextElementSibling;while(sec&&!sec.offsetParent)sec=sec.nextElementSibling;
let best=null;sec.querySelectorAll('*').forEach(e=>{if(!e.offsetParent&&getComputedStyle(e).position!=='fixed')return;const r=e.getBoundingClientRect();if(r.height<1||r.width<1)return;if(!best||r.top<best[1])best=[e.id||e.className,r.top]});
return [best[0],Math.round(best[1]-hb)]}
