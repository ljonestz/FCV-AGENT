(function (global) {
  const LARGE_SESSION_KEYS = new Set([
    'stage2_under_hood',
    'fcv_express_stageOutputs',
    'fcv_express_stageHists',
    'fcv_express_curS'
  ]);
  const CACHE_PREFIXES = ['deeper_', 'explorer_priority_'];
  const nativeRemoveItem = global.Storage && global.Storage.prototype
    ? global.Storage.prototype.removeItem
    : null;

  function isQuotaExceededError(error) {
    return !!error && (
      error.name === 'QuotaExceededError' ||
      error.name === 'NS_ERROR_DOM_QUOTA_REACHED' ||
      error.code === 22 ||
      error.code === 1014
    );
  }

  function getCurrentAssessmentIdSafe() {
    try {
      return typeof global.getCurrentAssessmentId === 'function'
        ? global.getCurrentAssessmentId()
        : '';
    } catch (_) {
      return '';
    }
  }

  function storageKeys(storage) {
    const keys = [];
    try {
      for (let i = 0; i < storage.length; i++) {
        const key = storage.key(i);
        if (key) keys.push(key);
      }
    } catch (_) {}
    return keys;
  }

  function removeActualStorageKey(storage, key) {
    try {
      if (nativeRemoveItem) nativeRemoveItem.call(storage, key);
      else storage.removeItem(key);
      return true;
    } catch (_) {
      return false;
    }
  }

  function isPrunableKey(key, currentAssessmentId) {
    if (!key) return false;
    if (CACHE_PREFIXES.some(prefix => key.indexOf(prefix) === 0)) return true;
    if (LARGE_SESSION_KEYS.has(key)) return true; // legacy unscoped large entries

    if (key.indexOf('fcv:') === 0) {
      const parts = key.split(':');
      if (parts.length >= 3) {
        const assessmentId = parts[1];
        const sessionKey = parts.slice(2).join(':');
        return assessmentId !== currentAssessmentId && LARGE_SESSION_KEYS.has(sessionKey);
      }
    }
    return false;
  }

  function pruneAppStorage(storage) {
    if (!storage) return 0;
    const currentAssessmentId = getCurrentAssessmentIdSafe();
    let removed = 0;

    storageKeys(storage).forEach(key => {
      if (isPrunableKey(key, currentAssessmentId) && removeActualStorageKey(storage, key)) {
        removed += 1;
      }
    });

    return removed;
  }

  function safeLocalStorageSet(key, value) {
    try {
      global.localStorage.setItem(key, value);
      return true;
    } catch (error) {
      if (!isQuotaExceededError(error)) return false;
    }

    pruneAppStorage(global.localStorage);

    try {
      global.localStorage.setItem(key, value);
      return true;
    } catch (_) {
      return false;
    }
  }

  function saveStage2UnderHood(underHood) {
    let payload = '{}';
    try {
      payload = JSON.stringify(underHood || {});
    } catch (_) {
      return false;
    }
    return safeLocalStorageSet('stage2_under_hood', payload);
  }

  function readStage2UnderHood(fallback) {
    if (fallback && (
      fallback.recs_table ||
      fallback.dnh_checklist ||
      fallback.questions_map ||
      fallback.evidence_trail
    )) {
      return fallback;
    }
    try {
      return JSON.parse(global.localStorage.getItem('stage2_under_hood') || '{}');
    } catch (_) {
      return {};
    }
  }

  global.fcvIsQuotaExceededError = isQuotaExceededError;
  global.fcvPruneAppStorage = pruneAppStorage;
  global.fcvSafeLocalStorageSet = safeLocalStorageSet;
  global.fcvSaveStage2UnderHood = saveStage2UnderHood;
  global.fcvReadStage2UnderHood = readStage2UnderHood;
})(typeof window !== 'undefined' ? window : globalThis);
