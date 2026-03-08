#!/usr/bin/env python3
"""
AI Infrastructure 仓库监控脚本
- 增量分析：只分析自上次运行以来的新 commits
- 支持 REST DAY：无新 commits 时显示休息日
"""

import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import requests

# 加载配置
config_path = Path(__file__).parent / "config.json"
with open(config_path) as f:
    config = json.load(f)

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", config.get("deepseek_api_key"))

def get_last_run_time():
    """获取上次运行的时间"""
    state_file = Path("data/state.json")
    if state_file.exists():
        with open(state_file) as f:
            state = json.load(f)
            return datetime.fromisoformat(state.get("last_run", "2026-01-01"))
    else:
        # 虚拟起点：2026年1月1日
        return datetime(2026, 1, 1)

def save_run_time():
    """保存本次运行时间"""
    state_file = Path("data/state.json")
    state_file.parent.mkdir(exist_ok=True)
    with open(state_file, "w") as f:
        json.dump({"last_run": datetime.now().isoformat()}, f, indent=2)

def clone_or_update_repo(owner, repo, branch="main"):
    """克隆或更新仓库"""
    repo_name = f"{owner}/{repo}"
    repo_path = Path(f"repos/{repo_name}")
    
    if repo_path.exists():
        # 更新现有仓库
        try:
            subprocess.run(
                ["git", "fetch", "origin"],
                cwd=str(repo_path),
                capture_output=True,
                check=True,
                text=True
            )
            print(f"✅ 已更新 {repo_name}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ 更新失败: {e.stderr}")
            # 删除旧目录，重新克隆
            import shutil
            shutil.rmtree(repo_path)
            return clone_or_update_repo(owner, repo, branch)
    else:
        # 克隆新仓库
        repo_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            # git clone 会创建最后一层目录，所以只需要到 parent
            result = subprocess.run(
                ["git", "clone", "--depth", "1", "-b", branch, 
                 f"https://github.com/{owner}/{repo}.git"],
                cwd=str(repo_path.parent),
                capture_output=True,
                text=True,
                check=True,
                timeout=300  # 5分钟超时
            )
            print(f"✅ 已克隆 {repo_name}")
        except subprocess.CalledProcessError as e:
            print(f"❌ 克隆失败: {e.stderr}")
            raise
        except subprocess.TimeoutExpired:
            print(f"❌ 克隆超时")
            raise
    
    # 验证仓库是否存在
    if not repo_path.exists():
        raise FileNotFoundError(f"仓库目录不存在: {repo_path}")
    
    # 验证是否是 git 仓库
    git_dir = repo_path / ".git"
    if not git_dir.exists():
        raise FileNotFoundError(f"不是有效的 git 仓库: {repo_path}")
    
    return repo_path

def get_commits_since(repo_path, owner, repo, since_date):
    """获取指定日期之后的 commits"""
    since_str = since_date.strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        result = subprocess.run(
            ["git", "log", f"--since={since_str}", 
             "--pretty=format:%H|%ai|%s|%an", "--max-count=50"],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            check=True,
            timeout=60
        )
    except subprocess.CalledProcessError as e:
        print(f"⚠️ git log 失败: {e.stderr}")
        return []
    except subprocess.TimeoutExpired:
        print(f"⚠️ git log 超时")
        return []
    
    commits = []
    for line in result.stdout.strip().split("\n"):
        if line:
            try:
                sha, date, title, author = line.split("|", 3)
                commits.append({
                    "sha": sha,
                    "date": date,
                    "title": title,
                    "author": author
                })
            except ValueError as e:
                print(f"⚠️ 解析 commit 失败: {line}")
                continue
    
    return commits

def analyze_with_deepseek(owner, repo, commits):
    """使用 DeepSeek 分析 commits"""
    if not commits:
        return []
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    results = []
    for commit in commits:
        # 构造分析请求
        prompt = f"""你是一个专业的代码审查专家。请分析这个 commit：

仓库: {owner}/{repo}
Commit: {commit['sha'][:8]}
标题: {commit['title']}
作者: {commit['author']}
时间: {commit['date']}

请分析：
1. 这个 commit 做了什么？（功能、bug修复、重构、文档等）
2. 技术亮点是什么？（性能优化、新特性、架构改进等）
3. 对项目有什么影响？（用户、开发者、性能等）

请用简洁的中文回答（2-3句话）。"""
        
        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300,
                    "temperature": 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                analysis = response.json()["choices"][0]["message"]["content"]
                print(f"✅ 分析成功: {commit['sha'][:8]}")
            else:
                analysis = f"分析失败: {response.status_code}"
                print(f"⚠️ 分析失败: {commit['sha'][:8]}")
            
            results.append({
                "repo": f"{owner}/{repo}",
                "commit": commit,
                "analysis": analysis,
                "github_url": f"https://github.com/{owner}/{repo}/commit/{commit['sha']}"
            })
            
        except Exception as e:
            print(f"❌ 分析错误: {commit['sha'][:8]} - {e}")
            results.append({
                "repo": f"{owner}/{repo}",
                "commit": commit,
                "analysis": f"分析异常: {str(e)}",
                "github_url": f"https://github.com/{owner}/{repo}/commit/{commit['sha']}"
            })
    
    return results

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 AI Infrastructure 仓库监控")
    print("=" * 60)
    
    # 获取上次运行时间
    last_run = get_last_run_time()
    print(f"\n📅 上次运行: {last_run.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📅 本次运行: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 分析每个仓库
    all_results = []
    total_commits = 0
    
    for repo_config in config["repos"]:
        owner = repo_config["owner"]
        repo = repo_config["repo"]
        branch = repo_config.get("branch", "main")
        
        print(f"\n{'=' * 60}")
        print(f"📦 分析仓库: {owner}/{repo}")
        print(f"{'=' * 60}")
        
        try:
            # 克隆或更新仓库
            repo_path = clone_or_update_repo(owner, repo, branch)
            
            # 获取新 commits
            commits = get_commits_since(repo_path, owner, repo, last_run)
            
            if not commits:
                print(f"💤 无新 commits - REST DAY! 🎉")
                continue
            
            print(f"📊 发现 {len(commits)} 个新 commits")
            
            # 分析 commits
            results = analyze_with_deepseek(owner, repo, commits)
            all_results.extend(results)
            total_commits += len(commits)
            
        except Exception as e:
            print(f"❌ 处理仓库失败: {e}")
            continue
    
    # 保存结果
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = reports_dir / f"report_{timestamp}.json"
    
    report_data = {
        "generated_at": datetime.now().isoformat(),
        "last_run": last_run.isoformat(),
        "total_commits": total_commits,
        "commits": all_results
    }
    
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'=' * 60}")
    print(f"✅ 报告已生成: {report_file}")
    print(f"📊 总共分析了 {total_commits} 个 commits")
    print(f"{'=' * 60}\n")
    
    # 保存本次运行时间
    save_run_time()
    
    return report_file

if __name__ == "__main__":
    main()
