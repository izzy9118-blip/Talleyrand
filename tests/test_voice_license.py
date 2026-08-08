from voice_license import PASS_STATUS, validate_voice_license


def test_voice_pin_resolves_but_does_not_self_release():
    result = validate_voice_license('.')
    assert result['status'] == PASS_STATUS
    assert result['page_pin'] == 'TAL-VOICE-PIN-001'
    assert result['owner_ruling_required'] is True
