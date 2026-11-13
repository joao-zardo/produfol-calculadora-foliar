import os
from flask import Flask, render_template_string
from dotenv import load_dotenv
from app.models import db, Usuario, Produto, Produtor

load_dotenv()


def create_app(test_config=None):
    app = Flask(__name__)

    database_url = os.getenv("DATABASE_URL", "sqlite:///produfol_mvp.db")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "chave-desenvolvimento-produfol-2026")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    @app.after_request
    def aplicar_cabecalhos_seguranca(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net;"
        )
        return response

    @app.errorhandler(404)
    def pagina_nao_encontrada(_error):
        return render_template_string("<h1>404 - Página não encontrada</h1><a href='/'>Voltar</a>"), 404

    @app.errorhandler(500)
    def erro_interno(_error):
        return render_template_string("<h1>500 - Erro interno no processamento</h1><a href='/'>Voltar</a>"), 500

    from app.routes import bp
    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()
        _popular_dados_iniciais()

    return app


def _popular_dados_iniciais():
    if not Usuario.query.filter_by(email="janaina@produfol.com.br").first():
        gestora = Usuario(nome="Janaina Seraglio", email="janaina@produfol.com.br", ativo=True)
        gestora.set_senha("Produfol2026")
        db.session.add(gestora)

    if not Produto.query.first():
        db.session.add_all([
            Produto(nome="NanoFoliar Soy", dose_padrao_ha=0.5, volume_embalagem=5.0, culturas_indicadas="Soja"),
            Produto(nome="NanoFoliar Corn", dose_padrao_ha=0.75, volume_embalagem=5.0, culturas_indicadas="Milho"),
        ])

    if not Produtor.query.first():
        db.session.add(
            Produtor(
                nome="Carlos Alberto Mendes",
                municipio="Lagoa Vermelha/RS",
                telefone="(54) 99999-0001",
                propriedade="Fazenda Boa Vista",
            )
        )

    db.session.commit()
