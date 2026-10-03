import os
import glob
import re
import json

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

def extract_core_prompt_elements(body):
    # Extracts role, rules, deliverables
    # Let's clean body or extract relevant sections
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

def get_department_icon(dep):
    mapping = {
        '公司经营部': '🏢',
        '工程部': '🛠️',
        '设计部': '🎨',
        '营销部': '📢',
        '付费媒体部': '💰',
        '销售部': '💼',
        '金融部': '🏦',
        '人力资源部': '👥',
        '法务部': '⚖️',
        '供应链部': '📦',
        '产品部': '📱',
        '项目管理部': '📊',
        '测试部': '🧪',
        '支持部': '🎧',
        '专项部': '🎯',
        '空间计算部': '🥽',
        '游戏开发部': '🎮',
        '学术部': '📖',
        'GIS 部': '🗺️',
        '安全部': '🛡️'
    }
    for k, v in mapping.items():
        if k in dep:
            return v
    return '🤖'

def determine_recommended_settings(dep, name, desc):
    # Determine model & cot level for this agent
    dep_name = dep + ' ' + name + ' ' + desc
    if any(k in dep_name for k in ['工程', '代码', '架构', '算法', '安全', '数学', '数据', '固件', '开发', 'SQL']):
        return {
            'model': 'deepseek-v4-pro',
            'cot': 'deep',
            'format': 'markdown',
            'hallucination_guard': True,
            'preset_key': 'code'
        }
    elif any(k in dep_name for k in ['经营', '战略', 'CEO', 'CTO', '金融', '法务', '学术', '研究']):
        return {
            'model': 'deepseek-v4-pro',
            'cot': 'deep',
            'format': 'markdown',
            'hallucination_guard': True,
            'preset_key': 'research'
        }
    elif any(k in dep_name for k in ['营销', '小红书', '抖音', '文案', '设计', '视频', '创意', '社交']):
        return {
            'model': 'deepseek-v4.1-flash',
            'cot': 'standard',
            'format': 'markdown',
            'hallucination_guard': False,
            'preset_key': 'system'
        }
    else:
        return {
            'model': 'deepseek-v4-pro',
            'cot': 'standard',
            'format': 'markdown',
            'hallucination_guard': True,
            'preset_key': 'system'
        }

def main():
    root = 'temp_agency'
    if not os.path.exists(root):
        print(f"Directory {root} does not exist!")
        return

    # Parse AGENT-LIST.md to get official list, order, department, description, source
    agent_list_path = os.path.join(root, 'AGENT-LIST.md')
    agents = []
    agent_map = {}
    
    with open(agent_list_path, 'r', encoding='utf-8') as f:
        agent_list_content = f.read()

    # Split by ## Section
    sections = re.split(r'\n##\s+', agent_list_content)
    
    for sec in sections[1:]:
        lines = sec.split('\n')
        dep_title = lines[0].strip()
        if '统计' in dep_title or '概览' in dep_title:
            continue
        
        # Clean department name
        dep_name = dep_title.split('(')[0].strip()
        dep_en = ''
        if '(' in dep_title:
            dep_en = dep_title.split('(')[1].replace(')', '').strip()
            
        icon = get_department_icon(dep_name)
        
        # Parse table rows: | `Agent ID` | 中文名 | 描述 | 来源 |
        for line in lines[1:]:
            line = line.strip()
            if not line.startswith('|') or '---' in line or 'Agent ID' in line:
                continue
            cols = [c.strip() for c in line.split('|')[1:-1]]
            if len(cols) >= 4:
                agent_id = cols[0].replace('`', '').strip()
                name_cn = cols[1].strip()
                desc = cols[2].strip()
                source = cols[3].strip()
                
                agent_map[agent_id] = {
                    'id': agent_id,
                    'name': name_cn,
                    'desc': desc,
                    'source': source,
                    'department': dep_name,
                    'department_en': dep_en,
                    'icon': icon
                }

    print(f"Parsed {len(agent_map)} agents from AGENT-LIST.md")

    # Now find each agent's markdown file
    md_files = glob.glob(os.path.join(root, '**/*.md'), recursive=True)
    file_map = {}
    for mf in md_files:
        basename = os.path.splitext(os.path.basename(mf))[0]
        file_map[basename] = mf

    final_agents = []
    
    for agent_id, info in agent_map.items():
        # Match file
        target_file = file_map.get(agent_id)
        if not target_file:
            # Try finding with prefix
            for k, p in file_map.items():
                if k.endswith(agent_id) or agent_id.endswith(k):
                    target_file = p
                    break
        
        system_prompt = ""
        emoji = info['icon']
        core_mission = ""
        key_rules = ""
        deliverables = ""

        if target_file and os.path.exists(target_file):
            with open(target_file, 'r', encoding='utf-8') as f:
                content = f.read()
            fm, body = parse_frontmatter(content)
            if 'emoji' in fm:
                emoji = fm['emoji']
            if 'description' in fm and len(fm['description']) > len(info['desc']):
                info['desc'] = fm['description']
                
            sections = extract_core_prompt_elements(body)
            # Find mission / rules / deliverables
            for k, v in sections.items():
                k_lower = k.lower()
                if any(x in k_lower for x in ['使命', 'mission', '职责', '目标']):
                    core_mission = v
                elif any(x in k_lower for x in ['规则', 'rule', '原则', '边界', '合规']):
                    key_rules = v
                elif any(x in k_lower for x in ['交付', 'deliverable', '模板', '输出']):
                    deliverables = v
            
            # The full prompt can be the clean body or structured prompt
            system_prompt = body.strip()
        else:
            system_prompt = f"你是一位资深的{info['name']}。你的专长领域是：{info['desc']}。"

        rec_settings = determine_recommended_settings(info['department'], info['name'], info['desc'])
        
        # Build optimized prompt template task & context
        # This will be loaded into the generator:
        # Task: Persona + Mission + Deliverable goals
        # Context: Rules + domain standards
        task_prompt = f"作为专业的【{info['name']}】，请执行以下任务：\n\n【核心目标与职责】\n{core_mission[:400] if core_mission else info['desc']}\n\n【期望交付物】\n{deliverables[:300] if deliverables else '按照工业级专业标准输出完整方案/代码/文档，包含具体执行步骤与落地要点。'}"
        
        context_prompt = f"【专业身份与原则】\n- 角色定位：{info['name']}（{info['department']}）\n- 关键规则与边界：\n{key_rules[:400] if key_rules else '- 确保专业性、真实性与合规性；不使用空话套话，注重逻辑自洽与实操细节。'}"

        final_agents.append({
            'id': agent_id,
            'name': info['name'],
            'emoji': emoji,
            'desc': info['desc'],
            'department': info['department'],
            'department_en': info['department_en'],
            'source': info['source'],
            'is_china_original': (info['source'] == '原创'),
            'recommended': rec_settings,
            'task': task_prompt.strip(),
            'context': context_prompt.strip(),
            'full_prompt': system_prompt
        })

    # Sort: China originals first, then by department
    final_agents.sort(key=lambda x: (not x['is_china_original'], x['department'], x['name']))

    print(f"Total processed agents: {len(final_agents)}")
    os.makedirs('data', exist_ok=True)
    out_path = os.path.join('data', 'agents.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(final_agents, f, ensure_ascii=False, indent=2)
    print(f"Saved to {out_path} ({os.path.getsize(out_path)} bytes)")

    # Also generate a lightweight search index version without full_prompt to keep page weight ultra small
    light_agents = []
    for a in final_agents:
        light_agents.append({
            'id': a['id'],
            'name': a['name'],
            'emoji': a['emoji'],
            'desc': a['desc'],
            'department': a['department'],
            'is_china_original': a['is_china_original'],
            'recommended': a['recommended'],
            'task': a['task'],
            'context': a['context']
        })
    light_path = os.path.join('data', 'agents_index.json')
    with open(light_path, 'w', encoding='utf-8') as f:
        json.dump(light_agents, f, ensure_ascii=False)
    print(f"Saved light index to {light_path} ({os.path.getsize(light_path)} bytes)")

if __name__ == '__main__':
    main()
