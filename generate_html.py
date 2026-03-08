#!/usr/bin/env python3
"""
生成 HTML 报告
- 支持按仓库分页
- 支持 AI 自动分类
- 支持 REST DAY 显示
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
    
    # 按仓库分组
    repos = {}
    for item in data['commits']:
        repo = item['repo']
        if repo not in repos:
            repos[repo] = []
        repos[repo].append(item)
    
    # 生成主页
    if total_commits == 0:
        # REST DAY 页面
        index_html = generate_rest_day_html(last_run, generated_at)
    else:
        # 主页 - 显示所有仓库概览
        index_html = generate_index_html(repos, generated_at, last_run, total_commits)
    
    # 保存主页
    index_file = reports_dir / "index.html"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    print(f"✅ 主页已生成: {index_file}")
    
    # 为每个仓库生成独立页面
    for repo_name, commits in repos.items():
        repo_slug = repo_name.replace('/', '_')
        repo_file = reports_dir / f"repo_{repo_slug}.html"
        
        repo_html = generate_repo_html(repo_name, commits, generated_at, last_run)
        
        with open(repo_file, 'w', encoding='utf-8') as f:
            f.write(repo_html)
        
        print(f"✅ {repo_name} 页面已生成: {repo_file}")
    
    print(f"📁 绝对路径: {index_file.absolute()}")
    
    return index_file

def get_category_emoji(analysis):
    """根据分析内容返回分类 emoji"""
    analysis_lower = analysis.lower()
    
    # 优先级从高到低
    if any(word in analysis_lower for word in ['bug', 'fix', '修复', '错误', '问题']):
        return '🐛', 'BugFix'
    elif any(word in analysis_lower for word in ['refactor', '重构', '优化结构', '改进']):
        return '♻️', 'Refactor'
    elif any(word in analysis_lower for word in ['doc', '文档', 'readme', '注释']):
        return '📚', 'Docs'
    elif any(word in analysis_lower for word in ['performance', '性能', '速度', '延迟', '吞吐']):
        return '⚡', 'Performance'
    elif any(word in analysis_lower for word in ['config', '配置', '设置', '环境']):
        return '🔧', 'Config'
    elif any(word in analysis_lower for word in ['test', '测试', 'ci']):
        return '✅', 'Test'
    elif any(word in analysis_lower for word in ['feature', '功能', '新增', '支持']):
        return '🚀', 'Feature'
    else:
        return '📝', 'Other'

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

def generate_index_html(repos, generated_at, last_run, total_commits):
    """生成主页 - 显示所有仓库概览"""
    repo_cards = ""
    
    for repo_name, commits in sorted(repos.items()):
        repo_slug = repo_name.replace('/', '_')
        
        # 统计分类
        categories = {}
        for item in commits:
            analysis = item.get('analysis', '')
            emoji, cat = get_category_emoji(analysis)
            categories[cat] = categories.get(cat, 0) + 1
        
        category_tags = ""
        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            category_tags += f'<span class="category-tag">{cat}: {count}</span>'
        
        repo_cards += f"""
        <div class="repo-card">
            <div class="repo-header">
                <h2>{repo_name}</h2>
                <a href="repo_{repo_slug}.html" class="btn">查看详情 →</a>
            </div>
            
            <div class="repo-stats">
                <div class="stat">
                    <div class="stat-number">{len(commits)}</div>
                    <div class="stat-label">Commits</div>
                </div>
            </div>
            
            <div class="repo-categories">
                {category_tags}
            </div>
        </div>
        """
    
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Infrastructure 仓库监控 - Infra Daily</title>
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
            max-width: 1400px;
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
        
        .content {{
            padding: 30px;
        }}
        
        .repo-card {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 20px;
            border-left: 5px solid #667eea;
        }}
        
        .repo-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .repo-header h2 {{
            color: #333;
            font-size: 1.5em;
        }}
        
        .btn {{
            padding: 10px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-weight: bold;
            transition: transform 0.3s;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
        }}
        
        .repo-stats {{
            display: flex;
            gap: 20px;
            margin-bottom: 15px;
        }}
        
        .stat {{
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
        
        .repo-categories {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .category-tag {{
            background: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            color: #666;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
            <h1>🚀 AI Infrastructure 仓库监控</h1>
            <p>生成时间: {generated_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="time-range">
                <p>📅 监控时间范围: <strong>{last_run.strftime('%Y-%m-%d %H:%M')}</strong> → <strong>{generated_at.strftime('%Y-%m-%d %H:%M')}</strong></p>
                <p>📊 总计: <strong>{total_commits}</strong> 个 commits | <strong>{len(repos)}</strong> 个仓库</p>
            </div>
        </div>
        
        <div class="content">
            {repo_cards}
        </div>
        
        <div class="footer">
            <p>⚡ Powered by DeepSeek AI | 🔄 自动更新</p>
        </div>
    </div>
</body>
</html>"""

def generate_repo_html(repo_name, commits, generated_at, last_run):
    """生成单个仓库的详细页面"""
    
    # 统计分类
    categories_count = {}
    for item in commits:
        analysis = item.get('analysis', '')
        emoji, cat = get_category_emoji(analysis)
        categories_count[cat] = categories_count.get(cat, 0) + 1
    
    # 生成分类统计
    category_stats = ""
    for cat, count in sorted(categories_count.items(), key=lambda x: -x[1]):
        emoji = {'BugFix': '🐛', 'Refactor': '♻️', 'Docs': '📚', 'Performance': '⚡', 'Config': '🔧', 'Test': '✅', 'Feature': '🚀', 'Other': '📝'}.get(cat, '📝')
        category_stats += f'<span class="category-stat">{emoji} {cat}: {count}</span>'
    
    # 生成 commits 列表
    commits_html = ""
    for item in commits:
        commit = item['commit']
        analysis = item.get('analysis', '分析失败')
        
        # 构造 GitHub URL
        if 'github_url' not in item:
            owner, repo_name_part = repo_name.split('/')
            item['github_url'] = f"https://github.com/{owner}/{repo_name_part}/commit/{commit['sha']}"
        
        # 获取分类
        emoji, cat = get_category_emoji(analysis)
        
        commits_html += f"""
        <div class="commit-item">
            <div class="commit-header">
                <span class="category-badge" data-category="{cat}">{emoji} {cat}</span>
                <div class="commit-title">
                    <a href="{item['github_url']}" target="_blank">
                        {commit['title']}
                    </a>
                </div>
            </div>
            
            <div class="commit-meta">
                👤 {commit['author']} | 🕒 {commit['date']}
            </div>
            
            <div class="commit-analysis">
                📝 <strong>AI 分析:</strong>
                {analysis}
            </div>
        </div>
        """
    
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{repo_name} - Infra Daily</title>
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
        }}
        
        .back-btn {{
            display: inline-block;
            padding: 10px 20px;
            background: rgba(255,255,255,0.2);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            margin-bottom: 20px;
            transition: transform 0.3s;
        }}
        
        .back-btn:hover {{
            transform: translateY(-2px);
            background: rgba(255,255,255,0.3);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .category-stats {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-top: 20px;
        }}
        
        .category-stat {{
            background: rgba(255,255,255,0.2);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 1.1em;
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
            align-items: center;
            gap: 15px;
            margin-bottom: 10px;
        }}
        
        .category-badge {{
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: bold;
            white-space: nowrap;
        }}
        
        .category-badge[data-category="Feature"] {{ background: #e3f2fd; color: #1976d2; }}
        .category-badge[data-category="BugFix"] {{ background: #ffebee; color: #c62828; }}
        .category-badge[data-category="Refactor"] {{ background: #f3e5f5; color: #7b1fa2; }}
        .category-badge[data-category="Performance"] {{ background: #fff3e0; color: #f57c00; }}
        .category-badge[data-category="Docs"] {{ background: #e8f5e9; color: #388e3c; }}
        .category-badge[data-category="Config"] {{ background: #fce4ec; color: #c2185b; }}
        .category-badge[data-category="Test"] {{ background: #e0f2f1; color: #00796b; }}
        .category-badge[data-category="Other"] {{ background: #eceff1; color: #455a64; }}
        
        .commit-title {{
            flex: 1;
        }}
        
        .commit-title a {{
            color: #333;
            text-decoration: none;
            font-size: 1.2em;
            font-weight: bold;
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
            <a href="index.html" class="back-btn">← 返回主页</a>
            <h1>📦 {repo_name}</h1>
            <p>生成时间: {generated_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="category-stats">
                {category_stats}
            </div>
        </div>
        
        <div class="content">
            {commits_html}
        </div>
        
        <div class="footer">
            <p>⚡ Powered by DeepSeek AI | 🔄 自动更新</p>
        </div>
    </div>
</body>
</html>"""

if __name__ == "__main__":
    generate_html()
