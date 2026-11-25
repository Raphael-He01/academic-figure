#!/usr/bin/env python3
"""Inspect the local colour registry and build its documentation-only swatch UI."""
import argparse
import base64
from html import escape
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'assets/palettes/catalog.json'


def read_catalog():
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    seen = set()
    aliases = set()
    for p in data['palettes']:
        if not re.fullmatch(r'[a-z][a-z0-9_]*', p['id']) or p['id'] in seen:
            raise ValueError('Invalid or duplicate ID: ' + p['id'])
        seen.add(p['id'])
        for key in [p['id'], p['name']] + p['aliases']:
            if key in aliases:
                raise ValueError('Ambiguous name/alias: ' + key)
            aliases.add(key)
        if p['kind'] not in ('categorical', 'sequential', 'diverging', 'cyclic', 'emphasis'):
            raise ValueError('Invalid semantic kind')
        if p['status'] not in ('candidate', 'reviewed-in-context', 'deprecated'):
            raise ValueError('Invalid status')
        colours = p['source_colors']
        for c in colours + p['main'] + p['support'] + [p['background'], p['text']]:
            if not re.fullmatch(r'#[0-9A-F]{6}', c):
                raise ValueError('Invalid HEX: ' + c)
        if not p['main'] or not set(p['main'] + p['support']) <= set(colours):
            raise ValueError('Selected colours must have recorded values')
        if set(p['main']) & set(p['support']):
            raise ValueError('Main/support roles overlap')
        for c in colours:
            if p['rgb'][c] != [int(c[i:i+2], 16) for i in (1, 3, 5)]:
                raise ValueError('HEX/RGB mismatch: ' + c)
        source = (ROOT / p['source']['record']).resolve()
        if not source.is_relative_to(ROOT) or not source.is_file():
            raise ValueError('Invalid source record')
        if p['status'] == 'reviewed-in-context' and not p.get('review_evidence'):
            raise ValueError('Reviewed status needs evidence and scope')
    if data['default_id'] not in seen:
        raise ValueError('Missing default ID')
    return data


# This attribution applies to the thirteen founding entries, even as the library grows.
SOURCE_CREDITS = (
    "首批色卡含 10 套参考组合和 3 套新编组合，由 Raphael He 整理并分配用途。",
    "参考海报可见“科研调色谱”水印，原作者、首发出处及许可尚待核实。",
)


def render_page(data, standalone=False, overview=None):
    links = '<a href="../../references/palette-library.md">使用与收录说明</a> · <a href="catalog.json">机器可读色卡</a>'
    if standalone:
        encoded = base64.b64encode(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")).decode("ascii")
        links = (
            '<details id="guide"><summary>配色使用说明</summary><p>输入名称、ID 或色值查找。'
            '选用组合后可复制绘图指令。一套图使用一套色卡，跨面板保持组别对应关系。</p></details>'
            f'<a download="academic-figure-palettes.json" href="data:application/json;base64,{encoded}">下载完整色值 JSON</a>'
        )
        if overview is not None:
            png = base64.b64encode(overview).decode("ascii")
            links += f' · <a download="palettes.png" href="data:image/png;base64,{png}">下载高清色卡总览</a>'
    payload = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
    page = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Academic Figure · 科研色卡库</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#FAF8F5;color:#292929;font:16px/1.65 system-ui,sans-serif}main{max-width:1180px;margin:auto;padding:36px 24px}h1{margin:0;font-size:30px}h2{font-size:21px;margin:0}p{margin:8px 0 20px}.muted{color:#626262;font-size:14px}.tools{display:flex;gap:12px;flex-wrap:wrap;margin:24px 0}input,select,button,textarea{font:inherit;border:1px solid #ADA59D;border-radius:7px;padding:10px;background:white;color:#292929}input{flex:1;min-width:230px}button{cursor:pointer}button:hover,button:focus{outline:2px solid #527F94}#cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(310px,100%),1fr));gap:20px}.card{background:white;border:1px solid #DDD8D2;border-radius:12px;padding:22px}.label{font-size:13px;color:#66574C;margin:10px 0 6px}.swatches{display:flex;gap:8px}.chip{flex:1;min-width:0}.patch{height:58px;border-radius:6px;border:1px solid #0002}.code{font:12px/1.8 ui-monospace,monospace;color:#333}.badge{display:inline-block;background:#F3E6CE;border-radius:4px;padding:1px 7px;font-size:12px}.selected{border:2px solid #527F94}textarea{display:block;width:100%;min-height:90px;margin-top:12px}details{font-size:14px;margin:14px 0}.feedback{min-height:25px}a{color:#365D6B}.notice{padding:16px;background:#F3E6CE;border-radius:8px}footer{margin-top:28px}@media print{.tools,button,#selection{display:none}.card{break-inside:avoid}}
</style><main><h1>科研色卡库</h1><p>Academic Figure · Raphael He<br>简约、清爽、浅暖为主；以可读性和数据含义决定最终配色。</p>
<div class="notice">这些色卡是候选组合。色卡展示不等于色盲、灰度或真实图稿验收。浅色主要用于填充，关键文字和细线须保持清晰。</div>
<div class="tools"><input id="search" aria-label="搜索色卡" placeholder="搜索中文名、ID 或 HEX"><select id="filter" aria-label="筛选"><option value="all">全部色卡</option><option value="recommended">优先组合</option></select></div>
<p id="count" class="muted"></p><section id="selection" hidden><h2>已选择的配色指令</h2><textarea id="prompt" readonly aria-label="可复制的配色指令"></textarea><button id="copy">复制指令</button><span id="feedback" role="status" class="feedback"></span><p class="muted">将指令发送给使用 academic-figure 的助手。页面选择不会自动修改项目或已导出的图。</p></section><div id="cards"></div>
<footer class="muted">同一组别跨面板保持同色；连续热图需另按顺序、正负或周期语义选色。<br>FOOTER_LINKS<p>SOURCE_CREDITS_TEXT</p></footer></main>
<script type="application/json" id="data">PAYLOAD</script><script>
const data=JSON.parse(document.getElementById('data').textContent);
const cards=document.getElementById('cards');let selected='';
function el(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n}
function swatches(values){const row=el('div',undefined,'swatches');values.forEach(c=>{const chip=el('div',undefined,'chip'),patch=el('div',undefined,'patch');patch.style.backgroundColor=c;chip.append(patch,el('div',c,'code'));row.append(chip)});return row}
function render(){cards.replaceChildren();const q=document.getElementById('search').value.trim().toLowerCase();const f=document.getElementById('filter').value;const list=data.palettes.filter(p=>(f==='all'||['default','recommended'].includes(p.priority))&&[p.id,p.name,...p.aliases,...p.source_colors].join(' ').toLowerCase().includes(q));document.getElementById('count').textContent=`显示 ${list.length} / ${data.palettes.length} 套 · 记录更新 ${data.updated}`;
list.sort((a,b)=>(a.id===data.default_id?-1:b.id===data.default_id?1:0)).forEach(p=>{const card=el('article',undefined,'card'+(selected===p.id?' selected':''));card.append(el('h2',p.name),el('div',p.id+' · v'+p.version,'code'),el('span',p.priority==='default'?'默认候选':p.priority==='recommended'?'优先候选':'备选','badge'),el('div','主色 · 建议 '+p.recommended_categories.join('–')+' 类','label'),swatches(p.main),el('div','辅助填充 · 不自动增加类别','label'),swatches(p.support));const details=el('details');details.append(el('summary','用途、来源与验证状态'),el('p',p.uses),el('p',p.limits),el('p','来源：'+p.source.label+' · '+p.source.reviewed+'；色值依据：'+p.source.value_basis),el('p','状态：'+p.status+'；实际图稿/CVD/灰度：'+p.validation.actual_figure+' / '+p.validation.cvd+' / '+p.validation.grayscale),el('p','背景 '+p.background+'；文字 '+p.text));const extra=p.source_colors.filter(c=>!p.main.includes(c)&&!p.support.includes(c));
if(extra.length){details.append(el('div','原卡其余色值','label'),swatches(extra))}
card.append(details);const btn=el('button','选用此组合');btn.onclick=()=>{selected=p.id;document.getElementById('selection').hidden=false;document.getElementById('prompt').value=`请使用 academic-figure 的「${p.name}」（${p.id}，版本 ${p.version}）绘图。保持简约、清爽、浅暖风格，将颜色绑定真实组名，跨面板一致，并检查最终尺寸下的色觉差异与灰度可读性。连续色标按数据含义另选。`;document.getElementById('feedback').textContent='已选择；复制指令后发送给助手。';render()};card.append(btn);cards.append(card)})}
document.getElementById('search').oninput=render;document.getElementById('filter').onchange=render;document.getElementById('copy').onclick=async()=>{const p=document.getElementById('prompt');try{await navigator.clipboard.writeText(p.value);document.getElementById('feedback').textContent='已复制'}catch(e){p.focus();p.select();document.getElementById('feedback').textContent='请按 Command+C / Ctrl+C 复制选中文字'}};render();
</script></html>'''
    return page.replace('FOOTER_LINKS', links).replace('SOURCE_CREDITS_TEXT', escape(' '.join(SOURCE_CREDITS))).replace('PAYLOAD', payload)


def build(data):
    dest = ROOT / 'assets/palettes/catalog.html'
    dest.write_text(render_page(data), encoding="utf-8", newline="\n")
    print('Built assets/palettes/catalog.html (' + str(len(data['palettes'])) + ' cards)')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument('--list', action='store_true')
    group.add_argument('--show', metavar='NAME_OR_ID')
    group.add_argument('--build', action='store_true')
    args = ap.parse_args()
    try:
        data = read_catalog()
        if args.build:
            build(data)
        elif args.list:
            for p in data['palettes']:
                print(p['id'] + '\t' + p['name'] + '\t' + p['status'])
        else:
            matches = [p for p in data['palettes'] if args.show in [p['id'], p['name']] + p['aliases']]
            if not matches:
                raise ValueError('No palette matches; use --list. Never guess a replacement.')
            print(json.dumps(matches[0], ensure_ascii=False, indent=2))
    except (ValueError, KeyError, OSError, TypeError) as e:
        print('Palette catalog error: ' + str(e), file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
