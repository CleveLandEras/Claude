"""读本机配置 代码/本机配置.ini。

密钥和接口地址只放这个文件，不写进代码和报告，不进 git，不进源码包。
模板是 本机配置.示例.ini，里面写清了要填什么。
"""
from __future__ import annotations

import configparser
import math
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

CODE_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = CODE_ROOT / "本机配置.ini"
TEMPLATE_NAME = "本机配置.示例.ini"

# 没测过的保守值，真阈值有密钥后用 autoreply.tune 定。偏高只会多转二讲，不会多误发。
DEFAULT_THRESHOLD = 0.95
DEFAULT_TIMEOUT_SECONDS = 10.0

_LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


class ConfigError(Exception):
    """配置读不到或写错了。信息里不带密钥的值。"""


@dataclass(frozen=True)
class ModelConfig:
    base_url: str
    model: str
    api_key: str = field(repr=False)  # 不进日志和报错
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS


def parse_threshold(value) -> float:
    """阈值要是 (0, 1] 里的数，否则抛 ValueError。"""
    threshold = float(value)
    if math.isnan(threshold) or not 0 < threshold <= 1:
        raise ValueError(f"阈值要在 0 和 1 之间（可以等于 1）：{value}")
    return threshold


def _read(path: Path) -> configparser.ConfigParser:
    # 不做 % 替换：密钥里可能有 %。utf-8-sig：Windows 记事本可能在开头加 BOM。
    parser = configparser.ConfigParser(interpolation=None)
    try:
        with open(path, encoding="utf-8-sig") as handle:
            parser.read_file(handle)
    except (UnicodeDecodeError, configparser.Error) as exc:
        raise ConfigError(f"{path} 写法有错，要用 UTF-8 保存、照模板的格式写（{type(exc).__name__}）") from None
    return parser


def _fill_hint(path: Path, what: str) -> str:
    return (
        f"{what}。请这样填：\n"
        f"  1. 把 {path.parent / TEMPLATE_NAME} 复制成 {path}（已有就直接打开）\n"
        "  2. 在 [model] 下填 api_key（必填）；base_url、model 已按 DeepSeek 写好，换服务商才改\n"
        "填好再跑。"
    )


def load_model_config(path: Path = CONFIG_PATH) -> ModelConfig:
    """读模型配置。读不到密钥就抛 ConfigError，绝不静默换成别的后端。"""
    path = Path(path)
    if not path.is_file():
        raise ConfigError(_fill_hint(path, f"读不到模型密钥：没有 {path}"))
    parser = _read(path)
    section = parser["model"] if parser.has_section("model") else {}

    api_key = section.get("api_key", "").strip()
    if not api_key or not api_key.isascii():
        raise ConfigError(_fill_hint(path, f"读不到模型密钥：{path} 的 [model] api_key 是空的或不是密钥"))

    base_url = section.get("base_url", "").strip().rstrip("/")
    parts = urlsplit(base_url)
    is_local = parts.scheme == "http" and parts.hostname in _LOCAL_HOSTS
    if not (parts.scheme == "https" and parts.hostname) and not is_local:
        raise ConfigError(f"{path} 的 [model] base_url 要是 https 开头的地址（本机调试可用 http://localhost）")

    model = section.get("model", "").strip()
    if not model:
        raise ConfigError(f"{path} 的 [model] model 是空的，要填模型名")

    raw_timeout = section.get("timeout_seconds", "").strip()
    try:
        timeout = float(raw_timeout) if raw_timeout else DEFAULT_TIMEOUT_SECONDS
    except ValueError:
        raise ConfigError(f"{path} 的 [model] timeout_seconds 要是秒数") from None
    if not timeout > 0:
        raise ConfigError(f"{path} 的 [model] timeout_seconds 要大于 0")

    return ModelConfig(base_url=base_url, model=model, api_key=api_key, timeout_seconds=timeout)


def load_threshold(path: Path = CONFIG_PATH) -> float:
    """读 [classify] threshold。没有配置文件或没写这项时用保守默认值。"""
    path = Path(path)
    if not path.is_file():
        return DEFAULT_THRESHOLD
    raw = _read(path).get("classify", "threshold", fallback="").strip()
    if not raw:
        return DEFAULT_THRESHOLD
    try:
        return parse_threshold(raw)
    except ValueError as exc:
        raise ConfigError(f"{path} 的 [classify] threshold 写错了：{exc}") from None
