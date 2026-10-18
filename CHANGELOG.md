# CHANGELOG

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/ohara-lab-su/tango_frame/blob/main/CHANGELOG.en.md)
[![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://github.com/ohara-lab-su/tango_frame/blob/main/CHANGELOG.md)

## v0.1.1 - 2026-10-17

標準的な TANGO 環境で使用するための設定機能およびクライアント機能を追加。

- TANGO の接続設定を定義する `tango_frame.config.Config` を追加。
    - `device_name` で TANGO device name を指定可能。
    - `tango_host` で TANGO Database の接続先を指定可能。
    - `database` で Database 使用／Database-less 接続を選択可能。
- `tango_frame` に `DeviceProxy` wrapper を追加。
    - 内部では PyTango native の `DeviceProxy` を生成して使用。
    - `device_class` を必要とせず、既存の標準 TANGO device に接続可能。
    - TANGO command、attribute、および native `DeviceProxy` の操作を wrapper 経由で利用可能。
- 通常の TANGO Database を使用する構成に対応。
    - `database=True` の場合、標準の TANGO 名前空間を使用して device を解決。
    - `domain/family/member` 形式の TANGO device name で device を指定可能。
    - `tango_host` により TANGO Database の接続先を指定可能。
- ローカルテスト用の Database-less 接続を維持。
    - `database=False` の場合、`#dbase=no` を使用した Database-less TANGO URL で接続。
    - Database-less 動作はローカルテスト用であり、フレームワーク自体の前提とはしない。
- `AutoDispatchClient` から `Config` を使用できるように変更。
    - `device_class` が与えられた場合、その Python API をクライアント側に再構築し、TANGO device にディスパッチ。
    - native TANGO device を使用する場合は `device_class` を必要とせず、フレーム側の `DeviceProxy` から直接利用可能。
- サーバーフレームワークは通常の TANGO Device Server としての運用に対応。
    - フレームワーク自体は `-nodb` を必須としない。
    - `-nodb` はローカルでの Device Server 動作試験用として利用可能。
    - 通常運用では、生成した Device Server を TANGO Database に登録し、通常の TANGO 名前空間からアクセス可能。
- Google style の docstring およびソースコメントを追加。
- Python 3.7 互換の型アノテーションに整理。
- ソースコードから三項演算子を除去。

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
