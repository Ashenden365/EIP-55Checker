# EIP-55 Checksum Checker

EVM 系ウォレットアドレスが EIP-55 チェックサムとして正しいかどうかを判定する Streamlit アプリです。

## できること

- EVM アドレスの形式チェック
- EIP-55 チェックサムの判定
- Keccak-256 ハッシュの表示
- 期待される正しいチェックサム表記の表示
- 入力値と期待表記の差分表示
- どの英字を大文字にすべきかの可視化

## ディレクトリ構成

```text
EIP-55Checker/
├─ README.md
├─ app.py
├─ checker.py
├─ requirements.txt
└─ teststest_checker.py
