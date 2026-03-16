from checker import analyze_address, calculate_checksum_address, is_checksum_address


KNOWN_CHECKSUM_CASES = [
    (
        "0x52908400098527886e0f7030069857d2e4169ee7",
        "0x52908400098527886E0F7030069857D2E4169EE7",
    ),
    (
        "0x8617e340b3d01fa5f11f306f4090fd50e238070d",
        "0x8617E340B3D01FA5F11F306F4090FD50E238070D",
    ),
    (
        "0xde709f2102306220921060314715629080e2fb77",
        "0xde709f2102306220921060314715629080e2fb77",
    ),
    (
        "0x27b1fdb04752bbc536007a920d24acb045561c26",
        "0x27b1fdb04752bbc536007a920d24acb045561c26",
    ),
]


def flip_case_on_first_alpha(address: str) -> str:
    chars = list(address)
    for index, char in enumerate(chars):
        if char in "abcdefABCDEF":
            chars[index] = char.swapcase()
            return "".join(chars)
    raise ValueError("英字を含むアドレスが必要です。")


def test_calculate_checksum_address_known_cases():
    for lower_address, expected_checksum in KNOWN_CHECKSUM_CASES:
        assert calculate_checksum_address(lower_address) == expected_checksum


def test_is_checksum_address_accepts_valid_examples():
    valid_examples = [expected for _, expected in KNOWN_CHECKSUM_CASES]
    for address in valid_examples:
        assert is_checksum_address(address) is True


def test_analyze_address_detects_checksum_mismatch():
    valid_address = KNOWN_CHECKSUM_CASES[0][1]
    invalid_address = flip_case_on_first_alpha(valid_address)

    result = analyze_address(invalid_address)

    assert result["is_valid_format"] is True
    assert result["is_checksum_match"] is False
    assert result["status"] == "checksum_mismatch"
    assert result["expected_address"] == valid_address
    assert result["mismatch_count"] >= 1
    assert len(result["mismatch_positions"]) >= 1
    assert any(item["match"] is False for item in result["char_analysis"])


def test_analyze_address_rejects_invalid_length():
    result = analyze_address("0x1234")

    assert result["is_valid_format"] is False
    assert result["status"] == "format_error"
    assert "40 文字" in result["error_message"]


def test_analyze_address_rejects_non_hex_character():
    result = analyze_address("0x52908400098527886E0F7030069857D2E4169EEG")

    assert result["is_valid_format"] is False
    assert result["status"] == "format_error"
    assert "16進数以外" in result["error_message"]


def test_analyze_address_returns_hash_and_40_positions():
    result = analyze_address("0x52908400098527886E0F7030069857D2E4169EE7")

    assert result["is_valid_format"] is True
    assert len(result["keccak_hash"]) == 64
    assert len(result["char_analysis"]) == 40


def test_analyze_address_accepts_input_without_0x_prefix():
    result = analyze_address("52908400098527886E0F7030069857D2E4169EE7")

    assert result["is_valid_format"] is True
    assert result["is_checksum_match"] is True
    assert result["expected_address"] == "0x52908400098527886E0F7030069857D2E4169EE7"