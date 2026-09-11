from pathlib import Path
from html import escape
from hashlib import sha256
root=Path(__file__).resolve().parents[1]
source=root/'reviews/goal-audit.md'
text=source.read_text()
diagram='''<svg viewBox="0 0 900 190" role="img" aria-label="两个模式分别计算后汇总，避免提前聚合造成错误"><g font-family="sans-serif" font-size="19"><rect x="5" y="10" width="650" height="60" rx="12" fill="#dbeafe"/><text x="25" y="48">模式一：存在度 0.5 × 意愿 1 × 匹配 0 = 0</text><rect x="5" y="115" width="650" height="60" rx="12" fill="#dcfce7"/><text x="25" y="153">模式二：存在度 0.5 × 意愿 0 × 匹配 1 = 0</text><path d="M660 40 L720 95 L660 145" fill="none" stroke="#334155" stroke-width="3"/><text x="735" y="102">总贡献 0</text></g></svg>'''
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PBro完整目标复审</title><style>body{font:17px/1.8 system-ui;color:#172b42;background:#f1f5f9;margin:0}main{max-width:1000px;margin:auto;padding:32px}svg{width:100%;background:white}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit;background:white;padding:24px;border-radius:12px}small{overflow-wrap:anywhere}.warning{padding:16px;background:#fff1c2}</style><main><h1>为什么重新打开机制审查</h1><p class="warning">状态：未冻结。局部字段通过审核，不等于完整设计与原型通过。</p>'''+diagram+'<small>来源 reviews/goal-audit.md · SHA256 '+sha256(text.encode()).hexdigest()+'</small><pre>'+escape(text)+'</pre></main></html>'
(root/'assets/goal-audit.html').write_text(page)
