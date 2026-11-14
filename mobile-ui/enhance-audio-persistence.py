from pathlib import Path
import sys

p = Path(sys.argv[1])
s = p.read_text(encoding="utf-8")

anchor = "    const PROJECT_AUDIO_STORE = new Map(); // scriptId -> { buffer, wavBlob, duration, label, isAI }"
if anchor not in s:
    raise SystemExit("PROJECT_AUDIO_STORE anchor missing")

audio_js = r'''
    // Durable per-project audio storage: voice tracks survive app restarts.
    const AUDIO_DB_NAME = 'anas-studio-audio';
    let audioDbPromise = null;
    function openStudioAudioDb() {
      if (!window.indexedDB) return Promise.reject(new Error('IndexedDB unavailable'));
      if (!audioDbPromise) audioDbPromise = new Promise((resolve, reject) => {
        const request = indexedDB.open(AUDIO_DB_NAME, 1);
        request.onupgradeneeded = () => {
          if (!request.result.objectStoreNames.contains('assets')) {
            request.result.createObjectStore('assets', { keyPath: 'projectId' });
          }
        };
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
      });
      return audioDbPromise;
    }
    async function saveProjectAudioAsset(projectId, audio) {
      if (!audio?.wavBlob) return;
      try {
        const db = await openStudioAudioDb();
        await new Promise((resolve, reject) => {
          const tx = db.transaction('assets', 'readwrite');
          tx.objectStore('assets').put({
            projectId: String(projectId), blob: audio.wavBlob,
            label: String(audio.label || 'Audio'), isAI: Boolean(audio.isAI),
            savedAt: Date.now()
          });
          tx.oncomplete = resolve; tx.onerror = () => reject(tx.error);
          tx.onabort = () => reject(tx.error);
        });
      } catch (error) { console.warn('Could not save project audio:', error); }
    }
    async function deleteProjectAudioAsset(projectId) {
      try {
        const db = await openStudioAudioDb();
        await new Promise((resolve, reject) => {
          const tx = db.transaction('assets', 'readwrite');
          tx.objectStore('assets').delete(String(projectId));
          tx.oncomplete = resolve; tx.onerror = () => reject(tx.error); tx.onabort = () => reject(tx.error || new Error('Audio delete aborted'));
        });
      } catch (error) { console.warn('Could not delete project audio:', error); }
    }
    async function restoreProjectAudioAssets() {
      if (!window.indexedDB) return;
      try {
        const db = await openStudioAudioDb();
        for (const project of SCRIPTS) {
          const record = await new Promise((resolve, reject) => {
            const tx = db.transaction('assets', 'readonly');
            const request = tx.objectStore('assets').get(String(project.id));
            request.onsuccess = () => resolve(request.result || null);
            request.onerror = () => reject(request.error);
          });
          if (!record?.blob) continue;
          try {
            const buffer = await audioEngine.decodeAudioBlob(record.blob);
            Map.prototype.set.call(PROJECT_AUDIO_STORE, project.id, {
              buffer, wavBlob: record.blob, duration: buffer.duration,
              label: record.label || 'صوت محفوظ', isAI: Boolean(record.isAI)
            });
          } catch (error) { console.warn('Could not decode saved audio:', error); }
        }
        refreshAllUI();
      } catch (error) { console.warn('Audio restore unavailable:', error); }
    }
    const originalAudioSet = PROJECT_AUDIO_STORE.set.bind(PROJECT_AUDIO_STORE);
    PROJECT_AUDIO_STORE.set = function(projectId, audio) {
      const result = originalAudioSet(projectId, audio);
      if (audio?.wavBlob) saveProjectAudioAsset(projectId, audio);
      return result;
    };
    const originalAudioDelete = PROJECT_AUDIO_STORE.delete.bind(PROJECT_AUDIO_STORE);
    PROJECT_AUDIO_STORE.delete = function(projectId) {
      const result = originalAudioDelete(projectId);
      deleteProjectAudioAsset(projectId);
      return result;
    };
'''
if "const AUDIO_DB_NAME" not in s:
    s = s.replace(anchor, anchor + "\n\n" + audio_js, 1)

load_anchor = "        navigateTo('projects');\n        lastTick = performance.now();"
if load_anchor not in s:
    raise SystemExit("page load anchor missing")
if "restoreProjectAudioAssets();" not in s:
    s = s.replace(load_anchor, "        navigateTo('projects');\n        restoreProjectAudioAssets();\n        lastTick = performance.now();", 1)

render_anchor = "    async function startCompleteRender(onCompleteCallback = null) {\n      if (isRecording) return;"
if render_anchor not in s:
    raise SystemExit("render function anchor missing")
if "تصدير الفيديو غير مدعوم" not in s:
    s = s.replace(render_anchor, render_anchor + "\n      if (!window.MediaRecorder || !canvas.captureStream) { showToast('تصدير الفيديو غير مدعوم في إصدار WebView الحالي. حدّث Android System WebView ثم أعد المحاولة.'); return; }", 1)

stop_anchor = "      mediaRecorder.onstop = () => {\n        const finalMime"
if stop_anchor not in s:
    raise SystemExit("recorder stop anchor missing")
if "stream.getTracks().forEach" not in s:
    s = s.replace(stop_anchor, "      mediaRecorder.onstop = () => {\n        try { stream.getTracks().forEach(track => track.stop()); } catch (e) {}\n        const finalMime", 1)

p.write_text(s, encoding="utf-8")
