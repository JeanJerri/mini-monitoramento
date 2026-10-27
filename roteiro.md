# 📋 Roteiro Oficial de Apresentação na Bancada — Mini Monitoramento SNMP

> **Trabalho Prático:** Projeto e Administração de Redes  
> **Objetivo:** Guia passo a passo para demonstrar a aplicação ao professor na bancada, cobrindo **100% dos critérios de avaliação do edital** com dados reais de rede, sem simulações sintéticas.

---

## 🎯 Sumário dos Critérios de Avaliação e Pesos

| # | Critério de Avaliação | Peso | O que será avaliado pelo professor |
| :-: | :--- | :-: | :--- |
| **1** | **Coleta SNMP e Cálculos** | **25%** | Leitura das OIDs oficiais, fórmula de taxa em bps ($\Delta t$), contadores 32/64 bits e CPU. |
| **2** | **Gráficos Real Time e Controles** | **20%** | Janela deslizante contínua, botões `Iniciar`, `Pausar` e `Resetar`, fluidez e threshold. |
| **3** | **Sistema de Alertas e Histerese** | **20%** | Pop-up, e-mail (SMTP real), canais simultâneos e debounce (não enviar spam). |
| **4** | **Histórico e Persistência** | **15%** | Base prévia de 2h de dados reais capturados (`medicoes.csv`), filtro data/hora e exportação. |
| **5** | **Configuração e Resiliência** | **10%** | Validação de intervalo $> 0$, e-mail válido, tratamento de timeout/quedas sem travar. |
| **6** | **Documentação e Código** | **10%** | Repositório Git, README claro, modularidade e rastreabilidade técnica. |

---

## ⚙️ Preparação Inicial: Escolha do Ambiente de Execução (3 Opções)

Você pode apresentar o sistema utilizando qualquer uma das 3 opções abaixo. Todas operam **100% via protocolo SNMP real**:

### Opção 1: Roteador Físico de Laboratório (Cisco ou MikroTik)
1. Conecte o cabo de rede Ethernet do seu notebook a uma porta LAN do roteador.
2. Identifique o IP do roteador (ex.: `192.168.88.1` no MikroTik, `192.168.1.1` ou `10.0.0.1` no Cisco).
3. Abra o dashboard pelo arquivo `iniciar_dashboard.bat`.
4. No botão **Configurações (Cfg ⚙️)**:
   * **IP do Roteador:** Digite o IP do roteador físico.
   * **Porta:** `161` | **Comunidade:** Comunidade SNMP do laboratório (ex.: `public`).
   * **Interface (ifIndex):** Use o botão *"Descobrir Interfaces"* e selecione a porta conectada.

### Opção 2: MikroTik RouterOS CHR no VirtualBox (Orientação Oficial)
1. No VirtualBox, selecione a VM do MikroTik CHR $\rightarrow$ **Configurações** $\rightarrow$ **Rede**:
   * **Adaptador 1:** Defina como **Placa em modo Bridge** (Bridged) com seu Wi-Fi/Ethernet OU **Placa exclusiva de hospedeiro** (Host-Only).
2. Ligue a VM, faça login como `admin` (sem senha) e consulte o IP recebido:
   ```routeros
   /snmp set enabled=yes
   /snmp community add name=public read-access=yes
   /ip address print
   ```
3. No Dashboard (**Cfg ⚙️**), insira o IP retornado pelo comando acima (ex.: `192.168.56.10` ou `192.168.1.X`), porta `161`, comunidade `public` e interface `1` ou `2`.

### Opção 3: MikroTik RouterOS CHR via Docker (Ambiente Automatizado Local)
1. Dê dois cliques no arquivo `iniciar_mikrotik_docker.bat` (sobe o container MikroTik na porta `161/udp` e o servidor SMTP MailHog na porta `8025`).
2. Abra o dashboard pelo arquivo `iniciar_dashboard.bat`.
3. No Dashboard (**Cfg ⚙️**), confirme:
   * **IP do Roteador:** `127.0.0.1` | **Porta:** `161` | **Comunidade:** `public`
   * **Interface (ifIndex):** `2` (`ether1` no RouterOS).
   * **Perfil de CPU:** `MikroTik RouterOS CHR`.

---

## 🎬 Passo a Passo da Apresentação na Bancada

Siga esta sequência quando o professor estiver na sua bancada:

```
[ 1. Histórico 2h ] ➔ [ 2. Controles RT ] ➔ [ 3. SNMP & Fórmulas ] 
➔ [ 4. Carga Real & Alertas ] ➔ [ 5. Resiliência ] ➔ [ 6. Código & Git ]
```

---

### Passo 1: Comprovar a Carga Inicial de 1 a 2 Horas
> **Critério Avaliado:** Histórico e Persistência (Peso: 15%)

1. **O que fazer na tela:**
   * Vá direto no bloco inferior do dashboard (**Filtro de Histórico**).
   * Clique no botão de atalho rápido **"Últimas 2 horas"** (ou preencha a data e hora do período da captura prévia).
   * Clique em **"Filtrar Período"**.
2. **O que mostrar e falar ao professor:**
   > *"Professor, cumprindo a exigência de termos no mínimo 1 a 2 horas de dados reais pré-coletados, aqui está a nossa base contínua com centenas de amostras reais registradas a cada intervalo pelo coletor SNMP e gravadas em disco no arquivo `data/medicoes.csv`."*
3. Mostre os dois gráficos estáticos de **Tráfego IN/OUT** e **Utilização de CPU**, destacando que não há falhas ou buracos nos dados.
4. Abra o expander **"Tabela de Registros Históricos (CSV)"** e mostre as medições com data/hora, taxas em bps e clique no botão **"Exportar Amostras (CSV)"** para mostrar a capacidade de auditoria.

---

### Passo 2: Demonstrar os Controles e Gráficos em Tempo Real
> **Critério Avaliado:** Gráficos Real Time e Controles (Peso: 20%)

1. **O que fazer na tela:**
   * Suba para o bloco superior (**Painel Tempo Real**).
   * Clique no botão **`▶ Iniciar`**:
     * Aponte para o badge verde **"Coleta Ativa"** e mostre a **janela deslizante** atualizando continuamente a cada intervalo configurado (ex.: 5s).
     * Destaque as **linhas tracejadas vermelhas** indicando os limiares de tráfego e CPU.
   * Clique no botão **`⏸ Pausar`**:
     * Mostre que o painel congela instantaneamente, preservando todos os pontos já desenhados na tela para inspeção técnica sem interromper a execução do app.
   * Clique no botão **`↻ Resetar Tela`**:
     * Mostre que a visualização em tempo real é limpa para uma nova observação, **sem apagar ou corromper** a base de dados histórica gravada no arquivo `medicoes.csv`.
   * Clique novamente em **`▶ Iniciar`** para manter o fluxo ativo.

---

### Passo 3: Explicar a Coleta SNMP e os Cálculos Matemáticos
> **Critério Avaliado:** Coleta SNMP e Cálculos (Peso: 25%)

1. **O que fazer na tela:**
   * Clique no botão **Configurações (Cfg ⚙️)** no cabeçalho.
   * Mostre os parâmetros configurados (IP, porta, comunidade, versão SNMP e ifIndex).
   * Clique no botão **"Testar SNMP"** e aponte para a mensagem de sucesso: `RouterOS CHR conectado`.
2. **O que explicar ao professor sobre a matemática implementada:**
   * **Cálculo da Taxa em bps:**
     $$\text{Taxa (bps)} = \frac{(\text{Bytes}_{\text{atual}} - \text{Bytes}_{\text{anterior}}) \times 8}{\Delta t}$$
     * Mostre que $\Delta t$ é medido com precisão de microssegundos via `time.time()` entre duas amostras sucessivas.
     * Os octetos são multiplicados por $8$ para conversão exata de bytes em bits por segundo.
   * **Proteção contra Counter Rollover (32 bits):**
     * Contadores SNMP MIB-II de 32 bits estouram em $2^{32} - 1 = 4.294.967.295$ e voltam a zero.
     * Quando $\text{Bytes}_{\text{atual}} < \text{Bytes}_{\text{anterior}}$, o código aplica a compensação de módulo:
       $$\Delta\text{Bytes} = (4.294.967.296 - \text{Bytes}_{\text{anterior}}) + \text{Bytes}_{\text{atual}}$$
       evitando taxas negativas irreais.
     * Além disso, suporta contadores de 64 bits (`ifHCInOctets` / `ifHCOutOctets`) para interfaces de alta velocidade.
   * **Utilização de CPU (%):**
     * Consulta direta às OIDs oficiais: `hrProcessorLoad` (RFC 2790 universal) e `mtxrProcessorLoad` (Enterprise MikroTik).

---

### Passo 4: Demonstrar a Reatividade ao Tráfego Real e o Sistema de Alertas
> **Critério Avaliado:** Sistema de Alertas (Peso: 20%)

1. **Preparar os Limiares (na janela `Cfg ⚙️` $\rightarrow$ aba *Limiares e Alertas*):**
   * Marque **[x] Pop-up na Interface** e **[x] Notificação por E-mail (SMTP)** simultaneamente (cumprindo a exigência de seleção múltipla do PDF).
   * Configure um threshold de teste fácil de ultrapassar:
     * **Threshold de Tráfego:** `50.000 bps` (ou `100.000 bps`).
     * **Threshold de CPU:** `20%` (ou `30%`).
   * Clique em **Salvar Configurações**.
2. **Gerar Carga Real no Terminal (CMD / PowerShell):**
   * Abra o **PowerShell** ou **CMD** ao lado do navegador.
   * **Se estiver no VirtualBox ou Roteador Físico:**
     Execute o ping com pacotes de 6.000 bytes em loop:
     ```cmd
     ping -t -l 6000 <IP_DO_ROTEADOR>
     ```
     *(Os pacotes ICMP fragmentados de 6 KB atravessam a rede, o roteador processa a fragmentação e responde, elevando o tráfego para ~60 a 100 kbps e a CPU para ~30%).*
   * **Se estiver no Docker:**
     Execute o comando de estresse via SSH contra o container:
     ```cmd
     ssh -o StrictHostKeyChecking=no -p 2222 admin@127.0.0.1 ":for i from=1 to=25 do={ :for j from=1 to=3000 do={ :put \"BURST_TEST_STREAM_MIKROTIK_0123456789_ABCDEFGHIJ\" }; :delay 500ms }"
     ```
     *(Ou clique no botão da barra lateral "Gerar Pico no MikroTik (SSH)").*
3. **Comprovar a Reatividade e os Alertas:**
   * Aponte para o gráfico: as curvas de tráfego e CPU sobem imediatamente e **ultrapassam a linha vermelha tracejada**.
   * O **Pop-up** (`st.toast`) surge na tela alertando a violação do limite.
   * Abra a aba do **MailHog** (`http://localhost:8025`) ou a sua caixa postal: o e-mail de alerta estará lá com métrica violada, valor medido, threshold e timestamp exato.
4. **Comprovar a Histerese (Debouncing / Anti-Spam):**
   * Mantenha o ping ou o estresse rodando por mais alguns ciclos.
   * Mostre que o sistema **NÃO enviou múltiplos e-mails repetidos**.
   * **O que falar ao professor:**
     > *"Professor, observe que mesmo com a sobrecarga persistindo por vários ciclos, o sistema disparou o e-mail apenas uma vez na transição de Normal para Excedido. A histerese impede que a caixa de entrada sofra com tempestades de spam."*
   * Interrompa o ping (`Ctrl + C`) no terminal: o gráfico cai abaixo do limiar, normalizando o estado.

---

### Passo 5: Demonstrar Resiliência e Tratamento de Erros
> **Critério Avaliado:** Configuração e Tratamento de Erros (Peso: 10%)

1. **Validações na Interface:**
   * No cabeçalho, tente digitar `0` ou `-5` no campo *Intervalo de Coleta*: o campo rejeita ou bloqueia automaticamente (requisito estrito do edital).
   * No modal `Cfg` $\rightarrow$ aba *Servidor SMTP*, mostre que e-mails sem `@` ou domínio inválido são rejeitados com mensagem de erro amigável.
2. **Teste de Queda / Perda de Conexão:**
   * No modal `Cfg ⚙️`, altere temporariamente a porta SNMP de `161` para `162` (porta fechada) ou desconecte o cabo de rede.
   * Clique em **Salvar Configurações**.
   * **O que mostrar:** O dashboard **não quebra, não gera tela de traceback do Python e não fecha sozinho**. A interface exibe o badge vermelho: `"Falha de Conexão SNMP"`.
   * Restaure a porta para `161` e salve: a telemetria é restabelecida imediatamente de forma 100% transparente.

---

### Passo 6: Apresentação do Código e Repositório Git
> **Critério Avaliado:** Documentação e Código (Peso: 10%)

1. Mostre a estrutura modular do projeto no VS Code:
   * [app.py](file:///c:/Users/jeanj/Projetos/mini-monitoramento/mini-monitoramento/app.py): Interface gráfica, fragmentos em tempo real e gráficos Plotly.
   * [snmp_engine.py](file:///c:/Users/jeanj/Projetos/mini-monitoramento/mini-monitoramento/snmp_engine.py): Coleta MIB-II, cálculo $\Delta t$, rollover 32/64 bits e isolamento thread-safe.
   * [alert_engine.py](file:///c:/Users/jeanj/Projetos/mini-monitoramento/mini-monitoramento/alert_engine.py): Máquina de estados com histerese e envio SMTP.
   * [config_manager.py](file:///c:/Users/jeanj/Projetos/mini-monitoramento/mini-monitoramento/config_manager.py): Validações e persistência em `config.json`.
   * [historico_csv.py](file:///c:/Users/jeanj/Projetos/mini-monitoramento/mini-monitoramento/historico_csv.py): Persistência contínua e exportação CSV real.
2. Mostre o histórico do Git no terminal (`git log --oneline -n 6`): commits atômicos padronizados no padrão Conventional Commits.
3. Mostre o [README.md](file:///c:/Users/jeanj/Projetos/mini-monitoramento/mini-monitoramento/README.md) completo com explicação formal de todas as MIBs, OIDs e fórmulas.