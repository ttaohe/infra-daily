#!/usr/bin/env python3
"""
生成 HTML 报告
支持 REST DAY 显示
"""

import json
import os
from datetime import datetime
from pathlib import Path

def generate_html():
    """生成 HTML 报告"""
    
    # 使用相对路径查找报告目录
    reports_dir = Path("reports")
    
    if not reports_dir.exists():
        print(f"❌ 找不到 reports 目录")
        print(f"当前目录: {os.getcwd()}")
        print(f"查找的路径: {reports_dir.absolute()}")
        return None
    
    print(f"📁 报告目录: {reports_dir.absolute()}")
    
    # 读取最新的报告
    report_files = sorted(reports_dir.glob("report_*.json"))
    
    if not report_files:
        print("❌ 没有找到报告文件")
        return None
    
    latest_report = report_files[-1]
    print(f"📄 最新报告: {latest_report.name}")
    
    with open(latest_report, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 解析时间信息
    generated_at = datetime.fromisoformat(data['generated_at'])
    last_run = datetime.fromisoformat(data['last_run'])
    total_commits = data['total_commits']
    
    # 生成 HTML
    if total_commits == 0:
        # REST DAY 页面
        html = generate_rest_day_html(last_run, generated_at)
    else:
        # 正常报告页面
        html = generate_normal_html(data, generated_at, last_run)
    
    # 保存 HTML
    html_file = reports_dir / "index.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ HTML 报告已生成: {html_file}")
    print(f"📁 绝对路径: {html_file.absolute()}")
    
    return html_file

def generate_rest_day_html(last_run, generated_at):
    """生成 REST DAY 页面"""
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>REST DAY 🎉 - Infra Daily</title>
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
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        
        .container {{
            max-width: 800px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 60px 40px;
            text-align: center;
        }}
        
        .emoji {{
            font-size: 8em;
            margin-bottom: 30px;
            animation: bounce 2s infinite;
        }}
        
        @keyframes bounce {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-20px); }}
        }}
        
        h1 {{
            font-size: 3em;
            margin-bottom: 20px;
            color: #333;
        }}
        
        p {{
            font-size: 1.3em;
            color: #666;
            margin-bottom: 15px;
            line-height: 1.6;
        }}
        
        .time-range {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 30px 0;
            font-size: 1.1em;
        }}
        
        .time-range strong {{
            color: #667eea;
        }}
        
        .footer {{
            margin-top: 40px;
            color: rgba(255,255,255,0.8);
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="emoji">🏖️</div>
        <h1>REST DAY!</h1>
        <p>今天没有新的 commits</p>
        <p>大家都在休息，享受宁静的一天吧~</p>
        
        <div class="time-range">
            <p>监控时间范围:</p>
            <p><strong>从: {last_run.strftime('%Y-%m-%d %H:%M')}</strong></p>
            <p><strong>到: {generated_at.strftime('%Y-%m-%d %H:%M')}</strong></p>
        </div>
        
        <p>监控的仓库都在保持稳定运行 ✅</p>
        
        <div class="footer">
            <p>⚡ Powered by DeepSeek AI | 🔄 下次更新: 2天后</p>
        </div>
    </div>
</body>
</html>"""

def generate_normal_html(data, generated_at, last_run):
    """生成正常报告页面"""
    commits = data['commits']
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub 仓库监控报告 - Infra Daily</title>
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
        
        .time-range {{
            background: rgba(255,255,255,0.2);
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            font-size: 0.9em;
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
        
        .commit-title {{
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
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
            white-space: pre-wrap;
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
            <p>生成时间: {generated_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="time-range">
                <p>📅 监控时间范围: <strong>{last_run.strftime('%Y-%m-%d %H:%M')}</strong> → <strong>{generated_at.strftime('%Y-%m-%d %H:%M')}</strong></p>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{len(commits)}</div>
                <div>新 Commits</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(set(c['repo'] for c in commits))}</div>
                <div>活跃仓库</div>
            </div>
        </div>
        
        <div class="content">
"""
    
    # 添加每个 commit
    for item in commits:
        commit = item['commit']
        analysis = item.get('analysis', '分析失败')
        
        # 构造 GitHub URL（如果不存在）
        if 'github_url' not in item:
            repo = item['repo']
            sha = commit['sha']
            owner, repo_name = repo.split('/')
            item['github_url'] = f"https://github.com/{owner}/{repo_name}/commit/{sha}"
        
        # 处理 analysis 可能是字符串或字典
        if isinstance(analysis, dict):
            analysis_text = analysis.get('functionality', str(analysis))
        else:
            analysis_text = str(analysis)
        
        html += f"""
            <div class="commit-item">
                <div class="commit-title">
                    <a href="{item['github_url']}" target="_blank">
                        {commit['title']}
                    </a>
                </div>
                
                <div class="commit-meta">
                    📦 {item['repo']} | 
                    👤 {commit['author']} | 
                    🕒 {commit['date']}
                </div>
                
                <div class="commit-analysis">
                    📝 <strong>AI 分析:</strong><br>
                    {analysis_text}
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
    
    return html

if __name__ == "__main__":
    generate_html()
