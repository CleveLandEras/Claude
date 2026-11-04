"""模型层：去标识化、请求组装、返回解析、出错一律「都不是／拿不准」。不连外网，只用本机回环。"""
import json
import re
import socket
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from autoreply import model
from autoreply.config import ModelConfig
from autoreply.dataset_stats import ALL_LABELS, UNSURE_LABEL
from autoreply.model import CloudBackend, FakeBackend, ModelError, build_request, parse_envelope, parse_scores, predict

KEY = "test-key-not-real"
CONFIG = ModelConfig(base_url="https://example.invalid/v1/", model="some-model", api_key=KEY)


def scores_json(**overrides):
    scores = {label: 0.0 for label in ALL_LABELS}
    scores.update(overrides)
    return json.dumps({"scores": scores}, ensure_ascii=False)


def envelope(content):
    return json.dumps({"choices": [{"message": {"role": "assistant", "content": content}}]}, ensure_ascii=False)


# ---- 去标识化 ----


def test_backend_never_sees_raw_phone_or_name():
    backend = FakeBackend(scores_json(上课时间=0.9))
    predict("我是王小测妈妈，电话13000000001，下节课几点", backend)
    assert len(backend.seen) == 1
    assert "13000000001" not in backend.seen[0] and "王小测" not in backend.seen[0]
    assert "<手机号>" in backend.seen[0] and "<姓名>" in backend.seen[0]


def test_known_names_are_replaced_before_sending():
    backend = FakeBackend(scores_json(作业截止=0.9))
    predict("问下思涵的作业", backend, known_names=["思涵"])
    assert "思涵" not in backend.seen[0]


def test_redact_failure_does_not_send(monkeypatch):
    def boom(*_args, **_kwargs):
        raise RuntimeError("坏了")

    monkeypatch.setattr(model, "redact", boom)
    backend = FakeBackend(scores_json(上课时间=0.9))
    result = predict("下节课几点", backend)
    assert backend.seen == []
    assert (result.category, result.error) == (UNSURE_LABEL, "redact_failed")


# ---- 解析模型答的正文 ----


def test_parse_scores_gives_top_category_and_confidence():
    result = parse_scores(scores_json(上课时间=0.9, 回放链接=0.2))
    assert (result.category, result.confidence, result.error) == ("上课时间", 0.9, None)
    assert set(result.scores) == set(ALL_LABELS)


def test_tie_shows_the_handoff_category():
    assert parse_scores(scores_json(上课时间=0.8, 退费=0.8)).category == "退费"


@pytest.mark.parametrize(
    "content, kind",
    [
        ("这不是 JSON", "bad_json"),
        ('```json\n{"scores": {}}\n```', "bad_json"),
        (None, "bad_json"),
        ("[1, 2]", "bad_schema"),
        ('{"category": "上课时间", "confidence": 0.9}', "bad_schema"),
        ('{"scores": "上课时间"}', "bad_schema"),
        ('{"scores": {"上课时间": 0.9}}', "bad_schema"),
        (scores_json(寒暄=0.9), "bad_category"),
        (scores_json(上课时间="0.9"), "bad_schema"),
        (scores_json(上课时间=True), "bad_schema"),
        (scores_json(上课时间=None), "bad_schema"),
        (scores_json(上课时间=1.5), "bad_schema"),
        (scores_json(上课时间=-0.1), "bad_schema"),
        (scores_json().replace('"上课时间": 0.0', '"上课时间": NaN'), "bad_schema"),
        (scores_json().replace('"上课时间": 0.0', '"上课时间": Infinity'), "bad_schema"),
    ],
)
def test_bad_content_is_rejected_and_predict_falls_back(content, kind):
    with pytest.raises(ModelError) as caught:
        parse_scores(content)
    assert caught.value.kind == kind

    result = predict("下节课几点", FakeBackend(lambda _text: content))
    assert (result.category, result.confidence, result.scores, result.error) == (UNSURE_LABEL, 0.0, {}, kind)


def test_unexpected_backend_exception_falls_back():
    result = predict("下节课几点", FakeBackend(ZeroDivisionError("坏了")))
    assert result.category == UNSURE_LABEL
    assert result.error == "unexpected_ZeroDivisionError"


# ---- 请求组装 ----


def test_build_request_matches_openai_format():
    request = build_request(CONFIG, "下节课几点")
    assert request.full_url == "https://example.invalid/v1/chat/completions"
    assert request.get_method() == "POST"
    assert request.get_header("Authorization") == f"Bearer {KEY}"
    assert request.get_header("Content-type") == "application/json"

    body = json.loads(request.data.decode("utf-8"))
    assert body["model"] == "some-model"
    assert body["temperature"] == 0
    assert body["stream"] is False
    assert body["response_format"] == {"type": "json_object"}
    assert [message["role"] for message in body["messages"]] == ["system", "user"]
    assert body["messages"][1]["content"] == "下节课几点"
    assert KEY not in request.data.decode("utf-8")


def test_prompt_names_every_category_and_asks_for_json():
    for label in ALL_LABELS:
        assert label in model.SYSTEM_PROMPT
    assert "JSON" in model.SYSTEM_PROMPT  # 接口的 json_object 模式要求提示词里提到 JSON
    # 提示词里的格式样例本身要能通过校验。
    assert parse_scores(model.SYSTEM_PROMPT[model.SYSTEM_PROMPT.rindex('{"scores"'):]).error is None


def test_no_key_or_address_in_code():
    for path in (Path(model.__file__).parent).glob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "deepseek.com" not in text, path
        assert not re.search(r"\bsk-[A-Za-z0-9]{8,}", text), path


# ---- 解析接口返回 ----


def test_parse_envelope_returns_content():
    assert parse_envelope(envelope("正文").encode("utf-8")) == "正文"


def test_parse_envelope_tolerates_keepalive_blank_lines():
    assert parse_envelope(b"\n\n" + envelope("正文").encode("utf-8")) == "正文"


@pytest.mark.parametrize(
    "body, kind",
    [
        (b"<html>bad gateway</html>", "bad_json"),
        (b"\xff\xfe\xfa", "bad_json"),
        (b"[]", "bad_schema"),
        (b"{}", "bad_schema"),
        (b'{"choices": []}', "bad_schema"),
        (b'{"choices": [{"message": {}}]}', "bad_schema"),
        (b'{"choices": [{"message": {"content": null}}]}', "bad_schema"),
    ],
)
def test_parse_envelope_rejects_bad_bodies(body, kind):
    with pytest.raises(ModelError) as caught:
        parse_envelope(body)
    assert caught.value.kind == kind


# ---- 真走一遍 urllib（本机回环）----


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        self.server.seen.append(
            {"path": self.path, "auth": self.headers["Authorization"], "body": json.loads(body.decode("utf-8"))}
        )
        self.server.respond(self)

    def log_message(self, *_args):
        pass


def send(handler, status, body=b"", headers=()):
    handler.send_response(status)
    for name, value in headers:
        handler.send_header(name, value)
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


@pytest.fixture
def server():
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    httpd.daemon_threads = True
    httpd.seen = []
    thread = threading.Thread(target=httpd.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
    thread.start()
    yield httpd
    httpd.shutdown()
    httpd.server_close()


def local_backend(port, timeout=2.0):
    config = ModelConfig(f"http://127.0.0.1:{port}", "some-model", KEY, timeout)
    # 不走本机可能设着的代理；其余和正式的 opener 一样。
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), model.NoRedirect())
    return CloudBackend(config, opener=opener)


def test_cloud_round_trip(server):
    server.respond = lambda h: send(h, 200, envelope(scores_json(回放链接=0.9)).encode("utf-8"))
    result = predict("我是王小测妈妈，13000000001，回放在哪", local_backend(server.server_port))
    assert (result.category, result.confidence, result.error) == ("回放链接", 0.9, None)

    seen = server.seen[0]
    assert seen["path"] == "/chat/completions"
    assert seen["auth"] == f"Bearer {KEY}"
    user_text = seen["body"]["messages"][1]["content"]
    assert "13000000001" not in user_text and "王小测" not in user_text


@pytest.mark.parametrize("status", [400, 401, 429, 500, 503])
def test_cloud_http_error_falls_back(server, status):
    server.respond = lambda h: send(h, status, b'{"error": "nope"}')
    result = predict("下节课几点", local_backend(server.server_port))
    assert (result.category, result.error) == (UNSURE_LABEL, f"http_{status}")


def test_cloud_non_json_body_falls_back(server):
    server.respond = lambda h: send(h, 200, b"<html>oops</html>")
    assert predict("下节课几点", local_backend(server.server_port)).error == "bad_json"


def test_cloud_unknown_category_falls_back(server):
    server.respond = lambda h: send(h, 200, envelope(scores_json(寒暄=0.9)).encode("utf-8"))
    result = predict("下节课几点", local_backend(server.server_port))
    assert (result.category, result.error) == (UNSURE_LABEL, "bad_category")


def test_cloud_timeout_falls_back(server):
    def respond(handler):
        time.sleep(1.0)
        send(handler, 200, envelope(scores_json(上课时间=0.9)).encode("utf-8"))

    server.respond = respond
    started = time.monotonic()
    result = predict("下节课几点", local_backend(server.server_port, timeout=0.2))
    assert (result.category, result.error) == (UNSURE_LABEL, "timeout")
    assert time.monotonic() - started < 0.9


def test_cloud_keepalive_lines_cannot_outlast_the_deadline(server):
    """服务商排队时一直发空行，每次都重置套接字超时，要靠总时长截住。"""

    def respond(handler):
        handler.send_response(200)
        handler.end_headers()
        try:
            for _ in range(30):
                handler.wfile.write(b"\n")
                handler.wfile.flush()
                time.sleep(0.05)
        except OSError:
            pass

    server.respond = respond
    started = time.monotonic()
    result = predict("下节课几点", local_backend(server.server_port, timeout=0.2))
    assert result.error == "timeout"
    assert time.monotonic() - started < 1.0


def test_cloud_does_not_follow_redirect(server):
    server.respond = lambda h: send(h, 302, headers=[("Location", f"http://127.0.0.1:{server.server_port}/other")])
    result = predict("下节课几点", local_backend(server.server_port))
    assert result.error == "http_302"
    assert len(server.seen) == 1


def test_default_opener_refuses_redirect():
    handlers = CloudBackend(CONFIG)._opener.handlers
    assert any(isinstance(handler, model.NoRedirect) for handler in handlers)


def test_cloud_connection_refused_falls_back():
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    assert predict("下节课几点", local_backend(port)).error == "network"


def test_config_repr_hides_key():
    assert KEY not in repr(CONFIG)


# ---- 假后端 ----


def test_fake_reply_is_valid_and_repeatable():
    first = predict("下节课几点", FakeBackend())
    second = predict("下节课几点", FakeBackend())
    assert first == second
    assert first.error is None and first.category == "上课时间"
    assert predict("在吗", FakeBackend()).category == UNSURE_LABEL
