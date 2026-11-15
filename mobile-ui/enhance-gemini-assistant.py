from pathlib import Path
import sys

p = Path(sys.argv[1])
s = p.read_text(encoding="utf-8")
if "anasGeminiAssistant" in s:
    print("Gemini assistant already installed")
    raise SystemExit(0)

ui = r"""
<!-- ANAS Studio Gemini Assistant -->
<style>
#anasGeminiFab{position:fixed;z-index:80;left:16px;bottom:calc(94px + env(safe-area-inset-bottom));border:1px solid #8ab9ff66;border-radius:999px;background:linear-gradient(135deg,#245db5,#6046c8);color:#fff;padding:12px 16px;font-weight:800;box-shadow:0 10px 32px #0008}
#anasGeminiPanel{position:fixed;z-index:90;inset: max(12px,env(safe-area-inset-top)) 12px max(12px,env(safe-area-inset-bottom));display:none;overflow:auto;background:#0c1422;color:#f4f6fa;border:1px solid #38506e;border-radius:22px;padding:16px;box-shadow:0 20px 70px #000c}
#anasGeminiPanel.open{display:block}
.anas-ai-field{width:100%;background:#111d2c;color:#fff;border:1px solid #34465e;border-radius:12px;padding:11px;margin:5px 0 12px;direction:auto}
.anas-ai-action{background:#1d3c67;border:1px solid #4779b7;color:#fff;border-radius:11px;padding:10px 12px;font-weight:700}
.anas-ai-action:disabled{opacity:.5}
#anasGeminiOutput{white-space:pre-wrap;overflow-wrap:anywhere;min-height:110px;background:#08101c;border:1px solid #26394f;border-radius:12px;padding:12px;line-height:1.8}
</style>
<button id="anasGeminiFab" type="button" onclick="anasGeminiToggle(true)">✦ Gemini AI</button>
<section id="anasGeminiPanel" role="dialog" aria-modal="true" aria-labelledby="anasGeminiTitle">
 <div style="display:flex;align-items:center;gap:10px;justify-content:space-between">
  <h2 id="anasGeminiTitle" style="font-size:20px;font-weight:900">مساعد Gemini</h2>
  <button class="anas-ai-action" type="button" onclick="anasGeminiToggle(false)">إغلاق</button>
 </div>
 <p style="color:#9fb1c8;font-size:12px;margin:4px 0 12px">اكتب فكرة أو نصاً، واختر المهمة. يلزم إعداد رابط وسيط API الآمن أولاً.</p>
 <details style="border:1px solid #34465e;border-radius:12px;padding:10px;margin-bottom:12px">
  <summary style="font-weight:800;cursor:pointer">إعداد الاتصال (مرة واحدة)</summary>
  <label for="anasGeminiEndpoint" style="display:block;font-size:12px;margin-top:10px">رابط Cloudflare Worker</label>
  <input id="anasGeminiEndpoint" class="anas-ai-field" type="url" inputmode="url" placeholder="https://your-worker.workers.dev">
  <label for="anasGeminiToken" style="display:block;font-size:12px">رمز الوصول الذي تضبطه في الخادم</label>
  <input id="anasGeminiToken" class="anas-ai-field" type="password" autocomplete="off" placeholder="رمز الوصول">
  <button class="anas-ai-action" type="button" onclick="anasGeminiSaveConfig()">حفظ الإعدادات</button>
  <p style="font-size:11px;color:#93a4b9">لا تضع مفتاح Google Gemini هنا. مفتاح Google يبقى سراً داخل إعدادات الخادم.</p>
 </details>
 <label for="anasGeminiTask" style="display:block;font-size:12px">المهمة</label>
 <select id="anasGeminiTask" class="anas-ai-field">
  <option value="script">إنشاء سكريبت من فكرة</option>
  <option value="rewrite">تحسين وإعادة صياغة النص</option>
  <option value="scenes">تقسيم النص إلى مشاهد</option>
  <option value="ideas">اقتراح أفكار وعناوين</option>
 </select>
 <label for="anasGeminiPrompt" style="display:block;font-size:12px">الفكرة أو النص</label>
 <textarea id="anasGeminiPrompt" class="anas-ai-field" rows="6" maxlength="12000" placeholder="اكتب فكرتك أو الصق النص هنا..."></textarea>
 <div style="display:flex;gap:8px;flex-wrap:wrap;margin:8px 0 14px">
  <button id="anasGeminiRun" class="anas-ai-action" type="button" onclick="anasGeminiRun()">توليد باستخدام Gemini</button>
  <button class="anas-ai-action" type="button" onclick="anasGeminiCopy()">نسخ النتيجة</button>
  <button class="anas-ai-action" type="button" onclick="anasGeminiInsert()">إدراج في السكريبت</button>
 </div>
 <div id="anasGeminiStatus" role="status" style="font-size:12px;color:#9fb1c8;margin:8px 0"></div>
 <div id="anasGeminiOutput" aria-live="polite">ستظهر النتيجة هنا.</div>
</section>
<script>
(function(){
 const KEY='anas-studio-gemini-config-v1';
 const $=id=>document.getElementById(id);
 window.anasGeminiToggle=function(open){$('anasGeminiPanel').classList.toggle('open',!!open);if(open){try{const c=JSON.parse(localStorage.getItem(KEY)||'{}');$('anasGeminiEndpoint').value=c.endpoint||'';$('anasGeminiToken').value=c.token||'';}catch(e){}}};
 window.anasGeminiSaveConfig=function(){
  const endpoint=$('anasGeminiEndpoint').value.trim().replace(/\/+$/,'');
  const token=$('anasGeminiToken').value.trim();
  try{const u=new URL(endpoint);if(u.protocol!=='https:')throw Error();if(!token||token.length<16)throw Error();localStorage.setItem(KEY,JSON.stringify({endpoint,token}));$('anasGeminiStatus').textContent='تم حفظ إعدادات الاتصال على هذا الجهاز.';}
  catch(e){$('anasGeminiStatus').textContent='أدخل رابط HTTPS صحيحاً ورمز وصول لا يقل عن 16 حرفاً.';}
 };
 window.anasGeminiRun=async function(){
  const btn=$('anasGeminiRun'),prompt=$('anasGeminiPrompt').value.trim(),task=$('anasGeminiTask').value;
  if(!prompt){$('anasGeminiStatus').textContent='اكتب فكرة أو نصاً أولاً.';return;}
  let cfg;try{cfg=JSON.parse(localStorage.getItem(KEY)||'null');}catch(e){}
  if(!cfg?.endpoint||!cfg?.token){$('anasGeminiStatus').textContent='اضبط رابط الوسيط ورمز الوصول أولاً.';return;}
  btn.disabled=true;$('anasGeminiStatus').textContent='يتصل بـ Gemini...';$('anasGeminiOutput').textContent='';
  const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),90000);
  try{
   const response=await fetch(cfg.endpoint+'/generate',{method:'POST',headers:{'Content-Type':'application/json','Authorization':'Bearer '+cfg.token},body:JSON.stringify({task,prompt}),signal:controller.signal});
   const data=await response.json().catch(()=>({}));
   if(!response.ok)throw Error(data.error||('فشل الطلب ('+response.status+')'));
   if(typeof data.text!=='string'||!data.text.trim())throw Error('لم يرجع Gemini نصاً صالحاً.');
   $('anasGeminiOutput').textContent=data.text;$('anasGeminiStatus').textContent='اكتمل التوليد.';
  }catch(e){$('anasGeminiStatus').textContent=e.name==='AbortError'?'انتهت مهلة الاتصال.':'تعذر الاتصال: '+e.message;}
  finally{clearTimeout(timeout);btn.disabled=false;}
 };
 window.anasGeminiCopy=async function(){const t=$('anasGeminiOutput').textContent;if(!t||t==='ستظهر النتيجة هنا.'){return;}try{await navigator.clipboard.writeText(t);$('anasGeminiStatus').textContent='تم نسخ النتيجة.';}catch(e){$('anasGeminiStatus').textContent='تعذر النسخ من هذا الجهاز.';}};
 window.anasGeminiInsert=function(){
  const t=$('anasGeminiOutput').textContent;if(!t||t==='ستظهر النتيجة هنا.')return;
  const areas=[...document.querySelectorAll('[data-scene-text]')];
  if(areas.length){areas[0].value=t;areas[0].dispatchEvent(new Event('input',{bubbles:true}));$('anasGeminiStatus').textContent='أُدرج النص في أول مشهد. احفظ التغييرات.';return;}
  $('anasGeminiStatus').textContent='افتح محرر السكريبت أولاً ثم أعد الإدراج.';
 };
})();
</script>
"""
if "</body>" not in s:
    raise SystemExit("HTML closing body tag not found")
s = s.replace("</body>", ui + "\n</body>", 1)
p.write_text(s, encoding="utf-8")
print("Gemini assistant injected")
