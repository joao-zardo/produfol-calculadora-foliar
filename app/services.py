import math


def _formatar_numero_br(valor: float) -> str:
    texto = f"{valor:.2f}".rstrip("0").rstrip(".")
    return texto.replace(".", ",")


def calcular_dosagem(area_hectares: float, dose_padrao_ha: float, volume_embalagem: float) -> dict:
    try:
        area = float(area_hectares)
        dose = float(dose_padrao_ha)
        embalagem = float(volume_embalagem)
    except (TypeError, ValueError) as exc:
        raise ValueError("Os parâmetros numéricos do cálculo são inválidos.") from exc

    if area <= 0:
        raise ValueError("A área da lavoura deve ser maior que zero hectares.")
    if dose <= 0 or embalagem <= 0:
        raise ValueError("A dose padrão e o volume da embalagem devem ser maiores que zero.")

    volume_total = round(area * dose, 2)
    qtd_embalagens = math.ceil(volume_total / embalagem)

    return {
        "volume_total": volume_total,
        "qtd_embalagens": qtd_embalagens,
    }


def gerar_resumo_whatsapp(
    produtor_nome: str,
    cultura: str,
    area_hectares: float,
    produto_nome: str,
    dose_padrao_ha: float,
    volume_total: float,
    qtd_embalagens: int,
    volume_embalagem: float,
) -> str:
    area_fmt = _formatar_numero_br(area_hectares)
    dose_fmt = _formatar_numero_br(dose_padrao_ha)
    total_fmt = _formatar_numero_br(volume_total)
    emb_fmt = _formatar_numero_br(volume_embalagem)
    unidade = "galão" if qtd_embalagens == 1 else "galões"

    return (
        f"*Recomendação Técnica Produfol* | "
        f"Produtor: {produtor_nome} | "
        f"Cultura: {cultura} ({area_fmt} ha) | "
        f"Produto: {produto_nome} (Dose: {dose_fmt} L/ha) | "
        f"Total: {total_fmt} L ({qtd_embalagens} {unidade} de {emb_fmt} L)"
    )
