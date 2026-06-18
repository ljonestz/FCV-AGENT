const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const helperPath = path.join(__dirname, '..', 'static', 'fcv_storage.js');
const helperSource = fs.readFileSync(helperPath, 'utf8');

function makeQuotaError() {
  const err = new Error('quota exceeded');
  err.name = 'QuotaExceededError';
  err.code = 22;
  return err;
}

function createStorage(seed = {}) {
  const store = new Map(Object.entries(seed));
  return {
    get length() {
      return store.size;
    },
    key(index) {
      return Array.from(store.keys())[index] || null;
    },
    getItem(key) {
      return store.has(key) ? store.get(key) : null;
    },
    setItem(key, value) {
      store.set(key, String(value));
    },
    removeItem(key) {
      store.delete(key);
    },
    dump() {
      return Object.fromEntries(store.entries());
    }
  };
}

function loadHelper(localStorage, extras = {}) {
  const context = {
    window: null,
    localStorage,
    console,
    ...extras
  };
  context.window = context;
  vm.createContext(context);
  vm.runInContext(helperSource, context);
  return context;
}

function testStage2UnderHoodQuotaDoesNotThrow() {
  const localStorage = createStorage();
  localStorage.setItem = function () {
    throw makeQuotaError();
  };
  const ctx = loadHelper(localStorage);

  assert.doesNotThrow(() => {
    const ok = ctx.fcvSaveStage2UnderHood({ evidence_trail: 'x'.repeat(1024) });
    assert.strictEqual(ok, false);
  });
}

function testOldAssessmentPayloadsArePrunedBeforeRetry() {
  const currentId = 'current-assessment';
  const localStorage = createStorage({
    'fcv:old-assessment:stage2_under_hood': 'x'.repeat(1024),
    'fcv:old-assessment:fcv_express_stageOutputs': 'x'.repeat(1024),
    'fcv:current-assessment:stage2_under_hood': 'keep-me',
    'deeper_0_trail': 'cached trail'
  });
  const originalSetItem = localStorage.setItem.bind(localStorage);
  let firstWrite = true;
  localStorage.setItem = function (key, value) {
    if (firstWrite) {
      firstWrite = false;
      throw makeQuotaError();
    }
    originalSetItem(key, value);
  };

  const ctx = loadHelper(localStorage, {
    getCurrentAssessmentId: () => currentId
  });
  const ok = ctx.fcvSafeLocalStorageSet('stage2_under_hood', '{"ok":true}');
  const dump = localStorage.dump();

  assert.strictEqual(ok, true);
  assert.strictEqual(dump['fcv:old-assessment:stage2_under_hood'], undefined);
  assert.strictEqual(dump['fcv:old-assessment:fcv_express_stageOutputs'], undefined);
  assert.strictEqual(dump.deeper_0_trail, undefined);
  assert.strictEqual(dump['fcv:current-assessment:stage2_under_hood'], 'keep-me');
  assert.strictEqual(dump.stage2_under_hood, '{"ok":true}');
}

testStage2UnderHoodQuotaDoesNotThrow();
testOldAssessmentPayloadsArePrunedBeforeRetry();
console.log('frontend storage helper tests passed');
