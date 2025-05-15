# CCXT 工具 MCP 服务

本项目提供了一个基于 MCP (My Custom Protocol) 的服务，封装了 CCXT 库的功能，允许用户通过 MCP 调用与加密货币交易所进行交互。

## 功能

目前已实现的 MCP 工具包括：

- `get_exchange_info`: 获取指定交易所的详细信息。
- `fetch_ticker`: 获取指定交易对的最新市场行情。
- `create_order`: 在指定的交易所创建订单。
- `fetch_balance`: 获取指定交易所的账户余额。
- `fetch_ohlcv`: 获取指定交易对的K线数据 (OHLCV)。

## 项目结构

```
.
├── .dockerignore       # 指定 Docker 构建时忽略的文件
├── Dockerfile          # 用于构建 Docker 镜像的配置文件
├── ccxt_tools.py       # 包含 MCP 工具的实现
├── main.py             # MCP 服务主程序 (假设)
└── requirements.txt    # Python 依赖项
```

## Docker 构建与运行

### 前提条件

- 已安装 Docker

### 构建 Docker 镜像

在项目根目录下执行以下命令：

```bash
docker build -t ccxt-mcp-service .
```

### 运行 Docker 容器

运行以下命令启动服务，并将容器的 8080 端口映射到主机的 8080 端口：

```bash
docker run -p 8080:8080 ccxt-mcp-service
```

服务将在 `http://localhost:8080` (或其他在 `main.py` 中配置的地址和端口) 上可用。

## 部署到 Koyeb

您可以将此服务部署到 Koyeb 平台。以下是推荐的步骤：

1.  **准备您的代码仓库**：
    *   确保您的项目（包含 `Dockerfile`, `requirements.txt`, `main.py`, `ccxt_tools.py`）已推送到 GitHub (或其他 Koyeb 支持的代码托管平台) 仓库。

2.  **在 Koyeb 上创建服务**：
    *   登录到您的 Koyeb 控制面板。
    *   点击 "Create Service"。
    *   选择 "GitHub" 作为部署方式，并授权 Koyeb 访问您的仓库。
    *   选择包含此项目的仓库和分支。

3.  **配置服务**：
    *   **Builder**: 选择 "Dockerfile"。Koyeb 将使用项目根目录下的 `Dockerfile` 来构建镜像。
    *   **Run command**: 通常可以留空，因为 `Dockerfile` 中的 `CMD` 指令 (`CMD ["python", "main.py"]`) 会被使用。如果需要覆盖，可以在此指定。
    *   **Port**: Koyeb 会自动检测 `Dockerfile` 中 `EXPOSE` 的端口 (8080)。如果您的 `main.py` 配置为使用 `PORT` 环境变量，Koyeb 会自动设置此环境变量，您的应用将使用它。确保您的应用监听在 `0.0.0.0` 上。
    *   **Service Type**: 选择 "Web Service"。
    *   **Regions**: 选择您希望部署的区域。
    *   **Instance Size**: 根据您的需求选择合适的实例大小。

4.  **环境变量 (可选)**：
    *   如果您的 MCP 工具或 CCXT 配置需要 API 密钥或其他敏感信息，您可以在 Koyeb 服务的 "Environment variables" 部分安全地配置它们。您的应用程序可以通过 `os.environ.get("YOUR_VARIABLE_NAME")` 来访问这些变量。

5.  **健康检查 (推荐)**：
    *   Koyeb 允许配置健康检查。您可以设置一个 HTTP 健康检查路径，例如 `/health` (您需要在您的应用中实现这个端点，使其返回 200 OK)。
    *   或者，如果您的应用在启动后立即可用，Koyeb 的默认 TCP 健康检查通常也足够。

6.  **部署**：
    *   点击 "Deploy"。
    *   Koyeb 将拉取您的代码，构建 Docker 镜像，并部署服务。
    *   部署成功后，Koyeb 会提供一个公共 URL (例如 `your-app-name.koyeb.app`)，您可以通过该 URL 访问您的 MCP 服务。

7.  **查看日志和监控**：
    *   您可以在 Koyeb 控制面板中查看应用的实时日志和监控指标。

## MCP 服务使用指南

您可以通过 MCP 客户端调用已注册的工具。以下是如何调用已实现工具的示例：

### 1. 获取交易所信息 (`get_exchange_info`)

**请求示例：**

假设 MCP 服务运行在 `http://localhost:8080/mcp`。

**基础请求：**
```json
{
  "tool_name": "get_exchange_info",
  "inputs": {
    "exchange_id": "binance"
  }
}
```

**使用 API 密钥和启用沙盒模式的请求：**
```json
{
  "tool_name": "get_exchange_info",
  "inputs": {
    "exchange_id": "kucoin",
    "apiKey": "YOUR_API_KEY",
    "secret": "YOUR_API_SECRET",
    "password": "YOUR_API_PASSWORD", // 如果交易所需要
    "sandboxMode": true // 如果交易所支持沙盒模式
  }
}
```

**预期响应 (成功时)：**

```json
{
  "outputs": {
    "exchange_info": {
      "id": "binance",
      "name": "Binance",
      "countries": "KY", // 示例数据，实际内容会更详细
      // ... 更多交易所信息
    }
  }
}
```

**预期响应 (交易所不存在时)：**

```json
{
  "outputs": {
    "error": "交易所 'your_invalid_exchange_id' 未找到。"
  }
}
```

### 2. 获取交易对行情 (`fetch_ticker`)

此工具现在也支持通过 `apiKey`, `secret`, `password`, 和 `sandboxMode` 参数来配置交易所实例。用法与 `get_exchange_info` 类似。

**请求示例：**

**基础请求：**
```json
{
  "tool_name": "fetch_ticker",
  "inputs": {
    "exchange_id": "binance",
    "symbol": "BTC/USDT"
  }
}
```

**使用 API 密钥的请求：**
```json
{
  "tool_name": "fetch_ticker",
  "inputs": {
    "exchange_id": "kraken",
    "symbol": "ETH/USD",
    "apiKey": "YOUR_KRAKEN_API_KEY",
    "secret": "YOUR_KRAKEN_API_SECRET"
  }
}
```

**预期响应 (成功时)：**

```json
{
  "outputs": {
    "ticker_data": {
      "symbol": "BTC/USDT",
      "timestamp": 1678886400000, // 示例时间戳
      "datetime": "2023-03-15T12:00:00.000Z", // 示例日期时间
      "high": 25000.0,
      "low": 24000.0,
      "bid": 24500.0,
      // ... 更多行情数据
    }
  }
}
```

**预期响应 (交易所不支持该功能或发生错误时)：**

```json
{
  "outputs": {
    "error": "交易所 'some_exchange' 不支持 fetchTicker 功能。"
    // 或其他错误信息，如网络错误、交易所错误等
  }
}
```

## 未来扩展

可以根据需要继续添加更多 CCXT 功能的封装。

请参考 `ccxt_tools.py` 文件添加新的 MCP 工具。