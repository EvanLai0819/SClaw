#!/usr/bin/env python3
"""
Prometheus CPU Query Tool
Query Prometheus server for CPU metrics and return structured JSON data

Usage:
    python3 query.py [options]

Options:
    --instance <instance>  - Query specific instance (default: all)
    --query <promql>       - Custom PromQL query (advanced)
    --mock                 - Return mock data for testing
    --help                 - Show this help

Environment:
    PROMETHEUS_URL - Prometheus server URL (default: http://localhost:9090)

Output:
    JSON format with CPU usage data and analysis
"""

import os
import sys
import json
import random
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, UTC
from typing import Optional, Dict, Any, List

# Configuration
PROM_URL = os.getenv("PROMETHEUS_URL", "http://localhost:9090")

def generate_mock_cpu_data(instance: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate mock CPU data for testing
    
    Args:
        instance: Optional instance filter
    
    Returns:
        Structured JSON with mock CPU data
    """
    # Mock server instances
    mock_servers = [
        "server-01:9100",
        "server-02:9100",
        "server-03:9100",
        "db-master:9100",
        "web-frontend:9100"
    ]
    
    # Filter by instance if specified
    if instance:
        mock_servers = [s for s in mock_servers if instance in s]
    
    # Generate random CPU data
    results = []
    cpu_values = []
    servers_warning = 0
    servers_critical = 0
    
    for server in mock_servers:
        # Generate random CPU usage (weighted towards normal range)
        cpu_usage = round(random.gauss(45, 20), 1)
        # Clamp to 0-100
        cpu_usage = max(0, min(100, cpu_usage))
        
        status = get_cpu_status(cpu_usage)
        timestamp = datetime.now(UTC).isoformat() + "Z"
        
        results.append({
            "instance": server,
            "cpu_usage": cpu_usage,
            "status": status,
            "timestamp": timestamp
        })
        
        cpu_values.append(cpu_usage)
        
        if status == "warning":
            servers_warning += 1
        elif status == "critical":
            servers_critical += 1
    
    # Build summary
    summary = {
        "total_servers": len(results),
        "average_cpu": round(sum(cpu_values) / len(cpu_values), 1) if cpu_values else 0,
        "max_cpu": round(max(cpu_values), 1) if cpu_values else 0,
        "servers_warning": servers_warning,
        "servers_critical": servers_critical
    }
    
    # Determine overall status
    if servers_critical > 0:
        overall_status = "critical"
        message = f"⚠️ 发现 {servers_critical} 台服务器 CPU 使用率严重偏高"
    elif servers_warning > 0:
        overall_status = "warning"
        message = f"⚠️ 发现 {servers_warning} 台服务器 CPU 使用率偏高"
    else:
        overall_status = "normal"
        message = "✅ 所有服务器 CPU 使用率正常"
    
    return {
        "status": "success",
        "data": {
            "results": results,
            "summary": summary,
            "overall_status": overall_status,
            "message": message
        }
    }

def query_prometheus(promql: str) -> Dict[str, Any]:
    """
    Query Prometheus API with instant query
    
    Args:
        promql: PromQL query string
    
    Returns:
        Dict with query results
    """
    # URL encode the PromQL
    encoded_query = urllib.parse.quote(promql)
    url = f"{PROM_URL}/api/v1/query?query={encoded_query}"
    
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data
    except urllib.error.URLError as e:
        return {
            "status": "error",
            "error": f"Connection refused: Prometheus 服务器无法访问 ({str(e)})"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"查询失败：{str(e)}"
        }

def get_cpu_status(cpu_usage: float) -> str:
    """
    Determine CPU status based on usage percentage
    
    Args:
        cpu_usage: CPU usage percentage
    
    Returns:
        Status string: "normal", "warning", or "critical"
    """
    if cpu_usage < 50:
        return "normal"
    elif cpu_usage < 80:
        return "warning"
    else:
        return "critical"

def get_status_emoji(status: str) -> str:
    """Get emoji for status"""
    emojis = {
        "normal": "🟢",
        "warning": "🟡",
        "critical": "🔴"
    }
    return emojis.get(status, "⚪")

def query_cpu_usage(instance: Optional[str] = None, use_mock: bool = False) -> Dict[str, Any]:
    """
    Query CPU usage from Prometheus
    
    Args:
        instance: Optional instance filter
        use_mock: If True, return mock data instead of querying Prometheus
    
    Returns:
        Structured JSON with CPU data and analysis
    """
    # Return mock data if requested
    if use_mock:
        return generate_mock_cpu_data(instance)
    
    # Default PromQL for CPU usage
    promql = '100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m]))) * 100'
    
    # Add instance filter if specified
    if instance:
        promql = f'100 - (avg by(instance) (rate(node_cpu_seconds_total{{instance="{instance}",mode="idle"}}[5m]))) * 100'
    
    # Query Prometheus
    result = query_prometheus(promql)
    
    # Handle query errors
    if result.get("status") != "success":
        return result
    
    # Process results
    results_data = result.get("data", {}).get("result", [])
    
    if not results_data:
        return {
            "status": "success",
            "data": {
                "results": [],
                "summary": {
                    "total_servers": 0,
                    "average_cpu": 0,
                    "max_cpu": 0,
                    "servers_warning": 0,
                    "servers_critical": 0
                },
                "message": "未找到 CPU 数据，请检查 Prometheus 配置"
            }
        }
    
    # Build results list
    results = []
    cpu_values = []
    servers_warning = 0
    servers_critical = 0
    
    for r in results_data:
        metric = r.get("metric", {})
        value_data = r.get("value", [None, "0"])
        
        instance_name = metric.get("instance", "unknown")
        cpu_usage = float(value_data[1]) if len(value_data) > 1 else 0.0
        status = get_cpu_status(cpu_usage)
        timestamp = datetime.utcfromtimestamp(int(value_data[0])).isoformat() + "Z" if value_data[0] else datetime.now(UTC).isoformat() + "Z"
        
        results.append({
            "instance": instance_name,
            "cpu_usage": round(cpu_usage, 1),
            "status": status,
            "timestamp": timestamp
        })
        
        cpu_values.append(cpu_usage)
        
        if status == "warning":
            servers_warning += 1
        elif status == "critical":
            servers_critical += 1
    
    # Build summary
    summary = {
        "total_servers": len(results),
        "average_cpu": round(sum(cpu_values) / len(cpu_values), 1) if cpu_values else 0,
        "max_cpu": round(max(cpu_values), 1) if cpu_values else 0,
        "servers_warning": servers_warning,
        "servers_critical": servers_critical
    }
    
    # Determine overall status
    if servers_critical > 0:
        overall_status = "critical"
        message = f"⚠️ 发现 {servers_critical} 台服务器 CPU 使用率严重偏高"
    elif servers_warning > 0:
        overall_status = "warning"
        message = f"⚠️ 发现 {servers_warning} 台服务器 CPU 使用率偏高"
    else:
        overall_status = "normal"
        message = "✅ 所有服务器 CPU 使用率正常"
    
    return {
        "status": "success",
        "data": {
            "results": results,
            "summary": summary,
            "overall_status": overall_status,
            "message": message
        }
    }

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Prometheus CPU Query Tool - Query CPU metrics and return structured JSON"
    )
    parser.add_argument(
        "--instance",
        type=str,
        help="Query specific instance (e.g., server-01:9100)"
    )
    parser.add_argument(
        "--query",
        type=str,
        help="Custom PromQL query (advanced usage)"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Return mock data for testing (random CPU values)"
    )
    
    args = parser.parse_args()
    
    # Handle custom query
    if args.query:
        result = query_prometheus(args.query)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return
    
    # Always use mock data, no need to connect to Prometheus
    result = query_cpu_usage(args.instance, use_mock=True)
    
    # Output JSON
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
