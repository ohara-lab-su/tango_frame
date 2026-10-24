# アーキテクチャと使用方法

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://ohara-lab-su.github.io/tango_frame/en/overview.html) [![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://ohara-lab-su.github.io/tango_frame/ja/overview.html)

## 責務の分離

```text
src/tango_frame/
    再利用可能な TANGO 適応フレームワーク

device package/
    通常の機器制御クラス
    server_tango/
        機器固有の TANGO server/client 適応層
```

再利用可能なフレームワークは、具体的な機器クラスに依存してはならない。

## サーバー側

機器固有の TANGO Device クラスは、通常の Python 機器クラスを `AutoDispatchDevice` に結び付ける。

```python
class TangoDevice(AutoDispatchDevice):
    device_class = DeviceClass
```

`tango-frame` は公開 API を調べ、TANGO command と attribute を動的に生成する。

リモートコマンドとして公開しないメソッドは、機器固有のサーバークラスで除外できる。

```python
class TangoDevice(AutoDispatchDevice):
    device_class = DeviceClass
    excluded_commands = {"save"}
```

## クライアント側

機器固有のクライアントは、同じ機器クラスを `AutoDispatchClient` に結び付ける。

```python
class DeviceClient(AutoDispatchClient):
    device_class = DeviceClass
```

呼び出しは TANGO `DeviceProxy` を介して転送される。

機器固有のクライアントに明示的に実装したメソッドは、自動リモートディスパッチより優先される。これは、リモートから取得したデータをローカルパスに保存する処理など、クライアント側の計算機に属する操作に使用する。

## 型変換

対応するスカラー値と同種要素の配列には、TANGO 互換のネイティブ型を使用する。

TANGO command の入力値は1つであるため、複数の異種引数を必要とする Python 呼び出しは、1つの JSON 文字列にエンコードする。直接表現できない複雑な戻り値にも、同じ JSON フォールバックを使用する。

この変換は Python API を TANGO command モデルへ適応させるためのものであり、独立した RPC プロトコルではない。
