---
name: lark-sheets
version: 1.1.0
description: "飞书电子表格：创建和操作电子表格。创建表格并写入表头和数据、读取和写入单元格、追加行数据、在已知电子表格中查找单元格内容、导出表格文件。当用户需要创建电子表格、批量读写数据、在已知表格中查找内容、导出或下载表格时使用。若用户是想按名称或关键词搜索云空间里的表格文件，请改用 lark-doc 的 docs +search 先定位资源。"
metadata:
  requires:
    bins: ["lark-cli"]
  cliHelp: "lark-cli sheets --help"
---

# sheets (v3)

**CRITICAL — 开始前 MUST 先用 Read 工具读取 [`../lark-shared/SKILL.md`](../lark-shared/SKILL.md)，其中包含认证、权限处理**

## 快速决策
- 按标题或关键词找云空间里的表格文件，先用 `lark-cli docs +search`。
- `docs +search` 会直接返回 `SHEET` 结果，不要把它误解成只能搜文档 / Wiki。
- 已知 spreadsheet URL / token 后，再进入 `sheets +info`、`sheets +read`、`sheets +find` 等对象内部操作。

## 核心概念

### 文档类型与 Token

飞书开放平台中，不同类型的文档有不同的 URL 格式和 Token 处理方式。在进行文档操作（如添加评论、下载文件等）时，必须先获取正确的 `file_token`。

### 文档 URL 格式与 Token 处理

| URL 格式 | 示例                                                      | Token 类型 | 处理方式 |
|----------|---------------------------------------------------------|-----------|----------|
| `/docx/` | `https://example.larksuite.com/docx/doxcnxxxxxxxxx`    | `file_token` | URL 路径中的 token 直接作为 `file_token` 使用 |
| `/doc/` | `https://example.larksuite.com/doc/doccnxxxxxxxxx`     | `file_token` | URL 路径中的 token 直接作为 `file_token` 使用 |
| `/wiki/` | `https://example.larksuite.com/wiki/wikcnxxxxxxxxx`    | `wiki_token` | ⚠️ **不能直接使用**，需要先查询获取真实的 `obj_token` |
| `/sheets/` | `https://example.larksuite.com/sheets/shtcnxxxxxxxxx`  | `file_token` | URL 路径中的 token 直接作为 `file_token` 使用 |
| `/drive/folder/` | `https://example.larksuite.com/drive/folder/fldcnxxxx` | `folder_token` | URL 路径中的 token 作为文件夹 token 使用 |

### Wiki 链接特殊处理（关键！）

知识库链接（`/wiki/TOKEN`）背后可能是云文档、电子表格、多维表格等不同类型的文档。**不能直接假设 URL 中的 token 就是 file_token**，必须先查询实际类型和真实 token。

#### 处理流程

1. **使用 `wiki.spaces.get_node` 查询节点信息**
   ```bash
   lark-cli wiki spaces get_node --params '{"token":"wiki_token"}'
   ```

2. **从返回结果中提取关键信息**
   - `node.obj_type`：文档类型（docx/doc/sheet/bitable/slides/file/mindnote）
   - `node.obj_token`：**真实的文档 token**（用于后续操作）
   - `node.title`：文档标题

3. **根据 `obj_type` 使用对应的 API**

   | obj_type | 说明 | 使用的 API |
   |----------|------|-----------|
   | `docx` | 新版云文档 | `drive file.comments.*`、`docx.*` |
   | `doc` | 旧版云文档 | `drive file.comments.*` |
   | `sheet` | 电子表格 | `sheets.*` |
   | `bitable` | 多维表格 | `bitable.*` |
   | `slides` | 幻灯片 | `drive.*` |
   | `file` | 文件 | `drive.*` |
   | `mindnote` | 思维导图 | `drive.*` |

#### 查询示例

```bash
# 查询 wiki 节点
lark-cli wiki spaces get_node --params '{"token":"wiki_token"}'
```

返回结果示例：
```json
{
   "node": {
      "obj_type": "docx",
      "obj_token": "xxxx",
      "title": "标题",
      "node_type": "origin",
      "space_id": "12345678910"
   }
}
```

### 资源关系

```
Wiki Space (知识空间)
└── Wiki Node (知识库节点)
    ├── obj_type: docx (新版文档)
    │   └── obj_token (真实文档 token)
    ├── obj_type: doc (旧版文档)
    │   └── obj_token (真实文档 token)
    ├── obj_type: sheet (电子表格)
    │   └── obj_token (真实文档 token)
    ├── obj_type: bitable (多维表格)
    │   └── obj_token (真实文档 token)
    └── obj_type: file/slides/mindnote
        └── obj_token (真实文档 token)

Drive Folder (云空间文件夹)
└── File (文件/文档)
    └── file_token (直接使用)
```

**操作流程（重要）：**

1. **create** — 创建筛选
   - 用于首次创建筛选
   - ⚠️ range 必须覆盖所有需要筛选的列（如 B1:E200）
   - 如果已有筛选存在，再用 create 会覆盖整个筛选

2. **update** — 更新筛选
   - 用于在已有筛选上添加/更新指定列的条件
   - 只需指定 col 和 condition，不需要 range

3. **delete** — 删除筛选

4. **get** — 获取筛选状态

**多列筛选示例：**

创建媒体名称(B列)和情感分析(E列)的双重筛选：

```bash
# 1. 删除现有筛选（如有）
lark-cli sheets spreadsheet.sheet.filters delete \
  --params '{"spreadsheet_token":"<spreadsheet_token>","sheet_id":"<sheet_id>"}'

# 2. 创建第一个筛选，range 覆盖所有要筛选的列
lark-cli sheets spreadsheet.sheet.filters create \
  --params '{"spreadsheet_token":"<spreadsheet_token>","sheet_id":"<sheet_id>"}' \
  --data '{"col":"B","condition":{"expected":["xx"],"filter_type":"multiValue"},"range":"<sheet_id>!B1:E200"}'

# 3. 添加第二个筛选条件
lark-cli sheets spreadsheet.sheet.filters update \
  --params '{"spreadsheet_token":"<spreadsheet_token>","sheet_id":"<sheet_id>"}' \
  --data '{"col":"E","condition":{"expected":["xx"],"filter_type":"multiValue"}}'
```

**常见错误：**
- `Wrong Filter Value`：筛选已存在，需要先 delete 再 create
- `Excess Limit`：update 时重复添加同一列条件

### 单元格数据类型

接受二维数组的 shortcut（`+write`/`+append` 的 `--values`、`+create` 的 `--data`）中，每个单元格值支持以下类型。**公式、带文本链接、@人、@文档、下拉列表必须使用对象格式**，直接传字符串会被当作纯文本存储。

| 类型 | 写入格式 | 示例 |
|------|---------|------|
| 字符串 | `"文本"` | `"hello"` |
| 数字 | `数字` | `123`、`3.14` |
| 日期 | `数字`（自 1899-12-30 起的天数，需先设单元格日期格式） | `42101` |
| 链接（纯 URL） | `"URL 字符串"` | `"https://example.com"` |
| 链接（带文本） | `{"type":"url","text":"显示文本","link":"URL"}` | `{"type":"url","text":"飞书","link":"https://www.feishu.cn"}` |
| 邮箱 | `"邮箱字符串"` | `"user@example.com"` |
| **公式** | `{"type":"formula","text":"=公式"}` | `{"type":"formula","text":"=SUM(A1:A10)"}` |
| @人 | `{"type":"mention","text":"标识","textType":"email\|openId\|unionId","notify":false}` | `{"type":"mention","text":"user@example.com","textType":"email","notify":false}`（notify 可选，默认 false；仅在用户明确要求通知时设为 true） |
| @文档 | `{"type":"mention","textType":"fileToken","text":"token","objType":"类型"}` | `{"type":"mention","textType":"fileToken","text":"shtXXX","objType":"sheet"}` |
| 下拉列表 | `{"type":"multipleValue","values":[值1,值2]}` | `{"type":"multipleValue","values":["选项A","选项B"]}` |

**写入公式示例**：

```bash
# ✅ 正确：使用对象格式
lark-cli sheets +write --url "URL" --sheet-id "sheetId" --range "C6" \
  --values '[[{"type":"formula","text":"=SUM(C2:C5)"}]]'

# ❌ 错误：直接传字符串，会被存为纯文本
lark-cli sheets +write --url "URL" --sheet-id "sheetId" --range "C6" \
  --values '[["=SUM(C2:C5)"]]'
```

> **公式语法参考**：涉及 ARRAYFORMULA、原生数组函数、MAP/LAMBDA、日期差、Excel 公式改写等飞书特有规则时，先阅读 [`references/lark-sheets-formula.md`](references/lark-sheets-formula.md)。

**限制**：
- 公式支持 IMPORTRANGE 跨表引用（最多 5 层嵌套、每个工作表最多 100 个引用）
- @人仅支持同租户用户，单次最多 50 人
- 下拉列表需**先配置下拉选项**，否则 `multipleValue` 写入会变成纯文本。配置方法见 [`references/lark-sheets-set-dropdown.md`](references/lark-sheets-set-dropdown.md)。值中的字符串不能包含逗号

## Shortcuts（推荐优先使用）

Shortcut 是对常用操作的高级封装（`lark-cli sheets +<verb> [flags]`）。有 Shortcut 的操作优先使用。

| Shortcut | 说明 |
|----------|------|
| [`+info`](references/lark-sheets-info.md) | 查看电子表格和工作表信息 |
| [`+read`](references/lark-sheets-read.md) | 读取电子表格单元格值 |
| [`+write`](references/lark-sheets-write.md) | 写入电子表格单元格（覆盖模式） |
| [`+write-image`](references/lark-sheets-write-image.md) | 将图片写入电子表格单元格 |
| [`+append`](references/lark-sheets-append.md) | 向电子表格追加行数据 |
| [`+find`](references/lark-sheets-find.md) | 在电子表格中查找单元格 |
| [`+create`](references/lark-sheets-create.md) | 创建电子表格（可选表头行和初始数据） |
| [`+export`](references/lark-sheets-export.md) | 导出电子表格（异步任务轮询 + 可选下载） |
| [`+merge-cells`](references/lark-sheets-merge-cells.md) | 合并电子表格中的单元格 |
| [`+unmerge-cells`](references/lark-sheets-unmerge-cells.md) | 取消合并（拆分）电子表格中的单元格 |
| [`+replace`](references/lark-sheets-replace.md) | 查找并替换单元格值 |
| [`+set-style`](references/lark-sheets-set-style.md) | 设置范围的单元格样式 |
| [`+batch-set-style`](references/lark-sheets-batch-set-style.md) | 批量设置多个范围的单元格样式 |
| [`+add-dimension`](references/lark-sheets-add-dimension.md) | 在工作表末尾添加行或列 |
| [`+insert-dimension`](references/lark-sheets-insert-dimension.md) | 在指定位置插入行或列 |
| [`+update-dimension`](references/lark-sheets-update-dimension.md) | 更新行或列属性（可见性、大小） |
| [`+move-dimension`](references/lark-sheets-move-dimension.md) | 将行或列移动到新位置 |
| [`+delete-dimension`](references/lark-sheets-delete-dimension.md) | 删除行或列 |
| [`+create-filter-view`](references/lark-sheets-create-filter-view.md) | 创建筛选视图 |
| [`+update-filter-view`](references/lark-sheets-update-filter-view.md) | 更新筛选视图 |
| [`+list-filter-views`](references/lark-sheets-list-filter-views.md) | 列出工作表中的所有筛选视图 |
| [`+get-filter-view`](references/lark-sheets-get-filter-view.md) | 通过 ID 获取筛选视图 |
| [`+delete-filter-view`](references/lark-sheets-delete-filter-view.md) | 删除筛选视图 |
| [`+create-filter-view-condition`](references/lark-sheets-create-filter-view-condition.md) | 在筛选视图上创建筛选条件 |
| [`+update-filter-view-condition`](references/lark-sheets-update-filter-view-condition.md) | 更新筛选条件 |
| [`+list-filter-view-conditions`](references/lark-sheets-list-filter-view-conditions.md) | 列出筛选视图的所有筛选条件 |
| [`+get-filter-view-condition`](references/lark-sheets-get-filter-view-condition.md) | 通过列获取筛选条件 |
| [`+delete-filter-view-condition`](references/lark-sheets-delete-filter-view-condition.md) | 删除筛选条件 |

### 下拉列表

| Shortcut | 说明 |
|----------|------|
| [`+set-dropdown`](references/lark-sheets-set-dropdown.md) | 设置下拉列表（`multipleValue` 写入的前置步骤） |
| [`+update-dropdown`](references/lark-sheets-update-dropdown.md) | 更新下拉列表选项 |
| [`+get-dropdown`](references/lark-sheets-get-dropdown.md) | 查询下拉列表配置 |
| [`+delete-dropdown`](references/lark-sheets-delete-dropdown.md) | 删除下拉列表 |

### 浮动图片

| Shortcut | 说明 |
|----------|------|
| [`+media-upload`](references/lark-sheets-media-upload.md) | 上传本地图片素材，返回 `file_token`（供 `+create-float-image` 使用；>20MB 自动分片） |
| [`+create-float-image`](references/lark-sheets-create-float-image.md) | 创建浮动图片 |
| [`+update-float-image`](references/lark-sheets-update-float-image.md) | 更新浮动图片属性 |
| [`+get-float-image`](references/lark-sheets-get-float-image.md) | 获取浮动图片 |
| [`+list-float-images`](references/lark-sheets-list-float-images.md) | 查询所有浮动图片 |
| [`+delete-float-image`](references/lark-sheets-delete-float-image.md) | 删除浮动图片 |

> 浮动图片相关的读接口只返回元数据（含 `float_image_token`），**不包含图片字节**。要读取图片内容，用 token 调 `lark-cli docs +media-preview --token "<float_image_token>" --output ./image.png`。

## API Resources

```bash
lark-cli schema sheets.<resource>.<method>   # 调用 API 前必须先查看参数结构
lark-cli sheets <resource> <method> [flags] # 调用 API
```

> **重要**：使用原生 API 时，必须先运行 `schema` 查看 `--data` / `--params` 参数结构，不要猜测字段格式。

### spreadsheets

  - `create` — 创建电子表格
  - `get` — 获取电子表格信息
  - `patch` — 修改电子表格属性

### spreadsheet.sheet.filters

  - `create` — 创建筛选
  - `delete` — 删除筛选
  - `get` — 获取筛选
  - `update` — 更新筛选

### spreadsheet.sheets

  - `find` — 查找单元格

### spreadsheet.sheet.float_images

  - `create` — 创建浮动图片
  - `patch` — 更新浮动图片
  - `get` — 获取浮动图片
  - `query` — 查询所有浮动图片
  - `delete` — 删除浮动图片

## 权限表

| 方法 | 所需 scope |
|------|-----------|
| `spreadsheets.create` | `sheets:spreadsheet:create` |
| `spreadsheets.get` | `sheets:spreadsheet.meta:read` |
| `spreadsheets.patch` | `sheets:spreadsheet.meta:write_only` |
| `spreadsheet.sheet.filters.create` | `sheets:spreadsheet:write_only` |
| `spreadsheet.sheet.filters.delete` | `sheets:spreadsheet:write_only` |
| `spreadsheet.sheet.filters.get` | `sheets:spreadsheet:read` |
| `spreadsheet.sheet.filters.update` | `sheets:spreadsheet:write_only` |
| `spreadsheet.sheets.find` | `sheets:spreadsheet:read` |
| `spreadsheet.sheet.float_images.create` | `sheets:spreadsheet:write_only` |
| `spreadsheet.sheet.float_images.patch` | `sheets:spreadsheet:write_only` |
| `spreadsheet.sheet.float_images.get` | `sheets:spreadsheet:read` |
| `spreadsheet.sheet.float_images.query` | `sheets:spreadsheet:read` |
| `spreadsheet.sheet.float_images.delete` | `sheets:spreadsheet:write_only` |

