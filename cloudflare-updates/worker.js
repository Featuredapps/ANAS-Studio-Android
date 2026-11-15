// Compatibility deployment: keep the legacy endpoint working for already-installed Android clients.
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
  if(p==="/api/health" && req.method==="GET") return json({ok:true,service:"ANAS Studio Update Service",storage:!!env.STUDIO_KV,adminPasswordConfigured:!!env.ADMIN_PASSWORD});
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

  // Lightweight community API backed by the existing KV namespace.
  // User-generated content is plain text only; the client escapes it before rendering.
  const communityPath = p.startsWith("/api/community/") || p === "/api/notifications";
  if (communityPath) {
    if (!env.STUDIO_KV) return json({error:"Community storage is not configured"},503);
    const kv = env.STUDIO_KV;
    const readJson = async (key, fallback) => (await kv.get(key,"json")) || fallback;
    const validDevice = value => typeof value === "string" && /^[a-zA-Z0-9_-]{12,80}$/.test(value);
    const limited = async (device, action, seconds) => {
      const key = "community:rate:" + action + ":" + device;
      if (await kv.get(key)) return false;
      await kv.put(key,"1",{expirationTtl:seconds});
      return true;
    };
    const body = async () => await req.json().catch(() => ({}));
    const cleanText = (value, max) => typeof value === "string"
      ? value.replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g,"").trim().slice(0,max) : "";
    if (p === "/api/notifications" && req.method === "GET") {
      const events = [];
      const manifest = await readJson("published",null);
      if (manifest && manifest.published && manifest.version) {
        events.push({
          id:"release:" + manifest.version,
          type:"release",
          title:"تحديث جديد لـ ANAS Studio",
          message:"الإصدار " + manifest.version + " أصبح متاحاً. افتح صفحة التنزيل للحصول على أحدث نسخة.",
          createdAt:manifest.publishedAt || new Date().toISOString()
        });
      }
      const listed = await kv.list({prefix:"community:post:",limit:30});
      const posts = await Promise.all(listed.keys.map(k=>readJson(k.name,null)));
      for (const post of posts.filter(Boolean)) {
        events.push({
          id:"post:" + post.id,
          type:"community",
          title:"مشاركة جديدة في المجتمع",
          message:post.text.slice(0,110),
          createdAt:post.createdAt
        });
      }
      events.sort((a,b)=>new Date(b.createdAt)-new Date(a.createdAt));
      return json({events:events.slice(0,25)});
    }
    if (p === "/api/community/feed" && req.method === "GET") {
      const device = u.searchParams.get("deviceId") || "";
      const listed = await kv.list({prefix:"community:post:",limit:50});
      const posts = (await Promise.all(listed.keys.map(async k=>{
        const post=await readJson(k.name,null);
        if(!post)return null;
        const reactions=await readJson("community:reactions:"+post.id,{});
        const comments=await readJson("community:comments:"+post.id,[]);
        return {...post,likes:Object.values(reactions).filter(x=>x==="like").length,
          dislikes:Object.values(reactions).filter(x=>x==="dislike").length,
          myReaction:validDevice(device)?(reactions[device]||null):null,commentCount:comments.length,
          comments:comments.slice(-3)};
      }))).filter(Boolean);
      posts.sort((a,b)=>new Date(b.createdAt)-new Date(a.createdAt));
      return json({posts:posts.slice(0,50)});
    }
    if (p === "/api/community/posts" && req.method === "POST") {
      const data=await body(), device=String(data.deviceId||""), text=cleanText(data.text,1200);
      if(!validDevice(device))return json({error:"معرّف الجهاز غير صالح. أعد فتح التطبيق."},400);
      if(text.length<3)return json({error:"اكتب مشاركة لا تقل عن 3 أحرف."},400);
      if(!await limited(device,"post",30))return json({error:"انتظر قليلاً قبل نشر مشاركة أخرى."},429);
      const post={id:crypto.randomUUID(),text,createdAt:new Date().toISOString()};
      await kv.put("community:post:"+post.id,JSON.stringify(post));
      return json({ok:true,post},201);
    }
    if (p === "/api/community/comments" && req.method === "GET") {
      const postId=u.searchParams.get("postId")||"";
      if(!/^[0-9a-f-]{36}$/i.test(postId))return json({error:"المشاركة غير صالحة."},400);
      return json({comments:await readJson("community:comments:"+postId,[])});
    }
    if (p === "/api/community/comments" && req.method === "POST") {
      const data=await body(),device=String(data.deviceId||""),postId=String(data.postId||""),text=cleanText(data.text,500);
      if(!validDevice(device)||!/^[0-9a-f-]{36}$/i.test(postId))return json({error:"بيانات التعليق غير صالحة."},400);
      if(text.length<2)return json({error:"اكتب تعليقاً لا يقل عن حرفين."},400);
      if(!await kv.get("community:post:"+postId))return json({error:"المشاركة غير موجودة."},404);
      if(!await limited(device,"comment",12))return json({error:"انتظر قليلاً قبل إرسال تعليق آخر."},429);
      const key="community:comments:"+postId, comments=await readJson(key,[]);
      const comment={id:crypto.randomUUID(),text,createdAt:new Date().toISOString()};
      comments.push(comment);
      await kv.put(key,JSON.stringify(comments.slice(-100)));
      return json({ok:true,comment},201);
    }
    if (p === "/api/community/reaction" && req.method === "POST") {
      const data=await body(),device=String(data.deviceId||""),postId=String(data.postId||""),reaction=String(data.reaction||"");
      if(!validDevice(device)||!/^[0-9a-f-]{36}$/i.test(postId)||!["like","dislike"].includes(reaction))
        return json({error:"بيانات التقييم غير صالحة."},400);
      if(!await kv.get("community:post:"+postId))return json({error:"المشاركة غير موجودة."},404);
      const key="community:reactions:"+postId,reactions=await readJson(key,{});
      if(reactions[device]===reaction)delete reactions[device];else reactions[device]=reaction;
      await kv.put(key,JSON.stringify(reactions));
      return json({ok:true,likes:Object.values(reactions).filter(x=>x==="like").length,
        dislikes:Object.values(reactions).filter(x=>x==="dislike").length,myReaction:reactions[device]||null});
    }
  }

  return json({error:"Not found"},404);
 }
};
