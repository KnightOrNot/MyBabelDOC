import pytest
from babeldoc.format.pdf.document_il.midend.il_translator import ILTranslator
from babeldoc.translator import translator
from babeldoc.translator.translator import OpenAITranslator


@pytest.fixture(autouse=True)
def disable_rate_limit_wait(monkeypatch):
    monkeypatch.setattr(translator._translate_rate_limiter, "wait", lambda: None)


class FakeCache:
    def __init__(self, cached=None):
        self.cached = cached
        self.saved = []

    def get(self, _text):
        return self.cached

    def set(self, text, translation):
        self.saved.append((text, translation))


class FakeTranslator(translator.BaseTranslator):
    name = "fake"

    def __init__(self, result, cached=None):
        self.ignore_cache = False
        self.cache = FakeCache(cached)
        self.result = result
        self.translate_call_count = 0
        self.translate_cache_call_count = 0
        self.request_count = 0

    def do_translate(self, text, rate_limit_params=None):
        self.request_count += 1
        return self.result

    def do_llm_translate(self, text, rate_limit_params=None):
        self.request_count += 1
        return self.result


@pytest.mark.parametrize("method", ["translate", "llm_translate"])
@pytest.mark.parametrize("empty_result", [None, "", "   "])
def test_empty_response_is_rejected_and_not_cached(method, empty_result):
    engine = FakeTranslator(empty_result)

    with pytest.raises(ValueError, match="empty response"):
        getattr(engine, method)("source")

    assert engine.cache.saved == []
    assert engine.request_count == 3


@pytest.mark.parametrize("method", ["translate", "llm_translate"])
def test_existing_empty_cache_entry_is_ignored(method):
    engine = FakeTranslator("译文", cached="")

    assert getattr(engine, method)("source") == "译文"
    assert engine.translate_cache_call_count == 0
    assert engine.cache.saved == [("source", "译文")]


def test_unchanged_translation_does_not_replace_paragraph():
    class Tracker:
        output = None

        def last_llm_translate_tracker(self):
            return None

        def set_output(self, output):
            self.output = output

    class TranslateInput:
        unicode = "all objects in"

    class Paragraph:
        unicode = "all objects in"

    paragraph = Paragraph()
    changed = ILTranslator.post_translate_paragraph(
        None, paragraph, Tracker(), TranslateInput(), " all objects in "
    )

    assert changed is False
    assert paragraph.unicode == "all objects in"


def test_openai_llm_request_allows_reasoning_output_budget():
    class Completions:
        request = None

        def create(self, **kwargs):
            self.request = kwargs
            message = type("Message", (), {"content": "译文"})()
            choice = type("Choice", (), {"message": message})()
            return type("Response", (), {"choices": [choice]})()

    engine = OpenAITranslator.__new__(OpenAITranslator)
    engine.send_temperature = False
    engine.enable_json_mode_if_requested = False
    engine.send_dashscope_header = False
    engine.model = "reasoning-model"
    engine.extra_body = {}
    completions = Completions()
    engine.client = type(
        "Client", (), {"chat": type("Chat", (), {"completions": completions})()}
    )()
    engine.update_token_count = lambda _response: None

    assert engine.do_llm_translate("prompt", {}) == "译文"
    assert completions.request["max_tokens"] == 8192
