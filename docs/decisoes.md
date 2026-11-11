# Decisões de arquitetura

Registro das decisões do FAMA Bot no formato **ADR** (*Architecture Decision Record*). Cada entrada traz o contexto, as alternativas consideradas, o que foi decidido e o custo disso.

Uma decisão aceita só muda com um motivo forte. Quando mudar, a entrada antiga continua aqui, marcada como **Substituída**, junto com a referência da nova.

| # | Decisão | Status |
|---|---|---|
| 001 | [Webhook em vez de polling](#001--receber-mensagens-por-webhook) | Aceita |
| 002 | [Flask no backend](#002--flask-no-backend) | Aceita |
| 003 | [SSE do backend para o tray](#003--sse-do-backend-para-o-tray) | Aceita |
| 004 | [Uma fila por pessoa](#004--uma-fila-por-pessoa) | Aceita |
| 005 | [Tray nativo com pystray + winotify](#005--app-de-bandeja-nativo) | Aceita |
| 006 | [Identificação da máquina por config.json](#006--identificação-da-máquina-por-configjson) | Aceita |
| 007 | [Um venv por componente](#007--um-venv-por-componente) | Aceita |
| 008 | [Segredos e dados reais fora do Git](#008--segredos-e-dados-reais-fora-do-git) | Aceita |
| 009 | [ngrok no desenvolvimento](#009--ngrok-no-desenvolvimento) | Aceita |

---

## 001 — Receber mensagens por webhook

**Contexto.** O backend precisa saber quando um cliente manda mensagem no WhatsApp.

**Alternativas.**
- **Polling:** o backend pergunta à API de tempos em tempos se chegou algo.
- **Webhook:** a Meta faz um `POST` para o backend no momento em que a mensagem chega.

**Decisão.** Webhook. A WhatsApp Cloud API foi feita para trabalhar assim.

**Por quê.**
- **Latência:** com polling, a resposta atrasa até um intervalo inteiro. Com webhook, ela é imediata.
- **Recursos:** com polling, a maioria das consultas volta vazia e só gasta CPU, rede e cota da API.
- **Falha silenciosa:** se o polling para, nada avisa, e as mensagens simplesmente não chegam. No webhook, a Meta registra as falhas de entrega e tenta de novo.

**Consequências.**
- O backend precisa de uma **URL pública com HTTPS** (ver [009](#009--ngrok-no-desenvolvimento)).
- Qualquer um pode chamar essa URL. Por isso é obrigatório validar o `hub.verify_token` (no GET de verificação) e a assinatura `X-Hub-Signature-256` (nos POSTs).
- O webhook precisa responder rápido (`200`), senão a Meta reenvia a mensagem. Trabalho demorado não pode travar a resposta.

---

## 002 — Flask no backend

**Contexto.** O backend é pequeno: um webhook, a lógica do menu, as filas e um endpoint SSE. O autor está aprendendo desenvolvimento web em Python.

**Alternativas.**
- **Django:** completo (ORM, admin, autenticação), mas pesado demais para um webhook com poucas rotas.
- **FastAPI:** moderno e assíncrono, o que se encaixa bem com conexões longas de SSE. Em troca, exige entender `async`/`await` logo de início.
- **Flask:** mínimo e síncrono, com pouca "mágica".

**Decisão.** Flask.

**Por quê.** Ele dá conta do escopo e deixa visível cada peça (rota, request, response), o que é bom para aprender. A escala é a de um escritório: poucos funcionários conectados e poucas mensagens por minuto.

**Consequências.**
- Cada conexão SSE ocupa uma thread enquanto fica aberta. O servidor de desenvolvimento do Flask não serve para isso em produção, então vai ser preciso um servidor com várias threads (`waitress`), como prevê a task 5.4.
- Se o número de conexões crescer muito, migrar para FastAPI é o caminho natural.

---

## 003 — SSE do backend para o tray

**Contexto.** Quando um cliente escolhe um setor, o PC do funcionário responsável precisa ser avisado na hora. O backend vai estar na internet, e os PCs ficam na rede interna do escritório, atrás de roteador e firewall.

**Alternativas.**
- **Backend chama o PC** (um `POST` direto para a máquina): cada PC precisaria rodar um servidor HTTP, ter IP conhecido e porta liberada no firewall/NAT. Isso é inviável na rede do escritório e frágil.
- **Tray faz polling no backend:** os mesmos problemas da [001](#001--receber-mensagens-por-webhook), multiplicados pelo número de PCs.
- **WebSocket:** canal bidirecional e persistente. Funciona, mas é mais complexo (protocolo próprio, *handshake* de *upgrade*), e o tray não tem nada a enviar.
- **SSE (Server-Sent Events):** o tray abre uma requisição HTTP comum e o backend mantém a resposta aberta, enviando eventos em texto conforme acontecem.

**Decisão.** SSE em `/eventos/<pessoa>`.

**Por quê.**
- A comunicação é **unidirecional** (backend → tray). Esse é exatamente o caso de uso do SSE.
- **Quem abre a conexão é o tray.** Conexões que *saem* da rede interna passam pelo firewall sem nenhuma configuração, e o PC não precisa de servidor nem de IP fixo.
- É HTTP puro: fácil de testar com `curl` ou no navegador, e passa por proxies.

**Consequências.**
- A conexão pode cair (Wi-Fi, reinício do backend). O tray precisa reconectar com *backoff* (task 6.2).
- Conexões ociosas podem ser derrubadas por proxies. O backend manda um *heartbeat* periódico (task 5.2).
- Se um dia o tray precisar enviar algo, como "marcar atendido", isso vai por um `POST` comum, separado. Não é motivo para trocar por WebSocket.

---

## 004 — Uma fila por pessoa

**Contexto.** Cada sub-opção do menu tem um responsável. Um evento precisa chegar só ao PC certo.

**Alternativas.**
- **Fila global:** todo evento entra numa fila só, e o endpoint SSE de cada pessoa filtra o que é dela.
- **Uma fila por pessoa:** o roteamento já coloca o evento na fila do destinatário.

**Decisão.** Uma fila por pessoa.

**Por quê.**
- Com fila global, cada conexão teria que olhar **todos** os eventos, e um consumidor poderia retirar da fila um evento que não é dele.
- Com filas separadas, `/eventos/<pessoa>` só lê a própria fila. A responsabilidade fica clara, e o teste também ("o evento do Fiscal-DAS caiu na fila da pessoa X?").

**Consequências.**
- As filas ficam em memória (`queue.Queue`, que é *thread-safe*). Se o backend reiniciar, os eventos pendentes se perdem. A persistência fica para a fase 8.
- Falta decidir o que acontece se a pessoa estiver offline: guardar até ela conectar, descartar ou avisar o cliente (task 5.5).

---

## 005 — App de bandeja nativo

**Contexto.** Os PCs do escritório são **fracos**. A notificação precisa ser visível e confiável, sem pesar na máquina.

**Alternativas.**
- **Notificação web (Chrome):** exige o navegador aberto o tempo todo, com uma aba específica. É pesado e fácil de fechar sem querer.
- **Electron:** embute um Chromium inteiro. Cada app consome centenas de MB de RAM.
- **ntfy.sh e serviços parecidos:** os eventos passariam por um servidor de terceiros (problema de LGPD) e o projeto ficaria dependente de um serviço externo.
- **Python nativo:** `pystray` para o ícone na bandeja, `winotify` para o toast nativo do Windows e Tkinter para a tela de configuração.

**Decisão.** Python nativo.

**Por quê.** É o mais leve dos quatro, usa a notificação do próprio Windows, não depende de terceiros e reaproveita a linguagem do backend.

**Consequências.**
- O app só funciona no Windows, o que não é problema porque o escritório inteiro usa Windows.
- Distribuição com PyInstaller, num `.exe` sem precisar instalar Python (ver [007](#007--um-venv-por-componente)).
- O consumo de memória e CPU precisa ser medido numa máquina fraca de verdade (task 10.1).

---

## 006 — Identificação da máquina por config.json

**Contexto.** Ao conectar, o tray precisa dizer "eu sou a pessoa X" para escutar a fila certa.

**Alternativas.**
- **IP:** com DHCP, o IP muda e duas pessoas podem trocar de endereço.
- **MAC address:** amarra a pessoa ao hardware. Trocar de PC, de placa de rede ou usar o notebook quebra tudo, e um PC compartilhado não funciona.
- **`config.json` local:** um arquivo com o identificador da pessoa, criado na 1ª execução por uma janelinha (`simpledialog`).

**Decisão.** `config.json`.

**Por quê.** Identifica a **pessoa**, e não a máquina ou a rede. É explícito, fácil de trocar e não depende da infraestrutura do escritório.

**Consequências.**
- O arquivo pode conter dado pessoal, então fica fora do Git ([008](#008--segredos-e-dados-reais-fora-do-git)).
- Um identificador digitado errado faria a pessoa escutar uma fila que ninguém usa. O tray valida o identificador com o backend (task 7.3).
- Não é autenticação: qualquer um que saiba o identificador consegue escutar a fila. Para a rede interna e para o escopo atual isso é aceitável, mas fica registrado como limitação.

---

## 007 — Um venv por componente

**Contexto.** O repositório tem dois programas com dependências bem diferentes. O backend usa Flask e afins. O tray usa `pystray`, Pillow e `winotify`.

**Alternativas.**
- **Um venv único na raiz:** mais simples de configurar.
- **Um venv por componente** (`backend/.venv`, `tray_app/.venv`), cada um com o seu `requirements.txt`.

**Decisão.** Um venv por componente.

**Por quê.**
- O **PyInstaller** empacota o que está no ambiente. Com venv único, Flask e companhia iriam parar dentro do `.exe` que roda nas máquinas fracas.
- O backend vai para um container **Docker** com o próprio `requirements.txt`, sem bibliotecas de interface do Windows.
- Cada `requirements.txt` documenta exatamente do que aquele componente depende.

**Consequências.** São dois ambientes para ativar. É preciso prestar atenção em qual está ativo, inclusive no interpretador selecionado no VS Code.

---

## 008 — Segredos e dados reais fora do Git

**Contexto.** O repositório é **público** (portfólio). O sistema lida com tokens da Meta, nomes e telefones de funcionários e mensagens de clientes, que são dados pessoais pela LGPD.

**Decisão.**
- Os tokens ficam só em `backend/.env`, que é ignorado pelo Git. No repositório vai o `backend/.env.example`, com as chaves vazias.
- O mapeamento real setor → pessoa → contato fica em `backend/responsaveis.json`, também ignorado. No repositório vai um `.example` com dados fictícios.
- O `config.json` do tray é ignorado.
- O conteúdo das mensagens dos clientes não vai para o log. Os testes usam dados fictícios.

**Por quê.** Qualquer coisa que entra no histórico do Git de um repositório público deve ser tratada como vazada, mesmo que depois seja apagada. Robôs varrem o GitHub atrás de tokens em minutos.

**Consequências.** Quem clona precisa criar os arquivos locais a partir dos `.example`. Se um segredo vazar, ele precisa ser **revogado** na Meta. Apagar do Git não basta.

---

## 009 — ngrok no desenvolvimento

**Contexto.** O webhook exige uma URL pública com HTTPS ([001](#001--receber-mensagens-por-webhook)), e em desenvolvimento o Flask roda em `localhost`.

**Decisão.** Usar o **ngrok** para criar um túnel HTTPS público até o `localhost`.

**Por quê.** Permite receber mensagens reais da Meta sem fazer deploy a cada mudança.

**Consequências.** No plano gratuito, a URL muda a cada execução, e é preciso reconfigurar o webhook na Meta. Isso vale só para desenvolvimento. Em produção, o backend vai para uma hospedagem com URL fixa (task 10.3).
