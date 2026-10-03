import os
import json
import html
import re

def escape(s):
    return html.escape(str(s or ''))

def markdown_to_html(md_text):
    if not md_text:
        return ""
    
    lines = md_text.split('\n')
    out = []
    in_code_block = False
    code_lines = []
    in_list = False

    for line in lines:
        stripped = line.strip()
        
        if stripped.startswith('```'):
            if in_code_block:
                in_code_block = False
                joined_code = escape("\n".join(code_lines))
                out.append(f'<div class="my-4 rounded-xl overflow-hidden border border-slate-800 bg-slate-950 text-slate-100 p-4 font-mono text-xs overflow-x-auto"><pre><code>{joined_code}</code></pre></div>')
                code_lines = []
            else:
                if in_list:
                    out.append('</ul>')
                    in_list = False
                in_code_block = True
            continue
            
        if in_code_block:
            code_lines.append(line)
            continue

        if stripped.startswith('# '):
            if in_list: out.append('</ul>'); in_list = False
            out.append(f'<h1 class="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white mt-8 mb-4 border-b border-slate-200 dark:border-slate-800 pb-2">{escape(stripped[2:])}</h1>')
        elif stripped.startswith('## '):
            if in_list: out.append('</ul>'); in_list = False
            out.append(f'<h2 class="text-lg sm:text-xl font-bold text-slate-900 dark:text-white mt-7 mb-3 flex items-center gap-2"><span class="w-2 h-2 rounded-full bg-sky-500"></span>{escape(stripped[3:])}</h2>')
        elif stripped.startswith('### '):
            if in_list: out.append('</ul>'); in_list = False
            out.append(f'<h3 class="text-sm sm:text-base font-bold text-slate-800 dark:text-slate-200 mt-5 mb-2">{escape(stripped[4:])}</h3>')
        elif stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                out.append('<ul class="list-disc list-inside space-y-1.5 my-3 text-xs sm:text-sm text-slate-600 dark:text-slate-400">')
                in_list = True
            item_text = escape(stripped[2:])
            item_text = re.sub(r'\*\*(.*?)\*\*', r'<strong class="text-slate-900 dark:text-slate-200 font-semibold">\1</strong>', item_text)
            out.append(f'<li>{item_text}</li>')
        elif stripped.startswith('> '):
            if in_list: out.append('</ul>'); in_list = False
            quote_text = escape(stripped[2:])
            quote_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', quote_text)
            out.append(f'<blockquote class="border-l-4 border-sky-500 pl-4 py-1.5 my-3 text-xs sm:text-sm text-slate-600 dark:text-slate-400 bg-sky-50/50 dark:bg-sky-950/20 rounded-r-lg italic">{quote_text}</blockquote>')
        elif stripped == '':
            if in_list:
                out.append('</ul>')
                in_list = False
        else:
            if in_list:
                out.append('</ul>')
                in_list = False
            para_text = escape(stripped)
            para_text = re.sub(r'\*\*(.*?)\*\*', r'<strong class="text-slate-900 dark:text-slate-200 font-semibold">\1</strong>', para_text)
            out.append(f'<p class="text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed my-2.5">{para_text}</p>')

    if in_list:
        out.append('</ul>')
    if in_code_block and code_lines:
        joined_code = escape("\n".join(code_lines))
        out.append(f'<div class="my-4 rounded-xl overflow-hidden border border-slate-800 bg-slate-950 text-slate-100 p-4 font-mono text-xs overflow-x-auto"><pre><code>{joined_code}</code></pre></div>')

    return '\n'.join(out)

def generate_agent_page(agent, peer_agents, china_agents):
    agent_id = agent['id']
    name_zh = agent.get('name_zh', agent['name'])
    name_en = agent.get('name_en', agent['name'])
    emoji = agent.get('emoji', '🤖')
    desc_zh = agent.get('desc_zh', agent['desc'])
    desc_en = agent.get('desc_en', agent['desc'])
    dept = agent['department']
    dept_en = agent.get('department_en', dept)
    is_china = agent.get('is_china_original', False)
    rec = agent.get('recommended', {})
    model_name = rec.get('model', 'deepseek-v4-pro')
    cot_level = rec.get('cot', 'deep')
    
    model_badge = 'DeepSeek-V4-Pro (Max Thinking)' if 'pro' in model_name else 'DeepSeek-V4.1-Flash (1M 上下文)'
    cot_label = '🔥 极致深度思考 (Max Thinking)' if cot_level in ['max', 'deep'] else '🧠 标准思维链 (Standard CoT)'
    
    # Page SEO title and description
    title = f"DeepSeek 【{name_zh}】 ({name_en}) 提示词与系统指令 - {dept} AI 专家 | DeepSeek Studio"
    meta_desc = f"专为 DeepSeek-V4/R1 设计的【{name_zh}】（{name_en}）工业级中英双语提示词与系统人设规范。{desc_zh}支持一键中英文切换、装填微调与直接复制。"
    canonical_url = f"https://deepseek.pacebowl.com/agents/{agent_id}.html"
    
    # Render documentation markdown bodies
    rendered_body_zh = markdown_to_html(agent.get('full_prompt_zh', agent.get('full_prompt', '')))
    rendered_body_en = markdown_to_html(agent.get('full_prompt_en', agent.get('full_prompt', '')))
    
    # Synthesized Prompt ZH
    prompt_zh = f"""你是一位专业的【{name_zh}】（{dept}）。

【角色定位与核心专长】
{desc_zh}

{agent.get('task_zh', agent.get('task', ''))}

{agent.get('context_zh', agent.get('context', ''))}"""

    # Synthesized Prompt EN (Native Upstream)
    prompt_en = f"""You are a professional [{name_en}] ({dept_en}).

[Core Mission & Domain Expertise]
{desc_en}

{agent.get('task_en', agent.get('task', ''))}

{agent.get('context_en', agent.get('context', ''))}"""

    # Peer links
    peer_html = ""
    for p in peer_agents[:6]:
        peer_name_en = p.get('name_en', '')
        peer_html += f"""
        <a href="{p['id']}.html" class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 hover:border-sky-400 dark:hover:border-sky-500/50 bg-white dark:bg-slate-900/60 transition group flex flex-col justify-between">
          <div>
            <div class="flex items-center gap-2 mb-1.5">
              <span class="text-base">{p.get('emoji', '🤖')}</span>
              <h4 class="text-xs font-bold text-slate-900 dark:text-white group-hover:text-sky-600 dark:group-hover:text-sky-400 transition truncate">{p.get('name_zh', p['name'])}</h4>
            </div>
            <p class="text-[11px] text-slate-500 line-clamp-2 leading-relaxed">{p.get('desc_zh', p['desc'])}</p>
          </div>
          <span class="text-[10px] text-sky-600 dark:text-sky-400 font-semibold mt-2 inline-flex items-center gap-1">中英双语 Prompt →</span>
        </a>
        """

    # China links
    china_html = ""
    for c in china_agents[:6]:
        china_html += f"""
        <a href="{c['id']}.html" class="p-3.5 rounded-xl border border-rose-200/70 dark:border-rose-950/60 hover:border-rose-400 bg-white dark:bg-slate-900/60 transition group flex flex-col justify-between">
          <div>
            <div class="flex items-center gap-2 mb-1.5">
              <span class="text-base">{c.get('emoji', '🤖')}</span>
              <span class="px-1.5 py-0.2 rounded text-[9px] font-bold bg-rose-50 text-rose-600 border border-rose-200 dark:bg-rose-950/40 dark:border-rose-900/60">🇨🇳 原创</span>
              <h4 class="text-xs font-bold text-slate-900 dark:text-white group-hover:text-rose-600 dark:group-hover:text-rose-400 transition truncate">{c.get('name_zh', c['name'])}</h4>
            </div>
            <p class="text-[11px] text-slate-500 line-clamp-2 leading-relaxed">{c.get('desc_zh', c['desc'])}</p>
          </div>
          <span class="text-[10px] text-rose-600 dark:text-rose-400 font-semibold mt-2 inline-flex items-center gap-1">使用中国专家 →</span>
        </a>
        """

    js_prompt_zh = json.dumps(prompt_zh)
    js_prompt_en = json.dumps(prompt_en)

    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(meta_desc)}">
  <meta name="keywords" content="DeepSeek {name_zh} 提示词, {name_en} prompt, DeepSeek V4 {name_en}, {dept} AI专家, DeepSeek-R1 提示词, agency-agents, msitarzewski/agency-agents">
  <link rel="canonical" href="{canonical_url}">

  <!-- OpenGraph -->
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(meta_desc)}">
  <meta property="og:url" content="{canonical_url}">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="DeepSeek Studio by PaceBowl">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{escape(title)}">
  <meta name="twitter:description" content="{escape(meta_desc)}">

  <!-- Favicon -->
  <link rel="icon" type="image/svg+xml" href="../favicon.svg">

  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          colors: {{
            deepseek: {{ 400: '#38bdf8', 500: '#0284c7', 600: '#0369a1', 900: '#082f49' }}
          }}
        }}
      }}
    }}
  </script>

  <!-- JSON-LD Structured Data -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@graph": [
      {{
        "@type": "BreadcrumbList",
        "itemListElement": [
          {{ "@type": "ListItem", "position": 1, "name": "首页", "item": "https://deepseek.pacebowl.com/" }},
          {{ "@type": "ListItem", "position": 2, "name": "AI 专家角色库", "item": "https://deepseek.pacebowl.com/agents/" }},
          {{ "@type": "ListItem", "position": 3, "name": "{dept}", "item": "https://deepseek.pacebowl.com/agents/#dept-{dept}" }},
          {{ "@type": "ListItem", "position": 4, "name": "{name_zh}", "item": "{canonical_url}" }}
        ]
      }},
      {{
        "@type": "TechArticle",
        "headline": "{escape(title)}",
        "description": "{escape(meta_desc)}",
        "url": "{canonical_url}",
        "inLanguage": "zh-CN",
        "author": {{ "@type": "Organization", "name": "PaceBowl & agency-agents (Upstream msitarzewski)" }},
        "publisher": {{ "@type": "Organization", "name": "PaceBowl Ecosystem", "url": "https://pacebowl.com" }}
      }},
      {{
        "@type": "FAQPage",
        "mainEntity": [
          {{
            "@type": "Question",
            "name": "如何使用 DeepSeek 调动【{name_zh}】（{name_en}）专家角色？",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "本页面支持一键切换【🇨🇳 中文 Prompt】与【🇺🇸 English Prompt】。点击【在 DeepSeek 生成器中微调】后，系统会自动根据所选语种将身份人设、使命与约束装填入生成器，并自动调配最佳的 DeepSeek-V4/R1 思考强度。"
            }}
          }},
          {{
            "@type": "Question",
            "name": "【{name_zh}】在 DeepSeek-V4 与 R1 中推荐使用什么思考模式？",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "官方推荐使用 {model_badge}，思考强度设定为 {cot_label}。这种配置能在保障逻辑严密性的同时，彻底杜绝无用客套寒暄。"
            }}
          }},
          {{
            "@type": "Question",
            "name": "【{name_zh}】（{name_en}）的开源依据与来源是什么？",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "本专家角色源自全球开源项目 msitarzewski/agency-agents 原版 English Specification 与 jnMetaCode/agency-agents-zh 中文社区版，经 DeepSeek-V4/R1 架构优化重构。"
            }}
          }}
        ]
      }}
    ]
  }}
  </script>
</head>
<body class="bg-[#07090e] text-slate-100 min-h-screen flex flex-col font-sans antialiased selection:bg-sky-500 selection:text-slate-950">

  <!-- Global Header -->
  <header class="border-b border-slate-800/80 bg-[#07090e]/90 backdrop-blur sticky top-0 z-40">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <a href="../index.html" class="flex items-center space-x-2 text-slate-200 hover:text-white transition">
          <div class="w-7 h-7 rounded-lg bg-sky-500 flex items-center justify-center font-bold text-slate-950 text-xs shadow-md shadow-sky-500/20">
            DS
          </div>
          <span class="font-bold text-sm tracking-tight">DeepSeek <span class="text-sky-400 font-mono text-[11px] px-1.5 py-0.5 rounded bg-sky-950/80 border border-sky-500/30">Studio</span></span>
        </a>
        <span class="text-slate-600">/</span>
        <a href="index.html" class="text-xs text-slate-400 hover:text-sky-400 transition font-medium">
          🎭 277 位专家库
        </a>
      </div>

      <div class="flex items-center space-x-2.5">
        <a id="header-tune-btn" href="../index.html?load_agent={agent_id}&prompt_lang=zh" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 text-xs font-bold transition shadow-sm hover:scale-[1.02]">
          <span>⚡</span>
          <span>在生成器中打开</span>
        </a>
        <a href="https://pacebowl.com" class="text-xs text-slate-400 hover:text-slate-200 hidden sm:inline transition">PaceBowl 母舰 →</a>
      </div>
    </div>
  </header>

  <!-- Main Container -->
  <main class="max-w-4xl mx-auto px-4 sm:px-6 py-8 flex-1 w-full space-y-8">

    <!-- Breadcrumb -->
    <nav class="flex items-center gap-2 text-xs text-slate-400">
      <a href="../index.html" class="hover:text-slate-200 transition">首页</a>
      <span>›</span>
      <a href="index.html" class="hover:text-slate-200 transition">AI 专家角色库</a>
      <span>›</span>
      <span class="text-slate-500">{dept}</span>
      <span>›</span>
      <span class="text-sky-400 font-semibold">{name_zh}</span>
    </nav>

    <!-- Hero Card -->
    <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-xl relative overflow-hidden">
      <div class="absolute -right-12 -top-12 w-48 h-48 bg-sky-500/10 rounded-full blur-3xl pointer-events-none"></div>

      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
        <div class="flex items-center gap-3">
          <span class="text-4xl sm:text-5xl p-2 rounded-2xl bg-slate-800/80 border border-slate-700/60 shadow-md">{emoji}</span>
          <div>
            <div class="flex items-center gap-2 mb-1 flex-wrap">
              <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-sky-500/20 text-sky-300 border border-sky-500/30">{dept}</span>
              {f'<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">🇨🇳 中国市场原创</span>' if is_china else '<span class="px-2 py-0.5 rounded-full text-[10px] font-medium bg-slate-800 text-slate-400 border border-slate-700/60">🌐 Upstream 原作</span>'}
            </div>
            <h1 class="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              {name_zh} <span class="text-slate-400 text-lg sm:text-xl font-normal">({name_en})</span>
            </h1>
          </div>
        </div>

        <div class="flex items-center gap-2.5">
          <button onclick="copyFullPrompt()" id="copy-btn" class="px-3.5 py-2 rounded-xl border border-slate-700 hover:border-slate-500 text-xs font-semibold text-slate-200 transition flex items-center gap-1.5 bg-slate-800/60">
            <span>📋</span>
            <span id="copy-btn-text">复制 Prompt</span>
          </button>
          <a id="cta-tune-btn" href="../index.html?load_agent={agent_id}&prompt_lang=zh" class="px-4 py-2 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-slate-950 font-bold text-xs transition shadow-lg shadow-sky-500/20 flex items-center gap-1.5 hover:scale-[1.02]">
            <span>⚡</span>
            <span>在生成器中微调</span>
          </a>
        </div>
      </div>

      <p class="text-slate-300 text-xs sm:text-sm leading-relaxed max-w-3xl mb-1">
        {desc_zh}
      </p>
      <p class="text-slate-400 text-xs leading-relaxed max-w-3xl italic">
        {desc_en}
      </p>

      <!-- DeepSeek Spec Matrix -->
      <div class="mt-6 pt-5 border-t border-slate-800 grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-mono">
        <div class="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
          <span class="text-slate-500 block text-[10px] uppercase mb-1">推荐底模架构</span>
          <span class="text-sky-400 font-bold">{model_badge}</span>
        </div>
        <div class="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
          <span class="text-slate-500 block text-[10px] uppercase mb-1">推荐思考强度 (CoT)</span>
          <span class="text-indigo-400 font-bold">{cot_label}</span>
        </div>
        <div class="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
          <span class="text-slate-500 block text-[10px] uppercase mb-1">格式规范 & 约束</span>
          <span class="text-emerald-400 font-bold">XML 语义封装 + 零客套废话</span>
        </div>
      </div>
    </div>

    <!-- Ready-to-use Bilingual Prompt Box -->
    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg space-y-3">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <h3 class="font-bold text-xs uppercase tracking-wider text-slate-300 flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
          <span>即插即用完整提示词 (Prompt Preview)</span>
        </h3>

        <!-- Language Switcher for Prompt -->
        <div class="flex items-center gap-2">
          <div class="inline-flex p-0.5 rounded-lg bg-slate-950 border border-slate-800">
            <button type="button" onclick="switchPromptLang('zh')" id="btn-lang-zh" class="px-2.5 py-1 rounded-md text-xs font-bold transition bg-sky-500 text-slate-950 shadow-xs">🇨🇳 中文</button>
            <button type="button" onclick="switchPromptLang('en')" id="btn-lang-en" class="px-2.5 py-1 rounded-md text-xs font-medium transition text-slate-400 hover:text-white">🇺🇸 English</button>
          </div>
          <button onclick="copyFullPrompt()" class="text-xs text-sky-400 hover:underline flex items-center gap-1 font-mono">
            <span>📋</span>
            <span>一键复制</span>
          </button>
        </div>
      </div>

      <div class="relative">
        <textarea id="prompt-content" readonly rows="8" class="w-full bg-[#07090e] border border-slate-800 rounded-xl p-4 text-xs font-mono text-slate-200 focus:outline-none selection:bg-sky-500 selection:text-slate-950 leading-relaxed resize-none">{escape(prompt_zh)}</textarea>
      </div>
      <p class="text-[11px] text-slate-500 flex flex-col sm:flex-row sm:items-center justify-between gap-1">
        <span>💡 支持自由切换中英文。可直接粘贴至 DeepSeek 官方聊天网页版或 API 中。</span>
        <a id="prompt-footer-link" href="../index.html?load_agent={agent_id}&prompt_lang=zh" class="text-sky-400 hover:underline">在主生成器中调配参数 →</a>
      </p>
    </div>

    <!-- High-Converting Fast API Partner Banner -->
    <div class="p-3.5 rounded-2xl bg-gradient-to-r from-sky-500/10 via-indigo-500/10 to-purple-500/10 border border-sky-500/30 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs shadow-md">
      <div class="flex items-center gap-2.5 min-w-0">
        <span class="text-xl p-1 rounded-lg bg-sky-500 text-slate-950 font-bold shrink-0">⚡</span>
        <div class="truncate">
          <div class="flex items-center gap-2 mb-0.5">
            <span class="font-bold text-white">免排队调用【{name_zh}】提示词</span>
            <span class="px-1.5 py-0.2 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">赠 2000万 Token</span>
          </div>
          <p class="text-slate-400 text-[11px] truncate">官方服务频繁拥堵？接入硅基流动 SiliconFlow 极速 API 专线，专属通道注册即送 20M 额度</p>
        </div>
      </div>
      <a href="../go/siliconflow" target="_blank" rel="noopener nofollow sponsored" class="inline-flex items-center justify-center gap-1 px-3.5 py-2 rounded-xl bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold text-xs transition shrink-0 shadow-sm hover:scale-[1.02]">
        <span>领取免费算力</span>
        <span>→</span>
      </a>
    </div>

    <!-- Detailed Role Specification (Bilingual Tabs) -->
    <div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-sm space-y-4">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3 mb-4">
        <div>
          <h2 class="text-lg font-bold text-white flex items-center gap-2">
            <span>📖</span>
            <span>【{name_zh}】深度人设与工程交付规范</span>
          </h2>
          <div class="flex items-center gap-2 mt-1">
            <span class="text-xs text-slate-500">双语规范源自:</span>
            <a href="https://github.com/msitarzewski/agency-agents" target="_blank" rel="noopener noreferrer" class="text-xs text-sky-400 hover:underline">msitarzewski/agency-agents (Upstream 原版)</a>
            <span class="text-slate-600">/</span>
            <a href="https://github.com/jnMetaCode/agency-agents-zh" target="_blank" rel="noopener noreferrer" class="text-xs text-rose-400 hover:underline">agency-agents-zh (中文社区版)</a>
          </div>
        </div>

        <div class="inline-flex p-0.5 rounded-lg bg-slate-950 border border-slate-800 text-xs">
          <button type="button" onclick="switchSpecTab('zh')" id="btn-tab-zh" class="px-2.5 py-1 rounded-md font-bold bg-slate-800 text-white transition">🇨🇳 中文规范</button>
          <button type="button" onclick="switchSpecTab('en')" id="btn-tab-en" class="px-2.5 py-1 rounded-md font-medium text-slate-400 hover:text-white transition">🇺🇸 Upstream Spec</button>
        </div>
      </div>

      <div id="spec-content-zh" class="prose prose-invert max-w-none text-slate-300">
        {rendered_body_zh}
      </div>
      <div id="spec-content-en" class="prose prose-invert max-w-none text-slate-300 hidden">
        {rendered_body_en}
      </div>
    </div>

    <!-- Peer Agents Links -->
    <div class="space-y-4 pt-4">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-bold text-white flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-sky-500"></span>
          <span>同部门其他 AI 专家角色 ({dept})</span>
        </h3>
        <a href="index.html" class="text-xs text-sky-400 hover:underline">浏览全部 277 位专家 →</a>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
        {peer_html}
      </div>
    </div>

    <!-- Featured China Originals -->
    <div class="space-y-4 pt-4">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-bold text-rose-300 flex items-center gap-2">
          <span>🇨🇳</span>
          <span>热门中国市场原创智能体精选</span>
        </h3>
        <a href="index.html#china-tab" class="text-xs text-rose-400 hover:underline">查看全部 64 个中国原创 →</a>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
        {china_html}
      </div>
    </div>

    <!-- FAQ Accordion -->
    <div class="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 space-y-4">
      <h3 class="text-sm font-bold text-white mb-2">常见问题 (FAQ)</h3>
      <div class="space-y-3 text-xs">
        <div class="border border-slate-800 rounded-xl p-3.5 bg-slate-950/40">
          <h4 class="font-bold text-slate-200 mb-1">Q: 如何在 DeepSeek-V4/R1 中最大化发挥【{name_zh}】的实力？</h4>
          <p class="text-slate-400 leading-relaxed">
            建议直接使用本页面推荐的 <strong>{model_badge}</strong>，并在指令开头声明角色权限。在 DeepSeek 中，避免使用过于冗长的 Few-shot 样本，而是通过明确的负向约束和交付物结构要求，让模型的内生思维链自主推导最优结果。
          </p>
        </div>
        <div class="border border-slate-800 rounded-xl p-3.5 bg-slate-950/40">
          <h4 class="font-bold text-slate-200 mb-1">Q: 点击【在生成器中微调】会发生什么？</h4>
          <p class="text-slate-400 leading-relaxed">
            系统将跳转回 DeepSeek Studio 主工具，自动装填该专家的角色定位、目标职责与红线规则（以您当前选中的中文或英文），并为您自动选定最优的思考强度。您可以随意补充代码或具体任务，一键生成符合工业级规范的 Prompt。
          </p>
        </div>
      </div>
    </div>

  </main>

  <!-- Global Footer -->
  <footer class="border-t border-slate-800/80 bg-[#07090e] py-8 text-center text-xs text-slate-500 mt-12">
    <div class="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
      <div>
        <span>PaceBowl &copy; 2026. 提示词角色规范源自 <a href="https://github.com/msitarzewski/agency-agents" target="_blank" rel="noopener noreferrer" class="text-sky-400 hover:underline">agency-agents (Upstream MIT)</a> 与 <a href="https://github.com/jnMetaCode/agency-agents-zh" target="_blank" rel="noopener noreferrer" class="text-rose-400 hover:underline">agency-agents-zh</a>.</span>
        <p class="text-[10px] text-slate-500 mt-1">
          Disclosure: We may earn an affiliate commission when you register through partner links on our site at no additional cost to you.
        </p>
      </div>
      <div class="flex items-center gap-4 text-slate-400">
        <a href="../index.html" class="hover:text-white transition">生成器主页</a>
        <a href="index.html" class="hover:text-white transition">专家库大全</a>
        <a href="https://pacebowl.com" class="hover:text-white transition">PaceBowl 母舰</a>
        <a href="https://buymeacoffee.com/pacebowl" target="_blank" rel="noopener noreferrer" class="text-amber-400 hover:underline">☕ 赞助</a>
      </div>
    </div>
  </footer>

  <!-- Toast Notification -->
  <div id="toast" class="fixed bottom-6 right-6 z-50 transform translate-y-20 opacity-0 transition-all duration-300 pointer-events-none bg-sky-500 text-slate-950 font-bold px-4 py-2.5 rounded-lg shadow-xl shadow-sky-500/20 text-xs flex items-center space-x-2">
    <span>✓ 提示词已成功复制到剪贴板！</span>
  </div>

  <script>
    const AGENT_ID = "{agent_id}";
    const PROMPTS = {{
      zh: {js_prompt_zh},
      en: {js_prompt_en}
    }};
    let currentPromptLang = 'zh';

    function switchPromptLang(lang) {{
      currentPromptLang = lang;
      const zhBtn = document.getElementById('btn-lang-zh');
      const enBtn = document.getElementById('btn-lang-en');
      const txt = document.getElementById('prompt-content');
      const cta = document.getElementById('cta-tune-btn');
      const headerCta = document.getElementById('header-tune-btn');
      const footerLink = document.getElementById('prompt-footer-link');

      if (lang === 'zh') {{
        if (zhBtn) zhBtn.className = 'px-2.5 py-1 rounded-md text-xs font-bold transition bg-sky-500 text-slate-950 shadow-xs';
        if (enBtn) enBtn.className = 'px-2.5 py-1 rounded-md text-xs font-medium transition text-slate-400 hover:text-white';
        if (txt) txt.value = PROMPTS.zh;
      }} else {{
        if (enBtn) enBtn.className = 'px-2.5 py-1 rounded-md text-xs font-bold transition bg-sky-500 text-slate-950 shadow-xs';
        if (zhBtn) zhBtn.className = 'px-2.5 py-1 rounded-md text-xs font-medium transition text-slate-400 hover:text-white';
        if (txt) txt.value = PROMPTS.en;
      }}

      const targetUrl = `../index.html?load_agent=${{AGENT_ID}}&prompt_lang=${{lang}}`;
      if (cta) cta.href = targetUrl;
      if (headerCta) headerCta.href = targetUrl;
      if (footerLink) footerLink.href = targetUrl;
    }}

    function switchSpecTab(lang) {{
      const zhTab = document.getElementById('btn-tab-zh');
      const enTab = document.getElementById('btn-tab-en');
      const zhContent = document.getElementById('spec-content-zh');
      const enContent = document.getElementById('spec-content-en');

      if (lang === 'zh') {{
        if (zhTab) zhTab.className = 'px-2.5 py-1 rounded-md font-bold bg-slate-800 text-white transition';
        if (enTab) enTab.className = 'px-2.5 py-1 rounded-md font-medium text-slate-400 hover:text-white transition';
        if (zhContent) zhContent.classList.remove('hidden');
        if (enContent) enContent.classList.add('hidden');
      }} else {{
        if (enTab) enTab.className = 'px-2.5 py-1 rounded-md font-bold bg-slate-800 text-white transition';
        if (zhTab) zhTab.className = 'px-2.5 py-1 rounded-md font-medium text-slate-400 hover:text-white transition';
        if (enContent) enContent.classList.remove('hidden');
        if (zhContent) zhContent.classList.add('hidden');
      }}
    }}

    function copyFullPrompt() {{
      const el = document.getElementById('prompt-content');
      if (!el) return;
      navigator.clipboard.writeText(el.value).then(() => {{
        const isZh = currentPromptLang === 'zh';
        showToast(isZh ? '✓ 【{name_zh}】中文提示词已复制到剪贴板！' : '✓ 【{name_en}】English prompt copied to clipboard!');
        const btn = document.getElementById('copy-btn-text');
        if (btn) {{
          const orig = btn.textContent;
          btn.textContent = isZh ? '✓ 已复制！' : '✓ Copied!';
          setTimeout(() => {{ btn.textContent = orig; }}, 2000);
        }}
      }});
    }}

    function showToast(msg) {{
      const toast = document.getElementById('toast');
      if (!toast) return;
      toast.querySelector('span').textContent = msg;
      toast.classList.remove('translate-y-20', 'opacity-0');
      toast.classList.add('translate-y-0', 'opacity-100');
      setTimeout(() => {{
        toast.classList.remove('translate-y-0', 'opacity-100');
        toast.classList.add('translate-y-20', 'opacity-0');
      }}, 2500);
    }}
  </script>
</body>
</html>
"""
    return html_content

def generate_catalog_page(agents, departments):
    title = "DeepSeek 277 位 AI 专家角色库大全 - 公司经营/工程研发/营销设计/中国原创 | DeepSeek Studio"
    meta_desc = "全网最全的 DeepSeek 277 位工业级 AI 专家角色与提示词目录，覆盖 20 个企业部门，包含 64 个中国市场独家原创智能体。支持一键检索、中英双语切换与一键装填至 DeepSeek-V4/R1 生成器。"
    canonical_url = "https://deepseek.pacebowl.com/agents/"

    dept_map = {}
    for a in agents:
        d = a['department']
        if d not in dept_map:
            dept_map[d] = []
        dept_map[d].append(a)

    sections_html = ""
    for d, a_list in dept_map.items():
        cards_html = ""
        for a in a_list:
            is_pro = 'pro' in a.get('recommended', {}).get('model', '')
            model_badge = '🧠 V4-Pro' if is_pro else '⚡ V4.1-Flash'
            badge_class = 'text-indigo-400 bg-indigo-950/40 border-indigo-900/50' if is_pro else 'text-sky-400 bg-sky-950/40 border-sky-900/50'
            name_zh = a.get('name_zh', a['name'])
            name_en = a.get('name_en', a['name'])

            cards_html += f"""
            <a href="{a['id']}.html" class="p-4 rounded-xl border border-slate-800 hover:border-sky-500/50 bg-slate-900/70 hover:bg-slate-900 transition flex flex-col justify-between group shadow-sm">
              <div>
                <div class="flex items-start justify-between gap-2 mb-2">
                  <div class="flex items-center gap-2 min-w-0">
                    <span class="text-2xl p-1.5 rounded-lg bg-slate-800 flex items-center justify-center shrink-0">{a.get('emoji', '🤖')}</span>
                    <div class="truncate">
                      <h4 class="text-xs sm:text-sm font-bold text-white group-hover:text-sky-400 transition truncate">{name_zh}</h4>
                      <span class="text-[10px] text-slate-500 font-mono truncate block">{name_en}</span>
                    </div>
                  </div>
                  <div class="flex flex-col items-end gap-1 shrink-0">
                    {f'<span class="px-1.5 py-0.5 rounded text-[9px] font-bold bg-rose-950/60 border border-rose-900/60 text-rose-400">🇨🇳 原创</span>' if a.get('is_china_original') else '<span class="px-1.5 py-0.5 rounded text-[9px] font-medium bg-slate-800 text-slate-400">🌐 Upstream</span>'}
                    <span class="px-1.5 py-0.5 rounded text-[9px] font-mono font-medium border {badge_class}">{model_badge}</span>
                  </div>
                </div>
                <p class="text-[11px] text-slate-400 line-clamp-3 leading-relaxed mb-3">
                  {a.get('desc_zh', a['desc'])}
                </p>
              </div>
              <div class="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-sky-400 font-semibold">
                <span>中英双语 Prompt</span>
                <span>→</span>
              </div>
            </a>
            """

        sections_html += f"""
        <section id="dept-{d}" class="space-y-4 pt-6">
          <div class="flex items-center justify-between border-b border-slate-800 pb-2.5">
            <h2 class="text-base sm:text-lg font-bold text-white flex items-center gap-2">
              <span class="w-2.5 h-2.5 rounded-full bg-sky-500"></span>
              <span>{d}</span>
              <span class="text-xs font-mono font-normal text-slate-500">({len(a_list)} 位)</span>
            </h2>
            <a href="#top" class="text-xs text-slate-500 hover:text-slate-300">返回顶部 ↑</a>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3.5">
            {cards_html}
          </div>
        </section>
        """

    pills_html = ""
    for d, a_list in dept_map.items():
        pills_html += f"""
        <a href="#dept-{d}" class="whitespace-nowrap px-3 py-1 rounded-full text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 transition">
          {d} ({len(a_list)})
        </a>
        """

    catalog_html = f"""<!DOCTYPE html>
<html lang="zh-CN" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(meta_desc)}">
  <link rel="canonical" href="{canonical_url}">

  <!-- OpenGraph -->
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(meta_desc)}">
  <meta property="og:url" content="{canonical_url}">
  <meta property="og:type" content="website">

  <!-- Favicon -->
  <link rel="icon" type="image/svg+xml" href="../favicon.svg">

  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          colors: {{
            deepseek: {{ 400: '#38bdf8', 500: '#0284c7', 600: '#0369a1', 900: '#082f49' }}
          }}
        }}
      }}
    }}
  </script>
</head>
<body id="top" class="bg-[#07090e] text-slate-100 min-h-screen flex flex-col font-sans antialiased selection:bg-sky-500 selection:text-slate-950">

  <!-- Global Header -->
  <header class="border-b border-slate-800/80 bg-[#07090e]/90 backdrop-blur sticky top-0 z-40">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <a href="../index.html" class="flex items-center space-x-2 text-slate-200 hover:text-white transition">
          <div class="w-7 h-7 rounded-lg bg-sky-500 flex items-center justify-center font-bold text-slate-950 text-xs shadow-md shadow-sky-500/20">
            DS
          </div>
          <span class="font-bold text-sm tracking-tight">DeepSeek <span class="text-sky-400 font-mono text-[11px] px-1.5 py-0.5 rounded bg-sky-950/80 border border-sky-500/30">Studio</span></span>
        </a>
        <span class="text-slate-600">/</span>
        <span class="text-xs text-sky-400 font-bold">🎭 277 位 AI 专家库大全</span>
      </div>

      <div class="flex items-center space-x-3">
        <a href="../index.html" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 text-xs font-bold transition shadow-sm">
          <span>⚡</span>
          <span>返回主生成器</span>
        </a>
      </div>
    </div>
  </header>

  <!-- Hero Section -->
  <section class="max-w-6xl mx-auto px-4 sm:px-6 pt-10 pb-6 text-center">
    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-950/60 border border-sky-500/30 text-sky-300 text-xs mb-3 font-mono">
      <span>🎭 277 AGENTS • 20 DEPARTMENTS • BILINGUAL PROMPTS</span>
    </div>
    <h1 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight mb-3">
      DeepSeek <span class="bg-gradient-to-r from-sky-400 via-blue-500 to-indigo-500 bg-clip-text text-transparent">277 位 AI 专家角色库大全</span>
    </h1>
    <p class="text-slate-400 text-xs sm:text-sm max-w-2xl mx-auto leading-relaxed mb-6">
      涵盖公司经营、工程研发、营销增长、设计创意等 20 个企业职能部门。支持中英文提示词自由切换，一键装填至 DeepSeek-V4/R1 生成器。规范源自全球开源项目 <a href="https://github.com/msitarzewski/agency-agents" target="_blank" rel="noopener noreferrer" class="text-sky-400 hover:underline">msitarzewski/agency-agents</a> 原作与 <a href="https://github.com/jnMetaCode/agency-agents-zh" target="_blank" rel="noopener noreferrer" class="text-rose-400 hover:underline">agency-agents-zh</a> 中文社区版。
    </p>

    <!-- Jump Pills -->
    <div class="flex items-center justify-center gap-1.5 flex-wrap max-w-4xl mx-auto">
      {pills_html}
    </div>

    <!-- Partner API Banner in Catalog -->
    <div class="mt-6 max-w-4xl mx-auto p-3.5 rounded-2xl bg-gradient-to-r from-sky-500/10 via-indigo-500/10 to-purple-500/10 border border-sky-500/30 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs shadow-md">
      <div class="flex items-center gap-2.5 min-w-0">
        <span class="text-xl p-1 rounded-lg bg-sky-500 text-slate-950 font-bold shrink-0">⚡</span>
        <div class="truncate">
          <div class="flex items-center gap-2 mb-0.5">
            <span class="font-bold text-white">DeepSeek 官方 API 频繁繁忙？免排队专线推荐</span>
            <span class="px-1.5 py-0.2 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">赠 2000万 Token</span>
          </div>
          <p class="text-slate-400 text-[11px] truncate">硅基流动 SiliconFlow 极速部署 V4 & R1，专属通道注册立送 2000万 Token 免费算力</p>
        </div>
      </div>
      <a href="../go/siliconflow" target="_blank" rel="noopener nofollow sponsored" class="inline-flex items-center justify-center gap-1 px-3.5 py-2 rounded-xl bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold text-xs transition shrink-0 shadow-sm hover:scale-[1.02]">
        <span>领取免费算力</span>
        <span>→</span>
      </a>
    </div>
  </section>

  <!-- Directory Main Content -->
  <main class="max-w-6xl mx-auto px-4 sm:px-6 py-6 flex-1 w-full space-y-10">
    {sections_html}
  </main>

  <!-- Global Footer -->
  <footer class="border-t border-slate-800/80 bg-[#07090e] py-8 text-center text-xs text-slate-500 mt-16">
    <div class="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
      <div>
        <span>PaceBowl &copy; 2026. 提示词角色规范源自 <a href="https://github.com/msitarzewski/agency-agents" target="_blank" rel="noopener noreferrer" class="text-sky-400 hover:underline">agency-agents (Upstream MIT)</a> 与 <a href="https://github.com/jnMetaCode/agency-agents-zh" target="_blank" rel="noopener noreferrer" class="text-rose-400 hover:underline">agency-agents-zh</a>.</span>
        <p class="text-[10px] text-slate-500 mt-1">
          Disclosure: We may earn an affiliate commission when you register through partner links on our site at no additional cost to you.
        </p>
      </div>
      <div class="flex items-center gap-4 text-slate-400">
        <a href="../index.html" class="hover:text-white transition">生成器主页</a>
        <a href="https://pacebowl.com" class="hover:text-white transition">PaceBowl 母舰</a>
        <a href="https://buymeacoffee.com/pacebowl" target="_blank" rel="noopener noreferrer" class="text-amber-400 hover:underline">☕ 赞助</a>
      </div>
    </div>
  </footer>

</body>
</html>
"""
    return catalog_html

def generate_sitemap(agents):
    base = "https://deepseek.pacebowl.com"
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        '  <url>',
        f'    <loc>{base}/</loc>',
        '    <lastmod>2026-10-03</lastmod>',
        '    <changefreq>daily</changefreq>',
        '    <priority>1.0</priority>',
        '  </url>',
        '  <url>',
        f'    <loc>{base}/agents/</loc>',
        '    <lastmod>2026-10-03</lastmod>',
        '    <changefreq>daily</changefreq>',
        '    <priority>0.9</priority>',
        '  </url>'
    ]

    for a in agents:
        xml_lines.extend([
            '  <url>',
            f'    <loc>{base}/agents/{a["id"]}.html</loc>',
            '    <lastmod>2026-10-03</lastmod>',
            '    <changefreq>weekly</changefreq>',
            '    <priority>0.8</priority>',
            '  </url>'
        ])

    xml_lines.append('</urlset>')
    return '\n'.join(xml_lines)

def main():
    with open('data/agents.json', 'r', encoding='utf-8') as f:
        agents = json.load(f)

    os.makedirs('agents', exist_ok=True)
    print(f"Loaded {len(agents)} agents from data/agents.json")

    dept_map = {}
    china_agents = [a for a in agents if a.get('is_china_original')]

    for a in agents:
        d = a['department']
        if d not in dept_map:
            dept_map[d] = []
        dept_map[d].append(a)

    for agent in agents:
        dept = agent['department']
        peers = [p for p in dept_map.get(dept, []) if p['id'] != agent['id']]
        page_html = generate_agent_page(agent, peers, china_agents)
        file_path = os.path.join('agents', f"{agent['id']}.html")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(page_html)

    print(f"Generated {len(agents)} bilingual landing pages in agents/")

    catalog_html = generate_catalog_page(agents, list(dept_map.keys()))
    catalog_path = os.path.join('agents', 'index.html')
    with open(catalog_path, 'w', encoding='utf-8') as f:
        f.write(catalog_html)
    print(f"Generated catalog index at {catalog_path}")

    sitemap_xml = generate_sitemap(agents)
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap_xml)
    print(f"Generated sitemap.xml with {len(agents) + 2} URLs")

if __name__ == '__main__':
    main()
