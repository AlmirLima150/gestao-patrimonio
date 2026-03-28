⛪ Sistema de Gestão de Patrimônio e Termos de Concessão
Este projeto nasceu de uma necessidade real: organizar e controlar o fluxo de equipamentos (notebooks, instrumentos musicais, projetores, etc.) de uma comunidade religiosa.

Como estudante de Sistema da informação, desenvolvi esta API para substituir controles manuais por uma solução automatizada que garante a integridade do inventário e a formalização das responsabilidades de uso.

🎯 O Problema & A Solução
O Desafio: Dificuldade em rastrear quem estava com determinado equipamento, falta de histórico de devoluções e incerteza sobre a quantidade de itens disponíveis no estoque para eventos.

A Solução: Uma API robusta que:

Centraliza o cadastro de Coordenadores e Patrimônios.

Automatiza a baixa de estoque no momento da retirada.

Gera Documentação Física (PDF) automática para assinatura, trazendo segurança jurídica e organizacional para a instituição.

🛠️ Tecnologias Utilizadas
O projeto utiliza uma stack moderna e escalável, ideal para ambientes de produção:

Linguagem: Python 3.11

Framework Web: FastAPI (Alta performance e documentação automática)

Banco de Dados: PostgreSQL 15

ORM: SQLModel (Baseado em SQLAlchemy e Pydantic)

Containerização: Docker & Docker-Compose

Geração de Documentos: FPDF2

Documentação: Swagger UI (OpenAPI)

🏗️ Estrutura do Projeto
Plaintext
├── backend/
│   ├── app/
│   │   ├── main.py          # Configurações da API e Rotas
│   │   ├── models.py        # Definição das tabelas do banco de dados
│   │   └── database.py      # Conexão e sessão do SQLAlchemy
│   ├── Dockerfile           # Receita para o container do backend
│   └── requirements.txt     # Dependências do projeto
├── temp_pdfs/               # Volume local para armazenamento dos termos gerados
├── .env                     # Variáveis de ambiente (não versionado)
└── docker-compose.yml       # Orquestração do App e Banco de Dados

🚀 Como Rodar o Projeto
Clone o repositório:

Bash
git clone https://github.com/seu-usuario/gestao-patrimonio-igreja.git
cd gestao-patrimonio-igreja
Configure as variáveis de ambiente:
Crie um arquivo .env na raiz do projeto com as credenciais do banco (veja o arquivo .env.example).

Suba os containers:

Bash
docker-compose up --build
Acesse a API:
Acesse http://localhost:8000/docs para visualizar e testar as rotas através da interface interativa do Swagger.

📊 Regras de Negócio Implementadas
Validação de Estoque: O sistema impede a criação de um termo se a quantidade solicitada for superior à disponível no banco de dados.

Baixa Automática: Ao vincular um item a um termo, o saldo disponível do patrimônio é subtraído instantaneamente.

Geração de Termo (PDF): Gera um documento formatado com os dados do coordenador, data de concessão, lista de itens e campo de assinatura.

Persistência: Utilização de volumes Docker para garantir que os dados do banco e os PDFs gerados não sejam perdidos ao reiniciar os containers.

🌟 Diferenciais Técnicos
Documentação Organizada: Rotas agrupadas por tags (Gestão, Inventário, Documentos) para facilitar o entendimento.

Tratamento de Erros: Respostas HTTP semânticas (404 para itens não encontrados, 400 para erros de estoque).

Código Limpo: Separação de responsabilidades e uso de tipagem estática com Python.

👨‍💻 Autor
Almir Lima
Estudante de Sistemas de Informação (SI).
