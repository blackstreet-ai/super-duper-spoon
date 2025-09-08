"""
MCP connection health checks and error handling utilities.
"""

import asyncio
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from agents.mcp.server import MCPServerStdio, MCPServerStreamableHttp
except Exception:
    from agents.mcp import MCPServerStdio, MCPServerStreamableHttp


class MCPStatus(Enum):
    """MCP server connection status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    NOT_CONFIGURED = "not_configured"


@dataclass
class MCPHealthCheck:
    """Result of an MCP server health check."""
    server_name: str
    status: MCPStatus
    response_time_ms: Optional[float]
    error_message: Optional[str]
    tools_count: Optional[int]


async def check_exa_mcp_health() -> MCPHealthCheck:
    """
    Check health of Exa Hosted MCP server.
    
    Returns:
        MCPHealthCheck with connection status and metrics
    """
    exa_api_key = os.getenv("EXA_API_KEY")
    if not exa_api_key:
        return MCPHealthCheck(
            server_name="exa-hosted",
            status=MCPStatus.NOT_CONFIGURED,
            response_time_ms=None,
            error_message="EXA_API_KEY not set",
            tools_count=None
        )
    
    try:
        import time
        start_time = time.time()
        
        # For hosted MCP, we can't directly test connection without the HostedMCPTool
        # So we'll do a basic validation of the API key format
        if not exa_api_key.startswith(('exa_', '2171d0a6')):  # Common Exa key patterns
            return MCPHealthCheck(
                server_name="exa-hosted",
                status=MCPStatus.DEGRADED,
                response_time_ms=(time.time() - start_time) * 1000,
                error_message="API key format appears invalid",
                tools_count=None
            )
        
        response_time = (time.time() - start_time) * 1000
        return MCPHealthCheck(
            server_name="exa-hosted",
            status=MCPStatus.HEALTHY,
            response_time_ms=response_time,
            error_message=None,
            tools_count=2  # web_search_exa, crawling typically available
        )
        
    except Exception as e:
        return MCPHealthCheck(
            server_name="exa-hosted",
            status=MCPStatus.FAILED,
            response_time_ms=None,
            error_message=str(e),
            tools_count=None
        )


async def check_notion_stdio_health() -> MCPHealthCheck:
    """
    Check health of Notion MCP stdio server.
    
    Returns:
        MCPHealthCheck with connection status and metrics
    """
    notion_token = os.getenv("NOTION_TOKEN")
    if not notion_token:
        return MCPHealthCheck(
            server_name="notion-stdio",
            status=MCPStatus.NOT_CONFIGURED,
            response_time_ms=None,
            error_message="NOTION_TOKEN not set",
            tools_count=None
        )
    
    try:
        import time
        start_time = time.time()
        
        server = MCPServerStdio(
            params={
                "command": "npx",
                "args": ["-y", "@notionhq/notion-mcp-server"],
                "env": {"NOTION_TOKEN": notion_token},
            },
            name="notion-stdio-health",
            cache_tools_list=True,
        )
        
        await server.connect()
        tools = await server.list_tools()
        # Note: MCPServerStdio doesn't have explicit disconnect method
        
        response_time = (time.time() - start_time) * 1000
        return MCPHealthCheck(
            server_name="notion-stdio",
            status=MCPStatus.HEALTHY,
            response_time_ms=response_time,
            error_message=None,
            tools_count=len(tools) if tools else 0
        )
        
    except Exception as e:
        return MCPHealthCheck(
            server_name="notion-stdio",
            status=MCPStatus.FAILED,
            response_time_ms=None,
            error_message=str(e),
            tools_count=None
        )


async def check_notion_http_health() -> MCPHealthCheck:
    """
    Check health of Notion MCP HTTP server.
    
    Returns:
        MCPHealthCheck with connection status and metrics
    """
    notion_url = os.getenv("NOTION_MCP_URL")
    notion_auth = os.getenv("NOTION_MCP_AUTH_TOKEN")
    
    if not notion_url:
        return MCPHealthCheck(
            server_name="notion-http",
            status=MCPStatus.NOT_CONFIGURED,
            response_time_ms=None,
            error_message="NOTION_MCP_URL not set",
            tools_count=None
        )
    
    try:
        import time
        start_time = time.time()
        
        server = MCPServerStreamableHttp(
            params={
                "url": notion_url,
                "headers": {"Authorization": f"Bearer {notion_auth}"} if notion_auth else {},
            },
            name="notion-http-health",
            cache_tools_list=True,
        )
        
        await server.connect()
        tools = await server.list_tools()
        # HTTP server should support proper cleanup
        try:
            await server.disconnect()
        except AttributeError:
            pass  # Some versions may not have disconnect
        
        response_time = (time.time() - start_time) * 1000
        return MCPHealthCheck(
            server_name="notion-http",
            status=MCPStatus.HEALTHY,
            response_time_ms=response_time,
            error_message=None,
            tools_count=len(tools) if tools else 0
        )
        
    except Exception as e:
        return MCPHealthCheck(
            server_name="notion-http",
            status=MCPStatus.FAILED,
            response_time_ms=None,
            error_message=str(e),
            tools_count=None
        )


async def run_all_health_checks() -> List[MCPHealthCheck]:
    """
    Run health checks for all configured MCP servers.
    
    Returns:
        List of MCPHealthCheck results
    """
    checks = await asyncio.gather(
        check_exa_mcp_health(),
        check_notion_stdio_health(),
        check_notion_http_health(),
        return_exceptions=True
    )
    
    results = []
    for check in checks:
        if isinstance(check, Exception):
            results.append(MCPHealthCheck(
                server_name="unknown",
                status=MCPStatus.FAILED,
                response_time_ms=None,
                error_message=str(check),
                tools_count=None
            ))
        else:
            results.append(check)
    
    return results


def format_health_report(checks: List[MCPHealthCheck]) -> str:
    """
    Format health check results into a readable report.
    
    Args:
        checks: List of MCPHealthCheck results
        
    Returns:
        Formatted health report string
    """
    report = ["=== MCP Health Check Report ===\n"]
    
    healthy_count = sum(1 for c in checks if c.status == MCPStatus.HEALTHY)
    total_configured = sum(1 for c in checks if c.status != MCPStatus.NOT_CONFIGURED)
    
    report.append(f"Overall Status: {healthy_count}/{total_configured} servers healthy\n")
    
    for check in checks:
        status_emoji = {
            MCPStatus.HEALTHY: "✅",
            MCPStatus.DEGRADED: "⚠️",
            MCPStatus.FAILED: "❌",
            MCPStatus.NOT_CONFIGURED: "⚪"
        }
        
        report.append(f"{status_emoji[check.status]} {check.server_name}")
        
        if check.status == MCPStatus.NOT_CONFIGURED:
            report.append(f"   Status: Not configured ({check.error_message})")
        elif check.status == MCPStatus.HEALTHY:
            report.append(f"   Status: Healthy")
            if check.response_time_ms:
                report.append(f"   Response Time: {check.response_time_ms:.1f}ms")
            if check.tools_count is not None:
                report.append(f"   Tools Available: {check.tools_count}")
        else:
            report.append(f"   Status: {check.status.value}")
            if check.error_message:
                report.append(f"   Error: {check.error_message}")
        
        report.append("")
    
    return "\n".join(report)


def get_mcp_recommendations(checks: List[MCPHealthCheck]) -> List[str]:
    """
    Generate recommendations based on health check results.
    
    Args:
        checks: List of MCPHealthCheck results
        
    Returns:
        List of recommendation strings
    """
    recommendations = []
    
    for check in checks:
        if check.status == MCPStatus.NOT_CONFIGURED:
            if check.server_name == "exa-hosted":
                recommendations.append("Set EXA_API_KEY in .env to enable web search and crawling")
            elif "notion" in check.server_name:
                recommendations.append("Set NOTION_TOKEN in .env to enable Notion integration")
        
        elif check.status == MCPStatus.FAILED:
            if "notion-stdio" in check.server_name:
                recommendations.append("Check that Node.js is installed and npx command works")
            elif "notion-http" in check.server_name:
                recommendations.append("Verify NOTION_MCP_URL is accessible and auth token is correct")
            else:
                recommendations.append(f"Investigate {check.server_name} connection issues")
        
        elif check.status == MCPStatus.DEGRADED:
            recommendations.append(f"Review {check.server_name} configuration for potential issues")
    
    if not recommendations:
        recommendations.append("All configured MCP servers are healthy!")
    
    return recommendations
