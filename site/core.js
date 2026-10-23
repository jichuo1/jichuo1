(function(root){'use strict';
const clamp=(v,a,b)=>Math.min(b,Math.max(a,v));
function clip(poly,value,keepPositive){const result=[];for(let i=0;i<poly.length;i++){const a=poly[i],b=poly[(i+1)%poly.length],va=value(a),vb=value(b),ina=keepPositive?va>=-1e-8:va<=1e-8,inb=keepPositive?vb>=-1e-8:vb<=1e-8;if(ina)result.push(a);if(ina!==inb){const t=va/(va-vb);result.push({x:a.x+(b.x-a.x)*t,y:a.y+(b.y-a.y)*t})}}return result}
function curl(rect,pointer){const C={x:rect.right,y:rect.bottom},D={x:clamp(pointer.x,rect.left-(rect.right-rect.left),C.x-.001),y:clamp(pointer.y,rect.top-(rect.bottom-rect.top),C.y-.001)},dx=C.x-D.x,dy=C.y-D.y,d=Math.hypot(dx,dy),n={x:dx/d,y:dy/d},m={x:(C.x+D.x)/2,y:(C.y+D.y)/2};const radius=Math.min(d*.24,8+Math.sqrt(d)*1.2,48),a=Math.PI*radius/2;
const signed=p=>(p.x-m.x)*n.x+(p.y-m.y)*n.y;
const map=p=>{const q=signed(p);let f=q,z=0;if(q>-a&&q<a){const theta=(q+a)/radius;f=-a+radius*Math.sin(theta);z=radius*(1-Math.cos(theta))}else if(q>=a){f=-q;z=2*radius}return{x:p.x+n.x*(f-q),y:p.y+n.y*(f-q),z}};
const polygon=[{x:rect.left,y:rect.top},{x:C.x,y:rect.top},C,{x:rect.left,y:C.y}];
const front=clip(polygon,p=>signed(p)+a,false),back=clip(polygon,signed,true),band=clip(clip(polygon,p=>signed(p)+a,true),signed,false);
function sample(poly){if(!poly.length)return[];const out=[];for(let i=0;i<poly.length;i++){const p=poly[i],q=poly[(i+1)%poly.length];const steps=clamp(Math.ceil(Math.hypot(q.x-p.x,q.y-p.y)/12),1,96);for(let j=0;j<steps;j++){const t=j/steps;out.push(map({x:p.x+(q.x-p.x)*t,y:p.y+(q.y-p.y)*t}))}}return out}
return{front,back:sample(back),band:sample(band),corner:map(C),radius,d,normal:n,midpoint:m,map,signed};}
const api={curl,clip,weight:(x,y)=>Math.pow(clamp((x-.3)/.7,0,1),2)*Math.pow(clamp((y-.38)/.62,0,1),2),hazard:t=>Math.max(0,Math.min(.0012,(t-40)*.000003)),probability:(rate,dt)=>1-Math.exp(-rate*Math.max(0,dt)),spring:(x,v,target,dt)=>{dt=Math.max(0,Math.min(.04,dt));const n=Math.max(1,Math.ceil(dt/.008));for(let i=0;i<n;i++){const h=dt/n;v+=(85*(target-x)-17*v)*h;x+=v*h}return[x,v]}};if(typeof module!=='undefined')module.exports=api;else root.PaperCore=api;
})(globalThis);
