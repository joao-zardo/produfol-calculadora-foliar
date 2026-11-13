from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256), nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)

    def set_senha(self, senha: str) -> None:
        if not senha or len(senha) < 8:
            raise ValueError("A senha deve ter no mínimo 8 caracteres.")
        self.senha_hash = generate_password_hash(senha, method="pbkdf2:sha256:600000")

    def verificar_senha(self, senha: str) -> bool:
        return check_password_hash(self.senha_hash, senha)


class Produto(db.Model):
    __tablename__ = "produtos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), unique=True, nullable=False)
    dose_padrao_ha = db.Column(db.Float, nullable=False)
    volume_embalagem = db.Column(db.Float, nullable=False)
    culturas_indicadas = db.Column(db.String(200), nullable=False, default="Soja, Milho, Trigo")
    ativo = db.Column(db.Boolean, default=True, nullable=False)


class Produtor(db.Model):
    __tablename__ = "produtores"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    municipio = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(30), nullable=True)
    propriedade = db.Column(db.String(150), nullable=True)
    ativo = db.Column(db.Boolean, default=True, nullable=False)


class Recomendacao(db.Model):
    __tablename__ = "recomendacoes"

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    id_produto = db.Column(db.Integer, db.ForeignKey("produtos.id"), nullable=False)
    id_produtor = db.Column(db.Integer, db.ForeignKey("produtores.id"), nullable=False)
    cultura = db.Column(db.String(60), nullable=False)
    area_hectares = db.Column(db.Float, nullable=False)
    volume_total = db.Column(db.Float, nullable=False)
    qtd_embalagens = db.Column(db.Integer, nullable=False)
    data_criacao = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    usuario = db.relationship("Usuario", backref="recomendacoes")
    produto = db.relationship("Produto", backref="recomendacoes")
    produtor = db.relationship("Produtor", backref="recomendacoes")
