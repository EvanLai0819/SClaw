---
name: prometheus-cpu
description: Query Prometheus server for CPU metrics via query.py script and provide analysis
author: Evan
version: 1.0.0
triggers:
  - "Query CPU"
  - "CPU usage"
  - "Server CPU"
  - "prometheus cpu"
  - "Check CPU"
metadata: 
  {"openclaw":{
    "emoji":"📊",
    "requires":{
      "bins":["python3"],
      "env":{"PROMETHEUS_URL":{"required":false,"default":"http://localhost:9090"}}
    }
  }}
---

# Prometheus CPU Query Skill

Query CPU metrics from Prometheus server by calling the `query.py` script, then organize and analyze the results from the JSON data returned by the script to respond to users.

## Workflow

```
User asks → LLM calls query.py → Script requests Prometheus → Returns JSON → LLM analyzes results → Responds to user
```

## When to Use

✅ **USE when:**
- "Query server CPU usage"
- "Is CPU usage high?"
- "Check CPU of xxx server"
- "Prometheus CPU metrics"

❌ **DON'T use for:**
- Other metrics like memory, disk, etc.
- Historical trend analysis (requires additional parameters)
- Grafana visualization

## Configuration

Configure Prometheus server address in `TOOLS.md`:

```markdown
### Prometheus

- **URL**: http://localhost:9090
```

Or specify via environment variable in command:
```bash
export PROMETHEUS_URL=http://your-prometheus:9090
```

**Default value**: `http://localhost:9090`

## Commands

### Basic Queries

```bash
# Query CPU usage for all servers
python3 {baseDir}/scripts/query.py

# Query CPU for specific server
python3 {baseDir}/scripts/query.py --instance "server-01:9100"

# Custom PromQL query
python3 {baseDir}/scripts/query.py --query "your PromQL"

# Show help
python3 {baseDir}/scripts/query.py --help
```

## Execution Flow

### Step 1: Call query.py script

When users ask about CPU-related information, **do not respond directly**, but first execute the script to get data:

```bash
python3 {baseDir}/scripts/query.py
```

### Step 2: Get JSON returned by script

The script will return structured JSON data, for example:

```json
{
  "status": "success",
  "data": {
    "results": [
      {
        "instance": "server-01:9100",
        "cpu_usage": 25.3,
        "status": "normal",
        "timestamp": "2026-04-01T20:30:00Z"
      },
      {
        "instance": "server-02:9100",
        "cpu_usage": 67.8,
        "status": "warning",
        "timestamp": "2026-04-01T20:30:00Z"
      }
    ],
    "summary": {
      "total_servers": 2,
      "average_cpu": 46.6,
      "max_cpu": 67.8,
      "servers_warning": 1,
      "servers_critical": 0
    }
  }
}
```

### Step 3: Parse JSON and organize conclusions

Extract key information from the JSON data:

1. **Overall status**: Check statistical data in `summary`
2. **Server details**: Iterate through `results` array
3. **Abnormal conditions**: Check for `warning` or `critical` status

### Step 4: Respond to user

Organize conclusions in friendly language and respond:

```
📊 CPU usage (as of 20:30):

**Overall status**: ✅ Normal
- Average CPU usage: 46.6%
- Maximum CPU usage: 67.8%

**Server details**:
- server-01: 25.3% 🟢 Normal
- server-02: 67.8% 🟡 High (needs attention)

**Recommendation**: server-02 has high CPU usage, suggest checking for abnormal processes.
```

## Examples

### Example 1: Query all servers CPU

**User asks**: "Query server CPU usage"

**Step 1 - Execute script**:
```bash
python3 {baseDir}/scripts/query.py
```

**Step 2 - Script returns JSON**:
```json
{
  "status": "success",
  "data": {
    "results": [
      {
        "instance": "server-01:9100",
        "cpu_usage": 25.3,
        "status": "normal",
        "timestamp": "2026-04-01T20:30:00Z"
      },
      {
        "instance": "server-02:9100",
        "cpu_usage": 67.8,
        "status": "warning",
        "timestamp": "2026-04-01T20:30:00Z"
      }
    ],
    "summary": {
      "total_servers": 2,
      "average_cpu": 46.6,
      "max_cpu": 67.8,
      "servers_warning": 1,
      "servers_critical": 0
    }
  }
}
```

**Step 3 - Organize conclusion and respond to user**:
"📊 CPU usage (as of 20:30):

**Overall status**: ✅ Normal
- Average CPU usage: 46.6%
- Maximum CPU usage: 67.8%

**Server details**:
- server-01: 25.3% 🟢 Normal
- server-02: 67.8% 🟡 High (needs attention)

**Recommendation**: server-02 has high CPU usage, suggest checking for abnormal processes."

---

### Example 2: Query specific server

**User asks**: "Query CPU of server-01"

**Step 1 - Execute script**:
```bash
python3 {baseDir}/scripts/query.py --instance "server-01:9100"
```

**Step 2 - Script returns JSON**:
```json
{
  "status": "success",
  "data": {
    "results": [
      {
        "instance": "server-01:9100",
        "cpu_usage": 25.3,
        "status": "normal",
        "timestamp": "2026-04-01T20:30:00Z"
      }
    ]
  }
}
```

**Step 3 - Organize conclusion and respond to user**:
"server-01 current CPU usage: 25.3% 🟢

Status is normal, load is low."

---

### Example 3: CPU alert situation

**User asks**: "Is there any CPU abnormality?"

**Step 1 - Execute script**:
```bash
python3 {baseDir}/scripts/query.py
```

**Step 2 - Script returns JSON**:
```json
{
  "status": "success",
  "data": {
    "results": [
      {
        "instance": "server-01:9100",
        "cpu_usage": 92.5,
        "status": "critical",
        "timestamp": "2026-04-01T20:30:00Z"
      }
    ],
    "summary": {
      "servers_critical": 1
    }
  }
}
```

**Step 3 - Organize conclusion and respond to user**:
"⚠️ **CPU Alert!**

🔴 server-01: 92.5% (Critical)

**Immediate action recommended**:
1. Check for abnormal processes consuming CPU
2. Check application logs for errors
3. Consider scaling up or optimizing performance

Would you like me to help query detailed process information?"

---

### Example 4: Script execution failure

**User asks**: "Query CPU usage"

**Step 1 - Execute script**:
```bash
python3 {baseDir}/scripts/query.py
```

**Step 2 - Script returns error**:
```json
{
  "status": "error",
  "error": "Connection refused: Prometheus 服务器无法访问"
}
```

**Step 3 - Organize conclusion and respond to user**:
"❌ Unable to connect to Prometheus server

Possible reasons:
1. Prometheus service is not started
2. Server address configuration error
3. Network issues

Please check Prometheus service status or contact administrator."

## Input/Output Format

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--instance` | string | ❌ | Specify server instance (default: all) |
| `--query` | string | ❌ | Custom PromQL (advanced usage) |
| `PROMETHEUS_URL` | string | ❌ | Prometheus address (default: http://localhost:9090) |

### Script Output Format (JSON)

**Success response**:
```json
{
  "status": "success",
  "data": {
    "results": [
      {
        "instance": "server address",
        "cpu_usage": value (percentage),
        "status": "normal|warning|critical",
        "timestamp": "ISO8601 time"
      }
    ],
    "summary": {
      "total_servers": total count,
      "average_cpu": average value,
      "max_cpu": maximum value,
      "servers_warning": warning count,
      "servers_critical": critical count
    }
  }
}
```

**Error response**:
```json
{
  "status": "error",
  "error": "error description"
}
```

### Status Judgment Criteria

| Status | CPU Usage | Description |
|--------|-----------|-------------|
| `normal` | < 50% | Normal |
| `warning` | 50% - 80% | High, needs attention |
| `critical` | > 80% | Critical, needs immediate action |

## Error Handling

### Error Handling Process

1. **Check `status` field in JSON**
   - `status: "success"` → Continue parsing `data`
   - `status: "error"` → Extract `error` field and inform user

2. **Common errors and responses**:

| Error | Possible Cause | Response Suggestion |
|-------|----------------|---------------------|
| `Connection refused` | Prometheus not started | Please check service status |
| `Empty result` | No data or instance error | Please check configuration |
| `Timeout` | Network issue | Please try again later |

3. **Respond to user** - Explain the problem in friendly language and provide solutions

## Tips

- **Execute script first**: Do not respond directly, first call `query.py` to get data
- **Parse JSON**: Extract key information from the JSON returned by the script
- **Organize conclusions**: Provide analysis and recommendations based on data, not just list numbers
- **Status indicators**: 🟢 Normal / 🟡 High / 🔴 Critical
- **Error handling**: When script fails, friendly inform user and explain possible reasons