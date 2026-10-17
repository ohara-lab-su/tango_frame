# tango-frame

`tango-frame` は、通常の Python 機器制御クラスを TANGO Device Server として自動公開し、それに対応する Python クライアントを構成するためのフレームワークである。

機器制御クラス自身は PyTango を import する必要がなく、`tango.server.Device` を継承する必要もない。公開メソッドを TANGO command、Python の property を TANGO attribute として対応付ける。

[English README](README.md)

## 基本思想

機器実装と通信層を分離する。

```text
通常の Python 機器制御クラス
        |
        +---- tango-frame ----> TANGO Device Server
        |                        method   -> command
        |                        property -> attribute
        |
        +---- tango-frame ----> Python client wrapper
                                 |
                                 +---- TANGO DeviceProxy
```

`tango-frame` は TANGO の上に別の RPC プロトコルを構築するものではない。TANGO 標準の command / attribute を自動生成し、クライアント側も `DeviceProxy` を用いてそれらを呼び出す。

## 主な機能

- 通常の Python class を機器 API の定義として利用する。
- public method を同名の TANGO command として公開する。
- `@property` を TANGO attribute として公開する。
- setter を持つ property は read/write attribute とする。
- TANGO で直接表現できる scalar / homogeneous array は native TANGO 型を優先する。
- 複数の異種引数など、TANGO command の1入力で直接表現できない呼び出しだけを1個の JSON string に変換する。
- native TANGO 型で表現できない複雑な戻り値は JSON string に変換する。
- クライアント側は内部で `tango.DeviceProxy` を使いながら、元の機器クラスに近い Python method / property API を提供する。
- 機器固有の client-side 処理は自動 remote dispatch を override できる。

## 構成

```text
src/
└── tango_frame/
    ├── __init__.py
    ├── auto_dispatch.py
    ├── client.py
    ├── codec.py
    ├── introspection.py
    ├── server.py
    └── type_mapping.py

example/
└── device_server/
    ├── src/
    │   └── device/
    │       ├── device_class.py
    │       └── server_tango/
    │           ├── tango_ds.py
    │           └── device_client.py
    └── example/
        ├── server_start.py
        └── client.py
```

`src/tango_frame/` は再利用可能な framework であり、具体的な機器クラスを含まない。

`example/device_server/src/device/` は具体的な機器モジュールの例である。`device_class.py` は TANGO 非依存で、`server_tango/` がその機器に対する TANGO adapter 層になる。

## インストール

```bash
pip install .
```

PyTango 10 以降を必要とする。

## 機器制御クラス

機器制御クラスは通常の Python class のままでよい。

```python
from typing import List


class DeviceClass(object):
    def __init__(self) -> None:
        self._position = 0.0

    def add(self, value: float) -> float:
        self._position += value
        return self._position

    def move(
        self,
        position: float,
        speed: float = 1.0,
        wait: bool = True,
    ) -> bool:
        self._position = position
        return wait

    def get_samples(self) -> List[float]:
        return [1.0, 2.0, 3.0]

    @property
    def position(self) -> float:
        return self._position

    @position.setter
    def position(self, value: float) -> None:
        self._position = value
```

このクラスは TANGO を使わず、通常の Python object として直接実行することもできる。

## TANGO Device Server

機器固有の TANGO server class では、`AutoDispatchDevice` に機器クラスを指定する。

```python
from tango_frame import AutoDispatchDevice

from device.device_class import DeviceClass


class TangoDevice(AutoDispatchDevice):
    device_class = DeviceClass
```

上の例は概ね次の TANGO API に変換される。

```text
add(value: float) -> float
    TANGO command: float -> float

move(position: float, speed: float, wait: bool) -> bool
    TANGO command: JSON string -> bool

get_samples() -> List[float]
    TANGO command: void -> homogeneous float array

position: float
    TANGO read/write attribute
```

サーバー側で実行すべきでないメソッドは、機器固有の server class から除外できる。

```python
class TangoDevice(AutoDispatchDevice):
    device_class = DeviceClass
    excluded_commands = {"save"}
```

Device Server の起動自体は通常の PyTango server runtime を使用する。example の `-nodb` は TANGO database を使わずローカル試験するためだけの指定であり、framework の前提ではない。

## クライアント

同じ機器クラスを `AutoDispatchClient` に指定する。

```python
from tango_frame import AutoDispatchClient

from device.device_class import DeviceClass


class DeviceClient(AutoDispatchClient):
    device_class = DeviceClass
```

内部通信には TANGO `DeviceProxy` を使用するが、利用側では Python の method / property として扱う。

```python
device = DeviceClient(
    "tango://127.0.0.1:10000/test/tango/device#dbase=no"
)

print(device.position)
print(device.add(2.5))
device.position = 20.0
```

機器固有の client-side 処理は通常の継承で override する。たとえば `save(path)` は Device Server 側ではなく client machine に保存すべきなので、次のように実装できる。

```python
from pathlib import Path


class DeviceClient(AutoDispatchClient):
    device_class = DeviceClass

    def save(self, path: str) -> str:
        data = self.get_data()
        Path(path).write_bytes(data)
        return path
```

明示的に実装した client method は自動 remote dispatch より優先される。

## 型変換

原則として native TANGO 型を使用する。

| Python API | TANGO 上の表現 |
| --- | --- |
| `bool` | native boolean |
| `int` | native integer |
| `float` | native double |
| `str` | native string |
| homogeneous `List[T]` | native TANGO array / spectrum |
| 引数なし / 戻り値なし | void |
| 複数または異種の引数 | 1個の JSON string input |
| native 型にできない複雑な戻り値 | JSON string |

したがって JSON は通常の通信形式ではなく、TANGO の command model に直接対応できない Python 呼び出しを扱うための fallback である。

## ドキュメント

Sphinx/MyST のドキュメントは `docs/` 以下に置く。

```bash
cd docs
./build.sh
```

## バージョン

現在のバージョン: **0.1.0**

変更内容は [CHANGELOG.md](CHANGELOG.md) を参照。
