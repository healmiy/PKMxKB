const autoLoadDuration = 5; //In Seconds
const eventList = ["keydown", "mousemove", "wheel", "touchmove", "touchstart", "touchend"];

const autoLoadTimeout = setTimeout(runScripts, autoLoadDuration * 1000);

eventList.forEach(function(event) {
    window.addEventListener(event, triggerScripts, { passive: true })
});

function triggerScripts() {
    runScripts();
    clearTimeout(autoLoadTimeout);
    eventList.forEach(function(event) {
         window.removeEventListener(event, triggerScripts, { passive: true });
    });
}

function runScripts() {
    (function(w,d){!function(d,e,f,g){d[f]=d[f]||{};d[f].executed=[];d.zaraz={deferred:[],listeners:[]};d.zaraz.q=[];d.zaraz._f=function(h){return function(){var i=Array.prototype.slice.call(arguments);d.zaraz.q.push({m:h,a:i})}};for(const j of["track","set","ecommerce","debug"])d.zaraz[j]=d.zaraz._f(j);d.zaraz.init=()=>{var k=e.getElementsByTagName(g)[0],l=e.createElement(g),m=e.getElementsByTagName("title")[0];d[f].c=e.cookie;m&&(d[f].t=e.getElementsByTagName("title")[0].text);d[f].x=Math.random();d[f].w=d.screen.width;d[f].h=d.screen.height;d[f].j=d.innerHeight;d[f].e=d.innerWidth;d[f].l=d.location.href;d[f].r=e.referrer;d[f].k=d.screen.colorDepth;d[f].n=e.characterSet;d[f].o=(new Date).getTimezoneOffset();d[f].q=[];for(;d.zaraz.q.length;){const t=d.zaraz.q.shift();d[f].q.push(t)}l.defer=!0;for(const u of[localStorage,sessionStorage])Object.keys(u||{}).filter((w=>w.startsWith("_zaraz_"))).forEach((v=>{try{d[f]["z_"+v.slice(7)]=JSON.parse(u.getItem(v))}catch{d[f]["z_"+v.slice(7)]=u.getItem(v)}}));l.referrerPolicy="origin";l.src="https://to.adsvise.me/insight.js?z="+btoa(encodeURIComponent(JSON.stringify(d[f])));k.parentNode.insertBefore(l,k)};["complete","interactive"].includes(e.readyState)?zaraz.init():d.addEventListener("DOMContentLoaded",zaraz.init)}(w,d,"zarazData","script");})(window,document);
}


