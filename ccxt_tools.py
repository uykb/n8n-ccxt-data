# ccxt_tools.py

from mcp_python.mcp_tool import mcp_tool
import ccxt

# 示例：获取交易所信息
# 您可以根据需要添加更多 CCXT 功能的封装

@mcp_tool(
    name="get_exchange_info",
    description="获取指定交易所的信息。",
    inputs=[
        {"name": "exchange_id", "type": "string", "description": "交易所的 ID (例如 'binance', 'coinbasepro')"},
        {"name": "apiKey", "type": "string", "description": "API 密钥 (可选)", "optional": True},
        {"name": "secret", "type": "string", "description": "API 密钥的私钥 (可选)", "optional": True},
        {"name": "password", "type": "string", "description": "API 密钥的口令 (可选, 某些交易所需要)", "optional": True},
        {"name": "sandboxMode", "type": "boolean", "description": "是否启用沙盒模式 (可选, 某些交易所支持)", "optional": True}
    ],
    outputs=[
        {"name": "exchange_info", "type": "object", "description": "交易所的详细信息"}
    ]
)
async def get_exchange_info(exchange_id: str, apiKey: str = None, secret: str = None, password: str = None, sandboxMode: bool = False):
    """获取指定交易所的信息。"""
    exchange = None
    try:
        exchange_class = getattr(ccxt, exchange_id)
        config = {}
        if apiKey:
            config['apiKey'] = apiKey
        if secret:
            config['secret'] = secret
        if password:
            config['password'] = password
        
        # CCXT 异步支持通常在实例化时处理，或者通过 async_support 模块
        # config['asyncio_loop'] = asyncio.get_event_loop() # 可能需要，取决于ccxt版本和用法
        config['enableRateLimit'] = True # 推荐开启速率限制

        if sandboxMode:
            # 尝试以通用方式启用沙盒模式，具体取决于交易所如何通过ccxt支持
            # 很多交易所通过 'test' URL 或特定的 'options' 来启用沙盒
            if hasattr(exchange_class, 'set_sandbox_mode'):
                # 如果交易所对象有 set_sandbox_mode 方法
                exchange = exchange_class(config)
                exchange.set_sandbox_mode(True)
            elif 'test' in exchange_class.urls: 
                config['urls'] = {'api': exchange_class.urls['test']}
                exchange = exchange_class(config)
            elif hasattr(exchange_class, 'sandbox') or (hasattr(exchange_class, 'options') and 'sandboxMode' in exchange_class.options) or (hasattr(exchange_class, 'options') and 'test' in exchange_class.options) :
                 # 某些交易所可能通过 options 支持
                 config['options'] = {'sandboxMode': True} # 或者 {'test': True}
                 exchange = exchange_class(config)
            else:
                # 如果没有明确的沙盒模式，正常实例化并记录一个警告或信息
                print(f"警告: 交易所 {exchange_id} 可能不支持通过此通用方式启用沙盒模式。")
                exchange = exchange_class(config)
        else:
            exchange = exchange_class(config)

        # ccxt 的 load_markets() 是同步的，如果需要在异步环境中使用，可能需要特殊处理
        # 或者在 MCP 服务启动时预加载一些常用交易所的市场信息
        # markets = await exchange.load_markets() # 这行在 ccxt 的异步模式下可能不同
        return {"exchange_info": exchange.describe()}
    except AttributeError:
        return {"error": f"交易所 '{exchange_id}' 未找到。"}
    except Exception as e:
        return {"error": f"获取交易所信息时发生错误: {str(e)}"}
    finally:
        if exchange and hasattr(exchange, 'close'):
            try:
                await exchange.close()
            except Exception as e:
                print(f"关闭交易所 {exchange_id} 连接时出错: {str(e)}")

@mcp_tool(
    name="fetch_ticker",
    description="获取指定交易对的最新市场行情。",
    inputs=[
        {"name": "exchange_id", "type": "string", "description": "交易所的 ID (例如 'binance')"},
        {"name": "symbol", "type": "string", "description": "交易对 (例如 'BTC/USDT')"},
        {"name": "apiKey", "type": "string", "description": "API 密钥 (可选)", "optional": True},
        {"name": "secret", "type": "string", "description": "API 密钥的私钥 (可选)", "optional": True},
        {"name": "password", "type": "string", "description": "API 密钥的口令 (可选, 某些交易所需要)", "optional": True},
        {"name": "sandboxMode", "type": "boolean", "description": "是否启用沙盒模式 (可选, 某些交易所支持)", "optional": True}
    ],
    outputs=[
        {"name": "ticker_data", "type": "object", "description": "交易对的行情数据"}
    ]
)
async def fetch_ticker(exchange_id: str, symbol: str, apiKey: str = None, secret: str = None, password: str = None, sandboxMode: bool = False):
    """获取指定交易对的最新市场行情。"""
    exchange = None
    try:
        exchange_class = getattr(ccxt, exchange_id)
        config = {}
        if apiKey:
            config['apiKey'] = apiKey
        if secret:
            config['secret'] = secret
        if password:
            config['password'] = password

        config['enableRateLimit'] = True

        if sandboxMode:
            if hasattr(exchange_class, 'set_sandbox_mode'):
                exchange = exchange_class(config)
                exchange.set_sandbox_mode(True)
            elif 'test' in exchange_class.urls:
                config['urls'] = {'api': exchange_class.urls['test']}
                exchange = exchange_class(config)
            elif hasattr(exchange_class, 'sandbox') or (hasattr(exchange_class, 'options') and 'sandboxMode' in exchange_class.options) or (hasattr(exchange_class, 'options') and 'test' in exchange_class.options) :
                 config['options'] = {'sandboxMode': True}
                 exchange = exchange_class(config)
            else:
                print(f"警告: 交易所 {exchange_id} 可能不支持通过此通用方式启用沙盒模式。")
                exchange = exchange_class(config)
        else:
            exchange = exchange_class(config)

        if exchange.has['fetchTicker']:
            ticker = await exchange.fetch_ticker(symbol)
            return {"ticker_data": ticker}
        else:
            return {"error": f"交易所 '{exchange_id}' 不支持 fetchTicker 功能。"}
    except ccxt.NetworkError as e:
        return {"error": f"网络错误: {str(e)}"}
    except ccxt.ExchangeError as e:
        return {"error": f"交易所错误: {str(e)}"}
    except Exception as e:
        return {"error": f"获取行情时发生未知错误: {str(e)}"}
    finally:
        if exchange and hasattr(exchange, 'close'):
            try:
                await exchange.close()
            except Exception as e:
                print(f"关闭交易所 {exchange_id} 连接时出错: {str(e)}")

# 您可以在此处添加更多工具，例如：
# - create_order (创建订单)
# - fetch_balance (获取账户余额)
# - fetch_ohlcv (获取K线数据)

@mcp_tool(
    name="create_order",
    description="在指定的交易所创建订单。",
    inputs=[
        {"name": "exchange_id", "type": "string", "description": "交易所的 ID (例如 'binance')"},
        {"name": "symbol", "type": "string", "description": "交易对 (例如 'BTC/USDT')"},
        {"name": "type", "type": "string", "description": "订单类型 (例如 'market', 'limit')"},
        {"name": "side", "type": "string", "description": "订单方向 ('buy' 或 'sell')"},
        {"name": "amount", "type": "number", "description": "订单数量"},
        {"name": "price", "type": "number", "description": "订单价格 (市价单则为 None)", "optional": True},
        {"name": "params", "type": "object", "description": "额外的参数 (例如止损价 'stopPrice')", "optional": True},
        {"name": "apiKey", "type": "string", "description": "API 密钥 (可选)", "optional": True},
        {"name": "secret", "type": "string", "description": "API 密钥的私钥 (可选)", "optional": True},
        {"name": "password", "type": "string", "description": "API 密钥的口令 (可选, 某些交易所需要)", "optional": True},
        {"name": "sandboxMode", "type": "boolean", "description": "是否启用沙盒模式 (可选, 某些交易所支持)", "optional": True}
    ],
    outputs=[
        {"name": "order_info", "type": "object", "description": "创建的订单信息"}
    ]
)
async def create_order(exchange_id: str, symbol: str, type: str, side: str, amount: float, price: float = None, params: dict = {}, apiKey: str = None, secret: str = None, password: str = None, sandboxMode: bool = False):
    """在指定的交易所创建订单。"""
    exchange = None
    try:
        exchange_class = getattr(ccxt, exchange_id)
        config = {}
        if apiKey:
            config['apiKey'] = apiKey
        if secret:
            config['secret'] = secret
        if password:
            config['password'] = password
        config['enableRateLimit'] = True

        if sandboxMode:
            if hasattr(exchange_class, 'set_sandbox_mode'):
                exchange = exchange_class(config)
                exchange.set_sandbox_mode(True)
            elif 'test' in exchange_class.urls:
                config['urls'] = {'api': exchange_class.urls['test']}
                exchange = exchange_class(config)
            elif hasattr(exchange_class, 'sandbox') or (hasattr(exchange_class, 'options') and 'sandboxMode' in exchange_class.options) or (hasattr(exchange_class, 'options') and 'test' in exchange_class.options) :
                 config['options'] = {'sandboxMode': True}
                 exchange = exchange_class(config)
            else:
                print(f"警告: 交易所 {exchange_id} 可能不支持通过此通用方式启用沙盒模式。")
                exchange = exchange_class(config)
        else:
            exchange = exchange_class(config)

        if exchange.has['createOrder']:
            order = await exchange.create_order(symbol, type, side, amount, price, params)
            return {"order_info": order}
        else:
            return {"error": f"交易所 '{exchange_id}' 不支持 createOrder 功能。"}
    except ccxt.NetworkError as e:
        return {"error": f"网络错误: {str(e)}"}
    except ccxt.ExchangeError as e:
        return {"error": f"交易所错误: {str(e)}"}
    except Exception as e:
        return {"error": f"创建订单时发生未知错误: {str(e)}"}
    finally:
        if exchange and hasattr(exchange, 'close'):
            try:
                await exchange.close()
            except Exception as e:
                print(f"关闭交易所 {exchange_id} 连接时出错: {str(e)}")

@mcp_tool(
    name="fetch_balance",
    description="获取指定交易所的账户余额。",
    inputs=[
        {"name": "exchange_id", "type": "string", "description": "交易所的 ID (例如 'binance')"},
        {"name": "params", "type": "object", "description": "额外的参数", "optional": True},
        {"name": "apiKey", "type": "string", "description": "API 密钥 (必须)"},
        {"name": "secret", "type": "string", "description": "API 密钥的私钥 (必须)"},
        {"name": "password", "type": "string", "description": "API 密钥的口令 (可选, 某些交易所需要)", "optional": True},
        {"name": "sandboxMode", "type": "boolean", "description": "是否启用沙盒模式 (可选, 某些交易所支持)", "optional": True}
    ],
    outputs=[
        {"name": "balance_info", "type": "object", "description": "账户余额信息"}
    ]
)
async def fetch_balance(exchange_id: str, params: dict = {}, apiKey: str = None, secret: str = None, password: str = None, sandboxMode: bool = False):
    """获取指定交易所的账户余额。"""
    exchange = None
    if not apiKey or not secret:
        return {"error": "API Key 和 Secret 是必须的。"}
    try:
        exchange_class = getattr(ccxt, exchange_id)
        config = {'apiKey': apiKey, 'secret': secret}
        if password:
            config['password'] = password
        config['enableRateLimit'] = True

        if sandboxMode:
            if hasattr(exchange_class, 'set_sandbox_mode'):
                exchange = exchange_class(config)
                exchange.set_sandbox_mode(True)
            elif 'test' in exchange_class.urls:
                config['urls'] = {'api': exchange_class.urls['test']}
                exchange = exchange_class(config)
            elif hasattr(exchange_class, 'sandbox') or (hasattr(exchange_class, 'options') and 'sandboxMode' in exchange_class.options) or (hasattr(exchange_class, 'options') and 'test' in exchange_class.options) :
                 config['options'] = {'sandboxMode': True}
                 exchange = exchange_class(config)
            else:
                print(f"警告: 交易所 {exchange_id} 可能不支持通过此通用方式启用沙盒模式。")
                exchange = exchange_class(config)
        else:
            exchange = exchange_class(config)

        if exchange.has['fetchBalance']:
            balance = await exchange.fetch_balance(params)
            return {"balance_info": balance}
        else:
            return {"error": f"交易所 '{exchange_id}' 不支持 fetchBalance 功能。"}
    except ccxt.NetworkError as e:
        return {"error": f"网络错误: {str(e)}"}
    except ccxt.ExchangeError as e:
        return {"error": f"交易所错误: {str(e)}"}
    except Exception as e:
        return {"error": f"获取余额时发生未知错误: {str(e)}"}
    finally:
        if exchange and hasattr(exchange, 'close'):
            try:
                await exchange.close()
            except Exception as e:
                print(f"关闭交易所 {exchange_id} 连接时出错: {str(e)}")

@mcp_tool(
    name="fetch_ohlcv",
    description="获取指定交易对的K线数据 (OHLCV)。",
    inputs=[
        {"name": "exchange_id", "type": "string", "description": "交易所的 ID (例如 'binance')"},
        {"name": "symbol", "type": "string", "description": "交易对 (例如 'BTC/USDT')"},
        {"name": "timeframe", "type": "string", "description": "时间周期 (例如 '1m', '5m', '1h', '1d')", "default": "1h"},
        {"name": "since", "type": "integer", "description": "起始时间戳 (毫秒, 可选)", "optional": True},
        {"name": "limit", "type": "integer", "description": "返回的数据点数量 (可选, 交易所可能有限制)", "optional": True},
        {"name": "params", "type": "object", "description": "额外的参数", "optional": True},
        {"name": "apiKey", "type": "string", "description": "API 密钥 (可选)", "optional": True},
        {"name": "secret", "type": "string", "description": "API 密钥的私钥 (可选)", "optional": True},
        {"name": "password", "type": "string", "description": "API 密钥的口令 (可选, 某些交易所需要)", "optional": True},
        {"name": "sandboxMode", "type": "boolean", "description": "是否启用沙盒模式 (可选, 某些交易所支持)", "optional": True}
    ],
    outputs=[
        {"name": "ohlcv_data", "type": "array", "description": "K线数据列表，每个元素是 [timestamp, open, high, low, close, volume]"}
    ]
)
async def fetch_ohlcv(exchange_id: str, symbol: str, timeframe: str = '1h', since: int = None, limit: int = None, params: dict = {}, apiKey: str = None, secret: str = None, password: str = None, sandboxMode: bool = False):
    """获取指定交易对的K线数据 (OHLCV)。"""
    exchange = None
    try:
        exchange_class = getattr(ccxt, exchange_id)
        config = {}
        if apiKey:
            config['apiKey'] = apiKey
        if secret:
            config['secret'] = secret
        if password:
            config['password'] = password
        config['enableRateLimit'] = True

        if sandboxMode:
            if hasattr(exchange_class, 'set_sandbox_mode'):
                exchange = exchange_class(config)
                exchange.set_sandbox_mode(True)
            elif 'test' in exchange_class.urls:
                config['urls'] = {'api': exchange_class.urls['test']}
                exchange = exchange_class(config)
            elif hasattr(exchange_class, 'sandbox') or (hasattr(exchange_class, 'options') and 'sandboxMode' in exchange_class.options) or (hasattr(exchange_class, 'options') and 'test' in exchange_class.options) :
                 config['options'] = {'sandboxMode': True}
                 exchange = exchange_class(config)
            else:
                print(f"警告: 交易所 {exchange_id} 可能不支持通过此通用方式启用沙盒模式。")
                exchange = exchange_class(config)
        else:
            exchange = exchange_class(config)

        if exchange.has['fetchOHLCV']:
            ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, since, limit, params)
            return {"ohlcv_data": ohlcv}
        else:
            return {"error": f"交易所 '{exchange_id}' 不支持 fetchOHLCV 功能。"}
    except ccxt.NetworkError as e:
        return {"error": f"网络错误: {str(e)}"}
    except ccxt.ExchangeError as e:
        return {"error": f"交易所错误: {str(e)}"}
    except Exception as e:
        return {"error": f"获取K线数据时发生未知错误: {str(e)}"}
    finally:
        if exchange and hasattr(exchange, 'close'):
            try:
                await exchange.close()
            except Exception as e:
                print(f"关闭交易所 {exchange_id} 连接时出错: {str(e)}")


# 注意: CCXT 的异步支持可能需要特定版本的库或特定的用法。
# 上述 fetch_ticker 示例假设了某种形式的异步调用，具体实现需参考 CCXT 文档。
# 如果 CCXT 的操作是同步阻塞的，在异步 MCP 服务中调用它们时，
# 需要使用 asyncio.to_thread (Python 3.9+) 或 loop.run_in_executor 来避免阻塞事件循环。