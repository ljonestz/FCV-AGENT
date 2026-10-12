"""File handlers must follow current arrays after removal or a new analysis."""

import subprocess

from tests.test_climate_lens_frontend import INDEX, _extract_js_function


def test_upload_handlers_use_current_file_arrays():
    source = INDEX.read_text(encoding="utf-8")
    script = """
const assert = require('assert');
const elements = {};
const document = {getElementById: id => elements[id] ||= {
  handlers: {}, classList: {add(){}, remove(){}},
  addEventListener(name, callback){this.handlers[name] = callback;}
}};
const setTimeout = () => {};
const addFiles = (files, arr) => arr.push(...files);
let current = [];
""" + _extract_js_function(source, "setupZone") + """
setupZone('zone', 'input', () => current, 'p');
for (const event of ['input', 'change']) {
  current = [];
  elements.input.files = [{name: 'replacement.pdf'}];
  elements.input.handlers[event].call(elements.input);
  assert.equal(current[0].name, 'replacement.pdf');
}
current = [];
elements.zone.handlers.drop({preventDefault(){}, dataTransfer:{files:[{name:'drop.pdf'}]}});
assert.equal(current[0].name, 'drop.pdf');
"""
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_reset_clears_all_upload_categories_and_metadata():
    reset = _extract_js_function(INDEX.read_text(encoding="utf-8"), "reset")
    for field in ("pF", "pkF", "cF"):
        assert f"{field}=[]" in reset
    assert "fileMetadata={}" in reset
