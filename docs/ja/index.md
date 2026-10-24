# tango-frame

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://ohara-lab-su.github.io/tango_frame/en/index.html) [![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://ohara-lab-su.github.io/tango_frame/ja/index.html)

[GitHub](https://github.com/ohara-lab-su/tango_frame/)

`tango-frame` は、通常の Python 機器制御クラスから TANGO Device Server と対応する Python client wrapper を自動構成するフレームワークである。

```{toctree}
:maxdepth: 2
:caption: 目次:

overview
api/modules
```

## 目的

機器制御クラスを TANGO 固有の実装へ書き換えるのではなく、既存の Python API を機器 API の定義として利用する。

```text
Python device class
      |
      +--> public method --> TANGO command
      |
      +--> @property     --> TANGO attribute
```

クライアント側では TANGO `DeviceProxy` を利用しながら、元の機器クラスに近い method / property API を提供する。

## 設計上の境界

`src/tango_frame/` は具体的な機器を知らない汎用 framework である。

具体的な機器側では、TANGO 非依存の機器制御クラスを保持し、その機器固有の `server_tango` 層から `AutoDispatchDevice` / `AutoDispatchClient` を利用する。

TANGO で直接表現できる値は native TANGO 型を使用する。複数の異種引数など、TANGO command の単一入力へ直接対応できない場合だけ JSON string へ変換する。

## Version

Current version: **0.1.0**
