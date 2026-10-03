import json
import glob
import os
import re

def parse_frontmatter(content):
    meta = {}
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            for line in fm_text.strip().split('\n'):
                if ':' in line:
                    k, v = line.split(':', 1)
                    meta[k.strip()] = v.strip().strip('"\'')
            body = parts[2].strip()
            return meta, body
    return meta, content

def extract_sections(body):
    sections = {}
    current_sec = 'intro'
    sec_lines = []
    
    for line in body.split('\n'):
        if line.startswith('## '):
            if sec_lines:
                sections[current_sec] = '\n'.join(sec_lines).strip()
                sec_lines = []
            current_sec = line[3:].strip()
        else:
            sec_lines.append(line)
    if sec_lines:
        sections[current_sec] = '\n'.join(sec_lines).strip()
    return sections

def main():
    with open('data/agents.json', 'r', encoding='utf-8') as f:
        agents = json.load(f)

    upstream_files = glob.glob('temp_upstream/**/*.md', recursive=True)
    upstream_map = {}
    for uf in upstream_files:
        base = os.path.splitext(os.path.basename(uf))[0]
        upstream_map[base] = uf

    matched_count = 0
    unmatched = []

    for a in agents:
        aid = a['id']
        uf = upstream_map.get(aid)
        if not uf:
            for k, p in upstream_map.items():
                if k == aid or k.endswith(aid) or aid.endswith(k):
                    uf = p
                    break
        
        if uf and os.path.exists(uf):
            matched_count += 1
            with open(uf, 'r', encoding='utf-8') as f:
                content = f.read()
            fm, body = parse_frontmatter(content)
            
            name_en = fm.get('name', a['name'])
            desc_en = fm.get('description', a['desc'])
            
            secs = extract_sections(body)
            core_mission_en = ""
            key_rules_en = ""
            deliverables_en = ""
            for k, v in secs.items():
                kl = k.lower()
                if any(x in kl for x in ['mission', 'core', 'role', 'responsibilit']):
                    core_mission_en = v
                elif any(x in kl for x in ['rule', 'boundary', 'constraint', 'guideline']):
                    key_rules_en = v
                elif any(x in kl for x in ['deliverable', 'output', 'template', 'deliver']):
                    deliverables_en = v
            
            task_en = f"As the professional [{name_en}], please execute the following objective:\n\n[Core Mission & Responsibilities]\n{core_mission_en[:400] if core_mission_en else desc_en}\n\n[Expected Deliverables]\n{deliverables_en[:300] if deliverables_en else 'Provide production-grade code, architectural specifications, or strategies adhering strictly to industry standards.'}"
            
            context_en = f"[Professional Authority & Guardrails]\n- Role: {name_en} ({a.get('department_en', a['department'])})\n- Key Boundaries:\n{key_rules_en[:400] if key_rules_en else '- Ensure absolute correctness, zero hallucinations, and rigorous adherence to domain standards.'}"
            
            a['name_en'] = name_en
            a['desc_en'] = desc_en
            a['task_en'] = task_en.strip()
            a['context_en'] = context_en.strip()
            a['full_prompt_en'] = body.strip()
        else:
            unmatched.append(a)
            # For China originals or unmatched, provide high-quality English translated version
            name_en = a['id'].replace('-', ' ').title()
            # If id has department prefix, clean it up
            for prefix in ['Engineering ', 'Marketing ', 'Specialized ', 'Support ', 'Testing ', 'Company ']:
                if name_en.startswith(prefix):
                    name_en = name_en[len(prefix):]
            
            desc_en = f"Specialized expert for {a['name']} ({a['department']}). {a['desc']}"
            task_en = f"As the professional [{name_en}], execute the following objective:\n\n[Core Mission]\n{a['task']}\n\n[Deliverables]\nDeliver complete, verified outputs following professional guidelines."
            context_en = f"[Role Specification]\n- Role: {name_en} ({a['department']})\n- Directives:\n{a['context']}"
            
            a['name_en'] = name_en
            a['desc_en'] = desc_en
            a['task_en'] = task_en
            a['context_en'] = context_en
            a['full_prompt_en'] = f"# {name_en}\n\nYou are {name_en}, a professional expert in {a['department']}.\n\n## Core Mission\n{a['desc']}\n\n## Directives & Rules\n{a['context']}"

        # Ensure Chinese fields exist with _zh suffix as well for clean parity
        a['name_zh'] = a['name']
        a['desc_zh'] = a['desc']
        a['task_zh'] = a['task']
        a['context_zh'] = a['context']
        a['full_prompt_zh'] = a['full_prompt']

    print(f"Total agents: {len(agents)}")
    print(f"Matched with native upstream English files: {matched_count}")
    print(f"China originals with generated English adaptation: {len(unmatched)}")

    # Save updated agents.json
    with open('data/agents.json', 'w', encoding='utf-8') as f:
        json.dump(agents, f, ensure_ascii=False, indent=2)
    print("Saved updated data/agents.json")

    # Generate lightweight search index with bilingual fields
    light_agents = []
    for a in agents:
        light_agents.append({
            'id': a['id'],
            'name': a['name_zh'],
            'name_en': a['name_en'],
            'emoji': a['emoji'],
            'desc': a['desc_zh'],
            'desc_en': a['desc_en'],
            'department': a['department'],
            'department_en': a.get('department_en', a['department']),
            'is_china_original': a['is_china_original'],
            'recommended': a['recommended'],
            'task': a['task_zh'],
            'task_en': a['task_en'],
            'context': a['context_zh'],
            'context_en': a['context_en'],
            'full_prompt': a['full_prompt_zh'],
            'full_prompt_en': a['full_prompt_en']
        })

    with open('data/agents_index.json', 'w', encoding='utf-8') as f:
        json.dump(light_agents, f, ensure_ascii=False)
    print("Saved updated data/agents_index.json")

    with open('data/agents_data.js', 'w', encoding='utf-8') as f:
        f.write('window.AGENTS_DATA = ' + json.dumps(light_agents, ensure_ascii=False) + ';')
    print("Saved updated data/agents_data.js")

if __name__ == '__main__':
    main()
