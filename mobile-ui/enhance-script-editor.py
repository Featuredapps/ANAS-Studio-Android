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

# Do not announce a save when browser storage rejected the write.
const saveBlock = `persistScripts();
      if (shouldRefresh) refreshAllUI();`;
const safeSaveBlock = `const saveSucceeded = persistScripts();
      if (saveSucceeded === false) {
        const failedStatus = document.getElementById('editorSaveStatus');
        if (failedStatus) failedStatus.textContent = 'فشل الحفظ؛ صدّر نسخة احتياطية وأفرغ مساحة التخزين';
        return;
      }
      if (shouldRefresh) refreshAllUI();`;
if (s.includes(saveBlock)) s = s.replace(saveBlock, safeSaveBlock, 1);

# Keep the current workspace intact if restoring a backup cannot be persisted.
const importBlock = `        SCRIPTS = restored;
        currentIdx = 0;
        PROJECT_AUDIO_STORE.clear();
        persistScripts();
        navigateTo('projects');`;
const safeImportBlock = `        const previousProjects = SCRIPTS;
        SCRIPTS = restored;
        currentIdx = 0;
        if (persistScripts() === false) {
          SCRIPTS = previousProjects;
          currentIdx = 0;
          showToast('تعذر حفظ النسخة المستعادة؛ بقيت مشاريعك الحالية كما هي.');
          return;
        }
        PROJECT_AUDIO_STORE.clear();
        navigateTo('projects');`;
if (s.includes(importBlock)) s = s.replace(importBlock, safeImportBlock, 1);

p.write_text(s)


# Surface storage failures instead of reporting a false successful save.
old_persist = """    function persistScripts() {
      try {
        localStorage.setItem(STORAGE_KEY_SCRIPTS, JSON.stringify(SCRIPTS));
      } catch (e) {}
    }"""
new_persist = """    function persistScripts() {
      try {
        localStorage.setItem(STORAGE_KEY_SCRIPTS, JSON.stringify(SCRIPTS));
        return true;
      } catch (e) {
        showToast('مساحة التخزين ممتلئة؛ صدّر نسخة احتياطية واحذف بيانات غير ضرورية.');
        return false;
      }
    }"""
if old_persist in s:
    s=s.replace(old_persist, new_persist, 1)

# Project backup / restore and quiet autosave.
projects_anchor = '''      <div id="projectsGrid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">'''
projects_block = '''      <div class="flex flex-wrap items-center gap-2 rounded-2xl border border-zinc-800 bg-black/30 p-3">
        <span class="text-xs font-bold text-zinc-300 ml-auto">نسخ احتياطي للمشاريع</span>
        <button type="button" onclick="exportStudioBackup()" class="px-3 py-2 rounded-xl bg-sky-500/10 border border-sky-400/30 text-sky-300 text-xs font-bold">تصدير نسخة JSON</button>
        <button type="button" onclick="document.getElementById('studioBackupInput').click()" class="px-3 py-2 rounded-xl bg-zinc-800 text-zinc-200 text-xs font-bold">استعادة نسخة</button>
        <input id="studioBackupInput" type="file" accept="application/json,.json" class="hidden" onchange="importStudioBackup(event)">
        <span class="w-full text-[10px] text-zinc-500">النسخة تشمل السكريبتات والمشاهد وإعداداتها. احتفظ بها خارج التطبيق.</span>
      </div>

'''
if 'exportStudioBackup()' not in s:
    if projects_anchor not in s: raise SystemExit('projects grid anchor missing')
    s=s.replace(projects_anchor, projects_block+projects_anchor, 1)

s=s.replace('<h3 class="font-cairo font-black text-base text-white leading-snug">\${item.title}</h3>', '<h3 class="font-cairo font-black text-base text-white leading-snug">\${escapeEditorHTML(item.title)}</h3>')
s=s.replace('function saveScriptEditorChanges() {', 'function saveScriptEditorChanges(shouldRefresh = true) {', 1)
s=s.replace('''      persistScripts();
      refreshAllUI();
      const status = document.getElementById('editorSaveStatus');''','''      persistScripts();
      if (shouldRefresh) refreshAllUI();
      const status = document.getElementById('editorSaveStatus');''',1)

backup_js = r'''
    let studioAutosaveTimer = null;
    function scheduleStudioAutosave() {
      const status = document.getElementById('editorSaveStatus');
      if (status) status.textContent = 'جارٍ حفظ التعديلات تلقائياً…';
      clearTimeout(studioAutosaveTimer);
      studioAutosaveTimer = setTimeout(() => {
        try { saveScriptEditorChanges(false); }
        catch (error) { if (status) status.textContent = 'تعذر الحفظ التلقائي؛ اضغط حفظ يدوياً'; }
      }, 1100);
    }

    function exportStudioBackup() {
      try {
        const payload = { format: 'anas-studio-backup', version: 1, exportedAt: new Date().toISOString(), projects: SCRIPTS };
        const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'ANAS-Studio-Backup-' + new Date().toISOString().slice(0,10) + '.json';
        document.body.appendChild(link); link.click(); link.remove();
        setTimeout(() => URL.revokeObjectURL(url), 1500);
        showToast('تم تصدير النسخة الاحتياطية. احتفظ بالملف في مكان آمن.');
      } catch (error) { showToast('تعذر إنشاء النسخة الاحتياطية.'); }
    }

    async function importStudioBackup(event) {
      const file = event.target.files && event.target.files[0];
      event.target.value = '';
      if (!file) return;
      if (file.size > 5 * 1024 * 1024) { showToast('حجم النسخة أكبر من 5 ميغابايت.'); return; }
      try {
        const data = JSON.parse(await file.text());
        if (!data || data.format !== 'anas-studio-backup' || !Array.isArray(data.projects) || data.projects.length < 1 || data.projects.length > 500) throw new Error('invalid backup');
        const seen = new Set();
        const restored = data.projects.map((project, index) => {
          if (!project || !Array.isArray(project.scenes) || project.scenes.length < 1 || project.scenes.length > 300) throw new Error('invalid project');
          const id = String(project.id == null ? 'restored-' + Date.now() + '-' + index : project.id);
          if (seen.has(id)) throw new Error('duplicate project');
          seen.add(id);
          const scenes = project.scenes.map(scene => {
            if (!scene || !Array.isArray(scene.lines) || scene.lines.length < 1 || scene.lines.length > 40) throw new Error('invalid scene');
            return {
              start: Number.isFinite(Number(scene.start)) ? Number(scene.start) : 0,
              end: Number.isFinite(Number(scene.end)) ? Math.max(0.1, Number(scene.end)) : 3,
              visual: String(scene.visual || 'camera_glare').slice(0,80),
              anim: String(scene.anim || 'reveal').slice(0,40),
              sfx: String(scene.sfx || 'whoosh').slice(0,40),
              lines: scene.lines.map(line => ({
                text: String(line && line.text != null ? line.text : '').slice(0,5000),
                color: /^#[0-9a-fA-F]{6}$/.test((line && line.color) || '') ? line.color : '#FFFFFF',
                size: Math.min(160, Math.max(12, Number(line && line.size) || 64)),
                weight: String((line && line.weight) || '700').slice(0,12),
                glow: Boolean(line && line.glow)
              }))
            };
          });
          return {
            id: id + '-' + Date.now() + '-' + index,
            num: String(index + 1).padStart(2, '0'),
            title: String(project.title || 'مشروع مستعاد ' + (index + 1)).slice(0,120),
            theme: Object.prototype.hasOwnProperty.call(THEME_META, project.theme) ? project.theme : 'time',
            scenes: scenes
          };
        });
        if (!confirm('سيتم استبدال ' + SCRIPTS.length + ' مشروع حالياً بـ ' + restored.length + ' مشروع من النسخة الاحتياطية. صدّر نسخة من الحالية أولاً إذا كنت تحتاجها. متابعة؟')) return;
        SCRIPTS = restored;
        currentIdx = 0;
        PROJECT_AUDIO_STORE.clear();
        persistScripts();
        navigateTo('projects');
        showToast('تمت استعادة ' + restored.length + ' مشروع. ملفات الصوت المولدة لا تتضمنها النسخة.');
      } catch (error) { showToast('ملف النسخة غير صالح أو تالف. لم يتم تغيير مشاريعك.'); }
    }

    document.addEventListener('input', event => {
      if (event.target.matches('[data-scene-text], #editorProjectTitle')) scheduleStudioAutosave();
      if (event.target.matches('[data-scene-text]')) updateScriptEditorMetrics();
    });
    document.addEventListener('change', event => {
      if (event.target.matches('#editorProjectTheme')) scheduleStudioAutosave();
    });
    // Flush pending edits synchronously when Android WebView backgrounds or closes the page.
    window.addEventListener('pagehide', () => {
      if (!studioAutosaveTimer) return;
      clearTimeout(studioAutosaveTimer);
      studioAutosaveTimer = null;
      try { saveScriptEditorChanges(false); } catch (error) {}
    });
'''
old_listener = '''    document.addEventListener('input', event => {
      if (event.target.matches('[data-scene-text]')) updateScriptEditorMetrics();
    });'''
if old_listener in s:
    s=s.replace(old_listener, backup_js, 1)
if 'function exportStudioBackup()' not in s:
    raise SystemExit('backup code insertion failed')

p.write_text(s)
