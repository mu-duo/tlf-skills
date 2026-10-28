# 仓库原型

spine 并不总是 `main` -> handler -> service。追踪之前先识别原型；错误的原型会产出一条看似合理、却教错心智模型的调用链。

## 快速识别

| 目录树中的信号 | 原型 |
| --- | --- |
| `Dockerfile` + `routes/` / `handlers/` + 一个 server bootstrap | HTTP service |
| `cmd/<name>/main.go`、`argparse`、`click`、`cobra`、`bin/` | CLI |
| `src/index.ts` 导出函数，没有 `main`，带已发布的 `package.json` / `pyproject.toml` | Library / SDK |
| `consumers/`、`subscribers/`、`handlers/` 以事件名为键，有 broker 配置 | Event-driven / queue |
| Registry、`plugins/`、`providers/`、DI 容器装配、`@Inject` | Plugin / DI container |
| 多个 `packages/` 或 `apps/`，各自带清单 | Monorepo |
| `dags/`、`jobs/`、`stages/`、`transform/`、schema 文件 | Data pipeline |
| `.proto`、`.graphql`、schema 优先的目录、`generated/`、`*_pb2.py` | Codegen-heavy |

## HTTP service

**入口点：** server bootstrap（`main.go`、`app.py`、`server.ts`）、路由注册、中间件链、健康检查。

**一条链：** 请求进入 -> 路由匹配 -> 中间件 -> handler -> service/use-case -> repository/DB -> 响应形状。

**什么会让自上而下的阅读失效：**

- 中间件全局注册且远离路由。即使 handler 从未提及，调用链也包含它。
- 装饰器或框架魔法（`@app.route`、自动装配）隐藏了分发这一跳。
- 一个仓库里有多个 server（公开 API、admin、worker），各有独立的 bootstrap。
- 前面有网关或代理重写路径。

先追中间件列表再看 handler。大多数 "为什么这个字段不见了" 的 bug 都在那里。

## CLI

**入口点：** `main` 加上命令树。真正的入口点是用户运行的子命令，而不是那个二进制。

**一条链：** argv 解析 -> 命令分发 -> 选项校验 -> 核心调用 -> 输出/退出码。

**什么会让自上而下的阅读失效：**

- 框架的命令树由许多文件拼装而成。读 `main` 看到的是注册，不是行为。
- 全局 flag 或配置文件在命令执行之前被合并。
- 共享的 `RunE` / `run()` 辅助函数隐藏了真正的工作。

挑最接近 `focus` 的子命令。从参数解析开始的 CLI "spine" 往往很无聊；说出来，然后跳到命令主体。

## Library / SDK

**入口点：** 公开表面 —— `index` 导出、`__init__.py`、`lib.rs` re-exports、`package.json` 中的 `exports`。

**一条链：** 公开调用 -> 编排层 -> 内部核心 -> 副作用或返回值。

**什么会让自上而下的阅读失效：**

- 公开 API 只是薄包装；真正的复杂性在三层之下。
- 版本化目录（`v1/`、`v2/`），只有一个是在用的。
- feature flag 选择不同的实现。
- README 记录的是比代码导出更旧的 API。

从用户会调用的某个导出符号开始，而不是从目录树开始。

## Event-driven / queue

**入口点：** 生产者位置（publish/emit）、消费者注册、broker 的 topic 或 queue 名称、schema 定义。

**一条链：** 触发 -> 发布 -> broker 一跳 -> 消费者 -> handler -> 副作用。这是一条中间有缺口的链；broker 不是代码。

**什么会让自上而下的阅读失效：**

- 没有单一调用栈。用 "find references" 追踪会在 publish 调用处断掉。
- topic 名是字符串，常常动态构造或来自配置。对字面量和配置键都做 grep。
- 重试、死信队列和幂等包装会改变实际顺序。
- 一个 topic 有多个消费者；用户只关心其中一个。

这里绝不要猜 spine。问是哪个事件、哪个消费者，并说明除非能看到配置，否则 broker 那一跳是 `inferred`。

## Plugin / DI container

**入口点：** 容器 bootstrap 和注册列表。行为在运行时装配。

**一条链：** bootstrap -> 注册 -> 解析/注入 -> plugin hook -> 效果。

**什么会让自上而下的阅读失效：**

- 调用 `new Foo()` 什么也找不到；实例由容器构造。
- 接口实现由配置、profile 或环境选择。
- hook 通过名字或注册表查找来调用，而不是直接调用。
- 装饰器或宏生成装配代码。

先追注册，再看解析出的实现。如果绑定依赖配置，就把两种可能的实现都记下来，并把当前生效的那个标为 `inferred`。

## Monorepo

**入口点：** 工作区清单（`pnpm-workspace.yaml`、`turbo.json`、`go.work`、`Cargo.toml` workspace），然后某个包的入口点。

**一条链：** 一个包的边界 -> 内部调用 -> 依赖包 -> 效果。这条链跨越包边界，而这正是重点。

**什么会让自上而下的阅读失效：**

- 多个应用名字有重叠；顶层 README 只描述了其中一个。
- 共享包被所有东西使用（`common/`、`shared/`、`core/`），所以 "find references" 返回一堆噪音。
- 构建工具会重写 import 或做路径别名。
- 两个包里有重复实现，其中一个是废弃的。

把 map 限定到 spine 上的包。覆盖所有内容的 monorepo map 只是目录，不是心智模型。

## Data pipeline

**入口点：** DAG 定义、调度器注册、job 入口脚本、阶段列表。

**一条链：** 读取源 -> 变换阶段 1..n -> 校验 -> 写入 sink。

**什么会让自上而下的阅读失效：**

- pipeline 是声明出来的，不是被调用的；顺序来自 DAG 或阶段列表。
- schema 才是真正的契约，而它们位于代码之外。
- 回填和重处理路径与正常运行不同。
- 幂等和分区逻辑改变了 "一条记录" 的含义。

追踪一条记录穿过各阶段。记录每个边界上的 schema；漂移就发生在那。

## Codegen-heavy

**入口点：** schema（`.proto`、`.graphql`、IDL）或生成器配置。生成的文件是输出，不是源。

**一条链：** schema 定义 -> 生成器 -> 生成类型 -> 手写消费者。

**什么会让自上而下的阅读失效：**

- 生成代码被提交进仓库，看起来像手写的；读它学不到持久的东西。
- 生成器添加了 schema 中从未出现的行为（校验、序列化）。
- 重新生成发生在构建步骤里，所以提交的输出可能已过期。
- 字段编号、wire format 或保留名称承载着代码中看不见的含义。

锚定到 schema，而不是生成输出。在 map 中显式标出生成路径，以免有人去改它们。
