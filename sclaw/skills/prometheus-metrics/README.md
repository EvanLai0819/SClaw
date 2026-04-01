# Prometheus Metrics Skill

通过 Prometheus HTTP API 查询服务器监控指标。

## 快速开始

### 1. 配置 Prometheus 地址

在 `TOOLS.md` 中添加：

```markdown
### Prometheus

- **URL**: http://your-server:9090
```

或设置环境变量：

```bash
export PROMETHEUS_URL=http://your-server:9090
```

### 2. 使用脚本

```bash
cd ~/.openclaw/workspace/skills/prometheus-metrics

# 查看完整健康概览
./scripts/query.sh all

# 查看 CPU 使用率
./scripts/query.sh cpu

# 查看内存使用率
./scripts/query.sh memory

# 自定义查询
./scripts/query.sh custom 'up{job="node"}'
```

### 3. 在对话中使用

直接告诉我：
- "查询服务器 CPU 使用率"
- "查看监控指标"
- "Prometheus 健康状态"

我会自动调用这个技能！

## 依赖

- `curl` - HTTP 请求
- `jq` - JSON 处理
- `python3` - URL 编码
- `bc` - 数值比较（可选，用于颜色告警）

安装依赖（Ubuntu/Debian）：
```bash
sudo apt install curl jq python3 bc
```

## 文件结构

```
prometheus-metrics/
├── SKILL.md              # AI 技能说明
├── README.md             # 人类可读文档
└── scripts/
    └── query.sh          # 查询脚本
```

## 常用 PromQL 参考

```promql
# CPU 使用率
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m]))) * 100

# 内存使用率
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# 磁盘使用率
(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100

# 网络流入速率
rate(node_network_receive_bytes_total[5m])

# 网络流出速率
rate(node_network_transmit_bytes_total[5m])

# 系统正常运行时间
node_time_seconds - node_boot_time_seconds
```

## 下一步

可以扩展的功能：
- [ ] 添加告警规则查询
- [ ] 支持 Recording Rules
- [ ] 添加图表生成（ASCII 或图片）
- [ ] 集成 Alertmanager
- [ ] 支持多 Prometheus 实例
