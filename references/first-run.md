# 首次使用与缺少绘图环境时的处理

第一次执行新图、重绘或数据到图的演示，先记下用户的数据、目标、指定应用、已有工程和已选色卡。在承载应用的电脑检查环境。仅浏览色卡可双击 HTML；学习参考图、阅读说明和审查现成图稿按各自需要调用工具。

## 先找到主机上的应用

在 skill 目录运行。选择原任务的路线，默认 `rstudio`，命令行演示用 `rscript`，原生 Origin 项目用 `origin`。Windows 可以使用 `py -3`。已有 RStudio Server/Workbench 会话时直接在该会话做下节检查。

```sh
python3 scripts/check_environment.py --route rstudio --json
```

没有 Python 时可以先用系统工具只读探测。macOS/Linux 运行 `command -v Rscript` 和 `Rscript --version`；Windows 在 PowerShell 运行 `Get-Command Rscript -ErrorAction SilentlyContinue`，也可在“已安装的应用”查 R 和 RStudio。macOS 查看“应用程序”里的 RStudio；已有 GUI 时直接在 Console 读取 `R.version.string` 和 `R.home()`。Windows 的 R 可能已安装在 Program Files 但没加入 PATH。

Python 检查器使用标准库。未装 Python 的电脑可在已有 RStudio 的 Console 直接做下一节检查。两者都缺且只需运行 R 示例时，先按下表补 R 和 RStudio，再打开试用包内的示例工程。使用 Python 脚手架、CSV 检查等功能时，再从 [Python 下载页](https://www.python.org/downloads/) 安装 Python 3.10 或更高版本。

`needs_setup` 指出缺少的程序或运行时错误，显式路线返回码为 2。`check_project_session` 表示可以进入工程会话检查，`host_missing_packages` 只反映 Rscript 的默认库。已有安装在自定义位置时用 `--rscript`、`--rstudio` 或 `--origin` 指定实际可执行文件。原有无路线的 `--json` 命令继续输出主机清单。

## 补齐实际缺项

助手按当前用户对安装的授权执行。用户已经要求安装或配置时，直接补齐缺项、复检并接回制图。仅请求作图且首次需要改动用户系统时，一次说清需安装的程序、R 包、安装目录和用途；需要管理员认证时让用户直接在系统提示框完成。保留同机的其他 R 和用户项目。

主机只读检查发现缺项并已获安装授权后，在 skill 根目录运行下面的命令。首次没有 Python 时使用下表的原生方式。选定的工程要求特定 R 版本时，使用对应版本的安装器；包管理器通常提供其当前版本。

```sh
python3 scripts/check_environment.py --route rstudio --install-missing --json
```

该选项仅用于 `rstudio` 或 `rscript`。它先检查现有运行时，按缺项调用已安装的包管理器，再重新检测。没有传 `--install-missing` 时只读取环境。macOS 使用 Homebrew；Windows 使用 WinGet 的 `RProject.R` 与 `Posit.RStudio` 精确 ID；Linux 查询已经配置的 apt 或 dnf 仓库，存在对应候选包时安装。普通 Linux 用户会得到需要系统权限的具体命令。未检测到包管理器或候选包时，报告提供官方安装入口。安装器可能需要用户在系统窗口认证或接受协议；退出失败时保留命令与返回码，请在交互终端完成后复检。复检显示 `check_project_session` 后继续原工程的 R 包检查。

| 环境 | 缺少 R 时 | 缺少 RStudio Desktop 时 |
|---|---|---|
| macOS | 按 arm64 或 Intel 从 [CRAN](https://cran.r-project.org/bin/macosx/) 选择系统支持的安装器。已使用 Homebrew 时可执行 `brew install --cask r-app`。 | 运行适配当前 macOS 的 [Posit 安装器](https://docs.posit.co/ide/user/download.html)，或执行 `brew install --cask rstudio`。 |
| Windows | 从 [CRAN](https://cran.r-project.org/bin/windows/base/) 安装。重新打开终端后检查实际 Rscript 路径。 | 从 [Posit](https://docs.posit.co/ide/user/download.html) 选择受支持的 Windows 安装器。安装后在 RStudio Console 核对 `R.home()`。 |
| Linux | 按 `/etc/os-release` 和 CPU 选择 [CRAN 对应发行版](https://cran.r-project.org/bin/linux/)；已配好仓库的 Debian/Ubuntu 可安装 `r-base`。 | 按 [Posit 下载页](https://docs.posit.co/ide/user/download.html) 匹配系统、架构和安装包。已经有 RStudio Server 的机构，使用其实际项目会话。 |

当前项目要求精确复现时，按 `renv.lock` 的 R 版本选择可共存的运行时。缺少编译器、系统头文件或网络访问时，读取首个失败包和安装器诊断，只处理影响此包的具体原因。Origin 在实际 Windows 主机或访客系统中确认安装、可用许可、启动和保存路径，再继续原生工程。宿主机未找到可执行文件时检查已连接的访客系统。[Origin 路线](origin-handoff.md)

## 在实际工程内检查与修复

打开目标工程的 RStudio Console，核对 `getwd()`、`R.version.string`、`.libPaths()`。新建工程使用脚手架或试用工程。启用 renv 的工程首次打开时，启动器可能下载 renv 并建立项目库，应将这部分纳入依赖安装说明。新建脚手架和试用工程均自带下面的检查脚本。在已有的其他工程中，可从 skill 安装目录用绝对路径加载同一脚本。Windows 的 R 字符串可以使用正斜杠。

```r
source("scripts/check_r_project.R")
env <- check_figure_environment()
env$ready
```

检查器读取当前工程 DESCRIPTION 的 Imports/Depends，核对实际包能否加载、声明版本约束及已激活 renv 锁定的直接依赖版本。小脚本或自有工程可以只传该图需要的包，例如 `check_figure_environment(packages = c("ggplot2", "ragg"))`。字体、输出设备和特殊系统依赖按图核验。RStudio 使用的 R 版本与终端不同，以当前工程的 R 会话为准。

有缺项并已授权时，在同一工程、带相同的 `packages` 参数运行 `check_figure_environment(install = TRUE)`。激活且带锁文件的 renv 工程按锁文件修复相关包及其依赖；普通 R 工程使用个人 R 库和已配置的软件源。包加载失败或版本仍不一致时保留诊断，检查网络、架构及库权限，按需要重启**同一工程**后再执行只读检查。[renv 项目恢复](https://rstudio.github.io/renv/reference/restore.html)

`ready` 为真后，在原任务选定的应用执行第一个需要实际绘图的步骤，检查生成的预览文件。在脚手架演示中运行 `source("R/run_example.R")`；在用户工程中执行它自己的脚本和数据。保留先前的色卡、五点契约和已有输入。安装等待期间继续可独立完成的数据核对，随后回到首个依赖绘图环境的步骤。记录实际使用的 R/GUI 和最后导出，确保成品与请求一致。
