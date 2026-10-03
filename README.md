# DeepSeek Prompt Studio & Agency Agents (277 Roles) 🐋

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Cloudflare Pages](https://img.shields.io/badge/Deploy-Cloudflare%20Pages-orange)](https://deepseek.pacebowl.com)
[![DeepSeek V4 & R1](https://img.shields.io/badge/DeepSeek-V4%20%7C%20R1%20Reasoning-blue)](https://deepseek.pacebowl.com)
[![Bilingual EN/ZH](https://img.shields.io/badge/i18n-EN%20%2F%20ZH-green)](https://deepseek.pacebowl.com)

> 🚀 **Live Production**: [https://deepseek.pacebowl.com](https://deepseek.pacebowl.com)  
> 🌐 **Agent Catalog Directory**: [https://deepseek.pacebowl.com/agents/](https://deepseek.pacebowl.com/agents/)

A zero-friction, 100% client-side prompt engineering studio and agency persona hub optimized for **DeepSeek-V4**, **V4.1-Flash (552B MoE)**, and **DeepSeek-R1** reasoning models.

---

## ✨ Features

- **277 Curated Bilingual Agency Personas**: Complete prompt directives covering 20+ departments (Engineering, Marketing, Legal, Finance, Security, Roblox, VisionOS, and China Market E-Commerce).
- **XML Tag Semantic Framework**: Automatic semantic wrapping for `<role>`, `<thinking_guidance>`, `<task>`, and `<guardrails>` to prevent prompt leakage and guide deep reasoning paths.
- **DeepSeek V4.1 Thinking Mode Control**: One-click toggling between Off (V3 Execution), Standard Thinking, and Max Thinking (Deep Recursive CoT).
- **Token Arbitrage & ROI Calculator**: Real-time interactive token cost and dollar savings estimator comparing DeepSeek V4.1-Flash ($0.28/1M) against OpenAI o1 / GPT-4o ($15.00/1M).
- **Programmatic SEO Engine**: Python pipeline generating 277 static, mobile-responsive, schema-annotated HTML landing pages and dynamic sitemaps for search engines.
- **Zero GPU / 100% Client-Side**: Completely private with zero server backend, no API key logging, and zero database latency.
- **PaceBowl Suite Shared State**: Cross-subdomain cookie sync for dark/light theme and English/Chinese language preference across the PaceBowl matrix.

---

## 📂 Project Structure

```
├── index.html                   # Main Interactive Prompt Studio Application
├── data/
│   └── agents.json              # 277 Agency Agent Personas (Bilingual specs)
├── agents/                      # 277 Pre-rendered Programmatic SEO Landing Pages
│   ├── index.html               # Searchable Agent Catalog Directory
│   └── *.html                   # Individual Agent Role Specifications
├── scripts/
│   └── generate_seo_pages.py    # Python SSG Compiler for Agent Landing Pages
├── _redirects                   # Edge 302 Cloaked Affiliate & Gateway Routing
├── robots.txt                   # Search Engine & AI Crawler Directives
├── sitemap.xml                  # Dynamic XML Sitemap (279 indexing targets)
├── llms.txt                     # Markdown AI Agent & Crawler Context Manifest
└── LICENSE                      # MIT License
```

---

## 🛠️ Quick Start & Local Development

No build tools, bundlers, or Node.js runtime required to run the core app!

```bash
# Clone the repository
git clone https://github.com/fullofjoy/deepseek-prompt-generator.git
cd deepseek-prompt-generator

# Open directly in any browser
# (or use a lightweight local HTTP server)
npx serve .
# or
python -m http.server 8080
```

### Regenerating SEO Agent Landing Pages

If you modify `data/agents.json` or page templates:

```bash
python scripts/generate_seo_pages.py
```

---

## 🚀 1-Click Deployment (Cloudflare Pages)

Deploy to Cloudflare Pages in seconds with zero build step:

```bash
npx wrangler pages deploy . --project-name=deepseek-prompt-generator
```

---

## 📜 Upstream Attribution & Credits

- The 277 agency agent personas are adapted and bilingual-localized from:
  - Upstream MIT: [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents)
  - Community Chinese: [jnMetaCode/agency-agents-zh](https://github.com/jnMetaCode/agency-agents-zh)
- Part of the [PaceBowl Suite Matrix](https://pacebowl.com).

---

## 📄 License

[MIT License](LICENSE) © 2026 PaceBowl Studio
