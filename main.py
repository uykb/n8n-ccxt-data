# main.py

import asyncio
import logging
import os
from mcp.server.fastmcp import FastMCP

# 导入我们定义的 CCXT 工具
# 假设 ccxt_tools.py 与 main.py 在同一目录下
from ccxt_tools import get_exchange_info, fetch_ticker

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 MCP 服务实例
mcp = FastMCP("CCXT Data Service")

# 注册工具
@mcp.tool()
def get_exchange_info_wrapper(*args, **kwargs):
    return get_exchange_info(*args, **kwargs)

@mcp.tool()
def fetch_ticker_wrapper(*args, **kwargs):
    return fetch_ticker(*args, **kwargs)
    logger.info("工具注册完成")

# 设置服务器配置
port = int(os.environ.get("PORT", 8080))
mcp.settings.host = "0.0.0.0"
mcp.settings.port = port

if __name__ == "__main__":
    try:
        logger.info(f"MCP 服务正在启动，监听地址: {mcp.settings.host}:{mcp.settings.port}")
        mcp.run(transport="streamable-http")
    except KeyboardInterrupt:
        logger.info("MCP 服务被用户中断。")
    except Exception as e:
        logger.error(f"MCP 服务启动失败: {e}", exc_info=True)