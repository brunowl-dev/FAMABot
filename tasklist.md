# Tasklist — FAMA Bot

Legenda: `[x]` pronto · `[~]` em andamento · `[ ]` pendente.
Uma task só é marcada `[x]` depois do commit e de o Bruno explicar com as palavras dele o que foi feito.

## Já feito (antes do plano)
- [x] Tray app Etapa 1: ícone + menu (`pystray`)
- [x] Tray app Etapa 2: notificações toast (`winotify`)
- [x] Tray app Etapa 3: loop paralelo ao ícone com `threading.Event`

## Fase 0 — Organização
- [x] 0.1 Estruturar o repositório
  - [x] Pastas `backend/`, `tray_app/`, `tests/`, `docs/` e arquivos movidos
  - [x] venv + `requirements.txt` do tray
  - [x] venv + `requirements.txt` do backend
  - [x] `.gitignore`
  - [x] `.env.example` (em `backend/`)
- [x] 0.2 `CLAUDE.md` e README inicial
- [x] 0.3 `docs/decisoes.md`: decisões arquiteturais e o motivo de cada descarte
- [x] 0.4 Revisar o tray app (Etapas 1 a 3) e propor refatoração mínima
  - [x] Renomear `testes.py` → `tray.py`
  - [x] Caminho do logo via `Path(__file__)` (constante `LOGO`)
  - [x] Extrair `cria_notificacao` (sem repetir `Notification`)
  - [x] Inverter threads: `icon.run()` na thread principal, loop numa thread `daemon`

## Fase 1 — Back-end base (Flask)
- [ ] 1.1 App Flask com `/health` e tratamento de erros
- [ ] 1.2 Configuração via `.env`
- [ ] 1.3 Testes básicos com pytest

## Fase 2 — Webhook do WhatsApp
- [ ] 2.1 Criar o app na Meta (Cloud API, número de teste) e entender o fluxo
- [ ] 2.2 GET de verificação (`hub.verify_token`)
- [ ] 2.3 POST que recebe mensagens e loga o JSON bruto para inspeção
- [ ] 2.4 Expor via ngrok e receber uma mensagem real
- [ ] 2.5 Validar `X-Hub-Signature-256`
- [ ] 2.6 Extrair número, texto e tipo, e ignorar notificações de status

## Fase 3 — Máquina de estados do menu
- [ ] 3.1 Menu como dados (setores, sub-opções, responsáveis)
- [ ] 3.2 Estado da conversa por cliente
- [ ] 3.3 Entradas inválidas, "voltar", "sair", mensagens fora do menu
- [ ] 3.4 TDD do roteamento

## Fase 4 — Envio de respostas
- [ ] 4.1 Enviar texto pela Cloud API (`requests`)
- [ ] 4.2 Menu interativo (botões/lista) vs. numerado: comparar e decidir
- [ ] 4.3 Janela de 24h, regras da Meta e o que muda em produção

## Fase 5 — Fila por pessoa e SSE
- [ ] 5.1 Filas em memória, uma por responsável
- [ ] 5.2 Endpoint SSE `/eventos/<pessoa>` com heartbeat
- [ ] 5.3 Roteamento → evento na fila certa
- [ ] 5.4 Concorrência com conexões longas (`waitress`/`gunicorn`)
- [ ] 5.5 Eventos com a pessoa offline: decidir e implementar

## Fase 6 — Tray app: cliente SSE
- [ ] 6.1 Conectar ao `/eventos/<pessoa>` numa thread sem travar o ícone
- [ ] 6.2 Reconexão automática com backoff
- [ ] 6.3 Toast com cliente, setor e assunto
- [ ] 6.4 Encerramento limpo da thread

## Fase 7 — Configuração local do tray
- [ ] 7.1 `config.json` com o identificador
- [ ] 7.2 Setup na 1ª execução (`simpledialog`)
- [ ] 7.3 Validar o identificador contra o backend

## Fase 8 — Persistência e histórico
- [ ] 8.1 SQLite: clientes, atendimentos, eventos
- [ ] 8.2 Registrar atendimentos sem conteúdo sensível desnecessário
- [ ] 8.3 Marcar "atendido" pela notificação ou pelo menu do ícone

## Fase 9 — Robustez
- [ ] 9.1 Logs e níveis de log
- [ ] 9.2 Falhas: Meta fora do ar, backend caindo, tray offline
- [ ] 9.3 Teste ponta a ponta

## Fase 10 — Empacotamento e implantação
- [ ] 10.1 PyInstaller + medir memória/CPU numa máquina fraca
- [ ] 10.2 Iniciar com o Windows
- [ ] 10.3 Hospedar o backend (sair do ngrok) e configurar o webhook definitivo
- [ ] 10.4 Dockerfile do backend

## Fase 11 — Documentação e portfólio
- [ ] 11.1 README completo
- [ ] 11.2 Diagramas de arquitetura e de sequência
- [ ] 11.3 Prints/GIF com dados fictícios
- [ ] 11.4 O que aprendi e o que faria diferente

## Pendências conhecidas
- Tray: renomear funções e variáveis para `snake_case` (PEP 8)
