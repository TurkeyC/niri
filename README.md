# niri（定制版）

<p align="center">
    <em>基于 <a href="https://github.com/niri-wm/niri">niri</a> 26.4.0 的定制滚动平铺 Wayland 合成器</em>
</p>

## 与原版的差异

本分支在原版 niri 基础上添加了以下功能：

### 新增：虚拟指针跳过 Overlay 层

> 用于 baspark 等点击穿透浮层场景，让虚拟指针事件透过 Overlay 层到达下方窗口。

- 虚拟指针（`VirtualPointerInputBackend`）的 `on_pointer_motion_absolute` 事件使用 `contents_under_skip_overlay()` 判定焦点的目标
- 新增 `Niri::contents_under_skip_overlay()`：与 `contents_under()` 逻辑相同，但跳过 `Layer::Overlay` 层

### 新增：`GetCursorPos` IPC 命令

> 用于鼠标点击特效等需要实时获取光标位置的场景。

- 新增 `niri msg get-cursor-pos` 命令，返回当前鼠标在逻辑坐标中的位置
- 支持两种输出格式：

```bash
niri msg get-cursor-pos            # 文本输出
# → Cursor position: 1920.5, 1080.0

niri msg get-cursor-pos --json     # JSON 输出
# → {"x":1920.5,"y":1080.0}
```

#### 实现说明

- **IPC 类型层**（`niri-ipc` crate）：新增 `Request::GetCursorPos`、`Response::CursorPos(CursorPos)`、`CursorPos { x: f64, y: f64 }` 结构体
- **CLI 层**（`src/cli.rs`）：新增 `Msg::GetCursorPos` 子命令
- **客户端层**（`src/ipc/client.rs`）：消息映射 + 文本/JSON 双格式输出
- **服务端层**（`src/ipc/server.rs`）：通过 `insert_idle` 模式在 compositor 事件循环中安全读取 `state.niri.seat.get_pointer().unwrap().current_location()`，返回 `Copy` 类型的坐标值，无借用冲突

---

## 构建与打包

### RPM 构建（Fedora）

本定制版已配置好 RPM 打包流程，可直接生成本地安装包。

#### 前置条件

```bash
sudo dnf install cargo-rpm-macros rpm-build rpmdevtools
```

#### 构建步骤

```bash
# 1. 初始化 RPM 构建目录
rpmdev-setuptree

# 2. 从当前 git HEAD 创建源码压缩包
git archive --prefix="niri-26.4.0/" \
  -o ~/rpmbuild/SOURCES/niri-26.4.0.tar.gz HEAD

# 3. 构建 RPM（包含 SRPM 和二进制包）
rpmbuild -ba --nocheck ~/rpmbuild/SPECS/niri.spec
```

#### 产物

| 文件 | 说明 |
|---|---|
| `~/rpmbuild/RPMS/x86_64/niri-26.4.0-*.fc43.x86_64.rpm` | 二进制 RPM（约 18 MB） |
| `~/rpmbuild/SRPMS/niri-26.4.0-*.fc43.src.rpm` | 源码 RPM |
| `~/rpmbuild/SPECS/niri.spec` | Spec 文件 |

#### 安装

```bash
sudo dnf install ~/rpmbuild/RPMS/x86_64/niri-26.4.0-*.fc43.x86_64.rpm
```

#### Spec 特点

- 基于 Fedora 官方 spec 简化，**无需 vendored 依赖**，直接在线构建
- RUSTFLAGS 保留完整 debuginfo 和 frame pointers（`-Cdebuginfo=2 -Ccodegen-units=1 -Cstrip=none -Cforce-frame-pointers=yes`），确保 panic 时给出完整回溯
- 版本号包含 git commit SHA：`26.4.0-1.dev20260603git<shortcommit>`
- panic 回溯验证：`niri panic` 可显示文件名和行号

### 手动构建（不打包）

```bash
cargo build --release
```

---

## 验证定制功能

安装后重启 niri，确认 `GetCursorPos` 命令可用：

```bash
# 检查版本
niri --version
# → niri 26.04 (8ed0da44d974c32c6877d2f4630c314da0717ecb)

# 测试光标位置查询
niri msg get-cursor-pos
```

---

## 原始项目说明

Niri 是一个滚动平铺 Wayland 合成器。窗口排列在无限向右延伸的列中，打开新窗口不会导致现有窗口调整大小。每个显示器拥有独立的窗口条和动态工作区。

更多信息请访问：[niri-wm/niri](https://github.com/niri-wm/niri)

### 功能特性

- 原生滚动平铺
- 动态工作区（类似 GNOME）
- 概览（Overview）模式
- 内置截图 UI
- 通过 xdg-desktop-portal-gnome 进行窗口/显示器屏幕捕获
- 触摸板和鼠标手势
- 标签页分组
- 可配置布局：间距、边框、窗口尺寸
- 渐变边框（支持 Oklab / Oklch）
- 窗口和 layer-shell 背景模糊
- 动画（支持自定义着色器）
- 配置热重载
- 屏幕阅读器支持

### 许可

GPL-3.0-or-later
