# 现有四川项目：复用索引与适配陷阱

这是 2026-11-03 从已跑通的 `V:/GIS/Sichuan` 提炼的项目知识。文件路径和软件版本是定位线索，执行时以当前文件与实际环境为准；技能本身不携带 GIS 大数据或地区引擎副本。

## 先看这些文件

- `docs/DUJIANGYAN_VOXEL_V01_GUIDE.md`：已完成体素流程、命令、成果与实测限制。
- `projects/blender/dujiangyan_voxel_v01/config.json`、`palettes.json`、`display_outline.geojson`：已冻结示例配置，不能作为新地区的正式轮廓。
- `docs/CHENGDU_V01_GUIDE.md`、`docs/SICHUAN_V02_GUIDE.md`：自然影像／平滑地形路径。
- `docs/web_asset_contract.md`、`docs/DOCKER.md`、`docs/LOCAL_WORKSPACE.md`：当前网页合同、打包和本机约定。
- `projects/web/public/data/areas.json`：已注册地区，新增时保持原有记录。

## 数据与环境

| 用途 | 当前路径 |
|---|---|
| 约 30 米高程 | `data/sichuan-copernicus-glo30/sichuan_glo30_clipped.tif` |
| RGB 影像 | `data/Sentinel2_2025Q3_30m/sichuan_2025Q3_RGB_texture_30m.tif` |
| 水系、地名等矢量 | `data/sichuan-map-support/vectors/sichuan_map_layers.gpkg` |
| 四川省界 | `data/sichuan-copernicus-glo30/sichuan_boundary_osm.geojson` |
| GIS Python | `work/geo-venv/Scripts/python.exe` |
| Blender 线索 | `C:/Program Files/Blender Foundation/Blender 5.2/blender.exe` |
| glTF 工具依赖 | `work/model_tools/node_modules` |
| 网页 | `projects/web` |

既有米制投影为 `+proj=lcc +lat_1=27 +lat_2=33 +lat_0=30 +lon_0=103 +datum=WGS84 +units=m +no_defs`。在该项目继续使用可保持坐标合同；新地区是否适用应检查。读取 GPKG 时沿用只读方式，SQLite 可用 `mode=ro&immutable=1`；先检查真实图层和字段，不猜表结构。

此前硬件为 RTX 3050 Laptop 4GB。Python 3.14、Blender 5.2、Node 22 是该次已验证环境，不表示必须升级／降级到这些版本。QGIS 可用于叠加检查，核心批处理可走 Python／Blender CLI，不必依赖 GUI 操作。

## 脚本复用分级

| 文件 | 如何复用 |
|---|---|
| `scripts/voxel_surface.py` | 外露高度场壳、硬法线、矩形合并可复用；**`coarsen_grid` 内仍写死 20 米量化，改台阶必须连同接口和调用修正**。 |
| `scripts/map_profile.py` | 地区输出路由可复用；`recipe_sha256` 仍为旧平滑地图配方，体素有自己的 recipe 逻辑。 |
| `scripts/package_gallery_v02.py --profile ...` | 按 profile 生成图片清单、缩略图与 DZI，先核对输入字段和本次宽度。 |
| `scripts/unpack_web_assets.py` | 资源包哈希／路径验证和解包器可复用。 |
| `scripts/smoke_web.py --url ...` | 现有站点可继续做回归；独立新站需调整其“保留旧地区”断言。 |
| `scripts/prepare_dujiangyan_voxel.py --config ...` | 地区制作示例；检查固定源路径、选名、水面修正、配色及格距，不能只换 bbox。 |
| `scripts/dujiangyan_geometry.py` | **资产目录写死**，水面偏移、装饰、角色有项目约定；先参数化或建新的地区入口。 |
| `scripts/build_dujiangyan_voxel.py`、`compose_dujiangyan_voxel.py`、`run_dujiangyan_voxel.py` | 配置、相机、标注和串行出图示例；检查硬编码 1.5 倍、60 米、20 米、字体、配方文件列表和宽度约定。 |
| `scripts/export_dujiangyan_voxel_web.mjs` | **WORK／ASSETS／输出／config 路径写死**，还有 30／60／20 米元数据；参数化后检查实际解码结果。 |
| `scripts/dujiangyan_preflight.py` | 从固定计划文档解析 JSON，并固定输入／旧资产筛选；不是通用新地区初始化器。 |
| `scripts/verify_dujiangyan_voxel.py` | 固定地区路径、维度、计数与数值；提炼可重复计算的不变量，不照抄该区域期望值。 |
| `scripts/package_dujiangyan_voxel.py`、`verify_dujiangyan_docker.py` | 固定候选输出、容器名、端口和标签；新地区使用新的名字，别覆盖旧包或停止旧容器。 |

适配时先用 `rg` 找旧地区 ID、路径和数值的实际用途；不要机械替换所有 `20`／`60`，其中可能是色板索引或角度。可选策略是给公共模块增加完整配置接口，或保留稳定旧入口并新增地区入口；以可验证的小改动为准。

## 新地区初始化

本技能的 `scripts/init_landform_project.py` 只需 Python 标准库。示例（脚本使用绝对路径；`--dry-run` 不创建文件）：

```powershell
python -X utf8 C:/Users/K1ndred/.codex/skills/terrain-diorama/scripts/init_landform_project.py --workspace V:/GIS/Sichuan --slug dawashan-jinkou --title '大瓦山与金口大峡谷' --landform plateau-canyon --style voxel --dry-run
```

去掉 `--dry-run` 才创建 `projects/blender/dawashan_jinkou_v01/config.draft.json`。未传的 bbox、格距、台阶和倍数保持待定；可在验证后传 `--bbox W S E N --cell-m N --height-step-m N --exaggeration N`。取景数字必须来自数据检查，示例不预置这些地区的坐标。

草稿的字段组织与当前 profile 接近，但 `sources`、`landform`、状态字段属于规划记录，且 `views` 为空；它不是已经适配好的地区执行器输入。先补齐并根据目标脚本 schema 形成 `config.json`，再运行 GIS 与渲染。

约定目录：`work/<run_id>` 放派生数组与检查，`renders/<run_id>` 放图片，`projects/blender/<run_id>` 放配置和场景，`projects/web/public/{data,models,gallery}/<area>` 放网页资产，`deliverables/<area>-<version>` 放新交付。已有目标则检查并复用或明确升版本，不通过覆盖来初始化。

## 只作为效果与预算参考的已验证结果

都江堰使用自然扇形、60 米基础格距、20 米台阶、静态默认 1.5 倍、3 个相机；桌面／移动约 27 万／12 万三角形，顶点色且无纹理。边缘和核心保持 60 米，移动内部为 120 米。这些值描述该区域，不是新峡谷／崖壁的默认配方。

都江堰水库采用受源水体约束的局部水面／水床修正，不能把这个库面高程或做法直接套给大渡河等流动河道。全省影像缺失约 0.53%，该次都江堰实际约 1.86%，必须按新取景重新计算。

桌面曾测得约 52 FPS，但测试期间自动降到移动档；不能写成桌面细档稳定 52 FPS。移动布局完成模拟，真实手机 GPU 与双指触控未验证。

都江堰最后交付是本地候选；此前 `web-assets.lock.json` 仍指向已发布旧资源，新资源使用独立候选 lock。继续操作时读取当前文件状态，不凭这份历史说明修改发布锁或推送远端。
