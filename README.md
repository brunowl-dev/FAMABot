# FAMA Bot — Atendimento automatizado via WhatsApp

Chatbot de WhatsApp para automatizar o atendimento de clientes de uma contabilidade (FAMA), roteando o cliente para o setor correto (Contábil, Fiscal, RH, Administrativo) e notificando os funcionários responsáveis em tempo real, através de uma aplicação leve rodando na bandeja do sistema (system tray) de cada máquina.

## Contexto

O escritório conta com máquinas de baixo desempenho, então a arquitetura evita soluções pesadas em recursos (como navegador sempre aberto). A notificação chega via aplicação nativa de bandeja, conectada ao backend em tempo real (WebSocket), sem polling.

## Stack

- **Backend**: Python + Flask (modelo event-driven via webhook)
- **Notificações**: Python + `pystray` (ícone de bandeja) + `winotify` (toast nativo do Windows)
- **Comunicação backend ↔️ tray app**: WebSocket
- **WhatsApp**: WhatsApp Cloud API (Meta)
- **Desenvolvimento local**: ngrok (tunelamento do webhook)

## Roadmap de versões

### v1 — Aplicação de bandeja (tray app)
Aplicação Python que roda na bandeja do sistema, com ícone, menu e disparo de notificações nativas (toast). Nessa etapa ainda não há integração com WhatsApp ou backend — é a base da aplicação cliente.

### v2 — Configuração do bot no WhatsApp
Configuração da conta no Meta for Developers, número de teste, webhook (Flask + ngrok) e menu de opções (Contábil, Fiscal, RH, Administrativo, Dúvidas, Sair) no fluxo de conversa do WhatsApp.

### v3 — Integração aplicação ↔ bot
Conexão entre o backend do bot e as aplicações de bandeja via WebSocket, permitindo que o servidor envie eventos para os clientes conectados.

### v4 — Disparo de notificações a partir do WhatsApp
Fechamento do fluxo completo: cliente escolhe uma opção no menu do WhatsApp → backend identifica o setor → evento é enviado via WebSocket → aplicação de bandeja do(s) funcionário(s) do setor exibe a notificação nativa.

## Status atual

🚧 Em desenvolvimento — v1 em andamento.