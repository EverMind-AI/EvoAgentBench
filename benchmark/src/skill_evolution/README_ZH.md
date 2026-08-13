# 自进化评测

公开版本只支持两条路径：

- **Baseline**：通过 `src/run.py` 运行 benchmark，不加载任何进化状态。
- **EverOS**：使用公开 EverOS 服务从训练轨迹提取可复用 skill，并在测试评测时注入检索到的 skill。

本仓库不包含第三方方法适配和实验结果。

## 流程

1. 运行 `src/run.py --split train` 收集训练 session。
2. 运行 `evermemos/extract_skills.py` 将 session 发送给 EverOS。
3. 运行 `evermemos/eval_with_skills.py --split test` 进行 skill 注入评测。
4. 运行 `src/run.py --split test` 获得匹配的 baseline。

配置和命令详见 [evermemos/README_ZH.md](evermemos/README_ZH.md)。
论文正式划分详见 [data/splits/README.md](../../data/splits/README.md)。
