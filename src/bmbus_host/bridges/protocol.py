from __future__ import annotations

import json
import uuid
from typing import Any, Callable


BRIDGE_PROTOCOL_VERSION = "bmbus-bridge/1"


class BridgeProtocolError(RuntimeError):
    pass


def send_bridge_request(
    write_line: Callable[[str], None],
    read_line: Callable[[], str],
    command: str,
    **params: Any,
) -> dict[str, Any]:
    request_id = uuid.uuid4().hex
    payload = {"request_id": request_id, "command": command, **params}
    write_line(json.dumps(payload, ensure_ascii=False))

    raw_line = read_line().strip()
    if not raw_line:
        raise BridgeProtocolError("桥接端未返回数据。")

    try:
        response = json.loads(raw_line)
    except json.JSONDecodeError as exc:
        raise BridgeProtocolError(f"桥接端返回了非法 JSON: {raw_line}") from exc

    if response.get("request_id") not in {None, request_id}:
        raise BridgeProtocolError("桥接端响应与当前请求不匹配。")

    if not response.get("ok", False):
        message = response.get("error") or "桥接端返回了未知错误。"
        raise BridgeProtocolError(str(message))

    result = response.get("result", {})
    if not isinstance(result, dict):
        raise BridgeProtocolError("桥接端响应格式错误，result 必须是对象。")
    return result