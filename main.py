# main.py

import asyncio
import logging
import os
from mcp_python.mcp_server import MCPServer
from mcp_python.mcp_tool_manager import MCPToolManager

# 导入我们定义的 CCXT 工具
# 假设 ccxt_tools.py 与 main.py 在同一目录下
from ccxt_tools import get_exchange_info, fetch_ticker

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """主函数，用于启动 MCP 服务。"""
    logger.info("开始初始化 MCP 服务...")

    # 创建工具管理器
    tool_manager = MCPToolManager()

    # 注册工具
    # mcp-python 会自动从函数签名和装饰器中提取工具定义
    tool_manager.register_tool(get_exchange_info)
    tool_manager.register_tool(fetch_ticker)
    logger.info(f"已注册工具: {', '.join(tool_manager.get_tool_names())}")

    # 创建 MCP 服务实例
    # 默认情况下，服务会监听在 localhost:8080
    # 您可以通过 host 和 port 参数进行修改
    # Koyeb (and many other platforms) will set the PORT environment variable.
    # It's good practice to use it if available, otherwise default to 8080.
    # For host, '0.0.0.0' is correct for Docker to allow external connections.
    port = int(os.environ.get("PORT", 8080))
    server = MCPServer(tool_manager=tool_manager, host="0.0.0.0", port=port)

    logger.info(f"MCP 服务正在启动，监听地址: {server.host}:{server.port}")
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("MCP 服务被用户中断。")
    except Exception as e:
        logger.error(f"MCP 服务启动失败: {e}", exc_info=True)
    finally:
        if server.is_running():
            await server.stop()
        logger.info("MCP 服务已停止。")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"应用程序启动时发生严重错误: {e}", exc_info=True)