from pathlib import Path
import sys
p=Path(sys.argv[1]); s=p.read_text()
old='''          <!-- Scenes List -->
          <div id="editorScenesList" class="flex flex-col gap-3 max-h-[52vh] overflow-y-auto pr-1">'''
new='''          <!-- Live writing metrics and script tools -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-2" aria-live="polite">
            <div class="rounded-xl border border-zinc-800 bg-black/40 p-3"><div class="text-[10px] text-zinc-400">عدد المشاهد</div><strong id="editorSceneCount" class="block text-lg text-amber-400">0</strong></div>
            <div class="rounded-xl border border-zinc-800 bg-black/40 p-3"><div class="text-[10px] text-zinc-400">عدد الكلمات</div><strong id="editorWordCount" class="block text-lg text-white">0</strong></div>
            <div class="rounded-xl border border-zinc-800 bg-black/40 p-3"><div class="text-[10px] text-zinc-400">مدة متوقعة</div><strong id="editorDuration" class="block text-lg text-emerald-400">0 ث</strong></div>
            <div class="rounded-xl border border-zinc-800 bg-black/40 p-3"><div class="text-[10px] text-zinc-400">وقت القراءة</div><strong id="editorReadTime" class="block text-lg text-white">0 د</strong></div>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <button type="button" onclick="exportCurrentScriptText()" class="px-3 py-2 rounded-xl bg-sky-500/10 border border-sky-400/30 text-sky-300 text-xs font-bold">تنزيل النص TXT</button>
            <button type="button" onclick="copyCurrentScriptText()" class="px-3 py-2 rounded-xl bg-zinc-800 text-zinc-200 text-xs font-bold">نسخ النص الكامل</button>
            <span id="editorSaveStatus" class="text-[11px] text-zinc-500 mr-auto" role="status">التعديلات تحفظ عند الضغط على حفظ</span>
          </div>
          <!-- Scenes List -->
          <div id="editorScenesList" class="flex flex-col gap-3 max-h-[52vh] overflow-y-auto pr-1">'''
if old in s and 'editorSceneCount' not in s: s=s.replace(old,new,1)
s=s.replace('''          <textarea data-scene-text="${sIdx}" rows="2" class="w-full bg-zinc-900/80 border border-zinc-700/80 focus:border-amber-500 rounded-xl p-2.5 text-sm text-white outline-none resize-none leading-relaxed">${lineText}</textarea>''','''          <textarea data-scene-text="${sIdx}" rows="3" aria-label="نص المشهد ${sIdx + 1}" class="w-full bg-zinc-900/80 border border-zinc-700/80 focus:border-amber-500 rounded-xl p-2.5 text-sm text-white outline-none resize-y leading-relaxed">${escapeEditorHTML(lineText)}</textarea>''')
if 'updateScriptEditorMetrics();' not in s: s=s.replace('''      // 3. Update Audio & TTS Lab Page''','''      updateScriptEditorMetrics();

      // 3. Update Audio & TTS Lab Page''',1)
old2="""      refreshAllUI();
      showToast('تم حفظ تعديلات السكريبت!');
    }

    function addNewSceneToEditor()"""
new2="""      refreshAllUI();
      const status = document.getElementById('editorSaveStatus');
      if (status) status.textContent = `تم الحفظ محلياً • ${new Date().toLocaleTimeString('ar')}`;
      showToast('تم حفظ تعديلات السكريبت!');
    }

    function escapeEditorHTML(value) {
      return String(value ?? '').replace(/[&<>\\"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','\\"':'&quot;',"'":'&#39;'}[ch]));
    }

    function getEditorPlainText() {
      const title = document.getElementById('editorProjectTitle')?.value || activeScript().title;
      const scenes = [...document.querySelectorAll('[data-scene-text]')].map((el, i) => `المشهد ${i + 1}\\n${el.value.trim()}`).join('\\n\\n');
      return `${title}\\n${'='.repeat(Math.min(50, title.length))}\\n\\n${scenes}\\n`;
    }

    function updateScriptEditorMetrics() {
      const areas = [...document.querySelectorAll('[data-scene-text]')];
      const text = areas.map(el => el.value.trim()).join(' ');
      const words = text ? text.split(/\\s+/).filter(Boolean).length : 0;
      const seconds = Math.max(0, Math.round(words / 2.4));
      const set = (id, value) => { const el = document.getElementById(id); if (el) el.textContent = value; };
      set('editorSceneCount', areas.length); set('editorWordCount', words);
      set('editorDuration', `${seconds} ث`); set('editorReadTime', `${(seconds / 60).toFixed(1)} د`);
      const status = document.getElementById('editorSaveStatus');
      if (status && status.textContent.startsWith('التعديلات تحفظ')) status.textContent = `${text.length} حرف • لم تحفظ التعديلات بعد`;
    }

    function exportCurrentScriptText() {
      const blob = new Blob([getEditorPlainText()], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob); const a = document.createElement('a');
      a.href = url; a.download = `${(activeScript().title || 'ANAS-Script').replace(/[^\\p{L}\\p{N}_-]+/gu, '_')}.txt`;
      document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
      showToast('تم تجهيز ملف النص للتنزيل.');
    }

    async function copyCurrentScriptText() {
      const text = getEditorPlainText();
      try {
        if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(text);
        else { const box = document.createElement('textarea'); box.value = text; document.body.appendChild(box); box.select(); document.execCommand('copy'); box.remove(); }
        showToast('تم نسخ النص الكامل.');
      } catch (e) { showToast('تعذر النسخ؛ استخدم تنزيل TXT.'); }
    }

    document.addEventListener('input', event => {
      if (event.target.matches('[data-scene-text]')) updateScriptEditorMetrics();
    });

    function addNewSceneToEditor()"""
if old2 in s: s=s.replace(old2,new2,1)
if 'editorSceneCount' not in s: raise Exception('patch failed')
p.write_text(s)
