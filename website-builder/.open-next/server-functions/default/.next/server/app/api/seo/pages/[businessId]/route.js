(()=>{var a={};a.id=532,a.ids=[532],a.modules={261:a=>{"use strict";a.exports=require("next/dist/shared/lib/router/utils/app-paths")},3295:a=>{"use strict";a.exports=require("next/dist/server/app-render/after-task-async-storage.external.js")},9573:(a,b,c)=>{"use strict";c.r(b),c.d(b,{handler:()=>C,patchFetch:()=>B,routeModule:()=>x,serverHooks:()=>A,workAsyncStorage:()=>y,workUnitAsyncStorage:()=>z});var d={};c.r(d),c.d(d,{GET:()=>v});var e=c(95736),f=c(9117),g=c(4044),h=c(39326),i=c(32324),j=c(261),k=c(54290),l=c(85328),m=c(38928),n=c(46595),o=c(3421),p=c(17679),q=c(41681),r=c(63446),s=c(86439),t=c(51356),u=c(10641);async function v(a,{params:b}){try{let{businessId:a}=b,c=await w(a);return u.NextResponse.json({success:!0,business_id:a,pages:c,total_pages:Object.keys(c).length,generated_at:new Date().toISOString()})}catch(a){return console.error("Failed to fetch SEO pages:",a),u.NextResponse.json({success:!1,error:"Failed to fetch SEO pages",pages:{}},{status:500})}}async function w(a){let b=[{id:"hvac-repair",name:"HVAC Repair"},{id:"ac-repair",name:"AC Repair"},{id:"heating-repair",name:"Heating Repair"},{id:"plumbing-repair",name:"Plumbing Repair"},{id:"electrical-service",name:"Electrical Service"},{id:"water-heater-repair",name:"Water Heater Repair"}],c=[{id:"austin-tx",city:"Austin",state:"TX",searches:5e3},{id:"round-rock-tx",city:"Round Rock",state:"TX",searches:2e3},{id:"cedar-park-tx",city:"Cedar Park",state:"TX",searches:1500},{id:"pflugerville-tx",city:"Pflugerville",state:"TX",searches:1200}],d={};return b.forEach(a=>{var b,c;d[`/services/${a.id}`]={title:`${a.name} Services | Professional ${a.name} | Elite HVAC`,meta_description:`Professional ${a.name} services. Licensed, insured, and experienced technicians. Same-day service available. Call for free estimate.`,h1_heading:`Professional ${a.name} Services`,content:(b=a.name,`
    <div class="service-content">
      <p>Looking for reliable ${b} services? Elite HVAC provides professional ${b} solutions with 15+ years of experience. Our licensed and insured technicians deliver quality workmanship and exceptional customer service.</p>
      
      <h2>Our ${b} Services</h2>
      <ul>
        <li>Emergency ${b} (24/7 availability)</li>
        <li>Routine maintenance and inspections</li>
        <li>New installations and replacements</li>
        <li>Repairs and troubleshooting</li>
        <li>Preventive maintenance programs</li>
      </ul>
      
      <h2>Why Choose Elite HVAC?</h2>
      <ul>
        <li>✅ Licensed and insured professionals</li>
        <li>🏆 15+ years of experience</li>
        <li>⚡ Same-day service available</li>
        <li>💰 Upfront, transparent pricing</li>
        <li>🛡️ 100% satisfaction guarantee</li>
      </ul>
      
      <p><strong>Contact us today at (512) 555-0100 for expert ${b} services.</strong></p>
    </div>
  `),schema_markup:(c=a.name,{"@context":"https://schema.org","@type":"Service",name:`${c} Services`,description:`Professional ${c} services by Elite HVAC`,provider:{"@type":"LocalBusiness",name:"Elite HVAC",telephone:"(512) 555-0100",url:"https://website.hero365.workers.dev"}}),target_keywords:[a.id,`${a.id} service`,`professional ${a.id}`],page_url:`/services/${a.id}`,generation_method:"template",page_type:"service",word_count:500,created_at:new Date().toISOString()}}),c.forEach(a=>{var b,c,e;d[`/locations/${a.id}`]={title:`Elite HVAC in ${a.city}, ${a.state} | Local HVAC Services`,meta_description:`Elite HVAC provides professional HVAC services in ${a.city}, ${a.state}. Serving ${a.city} residents with quality workmanship and reliable service.`,h1_heading:`Elite HVAC - Serving ${a.city}, ${a.state}`,content:(b=a.city,c=a.state,`
    <div class="location-content">
      <p>Welcome to Elite HVAC, your trusted HVAC professionals serving ${b}, ${c} and surrounding areas. We've been providing quality HVAC services to ${b} residents for 15+ years.</p>
      
      <h2>About Our ${b} Service Area</h2>
      <p>Our local team understands the unique needs of ${b} properties and climate conditions. We're committed to providing fast, reliable service throughout ${b} and the surrounding areas.</p>
      
      <h2>Services Available in ${b}</h2>
      <ul>
        <li>🚨 Emergency repairs and service calls</li>
        <li>🔧 Routine maintenance and inspections</li>
        <li>🏠 New installations and replacements</li>
        <li>📋 Preventive maintenance programs</li>
        <li>🏢 Commercial and residential services</li>
      </ul>
      
      <h2>Why ${b} Residents Choose Us</h2>
      <ul>
        <li>🎯 Local ${b} expertise and knowledge</li>
        <li>⚡ Fast response times throughout ${b}</li>
        <li>✅ Licensed, bonded, and insured</li>
        <li>💰 Transparent, upfront pricing</li>
        <li>🛡️ 100% satisfaction guarantee</li>
      </ul>
      
      <p><strong>Contact our ${b} team today at (512) 555-0100.</strong></p>
    </div>
  `),schema_markup:(e=a.city,{"@context":"https://schema.org","@type":"LocalBusiness",name:"Elite HVAC",address:{"@type":"PostalAddress",addressLocality:e,addressRegion:a.state,addressCountry:"US"},telephone:"(512) 555-0100",url:"https://website.hero365.workers.dev"}),target_keywords:[`hvac ${a.city.toLowerCase()}`,`${a.city.toLowerCase()} hvac`,`hvac services ${a.city.toLowerCase()}`],page_url:`/locations/${a.id}`,generation_method:"template",page_type:"location",word_count:450,created_at:new Date().toISOString()}}),b.forEach(a=>{c.forEach(b=>{var c,e,f,g,h,i,j,k,l,m,n,o;let p=b.searches>1e3&&Math.random()>.9;d[`/services/${a.id}/${b.id}`]={title:`${a.name} in ${b.city}, ${b.state} | 24/7 Service | Elite HVAC`,meta_description:`Professional ${a.name} services in ${b.city}, ${b.state}. Same-day service, licensed & insured. Call (512) 555-0100 for free estimate.`,h1_heading:`Expert ${a.name} Services in ${b.city}, ${b.state}`,content:(c=a.name,e=b.city,f=b.state,`
    <div class="service-location-content">
      <p>Need reliable ${c} in ${e}? Elite HVAC has been serving ${e} residents for 15+ years with professional, affordable ${c} solutions. Our certified technicians provide same-day service throughout ${e}, ${f}.</p>
      
      <h2>Why Choose Elite HVAC for ${c} in ${e}?</h2>
      <ul>
        <li>🏆 15+ years serving ${e} and surrounding areas</li>
        <li>✅ Licensed, bonded, and insured professionals</li>
        <li>⚡ Same-day service available</li>
        <li>🛡️ 100% satisfaction guarantee</li>
        <li>💰 Transparent, upfront pricing</li>
      </ul>
      
      <h2>${c} Services We Provide in ${e}</h2>
      <p>Our certified technicians provide comprehensive ${c} services throughout ${e}, ${f}. Whether you need emergency repairs, routine maintenance, or new installations, we have the expertise to get the job done right.</p>
      
      <h3>Emergency ${c} Service</h3>
      <p>Available 24/7 for urgent ${c} needs in ${e}. Our emergency technicians can respond quickly to minimize downtime and restore your comfort.</p>
      
      <h3>Residential ${c}</h3>
      <p>Homeowners in ${e} trust us for reliable ${c} solutions. We understand the unique needs of residential properties and provide personalized service.</p>
      
      <h3>Commercial ${c}</h3>
      <p>Businesses in ${e} rely on our commercial ${c} expertise. We minimize disruption to your operations while ensuring optimal performance.</p>
  `+(p?`
      <h2>Local ${e} Expertise</h2>
      <p>As longtime ${e} residents ourselves, we understand the unique challenges that ${f} weather can present to your HVAC system. From hot summers that strain air conditioning units to occasional cold snaps that test heating systems, we've seen it all in ${e}.</p>
      
      <h2>Serving ${e} Neighborhoods</h2>
      <p>We proudly serve all areas of ${e}, including downtown, surrounding residential neighborhoods, and commercial districts. Our local knowledge helps us provide faster, more effective service to every corner of ${e}.</p>
      
      <h2>Customer Reviews in ${e}</h2>
      <blockquote class="bg-gray-50 p-4 border-l-4 border-blue-500 italic">
        "Elite HVAC saved the day when our AC went out during the summer heat wave. They were at our ${e} home within 2 hours and had us cool again by evening. Highly recommend!" - Sarah M., ${e} resident
      </blockquote>
  `:"")+`
      <h2>Service Areas</h2>
      <p>We proudly serve ${e}, ${f} and surrounding areas within 25 miles of our location.</p>
      
      <h2>Contact Elite HVAC Today</h2>
      <p><strong>Ready for professional ${c} service in ${e}? Call (512) 555-0100 or contact us online for a free estimate. Emergency service available 24/7!</strong></p>
    </div>
  `),schema_markup:(g=a.name,h=b.city,i=b.state,{"@context":"https://schema.org","@type":"Service",name:`${g} in ${h}`,description:`Professional ${g} services in ${h}, ${i}`,provider:{"@type":"LocalBusiness",name:"Elite HVAC",telephone:"(512) 555-0100",address:{"@type":"PostalAddress",addressLocality:h,addressRegion:i,addressCountry:"US"},url:"https://website.hero365.workers.dev"},areaServed:{"@type":"City",name:h,containedInPlace:{"@type":"State",name:i}}}),target_keywords:[`${a.id} ${b.city.toLowerCase()}`,`${b.city.toLowerCase()} ${a.id}`,`${a.id} services ${b.city.toLowerCase()}`,`${a.id} ${b.city.toLowerCase()} ${b.state.toLowerCase()}`],page_url:`/services/${a.id}/${b.id}`,generation_method:p?"llm":"template",page_type:"service_location",word_count:p?1200:800,created_at:new Date().toISOString()},d[`/emergency/${a.id}/${b.id}`]={title:`Emergency ${a.name} in ${b.city}, ${b.state} | 24/7 Service`,meta_description:`24/7 emergency ${a.name} in ${b.city}, ${b.state}. Fast response, licensed technicians. Call (512) 555-0100 now for immediate service.`,h1_heading:`24/7 Emergency ${a.name} in ${b.city}, ${b.state}`,content:(j=a.name,k=b.city,l=b.state,`
    <div class="emergency-content">
      <div class="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
        <p class="text-red-800 font-bold">🚨 EMERGENCY ${j.toUpperCase()} SERVICE IN ${k.toUpperCase()}</p>
      </div>
      
      <p>Emergency ${j} in ${k}? Don't panic! Elite HVAC provides 24/7 emergency ${j} services throughout ${k}, ${l}. Our emergency technicians are on standby and can respond quickly to your urgent ${j} needs.</p>
      
      <h2>⚡ Fast Emergency Response</h2>
      <ul>
        <li>🕐 Available 24 hours a day, 7 days a week</li>
        <li>🚗 Rapid response throughout ${k}</li>
        <li>👨‍🔧 Licensed emergency technicians</li>
        <li>🧰 Fully stocked service vehicles</li>
        <li>💰 Upfront emergency pricing</li>
      </ul>
      
      <h2>🚨 Common Emergency ${j} Issues</h2>
      <p>Our emergency technicians handle:</p>
      <ul>
        <li>Complete system failures</li>
        <li>Safety hazards and urgent repairs</li>
        <li>After-hours breakdowns</li>
        <li>Weekend and holiday emergencies</li>
        <li>Storm damage and urgent issues</li>
      </ul>
      
      <h2>✅ Why Choose Us for Emergency Service?</h2>
      <ul>
        <li>🕐 24/7 availability in ${k}</li>
        <li>⚡ Fast response times</li>
        <li>👨‍🔧 Licensed emergency technicians</li>
        <li>💰 Transparent emergency pricing</li>
        <li>🚫 No hidden fees or surprises</li>
      </ul>
      
      <div class="bg-yellow-50 border-l-4 border-yellow-500 p-4 mt-6">
        <p class="text-yellow-800 font-bold text-lg">📞 Call (512) 555-0100 NOW for immediate emergency ${j} service in ${k}!</p>
      </div>
    </div>
  `),schema_markup:(m=a.name,n=b.city,o=b.state,{"@context":"https://schema.org","@type":"EmergencyService",name:`Emergency ${m}`,description:`24/7 emergency ${m} services in ${n}, ${o}`,provider:{"@type":"LocalBusiness",name:"Elite HVAC",telephone:"(512) 555-0100"},availableAtOrFrom:{"@type":"Place",address:{"@type":"PostalAddress",addressLocality:n,addressRegion:o,addressCountry:"US"}},hoursAvailable:{"@type":"OpeningHoursSpecification",dayOfWeek:["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],opens:"00:00",closes:"23:59"}}),target_keywords:[`emergency ${a.id} ${b.city.toLowerCase()}`,`24/7 ${a.id} ${b.city.toLowerCase()}`,`${a.id} emergency ${b.city.toLowerCase()}`],page_url:`/emergency/${a.id}/${b.id}`,generation_method:"template",page_type:"emergency_service",word_count:600,created_at:new Date().toISOString()}})}),d}let x=new e.AppRouteRouteModule({definition:{kind:f.RouteKind.APP_ROUTE,page:"/api/seo/pages/[businessId]/route",pathname:"/api/seo/pages/[businessId]",filename:"route",bundlePath:"app/api/seo/pages/[businessId]/route"},distDir:".next",relativeProjectDir:"",resolvedPagePath:"/Users/andre/Projects/hunter-apps/hero365-app/website-builder/app/api/seo/pages/[businessId]/route.ts",nextConfigOutput:"standalone",userland:d}),{workAsyncStorage:y,workUnitAsyncStorage:z,serverHooks:A}=x;function B(){return(0,g.patchFetch)({workAsyncStorage:y,workUnitAsyncStorage:z})}async function C(a,b,c){var d;let e="/api/seo/pages/[businessId]/route";"/index"===e&&(e="/");let g=await x.prepare(a,b,{srcPage:e,multiZoneDraftMode:!1});if(!g)return b.statusCode=400,b.end("Bad Request"),null==c.waitUntil||c.waitUntil.call(c,Promise.resolve()),null;let{buildId:u,params:v,nextConfig:w,isDraftMode:y,prerenderManifest:z,routerServerContext:A,isOnDemandRevalidate:B,revalidateOnlyGenerated:C,resolvedPathname:D}=g,E=(0,j.normalizeAppPath)(e),F=!!(z.dynamicRoutes[E]||z.routes[D]);if(F&&!y){let a=!!z.routes[D],b=z.dynamicRoutes[E];if(b&&!1===b.fallback&&!a)throw new s.NoFallbackError}let G=null;!F||x.isDev||y||(G="/index"===(G=D)?"/":G);let H=!0===x.isDev||!F,I=F&&!H,J=a.method||"GET",K=(0,i.getTracer)(),L=K.getActiveScopeSpan(),M={params:v,prerenderManifest:z,renderOpts:{experimental:{cacheComponents:!!w.experimental.cacheComponents,authInterrupts:!!w.experimental.authInterrupts},supportsDynamicResponse:H,incrementalCache:(0,h.getRequestMeta)(a,"incrementalCache"),cacheLifeProfiles:null==(d=w.experimental)?void 0:d.cacheLife,isRevalidate:I,waitUntil:c.waitUntil,onClose:a=>{b.on("close",a)},onAfterTaskError:void 0,onInstrumentationRequestError:(b,c,d)=>x.onRequestError(a,b,d,A)},sharedContext:{buildId:u}},N=new k.NodeNextRequest(a),O=new k.NodeNextResponse(b),P=l.NextRequestAdapter.fromNodeNextRequest(N,(0,l.signalFromNodeResponse)(b));try{let d=async c=>x.handle(P,M).finally(()=>{if(!c)return;c.setAttributes({"http.status_code":b.statusCode,"next.rsc":!1});let d=K.getRootSpanAttributes();if(!d)return;if(d.get("next.span_type")!==m.BaseServerSpan.handleRequest)return void console.warn(`Unexpected root span type '${d.get("next.span_type")}'. Please report this Next.js issue https://github.com/vercel/next.js`);let e=d.get("next.route");if(e){let a=`${J} ${e}`;c.setAttributes({"next.route":e,"http.route":e,"next.span_name":a}),c.updateName(a)}else c.updateName(`${J} ${a.url}`)}),g=async g=>{var i,j;let k=async({previousCacheEntry:f})=>{try{if(!(0,h.getRequestMeta)(a,"minimalMode")&&B&&C&&!f)return b.statusCode=404,b.setHeader("x-nextjs-cache","REVALIDATED"),b.end("This page could not be found"),null;let e=await d(g);a.fetchMetrics=M.renderOpts.fetchMetrics;let i=M.renderOpts.pendingWaitUntil;i&&c.waitUntil&&(c.waitUntil(i),i=void 0);let j=M.renderOpts.collectedTags;if(!F)return await (0,o.I)(N,O,e,M.renderOpts.pendingWaitUntil),null;{let a=await e.blob(),b=(0,p.toNodeOutgoingHttpHeaders)(e.headers);j&&(b[r.NEXT_CACHE_TAGS_HEADER]=j),!b["content-type"]&&a.type&&(b["content-type"]=a.type);let c=void 0!==M.renderOpts.collectedRevalidate&&!(M.renderOpts.collectedRevalidate>=r.INFINITE_CACHE)&&M.renderOpts.collectedRevalidate,d=void 0===M.renderOpts.collectedExpire||M.renderOpts.collectedExpire>=r.INFINITE_CACHE?void 0:M.renderOpts.collectedExpire;return{value:{kind:t.CachedRouteKind.APP_ROUTE,status:e.status,body:Buffer.from(await a.arrayBuffer()),headers:b},cacheControl:{revalidate:c,expire:d}}}}catch(b){throw(null==f?void 0:f.isStale)&&await x.onRequestError(a,b,{routerKind:"App Router",routePath:e,routeType:"route",revalidateReason:(0,n.c)({isRevalidate:I,isOnDemandRevalidate:B})},A),b}},l=await x.handleResponse({req:a,nextConfig:w,cacheKey:G,routeKind:f.RouteKind.APP_ROUTE,isFallback:!1,prerenderManifest:z,isRoutePPREnabled:!1,isOnDemandRevalidate:B,revalidateOnlyGenerated:C,responseGenerator:k,waitUntil:c.waitUntil});if(!F)return null;if((null==l||null==(i=l.value)?void 0:i.kind)!==t.CachedRouteKind.APP_ROUTE)throw Object.defineProperty(Error(`Invariant: app-route received invalid cache entry ${null==l||null==(j=l.value)?void 0:j.kind}`),"__NEXT_ERROR_CODE",{value:"E701",enumerable:!1,configurable:!0});(0,h.getRequestMeta)(a,"minimalMode")||b.setHeader("x-nextjs-cache",B?"REVALIDATED":l.isMiss?"MISS":l.isStale?"STALE":"HIT"),y&&b.setHeader("Cache-Control","private, no-cache, no-store, max-age=0, must-revalidate");let m=(0,p.fromNodeOutgoingHttpHeaders)(l.value.headers);return(0,h.getRequestMeta)(a,"minimalMode")&&F||m.delete(r.NEXT_CACHE_TAGS_HEADER),!l.cacheControl||b.getHeader("Cache-Control")||m.get("Cache-Control")||m.set("Cache-Control",(0,q.getCacheControlHeader)(l.cacheControl)),await (0,o.I)(N,O,new Response(l.value.body,{headers:m,status:l.value.status||200})),null};L?await g(L):await K.withPropagatedContext(a.headers,()=>K.trace(m.BaseServerSpan.handleRequest,{spanName:`${J} ${a.url}`,kind:i.SpanKind.SERVER,attributes:{"http.method":J,"http.target":a.url}},g))}catch(b){if(L||b instanceof s.NoFallbackError||await x.onRequestError(a,b,{routerKind:"App Router",routePath:E,routeType:"route",revalidateReason:(0,n.c)({isRevalidate:I,isOnDemandRevalidate:B})}),F)throw b;return await (0,o.I)(N,O,new Response(null,{status:500})),null}}},10846:a=>{"use strict";a.exports=require("next/dist/compiled/next-server/app-page.runtime.prod.js")},19121:a=>{"use strict";a.exports=require("next/dist/server/app-render/action-async-storage.external.js")},29294:a=>{"use strict";a.exports=require("next/dist/server/app-render/work-async-storage.external.js")},44870:a=>{"use strict";a.exports=require("next/dist/compiled/next-server/app-route.runtime.prod.js")},63033:a=>{"use strict";a.exports=require("next/dist/server/app-render/work-unit-async-storage.external.js")},78335:()=>{},86439:a=>{"use strict";a.exports=require("next/dist/shared/lib/no-fallback-error.external")},96487:()=>{}};var b=require("../../../../../webpack-runtime.js");b.C(a);var c=b.X(0,[586,692],()=>b(b.s=9573));module.exports=c})();