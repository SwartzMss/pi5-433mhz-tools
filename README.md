# pi5-433mhz-tools

Minimal 433 MHz communication helpers for the Raspberry Pi 5 using
[gpiozero](https://gpiozero.readthedocs.io/).

## Components

- `rfdevice.py` – Helper classes for sending and receiving codes.
- `sender.py` – Send a single integer code.
- `receive.py` – Listen and print received codes.

## Usage

Send a code on GPIO 17:

```bash
python3 sender.py --pin 17 --protocol 1 1234
```

Listen for codes on GPIO 27:

```bash
python3 receive.py --pin 27 --protocol 1
```

## 协议参数说明

`rfdevice.py` 中的 `PROTOCOLS` 字典定义了编码和解码方式，每个协议包含以下字段：

- **pulselength**：基准脉冲长度，单位是微秒 (µs)。
- **\*_high**/**\*_low**：分别表示高电平持续时间和低电平持续时间，
  都以 `pulselength` 为单位倍数，其中 `*` 可以是 `sync`、`zero` 或 `one`。
- **sync_high**/**sync_low**：一帧结束后的同步脉冲。
- **zero_high**/**zero_low**：发送比特 `0` 时的高低电平持续时间倍数。
- **one_high**/**one_low**：发送比特 `1` 时的高低电平持续时间倍数。
- **tolerance**：接收端判断脉冲是否在预期时长附近的容差比例（±35%）。

## License

This project is released under the MIT license.
