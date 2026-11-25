#!/usr/bin/env node
// Offline component tests. A minimal in-memory DOM is not a browser or visual audit.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'assets/palettes/catalog.html'), 'utf8');
const registry = JSON.parse(fs.readFileSync(path.join(root, 'assets/palettes/catalog.json'), 'utf8'));
const payload = html.match(/<script type="application\/json" id="data">([\s\S]*?)<\/script>/)[1];
const js = html.match(/<script>([\s\S]*?)<\/script>/)[1];
assert.deepEqual(JSON.parse(payload), registry);
let count = 0;
function passed(name) { count++; console.log('PASS ' + name); }
class Element {
  constructor(tag) {
    this.tagName = tag; this.children = []; this.style = {};
    this.textContent = ''; this.className = ''; this.value = ''; this.hidden = false;
  }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this.children = nodes; }
  focus() { this.focused = true; }
  select() { this.selected = true; }
}
const ids = Object.fromEntries(['data','cards','search','filter','count','selection','prompt','copy','feedback'].map(k => [k, new Element(k)]));
ids.data.textContent = payload; ids.filter.value = 'all'; ids.selection.hidden = true;
let copied = '';
const navigator = {clipboard: {writeText: async text => { copied = text; }}};
const context = vm.createContext({
  document: {getElementById: id => { assert.ok(ids[id], 'Unknown element ' + id); return ids[id]; }, createElement: tag => new Element(tag)},
  navigator
});
// Compile and execute only the generated page logic against these in-memory doubles.
new vm.Script(js, {filename: 'catalog-inline.js'}).runInContext(context, {timeout: 1000});
function title(card) { return card.children.find(x => x.tagName === 'h2').textContent; }
function find(card, tag) { return card.children.find(x => x.tagName === tag); }
function search(s) { ids.search.value = s; ids.search.oninput(); }
function filter(s) { ids.filter.value = s; ids.filter.onchange(); }
async function main() {
  assert.equal(ids.cards.children.length, registry.palettes.length);
  assert.equal(title(ids.cards.children[0]), registry.palettes.find(p => p.id === registry.default_id).name);
  passed('initial render and default-first ordering');
  for (const p of registry.palettes) {
    for (const key of [p.id, p.name, ...p.aliases]) {
      search(key);
      const expected = registry.palettes.filter(c => [c.id,c.name,...c.aliases,...c.source_colors].join(' ').toLowerCase().includes(key.toLowerCase())).map(c => c.name).sort();
      assert.deepEqual(ids.cards.children.map(title).sort(), expected);
      assert.ok(ids.cards.children.some(c => title(c) === p.name));
    }
    const card = ids.cards.children.find(c => title(c) === p.name);
    const rows = card.children.filter(x => x.className === 'swatches');
    assert.deepEqual(rows[0].children.map(x => x.children[0].style.backgroundColor), p.main);
    assert.deepEqual(rows[1].children.map(x => x.children[0].style.backgroundColor), p.support);
    find(card, 'button').onclick();
    assert.equal(ids.selection.hidden, false);
    assert.ok(ids.prompt.value.includes(p.id)); assert.ok(ids.prompt.value.includes(p.name));
    assert.ok(ids.prompt.value.includes('版本 ' + p.version));
    assert.ok(ids.cards.children.find(c => title(c) === p.name).className.includes('selected'));
    passed(p.id + ': name/alias search, swatch values, selection and versioned instruction');
  }
  search(' #e7af98 '); assert.ok(ids.cards.children.some(c => title(c) === '杏雨青荷')); passed('trimmed case-insensitive HEX search');
  search(''); filter('recommended'); assert.equal(ids.cards.children.length, registry.palettes.filter(p => ['default','recommended'].includes(p.priority)).length); passed('preferred filter');
  search('不存在的色卡'); assert.equal(ids.cards.children.length, 0); assert.ok(ids.count.textContent.startsWith('显示 0')); passed('no-match state');
  filter('all'); search('rose_mist'); find(ids.cards.children[0], 'button').onclick();
  await ids.copy.onclick(); assert.equal(copied, ids.prompt.value); assert.equal(ids.feedback.textContent, '已复制'); passed('copy-success branch with stub clipboard');
  navigator.clipboard.writeText = async () => { throw Error('test denied'); };
  await ids.copy.onclick(); assert.ok(ids.prompt.focused && ids.prompt.selected); assert.ok(ids.feedback.textContent.includes('Command+C')); passed('denied-copy manual-selection fallback');
  navigator.clipboard = undefined; ids.prompt.focused = false; ids.prompt.selected = false;
  await ids.copy.onclick(); assert.ok(ids.prompt.focused && ids.prompt.selected); passed('absent clipboard API fallback');
  assert.deepEqual(JSON.parse(fs.readFileSync(path.join(root, 'assets/palettes/catalog.json'), 'utf8')), registry);
  passed('selection leaves registry unchanged');
  console.log(`SUMMARY ${count} checks passed. Offline DOM doubles only; no real browser, layout, system clipboard or figure-accessibility acceptance.`);
}
main().catch(err => {console.error(err); process.exitCode = 1;});
