## 目标
- 创建 bcut 包并实现 `worksInfo.json` 的模型与 CRUD
- 为 main.py 增加 `works-*` 命令
- 保持现有功能可用，优先落地 works 路径

## 步骤
1. 新增 `bcut/models/works.py` 与 `bcut/services/works_repo.py`
2. 修改 `bcut_drafts.py` 使用新模块的 `load_works_info`
3. 扩展 `main.py`：`works-list/add/update/remove/find`
4. 编写测试 `tests/test_works_repo.py` 并运行验证