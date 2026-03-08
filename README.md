# Infra Daily - AI Infrastructure 仓库监控

## 📁 项目结构

```
/root/.openclaw/workspace/infra-daily/
├── README.md                   # 本文件
├── config.json                 # 配置文件
├── monitor.py                  # 主监控脚本
├── generate_html.py            # HTML 生成器
├── deepseek_reviewer.py        # DeepSeek 分析模块
├── repos/                      # 克隆的仓库
│   ├── vllm/                   # vLLM 项目
│   ├── pytorch/                # PyTorch 项目
│   └── sglang/                 # SGLang 项目
├── data/                       # 状态数据
│   └── state.json
└── reports/                    # 生成的报告
    ├── report_*.json           # JSON 报告
    └── index.html              # HTML 网页
```

## 🚀 快速开始

### 1. 运行监控（分析所有仓库）

```bash
cd /root/.openclaw/workspace/infra-daily
python3 monitor.py
```

### 2. 生成 HTML 报告

```bash
python3 generate_html.py
```

### 3. 查看报告

访问：`http://43.153.105.132:8080/index.html`

## 📊 当前配置

监控的仓库：
- ✅ vllm-project/vllm - LLM 推理引擎
- ✅ pytorch/pytorch - 深度学习框架
- ✅ sgl-project/sglang - 结构化生成语言

每个仓库分析最近 3 个 commits。

## 🔄 定时运行

### 方式 1：手动运行

```bash
cd /root/.openclaw/workspace/infra-daily
python3 monitor.py && python3 generate_html.py
```

### 方式 2：设置 cron

```bash
# 每 2 天运行一次
0 0 */2 * * cd /root/.openclaw/workspace/infra-daily && python3 monitor.py && python3 generate_html.py
```

### 方式 3：GitHub Actions（待部署）

推送此项目到 GitHub，自动运行。

## 📝 输出说明

### JSON 报告

包含每个 commit 的：
- SHA、标题、作者、时间
- DeepSeek AI 深度分析
- GitHub 链接

### HTML 网页

美观的网页展示：
- 📊 统计数据
- 🔗 GitHub 链接
- 📝 AI 分析结果
- 🎨 响应式设计

## 🔧 配置修改

编辑 `config.json`：

```json
{
  "repos": [
    {
      "owner": "your-username",
      "repo": "your-repo",
      "url": "https://github.com/your-username/your-repo.git",
      "branch": "main"
    }
  ],
  "deepseek_api_key": "your-api-key",
  "max_commits": 5
}
```

## 📊 监控指标

- **Commits 分析** - 代码变更、功能描述
- **DeepSeek Review** - 技术亮点、性能影响、潜在问题
- **GitHub 集成** - 直接跳转到 commit 页面

## 🎯 下一步

- [ ] 添加 Issue 跟踪
- [ ] 添加 PR 审查
- [ ] 添加 Release 监控
- [ ] 部署到 GitHub Actions
- [ ] 生成 GitHub Pages

---

**项目位置**: `/root/.openclaw/workspace/infra-daily/`
