
import re
from datetime import datetime

ALIASES = {
    "ibov_cash": [r"\bIbovespa\b"],
    "ibov_fut": [r"\bIbovespa Fut\b"],
    "dow": [r"\bDow Jones\b(?! Fut)"],
    "dow_fut": [r"\bDow Jones Fut\b"],
    "sp500": [r"\bS&P 500\b(?! Fut|\sVIX)"],
    "sp500_fut": [r"\bS&P 500 Fut\b"],
    "nasdaq": [r"\bNasdaq\b(?! Fut)"],
    "nasdaq_fut": [r"\bNasdaq Fut\b"],
    "russell": [r"\bRussell 2000\b"],
    "vix": [r"\bS&P 500 VIX\b", r"\bVIX\b"],
    "eurostoxx": [r"\bEuro Stoxx 50\b"],
    "dax": [r"\bAlemanha\b"],
    "nikkei": [r"\bJapão\b"],
    "hangseng": [r"\bHong Kong\b"],
    "china_a50": [r"\bChina A50\b(?! Fut)"],
    "china_a50_fut": [r"\bChina A50 Fut\b"],
    "usdbrl": [r"\bUSD/BRL\b", r"^\s*Dólar\s"],
    "dxy": [r"\bÍndice Dólar DXY\b", r"\bDXY\b"],
    "dolar_fut": [r"\bDólar Fut\b"],
    "wti": [r"\bPetróleo WTI\b"],
    "brent": [r"\bPetróleo Brent\b"],
    "gold": [r"\bOuro\b"],
    "copper": [r"\bCobre\b"],
    "us10y": [r"\bU\.S\. 10 Treasury\b"],
    "petrobras": [r"\bPetrobras SA\b"],
    "vale": [r"\bVale SA\b"],
    "ewz": [r"\bEWZ\b"],
    "ifnc": [r"\bIFNC\b"],
    "imob": [r"\bIMOB\b"],
}

def _to_float(num_str: str) -> float:
    s = num_str.strip().replace('.', '').replace(',', '.')
    if s in {"", "-", "Infinity"}:
        return 0.0
    try:
        return float(s)
    except Exception:
        return 0.0

def _extract_pct(text: str, patterns):
    for pattern in patterns:
        regex = re.compile(pattern + r".*?([+-]?\d+[.,]?\d*)%", re.IGNORECASE | re.MULTILINE)
        m = regex.search(text)
        if m:
            return _to_float(m.group(1))
    return 0.0

def _extract_timestamp(text: str) -> str:
    m = re.search(r"(\d{6})\s+([A-Za-zÀ-ÿ\-]+,\s+[A-Za-zÀ-ÿ]+\s+\d{1,2},\s+\d{4})", text)
    if m:
        hhmmss = m.group(1)
        return f"{m.group(2)} {hhmmss[:2]}:{hhmmss[2:4]}"
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def parse_market_text(text: str) -> dict:
    values = {key: _extract_pct(text, patterns) for key, patterns in ALIASES.items()}
    timestamp = _extract_timestamp(text)

    macro_us = [
        {"Ativo": "S&P 500", "Variação %": values["sp500"]},
        {"Ativo": "Nasdaq", "Variação %": values["nasdaq"]},
        {"Ativo": "Dow Jones", "Variação %": values["dow"]},
        {"Ativo": "Russell 2000", "Variação %": values["russell"]},
        {"Ativo": "VIX", "Variação %": values["vix"]},
        {"Ativo": "DXY", "Variação %": values["dxy"]},
        {"Ativo": "S&P Fut", "Variação %": values["sp500_fut"]},
        {"Ativo": "Nasdaq Fut", "Variação %": values["nasdaq_fut"]},
    ]
    brazil = [
        {"Ativo": "Ibovespa Fut", "Variação %": values["ibov_fut"]},
        {"Ativo": "Ibovespa", "Variação %": values["ibov_cash"]},
        {"Ativo": "Dólar Fut", "Variação %": values["dolar_fut"]},
        {"Ativo": "USD/BRL", "Variação %": values["usdbrl"]},
        {"Ativo": "EWZ", "Variação %": values["ewz"]},
        {"Ativo": "Petrobras ADR", "Variação %": values["petrobras"]},
        {"Ativo": "Vale ADR", "Variação %": values["vale"]},
        {"Ativo": "IFNC", "Variação %": values["ifnc"]},
        {"Ativo": "IMOB", "Variação %": values["imob"]},
    ]
    world = [
        {"Ativo": "Euro Stoxx 50", "Variação %": values["eurostoxx"]},
        {"Ativo": "DAX", "Variação %": values["dax"]},
        {"Ativo": "Nikkei", "Variação %": values["nikkei"]},
        {"Ativo": "Hang Seng", "Variação %": values["hangseng"]},
        {"Ativo": "China A50", "Variação %": values["china_a50"]},
        {"Ativo": "China A50 Fut", "Variação %": values["china_a50_fut"]},
    ]
    commod_fx = [
        {"Ativo": "WTI", "Variação %": values["wti"]},
        {"Ativo": "Brent", "Variação %": values["brent"]},
        {"Ativo": "Ouro", "Variação %": values["gold"]},
        {"Ativo": "Cobre", "Variação %": values["copper"]},
        {"Ativo": "Treasury 10Y", "Variação %": values["us10y"]},
        {"Ativo": "DXY", "Variação %": values["dxy"]},
        {"Ativo": "USD/BRL", "Variação %": values["usdbrl"]},
    ]

    return {
        "timestamp": timestamp,
        "values": values,
        "tables": {
            "macro_us": macro_us,
            "brazil": brazil,
            "world": world,
            "commod_fx": commod_fx,
        },
    }
