
from typing import Dict, List

def clamp(value, low, high):
    return max(low, min(high, value))

def classify_bias(score: float, asset: str) -> str:
    if score >= 7:
        return f"{asset} comprador forte"
    if score >= 3:
        return f"{asset} comprador moderado"
    if score <= -7:
        return f"{asset} vendedor forte"
    if score <= -3:
        return f"{asset} vendedor moderado"
    return f"{asset} neutro"

def analyze_market(parsed: Dict) -> Dict:
    v = parsed["values"]

    win_score = 0
    wdo_score = 0
    macro_score = 0
    turn_strength = 0

    # Macro global
    macro_score += 2 if v["sp500"] > 0 else -2
    macro_score += 2 if v["nasdaq"] > 0 else -2
    macro_score += 1 if v["dow"] > 0 else -1
    macro_score += 1 if v["eurostoxx"] > 0 else -1
    macro_score += 1 if v["dax"] > 0 else -1
    macro_score += 1 if v["nikkei"] > 0 else -1
    macro_score += 2 if v["vix"] < 0 else -2
    macro_score += 1 if v["dxy"] < 0 else -1

    # Brasil / correlação
    win_score += 3 if v["ibov_fut"] > 0 else -3 if v["ibov_fut"] < 0 else 0
    win_score += 2 if v["usdbrl"] < 0 else -2 if v["usdbrl"] > 0 else 0
    win_score += 2 if v["dolar_fut"] < 0 else -2 if v["dolar_fut"] > 0 else 0
    win_score += 1 if v["ewz"] > 0 else -1 if v["ewz"] < 0 else 0
    win_score += 1 if v["petrobras"] > 0 else 0
    win_score += 1 if v["vale"] > 0 else 0
    win_score += 1 if v["ifnc"] > 0 else -1 if v["ifnc"] < 0 else 0
    win_score += 1 if v["imob"] > 0 else 0

    # Dólar futuro
    wdo_score += 3 if v["dolar_fut"] > 0 else -3 if v["dolar_fut"] < 0 else 0
    wdo_score += 2 if v["usdbrl"] > 0 else -2 if v["usdbrl"] < 0 else 0
    wdo_score += 2 if v["dxy"] > 0 else -2 if v["dxy"] < 0 else 0
    wdo_score += 2 if v["vix"] > 0 else -2 if v["vix"] < 0 else 0
    wdo_score += 1 if v["sp500_fut"] < 0 else -1 if v["sp500_fut"] > 0 else 0
    wdo_score += 1 if v["nasdaq_fut"] < 0 else -1 if v["nasdaq_fut"] > 0 else 0

    # Comodities
    if v["wti"] > 0 or v["brent"] > 0:
        win_score += 1
    elif v["wti"] < 0 and v["brent"] < 0:
        win_score -= 1

    if v["gold"] > 0 and v["vix"] > 0:
        macro_score -= 1

    # Regime
    total_risk = macro_score + win_score - wdo_score
    if total_risk >= 8:
        regime = "RISK-ON FORTE"
    elif total_risk >= 3:
        regime = "RISK-ON MODERADO"
    elif total_risk <= -8:
        regime = "RISK-OFF FORTE"
    elif total_risk <= -3:
        regime = "RISK-OFF MODERADO"
    else:
        regime = "NEUTRO / TRANSIÇÃO"

    # Virada: sinais mistos relevantes ou forte desacoplamento
    if v["ibov_fut"] > 0 and (v["usdbrl"] < 0 or v["dolar_fut"] < 0):
        turn_strength += 35
    if v["sp500_fut"] > 0 and v["dxy"] < 0:
        turn_strength += 20
    if v["vix"] < 0:
        turn_strength += 15
    if v["ibov_fut"] * v["usdbrl"] > 0 and abs(v["ibov_fut"]) > 0.2 and abs(v["usdbrl"]) > 0.2:
        turn_strength += 10

    turn_strength = clamp(turn_strength, 0, 100)

    # Probabilidades
    up = clamp(45 + (win_score * 4) + (macro_score * 2) - max(0, wdo_score), 5, 85)
    down = clamp(45 + (wdo_score * 4) - (macro_score * 2) - max(0, win_score), 5, 85)
    side = clamp(100 - up - down, 10, 60)
    # normalize
    total = up + down + side
    up = round(up * 100 / total)
    down = round(down * 100 / total)
    side = 100 - up - down

    # Traps
    traps: List[str] = []
    if v["ibov_fut"] > 0 and v["usdbrl"] > 0:
        traps.append("Índice e dólar subindo juntos: atenção para desalinhamento e possível ruído de abertura.")
    if v["ibov_fut"] < 0 and v["usdbrl"] < 0:
        traps.append("Índice e dólar caindo juntos: correlação quebrada, cuidado com leitura simplista.")
    if abs(v["dolar_fut"]) < 0.05 and abs(v["usdbrl"]) < 0.05:
        traps.append("Dólar sem direção clara: cenário pode parecer bom no macro, mas sem confirmação no WDO.")
    if v["sp500_fut"] > 0 and v["ibov_fut"] < 0:
        traps.append("EUA sustentando alta e Brasil fraco: risco de venda atrasada no índice.")
    if v["sp500_fut"] < 0 and v["ibov_fut"] > 0:
        traps.append("Brasil forte contra EUA fraco: possível fluxo local ou short squeeze.")
    if turn_strength >= 50:
        traps.append("Mudança de regime em andamento: não use a leitura anterior sem revalidar.")

    if not traps:
        traps.append("Sem armadilha dominante no momento; ainda assim confirme preço e dólar antes da execução.")

    # Confidence
    align = 0
    align += 1 if v["sp500_fut"] > 0 and v["ibov_fut"] > 0 else 0
    align += 1 if v["sp500_fut"] < 0 and v["ibov_fut"] < 0 else 0
    align += 1 if v["usdbrl"] < 0 and v["ibov_fut"] > 0 else 0
    align += 1 if v["usdbrl"] > 0 and v["ibov_fut"] < 0 else 0
    align += 1 if v["dxy"] < 0 and wdo_score < 0 else 0
    align += 1 if v["dxy"] > 0 and wdo_score > 0 else 0
    align += 1 if v["vix"] < 0 and win_score > 0 else 0
    align += 1 if v["vix"] > 0 and win_score < 0 else 0

    confidence = "ALTA" if align >= 5 else "MÉDIA" if align >= 3 else "BAIXA"

    macro_summary = (
        f"O pano de fundo mostra EUA {('fortes' if v['sp500'] > 0 and v['nasdaq'] > 0 else 'mistos/pressionados')}, "
        f"Europa {('positiva' if v['eurostoxx'] > 0 and v['dax'] > 0 else 'mista')}, "
        f"VIX {('cedendo' if v['vix'] < 0 else 'pressionando risco')} e DXY "
        f"{('fraco' if v['dxy'] < 0 else 'forte')}. "
        f"No Brasil, o Ibovespa Futuro está {('positivo' if v['ibov_fut'] > 0 else 'negativo' if v['ibov_fut'] < 0 else 'neutro')} "
        f"e o dólar/real {('alivia' if v['usdbrl'] < 0 or v['dolar_fut'] < 0 else 'pressiona' if v['usdbrl'] > 0 or v['dolar_fut'] > 0 else 'não confirma')}."
    )

    operational_plan = (
        f"WIN: {classify_bias(win_score, 'WIN')}. "
        f"Prefira {'compra em pullback ou continuação' if win_score > 2 else 'venda em repique ou perda de suporte' if win_score < -2 else 'espera por confirmação antes de entrar'}. "
        f"WDO: {classify_bias(wdo_score, 'WDO')}. "
        f"Prefira {'compra apenas em correção' if wdo_score > 2 else 'venda em repique/correção' if wdo_score < -2 else 'evitar forçar operação sem correlação clara'}."
    )

    invalidation = (
        "Esta leitura perde validade se o índice inverter o sinal enquanto o dólar inverter junto, "
        "ou se os futuros americanos mudarem de direção e o VIX acompanhar o movimento contrário. "
        "Em dias de abertura, revalide em 09:30–09:45; em intraday, revalide após 10:00 e 14:30."
    )

    executive_summary = (
        f"Regime atual: {regime}. "
        f"Viés do índice: {classify_bias(win_score, 'WIN')}. "
        f"Viés do dólar: {classify_bias(wdo_score, 'WDO')}. "
        f"Confiança {confidence.lower()} e força de virada em {turn_strength}%."
    )

    return {
        "meta": {"timestamp": parsed["timestamp"]},
        "regime": regime,
        "bias": {
            "win_label": classify_bias(win_score, "WIN"),
            "wdo_label": classify_bias(wdo_score, "WDO"),
        },
        "scores": {
            "win_score": win_score,
            "wdo_score": wdo_score,
            "macro_score": macro_score,
            "turn_strength": turn_strength,
        },
        "probabilities": {
            "continuação_alta": up,
            "continuação_baixa": down,
            "lateralização": side,
        },
        "confidence": confidence,
        "macro_summary": macro_summary,
        "operational_plan": operational_plan,
        "invalidation": invalidation,
        "executive_summary": executive_summary,
        "traps": traps,
    }
