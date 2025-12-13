# Cloudflare DDNS

## Usage

### Requirements

Recommended: Windows 11 x64

### Basic

Global API Key: [https://dash.cloudflare.com/profile/api-tokens](https://dash.cloudflare.com/profile/api-tokens)

### Advanced

IPv4 and IPv6 Address Checking API changeable in `ddns.py` - `fetch_current_ip()`.

DNS Record update interval changeable in `main.py` - `main()`.

## Development

### Python uv

1. Install uv: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
2. Install Python in uv: `uv python install 3.12`; upgrade Python in uv: `uv python install 3.12`
3. Configure requirements:
  ```bash
  uv sync --refresh
  ```

### Pycharm Professional

1. Add New Interpreter >> Add Local Interpreter
  - Environment: Select existing
  - Type: uv
2. Add New Configuration >> uv run >> script: `./main.py`

### Build

```bash
uv run pyinstaller --onefile main.py
```
