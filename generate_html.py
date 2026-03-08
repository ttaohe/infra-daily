#!/usr/bin/env python3
"""
生成 HTML 报告
"""

import json
from datetime import datetime
from pathlib import Path

def generate_html():
    """生成 HTML 报告"""
    
    # 读取最新的报告
    reports_dir = Path("/root/.openclaw/workspace/infra-daily/reports")
    report_files = sorted(reports_dir.glob("report_*.json"))
    
    if not report_files:
        return None
    
    latest_report = report_files[-1]
    
    with open(latest_report, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 生成 HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub 仓库监控报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .commit-item {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            border-left: 4px solid #667eea;
        }}
        
        .commit-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .commit-title {{
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
        }}
        
        .commit-title a {{
            color: #333;
            text-decoration: none;
        }}
        
        .commit-title a:hover {{
            color: #667eea;
        }}
        
        .commit-meta {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }}
        
        .commit-analysis {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            line-height: 1.6;
            color: #444;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            color: white;
            background: rgba(0,0,0,0.2);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 GitHub 仓库监控报告</h1>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{len(data['commits'])}</div>
                <div>分析 Commits</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(set(c['repo'] for c in data['commits']))}</div>
                <div>监控仓库</div>
            </div>
        </div>
        
        <div class="content">
"""
    
    # 添加每个 commit
    for item in data['commits']:
        commit = item['commit']
        analysis = item['analysis']
        
        html += f"""
            <div class="commit-item">
                <div class="commit-header">
                    <div class="commit-title">
                        <a href="{item['github_url']}" target="_blank">
                            {commit['title']}
                        </a>
                    </div>
                </div>
                
                <div class="commit-meta">
                    📦 {item['repo']} | 
                    👤 {commit['author']} | 
                    🕒 {commit['date']}
                </div>
                
                <div class="commit-analysis">
                    📝 <strong>AI 分析:</strong><br>
                    {analysis.replace(chr(10), '<br>')}
                </div>
            </div>
"""
    
    html += """
        </div>
        
        <div class="footer">
            <p>⚡ Powered by DeepSeek AI | 🔄 自动更新</p>
        </div>
    </div>
</body>
</html>
"""
    
    # 保存 HTML
    html_file = reports_dir / "index.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return html_file

if __name__ == "__main__":
    html_file = generate_html()
    if html_file:
        print(f"✅ HTML 报告已生成: {html_file}")
        print(f"🌐 访问: http://43.153.105.132:8080/index.html")
    else:
        print("❌ 没有找到报告数据")
