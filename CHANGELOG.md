# CHANGELOG

## v0.1.0 - 2026-10-17

`tango-frame` の初期バージョン。

- 通常の Python 機器制御クラスから TANGO Device Server を自動構築する機能を追加。
- 公開メソッドを同名の TANGO command へ自動的にマッピングする機能を追加。
- Python の property を TANGO attribute へ自動的にマッピングする機能を追加。書き込み可能な attribute にも対応。
- 対応するスカラー値および同一型配列について、TANGO ネイティブ型へのマッピングを追加。
- TANGO command のネイティブ型では直接表現できない呼び出し形式および戻り値に対する JSON fallback encoding を追加。
- TANGO `DeviceProxy` を使用した Python client wrapper を追加。
- 機器固有の client override、およびサーバー側での command 除外に対応。
- TANGO に依存しないサンプル機器クラスと、それに対応する Device Server / client の実行例を追加。
- 英語版および日本語版 README を追加。
- Sphinx/MyST によるドキュメントと GitHub Pages workflow を追加。
