from __future__ import annotations

from typing import Any


HEX_DIGITS = set("0123456789abcdefABCDEF")


def _strip_0x_prefix(value: str) -> tuple[str, bool]:
    if value.startswith(("0x", "0X")):
        return value[2:], True
    return value, False


def _validate_hex_body(body: str) -> tuple[bool, str]:
    if not body:
        return False, "アドレスが空です。"

    if len(body) != 40:
        return False, "アドレスは 40 文字の16進数で入力してください（先頭の 0x は任意）。"

    for char in body:
        if char not in HEX_DIGITS:
            return False, "16進数以外の文字が含まれています。0-9, a-f, A-F のみ使用できます。"

    return True, ""


def _compute_keccak_hex(normalized_body: str) -> str:
    """
    EIP-55 で用いる Keccak-256 を計算して 16 進文字列で返す。

    import を関数内に置くことで、依存関係不足時に module import 時点では落とさず、
    analyze_address() 側で dependency_error として扱えるようにする。
    """
    try:
        from eth_utils import keccak
    except ImportError as exc:
        raise ImportError(
            "Keccak-256 の計算に必要な依存関係が未導入です。"
        ) from exc

    return keccak(text=normalized_body).hex()


def _build_char_analysis(
    input_body: str,
    normalized_body: str,
    hash_hex: str,
) -> tuple[list[dict[str, Any]], str]:
    analysis: list[dict[str, Any]] = []
    expected_chars: list[str] = []

    for index, lower_char in enumerate(normalized_body):
        hash_nibble = hash_hex[index]

        if lower_char.isdigit():
            should_upper = None
            expected_char = lower_char
        else:
            should_upper = int(hash_nibble, 16) >= 8
            expected_char = lower_char.upper() if should_upper else lower_char

        input_char = input_body[index]
        match = input_char == expected_char

        analysis.append(
            {
                "index": index,
                "position": index + 1,
                "input_char": input_char,
                "normalized_char": lower_char,
                "expected_char": expected_char,
                "hash_nibble": hash_nibble,
                "should_upper": should_upper,
                "is_alpha": lower_char.isalpha(),
                "match": match,
            }
        )
        expected_chars.append(expected_char)

    expected_body = "".join(expected_chars)
    return analysis, expected_body


def analyze_address(address: str) -> dict[str, Any]:
    original_input = "" if address is None else str(address)
    stripped_input = original_input.strip()
    body, had_prefix = _strip_0x_prefix(stripped_input)

    base_result: dict[str, Any] = {
        "input_original": original_input,
        "input_stripped": stripped_input,
        "input_has_prefix": had_prefix,
        "input_body": body,
        "normalized_body": "",
        "lowercase_address": "",
        "actual_address": "",
        "expected_address": "",
        "keccak_hash": "",
        "is_valid_format": False,
        "is_checksum_match": False,
        "status": "format_error",
        "error_message": "",
        "char_analysis": [],
        "mismatch_positions": [],
        "mismatch_count": 0,
    }

    is_valid, error_message = _validate_hex_body(body)
    if not is_valid:
        base_result["error_message"] = error_message
        return base_result

    normalized_body = body.lower()

    try:
        hash_hex = _compute_keccak_hex(normalized_body)
    except ImportError:
        base_result["error_message"] = (
            "Keccak-256 の計算に必要な依存関係が未導入です。"
            " requirements.txt を用いて依存関係をインストールしてください。"
            " 例: python -m pip install -r requirements.txt"
        )
        base_result["status"] = "dependency_error"
        return base_result

    char_analysis, expected_body = _build_char_analysis(body, normalized_body, hash_hex)

    mismatch_positions = [item["position"] for item in char_analysis if not item["match"]]
    is_checksum_match = len(mismatch_positions) == 0

    base_result.update(
        {
            "normalized_body": normalized_body,
            "lowercase_address": f"0x{normalized_body}",
            "actual_address": f"0x{body}",
            "expected_address": f"0x{expected_body}",
            "keccak_hash": hash_hex,
            "is_valid_format": True,
            "is_checksum_match": is_checksum_match,
            "status": "checksum_ok" if is_checksum_match else "checksum_mismatch",
            "error_message": "",
            "char_analysis": char_analysis,
            "mismatch_positions": mismatch_positions,
            "mismatch_count": len(mismatch_positions),
        }
    )

    return base_result


def calculate_checksum_address(address: str) -> str:
    result = analyze_address(address)
    if not result["is_valid_format"] or result["status"] == "dependency_error":
        raise ValueError(result["error_message"])
    return result["expected_address"]


def is_checksum_address(address: str) -> bool:
    result = analyze_address(address)
    return result["is_valid_format"] and result["is_checksum_match"]