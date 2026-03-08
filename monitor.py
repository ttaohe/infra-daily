#!/usr/bin/env python3
"""
GitHub Monitor - 测试版本
简化流程，快速验证
"""

import os
import json
import subprocess
import requests
from datetime import datetime
from pathlib import Path

class GitHubMonitor:
    def __init__(self, config_path="config.json"):
        # 自动检测工作目录
        self.base_dir = Path.cwd()
        
        # 如果当前目录没有 config.json，尝试使用绝对路径
        if not (self.base_dir / config_path).exists():
            self.base_dir = Path("/root/.openclaw/workspace/infra-daily")
        
        self.repos_dir = self.base_dir / "repos"
        self.data_dir = self.base_dir / "data"
        self.reports_dir = self.base_dir / "reports"
        
        # 加载配置
        config_file = self.base_dir / config_path
        with open(config_file) as f:
            self.config = json.load(f)
        
        self.api_key = self.config["deepseek_api_key"]
    
    def clone_repo(self, owner, repo, url):
        """克隆仓库"""
        repo_path = self.repos_dir / repo
        
        if repo_path.exists():
            print(f"✅ 仓库已存在: {repo}")
            subprocess.run(["git", "-C", str(repo_path), "pull"], 
                          capture_output=True)
            return repo_path
        
        print(f"📦 正在克隆 {owner}/{repo}...")
        result = subprocess.run(
            ["git", "clone", "--depth", "1", url, str(repo_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ 克隆失败: {result.stderr}")
            return None
        
        print(f"✅ 克隆成功: {repo}")
        return repo_path
    
    def get_commits(self, repo_path, limit=5):
        """获取最近的 commits"""
        result = subprocess.run([
            "git", "-C", str(repo_path),
            "log", f"-{limit}", "--pretty=format:%H|%s|%an|%ai"
        ], capture_output=True, text=True)
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if line:
                sha, title, author, date = line.split('|')
                commits.append({
                    "sha": sha,
                    "title": title,
                    "author": author,
                    "date": date
                })
        
        return commits
    
    def get_diff(self, repo_path, sha):
        """获取 commit diff"""
        result = subprocess.run([
            "git", "-C", str(repo_path),
            "show", sha, "--stat", "--format="
        ], capture_output=True, text=True)
        
        return result.stdout
    
    def analyze_with_deepseek(self, commit, diff):
        """使用 DeepSeek 分析"""
        prompt = f"""请分析以下 commit：

**标题**: {commit['title']}
**作者**: {commit['author']}
**时间**: {commit['date']}

**代码变更**:
```
{diff[:1000]}
```

请简要分析：
1. 这段代码做了什么？
2. 主要功能是什么？
3. 有什么技术亮点？

请用中文回答，3-5句话。"""
        
        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3
                },
                timeout=30
            )
            
            if response.status_code != 200:
                return f"❌ API 错误: {response.status_code}"
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            return content.strip()
        
        except Exception as e:
            return f"❌ 分析失败: {str(e)}"
    
    def run(self):
        """运行监控"""
        print(f"🚀 开始 GitHub 监控...")
        print(f"📁 工作目录: {self.base_dir}")
        print()
        
        all_results = []
        
        for repo_config in self.config["repos"]:
            owner = repo_config["owner"]
            repo = repo_config["repo"]
            url = repo_config["url"]
            
            print(f"\n📊 监控仓库: {owner}/{repo}")
            
            # 克隆仓库
            repo_path = self.clone_repo(owner, repo, url)
            if not repo_path:
                continue
            
            # 获取 commits
            commits = self.get_commits(
                repo_path, 
                limit=self.config.get("max_commits", 5)
            )
            
            print(f"📝 找到 {len(commits)} 个 commits")
            
            # 分析每个 commit
            for i, commit in enumerate(commits, 1):
                print(f"  [{i}/{len(commits)}] 分析: {commit['title'][:50]}...")
                
                diff = self.get_diff(repo_path, commit["sha"])
                analysis = self.analyze_with_deepseek(commit, diff)
                
                all_results.append({
                    "repo": f"{owner}/{repo}",
                    "commit": commit,
                    "analysis": analysis,
                    "github_url": f"https://github.com/{owner}/{repo}/commit/{commit['sha']}"
                })
        
        # 保存报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_commits": len(all_results),
            "commits": all_results
        }
        
        report_file = self.reports_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 报告已保存: {report_file}")
        print(f"📊 总共分析 {len(all_results)} 个 commits")
        
        return report_file

if __name__ == "__main__":
    monitor = GitHubMonitor()
    report_file = monitor.run()
    print(f"\n🎉 完成！查看报告: {report_file}")
