---
name: prometheus-metrics
description: Query Prometheus server for metrics data (CPU, memory, disk, network, etc.). Supports instant query, range query, and label discovery.
author: Evan
version: 1.0.0
triggers:
  - "查询 Prometheus"
  - "获取监控指标"
  - "服务器监控"
  - "Prometheus 指标"
  - "查看 CPU"
  - "查看内存"
  - "prometheus metrics"
  - "check server metrics"
metadata: {"openclaw":{"emoji":"📊","requires":{"bins":["curl","jq"]}}}
---

# Prometheus Metrics Query

通过 Prometheus HTTP API 查询服务器监控指标数据。

## When to Use

✅ **USE when:**
- "查询服务器 CPU 使用率"
- "获取内存监控数据"
- "查看磁盘使用情况"
- "Prometheus 指标查询"
- "服务器监控状态"

❌ **DON'T use for:**
- Alertmanager 告警管理（需要单独技能）
- Grafana 可视化（直接用 Grafana）
- 历史数据导出（考虑用 recording rules）

## Configuration

**Required:** 在 `TOOLS.md` 中配置 Prometheus 服务器地址：

```markdown
### Prometheus

- **URL**: http://localhost:9090
- **Auth**: 无 / Bearer Token / Basic Auth
```

或在命令中通过环境变量指定：
```bash
export PROMETHEUS_URL=http://your-prometheus:9090
```

## Common Metrics（常用指标）

### 系统指标

| 指标 | PromQL | 说明 |
|------|--------|------|
| CPU 使用率 | `100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)` | 5 分钟平均 CPU 使用率 |
| 内存使用率 | `(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100` | 内存使用百分比 |
| 磁盘使用率 | `(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100` | 磁盘使用百分比 |
| 网络流入 | `rate(node_network_receive_bytes_total[5m])` | 网络接收速率 |
| 网络流出 | `rate(node_network_transmit_bytes_total[5m])` | 网络发送速率 |

### 应用指标

| 指标 | PromQL | 说明 |
|------|--------|------|
| HTTP 请求率 | `rate(http_requests_total[5m])` | 每秒请求数 |
| 请求延迟 | `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))` | P95 延迟 |
| 错误率 | `rate(http_requests_total{status=~"5.."}[5m])` | 5xx 错误率 |

## Commands

### 1. 即时查询（Instant Query）

```bash
# 基础查询
curl -s "http://localhost:9090/api/v1/query?query=up" | jq '.data.result'

# CPU 使用率
curl -s "http://localhost:9090/api/v1/query?query=100%20-%20(avg%20by(instance)%20(rate(node_cpu_seconds_total%7Bmode%3D%22idle%22%7D%5B5m%5D)))%20*%20100" | jq -r '.data.result[] | .metric.instance + ": " + .value[1] + "%"'

# 内存使用率
curl -s "http://localhost:9090/api/v1/query?query=(1%20-%20(node_memory_MemAvailable_bytes%20/%20node_memory_MemTotal_bytes))%20*%20100" | jq -r '.data.result[] | .metric.instance + ": " + (.value[1]|tonumber|round|tostring) + "%"'
```

### 2. 范围查询（Range Query）

```bash
# 过去 1 小时的数据，每 5 分钟一个点
curl -s "http://localhost:9090/api/v1/query_range?query=up&start=$(date -d '1 hour ago' +%s)&end=$(date +%s)&step=300" | jq '.data.result[] | .values | length'

# CPU 使用率趋势（过去 24 小时）
curl -s "http://localhost:9090/api/v1/query_range?query=100%20-%20(avg%20by(instance)%20(rate(node_cpu_seconds_total%7Bmode%3D%22idle%22%7D%5B5m%5D)))%20*%20100&start=$(date -d '24 hours ago' +%s)&end=$(date +%s)&step=3600" | jq '.data.result[] | {instance: .metric.instance, points: (.values | length)}'
```

### 3. 标签发现（Label Discovery）

```bash
# 获取所有指标名称
curl -s "http://localhost:9090/api/v1/label/__name__/values" | jq '.data[]'

# 获取所有实例
curl -s "http://localhost:9090/api/v1/label/instance/values" | jq '.data[]'

# 获取所有作业
curl -s "http://localhost:9090/api/v1/label/job/values" | jq '.data[]'
```

### 4. 目标状态（Targets Status）

```bash
# 查看所有 target 状态
curl -s "http://localhost:9090/api/v1/targets" | jq -r '.data.activeTargets[] | .labels.job + "/" + .labels.instance + ": " + .health'

# 统计健康目标数量
curl -s "http://localhost:9090/api/v1/targets" | jq '[.data.activeTargets[] | select(.health == "up")] | length'
```

## Quick Scripts

### 📊 服务器健康概览

```bash
#!/bin/bash
PROM_URL="${PROMETHEUS_URL:-http://localhost:9090}"

echo "=== Prometheus Server Status ==="
curl -s "$PROM_URL/api/v1/query?query=up" | jq -r '.data.result[] | select(.value[1] == "1") | .metric.instance + " ✅ UP"'

echo -e "\n=== CPU Usage (5m avg) ==="
curl -s "$PROM_URL/api/v1/query?query=100%20-%20(avg%20by(instance)%20(rate(node_cpu_seconds_total%7Bmode%3D%22idle%22%7D%5B5m%5D)))%20*%20100" | jq -r '.data.result[] | .metric.instance + ": " + (.value[1]|tonumber|round|tostring) + "%"'

echo -e "\n=== Memory Usage ==="
curl -s "$PROM_URL/api/v1/query?query=(1%20-%20(node_memory_MemAvailable_bytes%20/%20node_memory_MemTotal_bytes))%20*%20100" | jq -r '.data.result[] | .metric.instance + ": " + (.value[1]|tonumber|round|tostring) + "%"'

echo -e "\n=== Disk Usage ==="
curl -s "$PROM_URL/api/v1/query?query=(1%20-%20(node_filesystem_avail_bytes%20/%20node_filesystem_size_bytes))%20*%20100" | jq -r '.data.result[] | select(.metric.mountpoint == "/") | .metric.instance + " /: " + (.value[1]|tonumber|round|tostring) + "%"'
```

### 🚨 告警检查

```bash
# 查询当前告警
curl -s "http://localhost:9090/api/v1/rules" | jq -r '.data.groups[].rules[] | select(.type == "alerting" and .health == "ok") | .name + ": " + .labels.severity'
```

## URL Encoding Tips

PromQL 需要 URL 编码，常用字符：
- 空格 → `%20`
- `{` → `%7B`
- `}` → `%7D`
- `"` → `%22`
- `[` → `%5B`
- `]` → `%5D`

**技巧**: 先在浏览器或 jq 中测试好 PromQL，再用 `python3 -c "import urllib.parse; print(urllib.parse.quote('你的 PromQL'))"` 编码。

## API Reference

| Endpoint | 说明 |
|----------|------|
| `/api/v1/query` | 即时查询 |
| `/api/v1/query_range` | 范围查询 |
| `/api/v1/labels` | 获取所有标签名 |
| `/api/v1/label/<name>/values` | 获取标签值 |
| `/api/v1/series` | 获取时间序列 |
| `/api/v1/targets` | 获取 target 状态 |
| `/api/v1/rules` | 获取规则（告警/记录） |
| `/api/v1/alerts` | 获取当前告警 |

官方文档：https://prometheus.io/docs/prometheus/latest/querying/api/

## Examples

**"查询服务器 CPU 使用率"**
```bash
curl -s "http://localhost:9090/api/v1/query?query=100%20-%20(avg%20by(instance)%20(rate(node_cpu_seconds_total%7Bmode%3D%22idle%22%7D%5B5m%5D)))%20*%20100" | jq -r '.data.result[] | .metric.instance + ": " + (.value[1]|tonumber|round|tostring) + "%"'
```

**"查看所有监控目标状态"**
```bash
curl -s "http://localhost:9090/api/v1/targets" | jq -r '.data.activeTargets[] | .labels.job + "/" + .labels.instance + ": " + .health'
```

**"获取过去 1 小时内存使用趋势"**
```bash
curl -s "http://localhost:9090/api/v1/query_range?query=(1%20-%20(node_memory_MemAvailable_bytes%20/%20node_memory_MemTotal_bytes))%20*%20100&start=$(date -d '1 hour ago' +%s)&end=$(date +%s)&step=300" | jq '.data.result[0].values | .[] | .[0] | strftime("%H:%M")'
```

## Tips

- **时间格式**: Prometheus 使用 Unix 时间戳（秒）
- **步长**: `step` 参数决定范围查询的采样间隔
- **超时**: 复杂查询可能需要更长时间，添加 `&timeout=30s`
- **认证**: 如需认证，添加 `-H "Authorization: Bearer xxx"` 或 `-u user:pass`
- **HTTPS**: 自签名证书用 `-k` 跳过验证

## Troubleshooting

**查询返回空结果？**
- 检查指标名称是否正确
- 检查时间范围是否合理
- 确认 target 状态为 "up"

**连接被拒绝？**
- 确认 Prometheus 服务运行中
- 检查防火墙/网络策略
- 确认 URL 和端口正确
