const assert=require('node:assert/strict'),p=require('../site/core.js');
const rect={left:12,top:8,right:900,bottom:1200};let count=0;
for(const D of [{x:899.999,y:1199.999},{x:800,y:1199},{x:899,y:500},{x:450,y:600},{x:12,y:8},{x:-875,y:-1183},{x:950,y:1300}]){const g=p.curl(rect,D);for(const list of [g.front,g.back,g.band])for(const q of list){assert(Number.isFinite(q.x)&&Number.isFinite(q.y));count++}const clamped={x:Math.max(-876,Math.min(899.999,D.x)),y:Math.max(-1184,Math.min(1199.999,D.y))};assert(Math.hypot(g.corner.x-clamped.x,g.corner.y-clamped.y)<1e-7);assert(g.radius<=g.d/Math.PI);count+=2;}
const area=poly=>Math.abs(poly.reduce((v,a,i)=>{const b=poly[(i+1)%poly.length];return v+a.x*b.y-a.y*b.x},0))/2;
let last=Infinity;for(let t=0;t<=1;t+=.05){const g=p.curl(rect,{x:899-1700*t,y:1199-2300*t});const a=area(g.front);assert(a<=last+1e-5);last=a;count++}
const g=p.curl(rect,{x:500,y:800}),R=g.radius,a=Math.PI*R/2,n=g.normal,m=g.midpoint;
for(const q of [-a-.00001,-a+.00001,a-.00001,a+.00001]){const pt={x:m.x+n.x*q,y:m.y+n.y*q};const mapped=g.map(pt);assert(Number.isFinite(mapped.z));count++}
assert(p.curl(rect,{x:-876,y:-1184}).front.length===0);count++;
console.log(`${count} finite-coordinate and cylindrical-curl geometry assertions passed`);
