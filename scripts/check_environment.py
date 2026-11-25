#!/usr/bin/env python3
"""Inspect the selected figure route. Opt in to install its missing desktop software."""
import argparse
import codecs
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DESCRIPTION = ROOT / "assets/r-template/DESCRIPTION"
RSTUDIO_DOWNLOAD = "https://docs.posit.co/ide/user/download.html"
R_DOWNLOADS = {
    "Windows": "https://cran.r-project.org/bin/windows/base/",
    "Darwin": "https://cran.r-project.org/bin/macosx/",
    "Linux": "https://cran.r-project.org/bin/linux/",
}


def find_program(name, override, system):
    """Prefer an explicit path, then PATH, then conventional installation locations."""
    if override:
        candidates = [Path(override).expanduser()]
    else:
        on_path = shutil.which(name)
        candidates = [Path(on_path)] if on_path else []
        if name == "Rscript" and os.environ.get("R_HOME"):
            candidates.append(Path(os.environ["R_HOME"]) / "bin" /
                              ("Rscript.exe" if system == "Windows" else "Rscript"))
        if system == "Darwin":
            if name == "Rscript":
                candidates.extend(map(Path, ["/Library/Frameworks/R.framework/Resources/bin/Rscript",
                                             "/opt/homebrew/bin/Rscript", "/usr/local/bin/Rscript"]))
            elif name == "rstudio":
                for base in (Path("/Applications"), Path.home() / "Applications"):
                    candidates.append(base / "RStudio.app/Contents/MacOS/RStudio")
        elif system == "Windows":
            patterns = {
                "Rscript": ["R/R-*/bin/Rscript.exe", "R/R-*/bin/x64/Rscript.exe"],
                "rstudio": ["RStudio/rstudio.exe", "RStudio/bin/rstudio.exe"],
                "Origin64": ["OriginLab/Origin*/Origin64.exe"],
            }
            for key in ("ProgramFiles", "LOCALAPPDATA", "ProgramFiles(x86)"):
                if os.environ.get(key):
                    root = Path(os.environ[key])
                    for base in (root, root / "Programs"):
                        for pattern in patterns.get(name, []):
                            candidates.extend(sorted(base.glob(pattern), reverse=True))
        elif name == "rstudio" and system == "Linux":
            candidates.append(Path("/usr/lib/rstudio/rstudio"))
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate.absolute())
    return None


def probe_r(executable):
    # --vanilla avoids running any project profile or bootstrapping renv during discovery.
    code = """
    deps <- strsplit(read.dcf(commandArgs(TRUE)[1], fields = "Imports")[1], ",")[[1]]
    cat(R.version.string, "\\n")
    for (p in trimws(deps)) cat(p, requireNamespace(p, quietly = TRUE), "\\n")
    cat("probe-complete\\n")
    """
    try:
        proc = subprocess.run([executable, "--vanilla", "-e", code, str(DESCRIPTION)],
                              capture_output=True, text=True, errors="replace", timeout=90)
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"r_probe_error": str(error), "r_probe_exit": None}
    lines = proc.stdout.strip().splitlines()
    if proc.returncode or not lines or lines[-1] != "probe-complete":
        return {"r_probe_exit": proc.returncode,
                "r_probe_error": proc.stderr.strip() or "Incomplete R runtime probe"}
    return {"r_probe_exit": 0, "r_package_report": "\n".join(lines[:-1]),
            "host_missing_packages": re.findall(r"^(\S+) FALSE\s*$", proc.stdout, re.M)}


def inspect_route(route, rscript=None, rstudio=None, origin=None):
    system = platform.system()
    report = {"platform": system, "architecture": platform.machine(), "python": platform.python_version(),
              "route": route, "setup_actions": [], "status": "ready"}
    if route == "palette":
        return report
    actions = report["setup_actions"]
    if route == "origin":
        exe = find_program("Origin64", origin, system) if system == "Windows" else None
        report["origin"] = exe
        if exe:
            report["status"] = "verify_gui"
            actions.append("打开现有 Origin 工程，核对许可、源工作簿与导出。")
        else:
            report["status"] = "needs_setup"
            actions.append("在承载 Origin 的 Windows 系统或虚拟机中检查现有安装与许可。可用 --origin 指定可执行文件。")
        return report

    report["Rscript"] = find_program("Rscript", rscript, system)
    report["node"] = shutil.which("node")
    report["pymupdf_available"] = importlib.util.find_spec("fitz") is not None
    report["rstudio"] = find_program("rstudio", rstudio, system)
    report["origin"] = "not inspected; optional licensed GUI route"
    report["status"] = "check_project_session"
    if report["Rscript"]:
        report.update(probe_r(report["Rscript"]))
        if "r_probe_error" in report:
            report["status"] = "needs_setup"
            actions.append("按 r_probe_error 排查运行时，或用 --rscript 指定正确的可执行文件后复检。")
    else:
        report["status"] = "needs_setup"
        url = R_DOWNLOADS.get(system, "https://cran.r-project.org/")
        actions.append(f"安装与系统和架构匹配的 R，或用 --rscript 指定已装路径。{url}")
    if route == "rstudio" and not report["rstudio"]:
        report["status"] = "needs_setup"
        actions.append(f"确认桌面版或现有 RStudio Server 会话；缺少桌面版时使用 Posit 安装器。{RSTUDIO_DOWNLOAD}")
    if report["status"] == "check_project_session":
        actions.append("在实际制图项目的 R 会话运行 scripts/check_r_project.R 中的 check_figure_environment()。")
    return report


def setup_command(system, component):
    """Return a manager command only for a package offered by the configured source."""
    if system == "Darwin":
        if shutil.which("brew"):
            cask = "r-app" if component == "R" else "rstudio"
            return ["brew", "install", "--cask", cask]
    elif system == "Windows":
        if shutil.which("winget"):
            package = "RProject.R" if component == "R" else "Posit.RStudio"
            return ["winget", "install", "--exact", "--id", package, "--source", "winget"]
    elif system == "Linux":
        if shutil.which("apt-get") and shutil.which("apt-cache"):
            package = "r-base" if component == "R" else "rstudio"
            query = ["apt-cache", "policy", package]
            install = ["apt-get", "install", "-y", package]
        elif shutil.which("dnf"):
            package = "R" if component == "R" else "rstudio"
            query = ["dnf", "-q", "repoquery", "--available", "--qf", "%{name}", package]
            install = ["dnf", "install", "-y", package]
        else:
            return None
        lookup = subprocess.run(query, capture_output=True, text=True, errors="replace",
                                env=dict(os.environ, LC_ALL="C"), timeout=90)
        if not lookup.returncode:
            if query[0] == "apt-cache":
                candidate = re.search(r"^[ \t]*Candidate:[ \t]*(\S+)", lookup.stdout, re.M)
                if candidate and candidate[1] != "(none)":
                    return install
            elif package in lookup.stdout.splitlines():
                return install
    return None


def install_missing(report, overrides):
    attempts = []
    components = {"R": report["Rscript"]}
    if report["route"] == "rstudio":
        components["RStudio"] = report["rstudio"]
    for component, installed in components.items():
        if installed:
            continue
        record = {"component": component}
        attempts.append(record)
        try:
            if overrides.get(component):
                record["action"] = "核对显式指定的可执行文件路径，然后复检。"
                break
            command = setup_command(report["platform"], component)
            if not command:
                record["action"] = ("使用匹配的官方安装器：" +
                                    (R_DOWNLOADS.get(report["platform"], "https://cran.r-project.org/")
                                     if component == "R" else RSTUDIO_DOWNLOAD))
                break
            record["command"] = command
            if report["platform"] == "Linux" and os.geteuid() != 0:
                record["action"] = "在系统终端授权执行：sudo " + " ".join(command)
                break
            # Keep stdout machine-readable. Package managers can show native prompts.
            result = subprocess.run(command, stdout=sys.stderr)
            record["exit"] = result.returncode
            if result.returncode:
                record["action"] = "查看安装器诊断；如需系统认证，在交互终端执行上述命令后复检。"
                break
        except (OSError, subprocess.TimeoutExpired) as error:
            record["error"] = str(error)
            break
    return attempts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="JSON is also the default output")
    parser.add_argument("--route", choices=("rstudio", "rscript", "origin", "palette"))
    parser.add_argument("--rscript", help="explicit Rscript executable")
    parser.add_argument("--rstudio", help="explicit RStudio Desktop executable")
    parser.add_argument("--origin", help="explicit Origin executable on Windows")
    parser.add_argument("--install-missing", action="store_true",
                        help="install missing R/RStudio using an existing system package manager")
    args = parser.parse_args()
    if args.install_missing and args.route not in ("rstudio", "rscript"):
        parser.error("--install-missing requires --route rstudio or --route rscript")
    report = inspect_route(args.route or "inventory", args.rscript, args.rstudio, args.origin)
    if args.install_missing:
        attempts = install_missing(report, {"R": args.rscript, "RStudio": args.rstudio})
        if attempts:
            report = inspect_route(args.route, args.rscript, args.rstudio, args.origin)
        report["install_attempts"] = attempts
        if any(step.get("exit") or "error" in step for step in attempts):
            report["status"] = "needs_setup"
    # Make redirected reports valid UTF-8 JSON even when the locale is a legacy code page.
    encoding = getattr(sys.stdout, "encoding", None) or "ascii"
    ascii_only = codecs.lookup(encoding).name != "utf-8"
    print(json.dumps(report, indent=2, ensure_ascii=ascii_only))
    # Preserve the inventory command's successful exit on machines without R.
    return 2 if args.route and report["status"] == "needs_setup" else 0


if __name__ == "__main__":
    raise SystemExit(main())
