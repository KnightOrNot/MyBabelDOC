from babeldoc.format.pdf.document_il.midend.il_translator_llm_only import (
    ILTranslatorLLMOnly,
)


def test_short_translation_allows_language_token_expansion():
    assert ILTranslatorLLMOnly._translation_length_is_plausible(1, 3)
    assert ILTranslatorLLMOnly._translation_length_is_plausible(2, 6)


def test_long_translation_still_rejects_extreme_length_changes():
    assert not ILTranslatorLLMOnly._translation_length_is_plausible(20, 4)
    assert not ILTranslatorLLMOnly._translation_length_is_plausible(20, 60)
    assert ILTranslatorLLMOnly._translation_length_is_plausible(20, 30)
