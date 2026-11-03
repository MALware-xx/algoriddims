(()=>{const BASE='https://cdn.jsdelivr.net/gh/MALware-xx/algoriddims@198db24f39a130a4e2159e499f5b19f69389099a/ready-oas-host/unified/dist/assets/ready-navigation-v5.js';const COMBINE={
'quick-start':'Foundation plan. Use it before the more detailed household topics. Included in READY/11 Household Library and READY/12 Complete Library.',
'power':'Pairs especially well with READY/09 Home Systems for property dependencies and READY/08 Offline for communications and payment fallback. Included in READY/11 Household Library and READY/12 Complete Library.',
'water':'Pairs with READY/07 Food + Water for pantry continuity and READY/09 Home Systems for supply and shut-off information. Included in READY/11 Household Library and READY/12 Complete Library.',
'weather-winter':'Often used with READY/02 Power and READY/09 Home Systems because severe weather exposes electricity, heating, travel and property dependencies. Included in READY/11 Household Library and READY/12 Complete Library.',
'family':'Pairs with READY/08 Offline so contacts and meeting plans remain usable without phones, and READY/01 Quick Start as the household baseline. Included in READY/11 Household Library and READY/12 Complete Library.',
'pets':'Complements READY/03 Water and READY/07 Food + Water where pet supplies affect household reserves. Included in READY/11 Household Library and READY/12 Complete Library.',
'food-water':'Pairs directly with READY/02 Power for cooking and refrigeration dependencies and READY/03 Water for household demand. Included in READY/11 Household Library and READY/12 Complete Library.',
'offline':'A cross-cutting plan supporting Family, Power, Home Systems and Business whenever phones, internet or digital payments are unavailable. Included in READY/11 Household Library and READY/12 Complete Library.',
'home-systems':'Provides the property-systems layer behind READY/02 Power, READY/03 Water and READY/04 Weather / Winter. Included in READY/11 Household Library and READY/12 Complete Library.',
'business':'The business-continuity layer of READY/. Pair with READY/08 Offline for communications fallback. Included in READY/12 Complete Library, but not READY/11 Household Library.',
'household-library':'Combines READY/01–09 with the READY/11 household master into one maintained household system. READY/10 Business is intentionally separate; choose READY/12 if you need household and business continuity together.',
'complete-library':'The complete READY/ system: all household topic plans, READY/10 Business, the READY/11 household master and READY/12 complete master, connecting household, income and business continuity from three days through longer-term recovery.'
};
function load(){if(document.querySelector('script[data-ready-v5]'))return;const s=document.createElement('script');s.src=BASE;s.defer=true;s.dataset.readyV5='1';document.head.appendChild(s)}
function patch(){const m=location.pathname.match(/\/topics\/([^/?]+)\.html$/);if(!m||!COMBINE[m[1]])return false;const p=document.querySelector('.ready-product-spec .r-combine p');if(!p)return false;p.textContent=COMBINE[m[1]];return true}
function run(){load();let n=0;const t=setInterval(()=>{if(patch()||n++>80)clearInterval(t)},50)}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',run,{once:true});else run();})();