import re
from typing import List, Dict, Any


SEVERITY_EMOJI = {
    "CRITICAL": "🔴",
    "HIGH": "🟠",
    "MEDIUM": "🟡",
    "LOW": "🟢",
}


CATEGORY_EMOJI = {
    "security": "🔒",
    "bug": "🐛",
    "performance": "⚡",
    "quality": "📝",
    "style": "🎨",
}


def format_review_comment(ai_content: str, stats: Dict = None) -> str:
    lines = ai_content.split('\n')
    
    formatted_lines = []
    issues = []
    current_issue = None
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('**Severity**'):
            severity = extract_severity(line)
            if current_issue:
                issues.append(current_issue)
            current_issue = {'severity': severity, 'lines': [line]}
        elif line.startswith('**File'):
            if current_issue:
                current_issue['lines'].append(line)
        elif line.startswith('**Problem**'):
            if current_issue:
                current_issue['lines'].append(line)
        elif line.startswith('**Fix**'):
            if current_issue:
                current_issue['lines'].append(line)
        elif current_issue:
            if line.startswith('**'):
                issues.append(current_issue)
                current_issue = None
                severity = extract_severity(line)
                current_issue = {'severity': severity, 'lines': [line]}
            else:
                current_issue['lines'].append(line)
        else:
            formatted_lines.append(line)
    
    if current_issue:
        issues.append(current_issue)
    
    formatted_lines.append("")
    formatted_lines.append("---")
    formatted_lines.append("")
    
    if issues:
        formatted_lines.append("### 📋 Znalezione problemy")
        formatted_lines.append("")
        
        for i, issue in enumerate(issues, 1):
            emoji = SEVERITY_EMOJI.get(issue['severity'], "⚪")
            formatted_lines.append(f"**{emoji} {issue['severity']}**")
            
            for line in issue['lines']:
                if not line.startswith('**Severity'):
                    formatted_lines.append(line)
            
            formatted_lines.append("")
    else:
        formatted_lines.append("### ✅ Brak problemów")
        formatted_lines.append("")
        formatted_lines.append("Kod wygląda dobrze!")
        formatted_lines.append("")
    
    if stats:
        formatted_lines.append("---")
        formatted_lines.append("")
        formatted_lines.append(f"📊 Statystyki: {stats.get('total', 0)} problemów")
        if stats.get('critical'):
            formatted_lines.append(f"🔴 Critical: {stats['critical']}")
        if stats.get('high'):
            formatted_lines.append(f"🟠 High: {stats['high']}")
    
    formatted_lines.append("")
    formatted_lines.append("---")
    formatted_lines.append("*Wystawione przez GitMind AI*")
    
    return '\n'.join(formatted_lines)


def extract_severity(line: str) -> str:
    match = re.search(r'(CRITICAL|HIGH|MEDIUM|LOW)', line, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return "INFO"


def extract_stats_from_content(content: str) -> Dict:
    stats = {'total': 0}
    
    critical = len(re.findall(r'\*\*Severity\*\*.*?CRITICAL', content, re.IGNORECASE | re.DOTALL))
    high = len(re.findall(r'\*\*Severity\*\*.*?HIGH', content, re.IGNORECASE | re.DOTALL))
    medium = len(re.findall(r'\*\*Severity\*\*.*?MEDIUM', content, re.IGNORECASE | re.DOTALL))
    low = len(re.findall(r'\*\*Severity\*\*.*?LOW', content, re.IGNORECASE | re.DOTALL))
    
    stats['critical'] = critical
    stats['high'] = high
    stats['medium'] = medium
    stats['low'] = low
    stats['total'] = critical + high + medium + low
    
    return stats


def format_ai_response(response: str) -> str:
    if "no issues" in response.lower() or "brak problemów" in response.lower():
        return "### ✅ Brak problemów\n\nKod wygląda dobrze!"
    
    return response
