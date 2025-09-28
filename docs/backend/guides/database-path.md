SQLite 数据库路径规范与运维指南

目标
- 统一后端 SQLite 数据库存放位置，避免因工作目录不同生成多个 .db 文件。
- 提供覆盖环境变量与验证步骤，减少排障时间。

默认规范
- 默认路径：仓库根目录下的 `auto_test.db`（绝对路径）。
- 后端启动时会将数据库路径标准化为绝对路径，并在日志中打印：`数据库连接成功: <绝对路径>`。
- 如未显式设置 `DATABASE_PATH`，系统固定使用仓库根目录的 `auto_test.db`。

如何覆盖路径
- 优先使用环境变量 `DATABASE_PATH` 指定文件位置：
  - 支持 `~`（家目录展开）。
  - 若提供相对路径，将自动转换为“仓库根目录”下的绝对路径。
- 若设置了 `DATABASE_URL` 且为 SQLite（`sqlite:///...`），它将与 `DATABASE_PATH` 保持一致。
- 示例（macOS/Linux）：
  - `DATABASE_PATH=/Users/yourname/Projects/auto-test/auto_test.db`
  - `export DATABASE_PATH=$(pwd)/auto_test.db`（在仓库根目录执行）

强约束（避免再次出现多个数据库文件）
- 不要在不同子目录内以相对路径启动后端（例如在 `backend/` 或 `backend/src/` 目录运行 uvicorn）。
- 若必须从子目录启动，依然会被标准化为仓库根目录下的绝对路径，不会新建额外 .db 文件。

验证步骤
1) 查看启动日志：应看到
   - `数据库连接成功: /absolute/path/to/auto_test.db`
   - 如有缺失列，日志会显示自动迁移补丁执行信息。
2) 直接验证表结构：
   - `sqlite3 /absolute/path/to/auto_test.db "PRAGMA table_info(systems);"`
   - 关键列应包含：`category`（systems）、`path`（modules）。

常见问题与处理
- 症状：接口报错 `no such column: category`
  - 原因：使用了旧库或路径不一致导致的库文件混淆。
  - 处理：
    1. 确认后端日志中的数据库绝对路径；
    2. 使用上方验证步骤确认表结构；
    3. 若仓库内存在多个 `*.db`，仅保留根目录 `auto_test.db`，其余归档到 `backups/db_archives/`。

附录
- 环境变量示例（.env）：
  - `# DATABASE_URL=mysql+pymysql://username:password@localhost:3306/autotest`（使用 MySQL 时）
  - `DATABASE_PATH=/absolute/path/auto_test.db`（使用 SQLite 时，推荐）