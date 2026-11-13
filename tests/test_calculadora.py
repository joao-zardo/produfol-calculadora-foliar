import pytest
from app import create_app
from app.models import db, Usuario
from app.services import calcular_dosagem, gerar_resumo_whatsapp


def test_calculo_dosagem_exato():
    resultado = calcular_dosagem(area_hectares=25, dose_padrao_ha=0.5, volume_embalagem=5.0)
    assert resultado["volume_total"] == 12.5
    assert resultado["qtd_embalagens"] == 3


def test_calculo_dosagem_area_invalida():
    with pytest.raises(ValueError):
        calcular_dosagem(area_hectares=0, dose_padrao_ha=0.5, volume_embalagem=5.0)
    with pytest.raises(ValueError):
        calcular_dosagem(area_hectares=-10, dose_padrao_ha=0.5, volume_embalagem=5.0)


def test_resumo_whatsapp_formatacao():
    texto = gerar_resumo_whatsapp("Carlos Mendes", "Soja", 25, "NanoFoliar Soy", 0.5, 12.5, 3, 5.0)
    assert "Carlos Mendes" in texto
    assert "12,5 L" in texto
    assert "3 galões de 5 L" in texto


def test_hash_senha_pbkdf2():
    usuario = Usuario(nome="Teste", email="teste@produfol.com.br")
    usuario.set_senha("SenhaForte123")
    assert usuario.senha_hash != "SenhaForte123"
    assert usuario.senha_hash.startswith("pbkdf2:sha256")
    assert usuario.verificar_senha("SenhaForte123") is True
    assert usuario.verificar_senha("Errada") is False


def test_protecao_rotas_e_fluxo_autenticado():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    client = app.test_client()

    resp_sem_login = client.get("/nova-recomendacao")
    assert resp_sem_login.status_code == 302

    client.post("/login", data={"email": "janaina@produfol.com.br", "senha": "Produfol2026"})
    resp_calc = client.post(
        "/nova-recomendacao",
        data={"id_produtor": 1, "id_produto": 1, "cultura": "Soja", "area_hectares": "25"},
        follow_redirects=True,
    )
    assert resp_calc.status_code == 200
    assert "12.5 Litros" in resp_calc.get_data(as_text=True)
