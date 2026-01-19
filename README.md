# Job Scout

Este projeto é uma ferramenta automatizada para buscar e avaliar vagas de emprego, utilizando um Large Language Model (LLM) para pontuar as vagas de acordo com o seu perfil e notificar você via Telegram.

## Configuração do Ambiente

Siga os passos abaixo para configurar e executar o Job Scout em sua máquina.

### 1. Clonar o Repositório

Primeiro, clone o repositório para a sua máquina local:

```bash
git clone https://github.com/seu-usuario/job-scout.git
cd job-scout
```

### 2. Criar e Ativar um Ambiente Virtual

É altamente recomendado o uso de um ambiente virtual para isolar as dependências do projeto.

```bash
python -m venv .venv
# No Windows
.venv\Scripts\activate
# No macOS/Linux
source .venv/bin/activate
```

### 3. Instalar Dependências

Você pode usar `uv` (recomendado para maior velocidade) ou `pip` para instalar as dependências.

#### Usando `uv` (Recomendado)

Se você ainda não tem `uv` instalado, pode aprender a instalá-lo em seu [repositório oficial](https://github.com/astral-sh/uv)

Com `uv` instalado, execute:

```bash
uv sync
```

#### Usando `pip`

```bash
pip install -e .
```

### 4. Instalar o Chromium para Playwright (Patchright)

O projeto utiliza `patchright` (um fork do Playwright) para automação do navegador. Você precisa instalar os drivers do Chromium:

```bash
patchright install chromium
```

### 5. Configurar Variáveis de Ambiente

Copie o arquivo de exemplo de variáveis de ambiente e preencha com suas credenciais:

```bash
cp .env.example .env
# No Windows, você pode usar: copy .env.example .env
```

Edite o arquivo `.env` e preencha as seguintes variáveis:

*   `ROUTELLM_API_KEY`: Sua chave de API da Abacus.AI para acessar o serviço RouteLLM, que é usado para a avaliação das vagas.
*   *AINDA NÃO DISPONÍVEL* `OPENAI_API_KEY`: Caso você queira usar a API da OpenAI diretamente no futuro. Atualmente, o projeto está configurado para usar RouteLLM.
*   `LLM_MODEL`: O modelo de linguagem a ser utilizado para a avaliação. Exemplos sugeridos incluem `gpt-4o-mini`, `gpt-4o`, `claude-3-5-sonnet`.
*   `DB_PATH`: O caminho para o arquivo de banco de dados SQLite onde as informações das vagas processadas serão armazenadas (ex: `data/jobs.db`).
*   `TELEGRAM_BOT_TOKEN`: O token do seu bot do Telegram, necessário para receber notificações.
*   `TELEGRAM_CHAT_ID`: O ID do chat/usuário do Telegram para o qual as notificações serão enviadas.

Para obter o `TELEGRAM_BOT_TOKEN` e o `TELEGRAM_CHAT_ID`, siga estes passos:
1.  **Crie um bot e obtenha o token:** Fale com o [@BotFather](https://t.me/BotFather) no Telegram, envie o comando `/newbot` e siga as instruções. Ele fornecerá um token de API.
2.  **Obtenha o Chat ID:**
    *   Inicie uma conversa com o seu novo bot.
    *   Envie qualquer mensagem para ele.
    *   Use um bot como o [@getidsbot](https://t.me/getidsbot) ou acesse a URL `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates` (substituindo `<SEU_TOKEN>` pelo token do seu bot) para ver o ID do seu chat.

Assista a este [vídeo tutorial para um guia visual](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnjnN41qzRi7yMLCEGy75PdIkXPvwIz-JYSEC65jp8S_DaVwlyWupr-DWds_DRQRDEYFaszzQmIDCBAJ4tJwTMe1lruwz9s0JRgbFK2RI9gI8QgchiRp4SnYY00FDohfxcIhtHrN8=).

### 6. Configurar Seu Currículo (`resume.md`)

Copie o arquivo de exemplo do currículo:

```bash
cp resume.md.example resume.md
# No Windows, você pode usar: copy .env.example .env
```

Edite o arquivo `resume.md` com as informações do seu currículo. Este arquivo será usado pelo LLM para entender sua experiência e qualificações ao avaliar as vagas.

### 7. Configurar Seu Perfil (`profile.yaml`)

Copie o arquivo de exemplo do perfil:

```bash
cp profile.yaml.example profile.yaml
# No Windows, você pode usar: copy .env.example .env
```

Edite o arquivo `profile.yaml` para definir suas preferências de vaga. Este arquivo permite que você especifique:

*   `target_seniority`: Senioridades desejadas (ex: `pleno`, `senior`).
*   `must_have`: Tecnologias obrigatórias em uma vaga.
*   `avoid`: Tecnologias ou termos a serem evitados.
*   `min_score_to_notify`: Pontuação mínima (0-100) para que uma vaga dispare uma notificação.
*   `language`: Idioma do prompt/resposta do LLM.
*   `notes`: Notas extras sobre suas preferências.

### 8. Executar o Projeto

Após todas as configurações, você pode executar o Job Scout:

```bash
python -m app.main
```

O script irá buscar, avaliar e, se houver vagas de alta pontuação, notificar você. Você pode configurar este comando para rodar periodicamente usando um `crontab` ou um agendador de tarefas.
