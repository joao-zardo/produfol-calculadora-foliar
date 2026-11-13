# Calculadora e Histórico de Recomendação Foliar — Produfol

MVP desenvolvido como Projeto de Software para otimizar o atendimento técnico-comercial da **Produfol Comércio de Fertilizantes** (Lagoa Vermelha/RS), automatizando o cálculo de dosagem por hectare de fertilizantes foliares com nanotecnologia e centralizando o histórico de recomendações aos produtores rurais.

## Alinhamento Social (ODS)
* **ODS 2 — Fome Zero e Agricultura Sustentável (Meta 2.4):** Redução de erros humanos na dosagem de insumos concentrados, evitando desperdício financeiro e impactos ambientais por superdosagem nas lavouras regionais.

## Arquitetura e Pilha Tecnológica
* **Padrão Arquitetural:** Arquitetura Monolítica em Camadas (**MVC + Service Layer**).
* **Linguagem / Runtime:** Python 3.12
* **Framework Web & Templates:** Flask 3.0.3 (Jinja2) + Bootstrap 5.3.3 (responsivo e acessível — WCAG 2.1 AA)
* **Persistência:** Flask-SQLAlchemy 3.1.1 + PostgreSQL 16 (gerenciado via Supabase)
* **Segurança:** Autenticação com hash robusto `PBKDF2-SHA256` (`werkzeug.security`), consultas parametrizadas via ORM, proteção contra XSS e controle de acesso por sessão.
* **Testes e Produção:** Pytest 8.3.4 e Gunicorn 22.0.0

## Estrutura do Projeto
```text
produfol-calculadora-foliar/
├── app/
│   ├── __init__.py       # Inicialização da aplicação, banco e cabeçalhos de segurança
│   ├── models.py         # Camada Model (usuarios, produtos, produtores, recomendacoes)
│   ├── services.py       # Service Layer (cálculo de dose, embalagens e resumo WhatsApp)
│   ├── routes.py         # Camada Controller (rotas protegidas e validações no servidor)
│   └── templates/        # Camada View (interfaces HTML5 responsivas)
├── tests/                # Suíte de testes unitários e de integração (Pytest)
├── .github/workflows/    # Pipeline de Integração Contínua (GitHub Actions)
├── .env.example          # Modelo de variáveis de ambiente
├── requirements.txt      # Dependências do projeto
└── run.py                # Ponto de entrada da aplicação
```

## Como Executar Localmente
```bash
python -m venv venv
# Windows: venv\Scripts\activate | Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```