/**
 * ANAS Studio Gemini proxy — Cloudflare Worker
 *
 * Configure Worker secrets:
 *   GEMINI_API_KEY     Google AI Studio API key (server-side only)
 *   APP_ACCESS_TOKEN   Random secret shared with the app's connection settings
 * Optional variables:
 *   GEMINI_MODEL       Defaults to gemini-2.5-flash
 *   ALLOWED_ORIGIN     Exact allowed app origin, e.g. https://anasgdxj.github.io
 *
 * Deploy with: npx wrangler deploy
 */
const cors = (origin, allowed) => ({
  "Access-Control-Allow-Origin": allowed === "*" ? "*" : (origin === allowed ? allowed : "null"),
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
  "Vary": "Origin"
});
export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    const allowed = env.ALLOWED_ORIGIN || "https://anasgdxj.github.io";
    const headers = cors(origin, allowed);
    if (request.method === "OPTIONS") return new Response(null, {status: 204, headers});
    const url = new URL(request.url);
    if (url.pathname !== "/generate" || request.method !== "POST")
      return Response.json({error:"Not found"}, {status:404, headers});
    if (origin && origin !== allowed)
      return Response.json({error:"Origin not allowed"}, {status:403, headers});
    if (!env.GEMINI_API_KEY || !env.APP_ACCESS_TOKEN)
      return Response.json({error:"Server is not configured"}, {status:503, headers});
    const auth = request.headers.get("Authorization") || "";
    const supplied = auth.startsWith("Bearer ") ? auth.slice(7) : "";
    if (supplied.length !== env.APP_ACCESS_TOKEN.length ||
        !crypto.subtle.timingSafeEqual(new TextEncoder().encode(supplied), new TextEncoder().encode(env.APP_ACCESS_TOKEN)))
      return Response.json({error:"Unauthorized"}, {status:401, headers});
    let body;
    try { body = await request.json(); } catch {
      return Response.json({error:"Invalid JSON"}, {status:400, headers});
    }
    const task = ["script","rewrite","scenes","ideas"].includes(body.task) ? body.task : null;
    const prompt = typeof body.prompt === "string" ? body.prompt.trim() : "";
    if (!task || !prompt || prompt.length > 12000)
      return Response.json({error:"Task or prompt is invalid"}, {status:400, headers});
    const instructions = {
      script:"اكتب سكريبت عربي احترافي مناسب لصناعة المحتوى، ببداية جذابة وبنية واضحة وخاتمة قوية. لا تضف ادعاءات غير مدعومة.",
      rewrite:"حسّن النص العربي التالي مع الحفاظ على معناه، واجعله واضحاً وطبيعياً وقوياً دون اختلاق معلومات.",
      scenes:"قسّم النص إلى مشاهد مرقمة. لكل مشهد اكتب الوصف البصري والتعليق الصوتي والنص الظاهر على الشاشة.",
      ideas:"اقترح أفكار محتوى وعناوين جذابة ومتنوعة، واشرح زاوية كل فكرة باختصار."
    };
    const model = env.GEMINI_MODEL || "gemini-2.5-flash";
    const upstream = await fetch("https://generativelanguage.googleapis.com/v1beta/models/" +
      encodeURIComponent(model) + ":generateContent", {
      method:"POST",
      headers:{"Content-Type":"application/json","x-goog-api-key":env.GEMINI_API_KEY},
      body:JSON.stringify({
        systemInstruction:{parts:[{text:"أنت مساعد إنتاج محتوى داخل ANAS Studio. أجب بالعربية ما لم يطلب المستخدم غير ذلك. "+instructions[task]}]},
        contents:[{role:"user",parts:[{text:prompt}]}],
        generationConfig:{temperature:0.7,maxOutputTokens:4096}
      })
    });
    const data = await upstream.json().catch(()=>({}));
    if (!upstream.ok) {
      const message = data?.error?.message || "Gemini request failed";
      return Response.json({error:message}, {status:upstream.status===429?429:502, headers});
    }
    const text = (data.candidates || []).flatMap(c => c.content?.parts || [])
      .map(p => p.text || "").join("").trim();
    if (!text) return Response.json({error:"Gemini returned no text"}, {status:502, headers});
    return Response.json({text}, {headers});
  }
};
