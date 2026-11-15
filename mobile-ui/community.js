(function () {
'use strict';
if (window.__ANAS_COMMUNITY_READY__) return;
window.__ANAS_COMMUNITY_READY__ = true;
const API='https://anas-studio-updates-api.anasgdxj.workers.dev/api';
const STORE=localStorage, DEVICE_KEY='anas.community.device.v1', READ_KEY='anas.community.read.v1';
const deviceId=(function(){let id=STORE.getItem(DEVICE_KEY);if(!id){id=(crypto&&crypto.randomUUID)?crypto.randomUUID().replace(/-/g,''):Math.random().toString(36).slice(2)+Math.random().toString(36).slice(2);STORE.setItem(DEVICE_KEY,id);}return id;})();
const css = `
#anas-community-launcher{position:fixed;left:16px;bottom:calc(92px + env(safe-area-inset-bottom,0px));z-index:10020;border:1px solid #eac77d55;border-radius:999px;padding:12px 16px;background:linear-gradient(135deg,#f2d69c,#d9a957);color:#20180b;font-family:inherit;font-weight:700;font-size:13px;box-shadow:0 10px 28px #0008;display:flex;align-items:center;gap:8px;cursor:pointer}
#anas-community-launcher:focus-visible,#anas-community button:focus-visible,#anas-community textarea:focus-visible{outline:2px solid #f6dca9;outline-offset:3px}
#anas-community-launcher .ac-badge{min-width:18px;height:18px;padding:0 5px;border-radius:99px;background:#9e352e;color:white;font-size:10px;display:none;align-items:center;justify-content:center}
#anas-community{position:fixed;inset:0;z-index:10030;display:none;align-items:flex-end;justify-content:center;background:#030711b8;backdrop-filter:blur(7px);font-family:inherit;color:#f4f7fc}
#anas-community.ac-open{display:flex}
#anas-community .ac-panel{width:min(760px,100%);height:min(84dvh,820px);display:flex;flex-direction:column;overflow:hidden;background:#0d1727;border:1px solid #a9bdd52c;border-bottom:0;border-radius:25px 25px 0 0;box-shadow:0 -22px 70px #0009}
#anas-community .ac-head{padding:17px 19px 13px;background:linear-gradient(120deg,#1a2c45,#101b2d);border-bottom:1px solid #ffffff18;display:flex;align-items:center;justify-content:space-between;gap:12px}
#anas-community .ac-title{font-size:17px;font-weight:800}#anas-community .ac-subtitle{font-size:11px;color:#a8b7ca;margin-top:3px}
#anas-community .ac-close{width:38px;height:38px;border:1px solid #ffffff20;border-radius:12px;background:#ffffff0a;color:#f4f7fc;font-size:22px;cursor:pointer}
#anas-community .ac-tabs{display:flex;gap:8px;padding:12px 16px 0;background:#0d1727}
#anas-community .ac-tab{flex:1;border:1px solid #ffffff16;border-radius:12px;background:#ffffff06;color:#aebbd0;padding:10px 8px;font-family:inherit;font-weight:600;font-size:12px;cursor:pointer}
#anas-community .ac-tab[aria-selected=true]{background:#eac77d18;border-color:#eac77d55;color:#f4d99e}
#anas-community .ac-body{overflow:auto;overscroll-behavior:contain;padding:14px 15px calc(20px + env(safe-area-inset-bottom,0px));flex:1}
#anas-community .ac-compose{padding:13px;border:1px solid #ffffff17;border-radius:17px;background:#142238;margin-bottom:14px}
#anas-community .ac-compose label{display:block;font-size:12px;font-weight:700;margin-bottom:9px}
#anas-community textarea{width:100%;min-height:82px;resize:vertical;box-sizing:border-box;border:1px solid #ffffff20;border-radius:12px;background:#091321;color:#f4f7fc;padding:12px;font:14px/1.7 inherit}
#anas-community textarea::placeholder{color:#8191a8}
#anas-community .ac-actions{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-top:9px}
#anas-community .ac-hint{font-size:10px;color:#91a0b5}
#anas-community .ac-primary{border:0;border-radius:11px;background:linear-gradient(120deg,#f2d69c,#d9a957);color:#21180b;padding:10px 15px;font-family:inherit;font-weight:700;font-size:12px;cursor:pointer}
#anas-community .ac-primary:disabled{opacity:.5;cursor:wait}
#anas-community .ac-card{padding:14px;margin-bottom:10px;border:1px solid #ffffff16;border-radius:16px;background:linear-gradient(145deg,#17263b,#101b2b)}
#anas-community .ac-meta{font-size:10px;color:#9eacc1;display:flex;justify-content:space-between;gap:8px;margin-bottom:8px}
#anas-community .ac-copy{font-size:13px;line-height:1.8;white-space:pre-wrap;overflow-wrap:anywhere;color:#e7edf6}
#anas-community .ac-votes{display:flex;gap:7px;margin-top:12px;flex-wrap:wrap}
#anas-community .ac-vote{border:1px solid #ffffff1c;border-radius:10px;background:#ffffff08;color:#c4cfde;padding:7px 10px;font-family:inherit;font-weight:600;font-size:11px;cursor:pointer}
#anas-community .ac-vote[aria-pressed=true]{border-color:#eac77d66;background:#eac77d18;color:#f5d99e}
#anas-community .ac-comments{margin-top:12px;padding-top:10px;border-top:1px solid #ffffff14}
#anas-community .ac-comment{font-size:11px;line-height:1.7;color:#c1ccda;padding:7px 0;border-bottom:1px solid #ffffff0d;white-space:pre-wrap;overflow-wrap:anywhere}
#anas-community .ac-reply{display:flex;gap:7px;margin-top:9px}#anas-community .ac-reply textarea{min-height:42px;flex:1}
#anas-community .ac-empty,#anas-community .ac-status{padding:28px 12px;text-align:center;color:#98a8bc;font-size:12px;line-height:1.8}
#anas-community .ac-notice{display:flex;gap:11px;padding:13px;margin-bottom:9px;border:1px solid #ffffff17;border-radius:15px;background:#142238}
#anas-community .ac-dot{width:8px;height:8px;flex:0 0 8px;border-radius:50%;background:#efc77f;margin-top:6px}
#anas-community .ac-notice strong{display:block;font-size:12px;margin-bottom:3px}
#anas-community .ac-notice span{display:block;font-size:11px;line-height:1.7;color:#aab8ca}
@media(min-width:700px){#anas-community{align-items:center;padding:20px}#anas-community .ac-panel{height:min(78vh,820px);border-bottom:1px solid #a9bdd52c;border-radius:25px}}
@media(prefers-reduced-motion:no-preference){#anas-community .ac-panel{animation:ac-rise .2s ease-out}@keyframes ac-rise{from{transform:translateY(18px);opacity:.7}to{transform:none;opacity:1}}}
`;
const style=document.createElement('style');style.id='anas-community-styles';style.textContent=css;document.head.appendChild(style);
const launcher=document.createElement('button');launcher.id='anas-community-launcher';launcher.type='button';launcher.innerHTML='<span aria-hidden="true">✦</span><span>المجتمع</span><span class="ac-badge" aria-live="polite"></span>';document.body.appendChild(launcher);
const shell=document.createElement('section');shell.id='anas-community';shell.setAttribute('role','dialog');shell.setAttribute('aria-modal','true');shell.setAttribute('aria-label','مجتمع ANAS Studio');
shell.innerHTML='<div class="ac-panel"><header class="ac-head"><div><div class="ac-title">مجتمع ANAS Studio</div><div class="ac-subtitle">شارك أفكارك وتواصل مع المبدعين</div></div><button class="ac-close" type="button" aria-label="إغلاق">×</button></header><div class="ac-tabs" role="tablist"><button class="ac-tab" data-tab="community" role="tab" aria-selected="true">المجتمع</button><button class="ac-tab" data-tab="notifications" role="tab" aria-selected="false">الإشعارات</button></div><div class="ac-body" id="ac-content"><div class="ac-status">جارٍ تحميل المجتمع…</div></div></div>';document.body.appendChild(shell);
const content=shell.querySelector('#ac-content'),badge=launcher.querySelector('.ac-badge');let activeTab='community',pollHandle=null;
const readIds=new Set(JSON.parse(STORE.getItem(READ_KEY)||'[]'));
function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function time(v){const d=new Date(v);return isNaN(d.getTime())?'':d.toLocaleString('ar',{dateStyle:'medium',timeStyle:'short'});}
async function request(path,options){const res=await fetch(API+path,Object.assign({headers:{'Content-Type':'application/json'}},options||{}));const data=await res.json().catch(()=>({}));if(!res.ok)throw new Error(data.error||'تعذر الاتصال بالخدمة');return data;}
function setBadge(events){const n=events.filter(e=>!readIds.has(String(e.id))).length;badge.textContent=n>99?'99+':String(n);badge.style.display=n?'inline-flex':'none';}
async function loadNotifications(mark){const data=await request('/notifications'),events=data.events||[];setBadge(events);if(mark){events.forEach(e=>readIds.add(String(e.id)));STORE.setItem(READ_KEY,JSON.stringify(Array.from(readIds).slice(-100)));setBadge(events);}content.innerHTML=events.length?events.map(e=>'<article class="ac-notice"><i class="ac-dot"></i><div><strong>'+esc(e.title)+'</strong><span>'+esc(e.message)+'</span><span>'+esc(time(e.createdAt))+'</span></div></article>').join(''):'<div class="ac-empty">لا توجد إشعارات حالياً.<br>ستظهر هنا تحديثات التطبيق والمشاركات الجديدة.</div>';}
async function loadCommunity(){content.innerHTML='<div class="ac-status">جارٍ تحميل المشاركات…</div>';const data=await request('/community/feed?deviceId='+encodeURIComponent(deviceId)),posts=data.posts||[];let html='<form class="ac-compose" id="ac-post-form"><label for="ac-post-text">ابدأ نقاشاً أو شارك فكرة</label><textarea id="ac-post-text" maxlength="1200" required placeholder="اكتب شيئاً مفيداً لمجتمع ANAS Studio…"></textarea><div class="ac-actions"><span class="ac-hint">حتى 1200 حرف · مشاركة عامة</span><button class="ac-primary" type="submit">نشر المشاركة</button></div></form>';if(!posts.length)html+='<div class="ac-empty">لا توجد مشاركات بعد. ابدأ أول نقاش في المجتمع.</div>';html+=posts.map(p=>'<article class="ac-card" data-post="'+esc(p.id)+'"><div class="ac-meta"><span>مستخدم المجتمع</span><span>'+esc(time(p.createdAt))+'</span></div><div class="ac-copy">'+esc(p.text)+'</div><div class="ac-votes"><button class="ac-vote" data-reaction="like" aria-pressed="'+(p.myReaction==='like')+'">إعجاب · '+Number(p.likes||0)+'</button><button class="ac-vote" data-reaction="dislike" aria-pressed="'+(p.myReaction==='dislike')+'">عدم إعجاب · '+Number(p.dislikes||0)+'</button><button class="ac-vote" data-comments>التعليقات · '+Number(p.commentCount||0)+'</button></div><div class="ac-comments" hidden><div class="ac-comment-list"></div><form class="ac-reply"><textarea maxlength="500" required placeholder="أضف تعليقاً…"></textarea><button class="ac-primary" type="submit">إرسال</button></form></div></article>').join('');content.innerHTML=html;}
async function switchTab(tab){activeTab=tab;shell.querySelectorAll('.ac-tab').forEach(b=>b.setAttribute('aria-selected',String(b.dataset.tab===tab)));if(tab==='notifications')await loadNotifications(true);else await loadCommunity();}
function error(e){content.insertAdjacentHTML('afterbegin','<div class="ac-status" role="alert">'+esc(e.message||'حدث خطأ')+'</div>');}
launcher.addEventListener('click',()=>{shell.classList.add('ac-open');switchTab(activeTab).catch(error);});
shell.querySelector('.ac-close').addEventListener('click',()=>shell.classList.remove('ac-open'));shell.addEventListener('click',e=>{if(e.target===shell)shell.classList.remove('ac-open');});
shell.querySelectorAll('.ac-tab').forEach(b=>b.addEventListener('click',()=>switchTab(b.dataset.tab).catch(error)));
document.addEventListener('keydown',e=>{if(e.key==='Escape')shell.classList.remove('ac-open');});
content.addEventListener('submit',async e=>{if(e.target.id==='ac-post-form'){e.preventDefault();const btn=e.target.querySelector('button'),field=e.target.querySelector('textarea'),text=field.value.trim();if(!text)return;btn.disabled=true;try{await request('/community/posts',{method:'POST',body:JSON.stringify({deviceId,text})});await loadCommunity();}catch(err){error(err);btn.disabled=false;}}else if(e.target.classList.contains('ac-reply')){e.preventDefault();const card=e.target.closest('[data-post]'),field=e.target.querySelector('textarea'),btn=e.target.querySelector('button'),text=field.value.trim();if(!text)return;btn.disabled=true;try{await request('/community/comments',{method:'POST',body:JSON.stringify({deviceId,postId:card.dataset.post,text})});await loadCommunity();}catch(err){error(err);btn.disabled=false;}}});
content.addEventListener('click',async e=>{const card=e.target.closest('[data-post]');if(!card)return;if(e.target.matches('[data-comments]')){const area=card.querySelector('.ac-comments');area.hidden=!area.hidden;if(!area.hidden){try{const data=await request('/community/comments?postId='+encodeURIComponent(card.dataset.post));area.querySelector('.ac-comment-list').innerHTML=(data.comments||[]).map(c=>'<div class="ac-comment">'+esc(c.text)+' <span style="color:#8191a8">· '+esc(time(c.createdAt))+'</span></div>').join('')||'<div class="ac-empty">لا توجد تعليقات بعد.</div>';}catch(err){error(err);}}}const reaction=e.target.closest('[data-reaction]');if(reaction){reaction.disabled=true;try{await request('/community/reaction',{method:'POST',body:JSON.stringify({deviceId,postId:card.dataset.post,reaction:reaction.dataset.reaction})});await loadCommunity();}catch(err){error(err);reaction.disabled=false;}}});
async function refreshBadge(){try{const data=await request('/notifications');setBadge(data.events||[]);}catch(_){}}
refreshBadge();pollHandle=setInterval(refreshBadge,90000);window.addEventListener('pagehide',()=>{if(pollHandle)clearInterval(pollHandle);});
})();