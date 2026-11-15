const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type,Authorization",
  "Access-Control-Max-Age": "86400"
};
const json = (data, status=200) => new Response(JSON.stringify(data), {
  status, headers: { ...CORS, "Content-Type":"application/json; charset=utf-8", "Cache-Control":"no-store" }
});
async function digest(value) {
  return [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value)))]
    .map(x=>x.toString(16).padStart(2,"0")).join("");
}
async function sign(value, secret) {
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret),
    {name:"HMAC",hash:"SHA-256"}, false, ["sign"]);
  return new Uint8Array(await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(value)));
}
function b64url(bytes) {
  let s=""; for (const b of bytes) s+=String.fromCharCode(b);
  return btoa(s).replace(/=/g,"").replace(/\+/g,"-").replace(/\//g,"_");
}
async function tokenFor(secret) {
  const payload=b64url(new TextEncoder().encode(JSON.stringify({exp:Date.now()+8*60*60*1000, nonce:b64url(crypto.getRandomValues(new Uint8Array(16)))})));
  return payload+"."+b64url(await sign(payload,secret));
}
async function validToken(token, secret) {
  if (!token || !secret) return false;
  const parts=token.split(".");
  if(parts.length!==2) return false;
  try {
    const expected=await sign(parts[0],secret);
    const actual=Uint8Array.from(atob(parts[1].replace(/-/g,"+").replace(/_/g,"/")+"==".slice((parts[1].length+2)%4)),c=>c.charCodeAt(0));
    if(expected.length!==actual.length || !crypto.subtle) return false;
    let diff=0; for(let i=0;i<expected.length;i++) diff|=expected[i]^actual[i];
    if(diff!==0) return false;
    const payload=JSON.parse(atob(parts[0].replace(/-/g,"+").replace(/_/g,"/")+"==".slice((parts[0].length+2)%4)));
    return Number(payload.exp)>Date.now();
  } catch { return false; }
}
export default {
 async fetch(req, env) {
  if(req.method==="OPTIONS") return new Response(null,{headers:CORS});
  const u=new URL(req.url), p=u.pathname;
  if(p==="/" && req.method==="GET") return Response.redirect("https://featuredapps.github.io/ANAS-Studio-Android/",302);
  if(p==="/api/health" && req.method==="GET") return json({ok:true,service:"ANAS Studio Update Service",storage:!!env.STUDIO_KV});
  if(p==="/api/version" && req.method==="GET") {
    if(!env.STUDIO_KV) return json({error:"KV binding STUDIO_KV is not configured"},503);
    const m=await env.STUDIO_KV.get("published","json"); return json(m||{version:0,published:false});
  }
  if(p==="/app" && req.method==="GET") {
    if(!env.STUDIO_KV) return new Response("Update storage is not configured",{status:503});
    const m=await env.STUDIO_KV.get("published","json");
    if(!m?.key)return new Response("No web build published",{status:404});
    const html=await env.STUDIO_KV.get(m.key);
    return html ? new Response(html,{headers:{...CORS,"Content-Type":"text/html; charset=utf-8","Cache-Control":"no-store","X-Studio-Version":String(m.version),"X-Studio-SHA256":String(m.sha256||"")}}) : new Response("Published build missing",{status:503});
  }
  if(p==="/api/admin/login" && req.method==="POST") {
    if(!env.ADMIN_PASSWORD) return json({error:"ADMIN_PASSWORD secret is not configured"},503);
    const body=await req.json().catch(()=>({}));
    if(await digest(String(body.password||""))!==await digest(env.ADMIN_PASSWORD)) return json({error:"بيانات الدخول غير صحيحة"},401);
    return json({token:await tokenFor(env.ADMIN_PASSWORD),expiresIn:28800});
  }
  if(p.startsWith("/api/admin/")) {
    if(!(await validToken((req.headers.get("Authorization")||"").replace(/^Bearer\s+/i,""),env.ADMIN_PASSWORD||"")))
      return json({error:"انتهت الجلسة أو لا يوجد تصريح. سجّل الدخول مجدداً."},401);
    if(!env.STUDIO_KV) return json({error:"KV binding STUDIO_KV is not configured"},503);
  }
  if(p==="/api/admin/publish" && req.method==="POST") {
    const body=await req.json().catch(()=>null);
    if(!body || typeof body.html!=="string" || new TextEncoder().encode(body.html).length>18000000 || !/<\s*html[\s>]/i.test(body.html)) return json({error:"ملف HTML غير صالح أو أكبر من 18MB"},400);
    const version=Date.now(), key="build:"+version;
    await env.STUDIO_KV.put(key,body.html);
    const manifest={version,key,sha256:await digest(body.html),bytes:new TextEncoder().encode(body.html).length,published:true,notes:String(body.notes||"").slice(0,500),publishedAt:new Date().toISOString()};
    await env.STUDIO_KV.put("published",JSON.stringify(manifest));
    return json({ok:true,manifest});
  }
  if(p==="/api/admin/rollback" && req.method==="POST") {
    const body=await req.json().catch(()=>({})), version=Number(body.version);
    if(!Number.isSafeInteger(version)||version<=0) return json({error:"رقم الإصدار غير صالح"},400);
    const key="build:"+version, html=await env.STUDIO_KV.get(key);
    if(!html)return json({error:"الإصدار غير موجود"},404);
    const manifest={version,key,sha256:await digest(html),bytes:new TextEncoder().encode(html).length,published:true,notes:"Rollback",publishedAt:new Date().toISOString()};
    await env.STUDIO_KV.put("published",JSON.stringify(manifest));
    return json({ok:true,manifest});
  }
  if(p==="/api/admin/history" && req.method==="GET") {
    const list=await env.STUDIO_KV.list({prefix:"build:",limit:100});
    return json({versions:list.keys.map(k=>Number(k.name.slice(6))).sort((a,b)=>b-a)});
  }
  return json({error:"Not found"},404);
 }
};
