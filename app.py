import html

import streamlit as st

from checker import analyze_address


st.set_page_config(
    page_title="EIP-55 Checksum Checker",
    page_icon="✅",
    layout="centered",
)

APP_CSS = """
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 900px;
}

.main-title {
    margin-bottom: 0.25rem;
}

.intro-text {
    color: #4b5563;
    margin-bottom: 1.25rem;
}

.input-guide {
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 0.9rem 1rem;
    margin-bottom: 1rem;
    color: #374151;
    font-size: 0.95rem;
    line-height: 1.7;
}

.result-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 1rem 1rem 0.8rem 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.result-title {
    font-size: 1.15rem;
    font-weight: 700;
    margin-bottom: 0.4rem;
}

.result-subtext {
    color: #4b5563;
    margin-bottom: 0.2rem;
}

.diff-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 1rem;
    margin-top: 0.5rem;
    margin-bottom: 1rem;
}

.address-block {
    margin-top: 0.45rem;
    margin-bottom: 1rem;
}

.address-label {
    font-size: 0.96rem;
    font-weight: 600;
    margin-bottom: 0.4rem;
}

.address-box {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
    background: #f6f8fa;
    border: 1px solid #d0d7de;
    border-radius: 10px;
    padding: 0.8rem 0.9rem;
    overflow-x: auto;
    white-space: nowrap;
    line-height: 1.8;
}

.prefix {
    display: inline-block;
    margin-right: 0.3rem;
    font-weight: 700;
    color: #57606a;
}

.char {
    display: inline-block;
    width: 0.74em;
    text-align: center;
    border-radius: 4px;
    padding: 0.02rem 0;
}

.should-upper {
    background: #e7f5ea;
    color: #116329;
    font-weight: 700;
}

.mismatch {
    background: #fde7e9;
    color: #b42318;
    font-weight: 700;
    box-shadow: inset 0 -2px 0 rgba(180, 35, 24, 0.25);
}

.legend-box {
    font-size: 0.92rem;
    color: #4b5563;
    margin-bottom: 1rem;
}

.legend-item {
    display: inline-block;
    margin-right: 1rem;
    margin-bottom: 0.35rem;
}

.legend-swatch {
    display: inline-block;
    width: 0.95rem;
    height: 0.95rem;
    border-radius: 4px;
    margin-right: 0.35rem;
    vertical-align: middle;
    border: 1px solid rgba(0, 0, 0, 0.08);
}

.legend-upper {
    background: #e7f5ea;
}

.legend-mismatch {
    background: #fde7e9;
}

.fix-list {
    margin-top: 0.5rem;
    margin-bottom: 0.2rem;
}

.fix-item {
    display: inline-block;
    background: #fff7ed;
    color: #9a3412;
    border: 1px solid #fed7aa;
    border-radius: 999px;
    padding: 0.3rem 0.65rem;
    margin-right: 0.45rem;
    margin-bottom: 0.45rem;
    font-size: 0.9rem;
    font-weight: 600;
}

.detail-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.92rem;
    margin-top: 0.25rem;
}

.detail-table th,
.detail-table td {
    border: 1px solid #e5e7eb;
    padding: 0.45rem 0.5rem;
    text-align: center;
}

.detail-table th {
    background: #f9fafb;
    font-weight: 700;
}

.detail-table tr:nth-child(even) {
    background: #fcfcfd;
}

.detail-ok {
    color: #116329;
    font-weight: 700;
}

.detail-ng {
    color: #b42318;
    font-weight: 700;
}

.mono-note {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
}

.section-caption {
    color: #6b7280;
    font-size: 0.93rem;
    margin-top: -0.2rem;
    margin-bottom: 0.7rem;
}
</style>
"""

st.markdown(APP_CSS, unsafe_allow_html=True)


VALID_SAMPLE = "0x68DD2cD04444b3981B156c6Ce812541cbe3Bd682"
INVALID_SAMPLE = "0x68DD2cD04444b3981B156c6Ce812541cbe3Bd681"


def build_expected_address_html(result: dict) -> str:
    spans = ['<span class="prefix">0x</span>']

    for item in result["char_analysis"]:
        char = html.escape(item["expected_char"])
        classes = ["char"]

        if item["is_alpha"] and item["should_upper"] is True:
            classes.append("should-upper")

        spans.append(f'<span class="{" ".join(classes)}">{char}</span>')

    return (
        '<div class="address-block">'
        '<div class="address-label">正しい EIP-55 表記（緑 = 大文字にすべき英字）</div>'
        f'<div class="address-box">{"".join(spans)}</div>'
        '</div>'
    )


def build_input_address_html(result: dict) -> str:
    spans = ['<span class="prefix">0x</span>']

    for item in result["char_analysis"]:
        char = html.escape(item["input_char"])
        classes = ["char"]

        if not item["match"]:
            classes.append("mismatch")

        spans.append(f'<span class="{" ".join(classes)}">{char}</span>')

    return (
        '<div class="address-block">'
        '<div class="address-label">入力された表記（赤 = 修正が必要な文字）</div>'
        f'<div class="address-box">{"".join(spans)}</div>'
        '</div>'
    )


def build_fix_items_html(result: dict) -> str:
    fix_items = []

    for item in result["char_analysis"]:
        if item["match"]:
            continue

        input_char = html.escape(item["input_char"])
        expected_char = html.escape(item["expected_char"])
        position = item["position"]

        fix_items.append(
            f'<span class="fix-item">{position}文字目: {input_char} → {expected_char}</span>'
        )

    if not fix_items:
        return "<p>修正が必要な文字はありません。</p>"

    return f'<div class="fix-list">{"".join(fix_items)}</div>'


def build_detail_table_html(result: dict, only_mismatches: bool = False) -> str:
    rows = []

    for item in result["char_analysis"]:
        if not item["is_alpha"]:
            continue

        if only_mismatches and item["match"]:
            continue

        rule_text = "大文字" if item["should_upper"] else "小文字"
        match_class = "detail-ok" if item["match"] else "detail-ng"
        match_text = "OK" if item["match"] else "NG"

        rows.append(
            "<tr>"
            f"<td>{item['position']}</td>"
            f"<td>{html.escape(item['normalized_char'])}</td>"
            f"<td>{html.escape(item['hash_nibble'])}</td>"
            f"<td>{rule_text}</td>"
            f"<td>{html.escape(item['expected_char'])}</td>"
            f"<td>{html.escape(item['input_char'])}</td>"
            f"<td class=\"{match_class}\">{match_text}</td>"
            "</tr>"
        )

    if not rows:
        return "<p>表示できる行がありません。</p>"

    return (
        '<table class="detail-table">'
        "<thead>"
        "<tr>"
        "<th>位置</th>"
        "<th>小文字化した文字</th>"
        "<th>対応するhash文字</th>"
        "<th>本来の表記</th>"
        "<th>期待文字</th>"
        "<th>入力文字</th>"
        "<th>一致</th>"
        "</tr>"
        "</thead>"
        "<tbody>"
        f"{''.join(rows)}"
        "</tbody>"
        "</table>"
    )


def get_status_heading_and_text(result: dict) -> tuple[str, str]:
    status = result["status"]

    if status == "checksum_ok":
        return (
            "✅ Checksum OK",
            "入力アドレスは EIP-55 チェックサムとして正しいです。",
        )

    if status == "checksum_mismatch":
        return (
            "❌ Checksum NG",
            "アドレス形式は有効ですが、EIP-55 の大文字・小文字ルールに一致していません。",
        )

    if status == "dependency_error":
        return (
            "⚠️ Dependency Error",
            result["error_message"],
        )

    return (
        "⚠️ Format Error",
        result["error_message"],
    )


def render_status_message(result: dict) -> None:
    status = result["status"]

    if status == "checksum_ok":
        st.success("Checksum OK: 入力アドレスは EIP-55 チェックサムとして正しいです。")
    elif status == "checksum_mismatch":
        st.error("Checksum NG: アドレス形式は有効ですが、EIP-55 の大文字・小文字ルールに一致していません。")
    elif status == "dependency_error":
        st.error(result["error_message"])
    else:
        st.error(f"Format Error: {result['error_message']}")


def render_top_summary(result: dict) -> None:
    title, text = get_status_heading_and_text(result)

    st.markdown(
        f"""
        <div class="result-card">
            <div class="result-title">{html.escape(title)}</div>
            <div class="result-subtext">{html.escape(text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if result["status"] in ("format_error", "dependency_error"):
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("形式", "OK")
    col2.metric("チェックサム", "OK" if result["is_checksum_match"] else "NG")
    col3.metric("要修正文字数", str(result["mismatch_count"]))

    st.subheader("正しい表記")
    st.code(result["expected_address"], language=None)


def render_diff_section(result: dict) -> None:
    st.subheader("比較結果")
    st.markdown(
        """
        <div class="section-caption">
        まずは「入力された表記」と「正しい EIP-55 表記」の差分を確認してください。
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="legend-box">
            <span class="legend-item"><span class="legend-swatch legend-upper"></span>緑: 大文字にすべき英字</span>
            <span class="legend-item"><span class="legend-swatch legend-mismatch"></span>赤: 修正が必要な文字</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="diff-card">', unsafe_allow_html=True)
    st.markdown(build_expected_address_html(result), unsafe_allow_html=True)
    st.markdown(build_input_address_html(result), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("修正ポイント")
    if result["mismatch_count"] == 0:
        st.success("修正が必要な文字はありません。")
    else:
        st.markdown(build_fix_items_html(result), unsafe_allow_html=True)


def render_details_section(result: dict) -> None:
    with st.expander("詳細を見る", expanded=False):
        st.subheader("入力値")
        st.code(result["actual_address"], language=None)

        st.subheader("Keccak-256 の計算対象")
        st.caption("EIP-55 では、先頭の 0x を外し、小文字化した 40 文字の16進文字列を Keccak-256 にかけます。")
        st.code(result["lowercase_address"], language=None)

        st.subheader("Keccak-256 ハッシュ")
        st.code(result["keccak_hash"], language=None)

        if result["mismatch_count"] > 0:
            st.subheader("不一致のある英字だけ表示")
            st.caption("まずは修正が必要な行だけ表示します。")
            st.markdown(build_detail_table_html(result, only_mismatches=True), unsafe_allow_html=True)

        st.subheader("英字ごとの詳細")
        st.caption("各英字について、hash のどの文字に基づいて大文字・小文字が決まるかを表示します。")
        st.markdown(build_detail_table_html(result, only_mismatches=False), unsafe_allow_html=True)


def render_result(result: dict) -> None:
    render_status_message(result)
    render_top_summary(result)

    if result["status"] in ("format_error", "dependency_error"):
        return

    render_diff_section(result)
    render_details_section(result)


if "address_input" not in st.session_state:
    st.session_state["address_input"] = ""

if "last_result" not in st.session_state:
    st.session_state["last_result"] = None


st.markdown('<h1 class="main-title">EIP-55 Checksum Checker</h1>', unsafe_allow_html=True)
st.markdown(
    '<div class="intro-text">EVM 系ウォレットアドレスが EIP-55 チェックサムとして正しいかどうかを判定します。</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="input-guide">
    <strong>入力ガイド</strong><br>
    ・<span class="mono-note">0x</span> 付きでも、なしでも入力できます。<br>
    ・40文字の16進数アドレスを対象に判定します。<br>
    ・アドレス値そのものではなく、大文字・小文字まで含めて EIP-55 と一致するかを確認します。
    </div>
    """,
    unsafe_allow_html=True,
)

sample_col1, sample_col2, sample_col3 = st.columns(3)
with sample_col1:
    if st.button("正常例を入力", use_container_width=True):
        st.session_state["address_input"] = VALID_SAMPLE
        st.session_state["last_result"] = None

with sample_col2:
    if st.button("エラー例を入力", use_container_width=True):
        st.session_state["address_input"] = INVALID_SAMPLE
        st.session_state["last_result"] = None

with sample_col3:
    if st.button("クリア", use_container_width=True):
        st.session_state["address_input"] = ""
        st.session_state["last_result"] = None

with st.form("checksum_form"):
    address_input = st.text_input(
        "EVM アドレスを入力してください",
        key="address_input",
        placeholder="0x52908400098527886E0F7030069857D2E4169EE7",
    )
    submitted = st.form_submit_button("Check", use_container_width=True)

if submitted:
    st.session_state["last_result"] = analyze_address(address_input)

if st.session_state["last_result"] is not None:
    render_result(st.session_state["last_result"])
else:
    st.info("アドレスを入力して Check を押すと、判定結果と差分を確認できます。")

with st.expander("このアプリで確認できること", expanded=False):
    st.markdown(
        """
- EVM アドレスの形式が正しいか
- EIP-55 チェックサムとして正しいか
- 小文字化したアドレスに対する Keccak-256 ハッシュ
- どの英字を大文字にすべきか
- 入力値と正しい表記のどこが違うか
        """
    )