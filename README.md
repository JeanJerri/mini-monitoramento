# 📡 Mini Monitoramento de Rede via SNMP

> **Trabalho Prático da Disciplina de Projeto e Administração de Redes**  
> Aplicação completa para monitoramento contínuo de telemetria de roteador via **SNMP**, cálculos de taxa em **bps** por $\Delta t$, tratamento de *counter rollover*, gráficos em tempo real com janela deslizante, histórico persistente e sistema de alertas com histerese (Pop-up e E-mail).

---

## 📑 Sumário
1. [Visão Geral e Arquitetura](#1-visão-geral-e-arquitetura)
2. [Estrutura de Arquivos](#2-estrutura-de-arquivos)
3. [Métricas Monitoradas, MIBs e OIDs](#3-métricas-monitoradas-mibs-e-oids)
4. [Fórmulas e Tratamento de Contadores (Rollover)](#4-fórmulas-e-tratamento-de-contadores-rollover)
5. [Sistema de Alertas e Histerese (Debounce)](#5-sistema-de-alertas-e-histerese-debounce)
6. [Instalação e Execução Passo a Passo](#6-instalação-e-execução-passo-a-passo)
7. [Roteiro Oficial de Demonstração na Bancada (Passo a Passo da Avaliação)](#7-roteiro-oficial-de-demonstração-na-bancada)

---

## 1. Visão Geral e Arquitetura

O sistema atende integralmente tanto ao documento oficial (PDF de requisitos) quanto às orientações passadas em aula (quadro e áudio do professor):

* **Coleta SNMP Real Nativa:** Suporta conexões diretas via protocolo SNMP (v2c e v3) a roteadores físicos (Cisco, MikroTik, Linux) e máquinas virtuais/containers com **MikroTik RouterOS CHR** (Docker ou VirtualBox).
* **Layout Fiel ao Quadro da Sala:**
  * **Cabeçalho:** Intervalo de coleta em segundos (com validação estrita $> 0$) e acesso rápido a configurações (`Cfg`).
  * **Painel Tempo Real (RT):** Controles `▶ Iniciar`, `⏸ Pausar` e `↻ Resetar`, janela deslizante configurável (1 a 30 min) e dois gráficos lado a lado com linhas tracejadas de *threshold* (*Tráfego IN/OUT em bps* e *CPU em %*).
  * **Painel Histórico (Hist.):** Filtro central por data e hora de início e fim (`DD/MM/AAAA HH:MM`) com atalhos rápidos e gráficos estáticos gerados a partir do banco de dados/CSV com coletas reais acumuladas.
* **Resiliência e Tratamento de Erros:** Quedas de link, timeouts e erros de comunidade não travam nem fecham o dashboard; o status é reportado visualmente e a reconexão ocorre de forma transparente.
* **Alertas com Histerese:** Notificações simultâneas por **Pop-up** e **E-mail (SMTP real)** com disparo exclusivo na transição de estado (*Normal $\rightarrow$ Excedido*), prevenindo tempestades de e-mails (*spam*).

---

## 2. Estrutura de Arquivos

```text
mini-monitoramento/
├── app.py                   # Dashboard principal em Streamlit (interface gráfica e gráficos)
├── snmp_engine.py           # Módulo de coleta SNMP, cálculos em bps, delta t e rollover
├── alert_engine.py          # Gerenciador de alertas, histerese/debounce e envio SMTP
├── config_manager.py        # Gerenciamento e persistência das configurações (config.json)
├── historico_csv.py         # Persistência contínua em CSV e carregador histórico (sem simulação)
├── iniciar_dashboard.bat    # Script de inicialização automática do dashboard no Windows
├── iniciar_mikrotik_docker.bat # Script para subir MikroTik CHR e MailHog no Docker
├── docker-compose.yml       # Definição dos containers de MikroTik CHR e SMTP
├── config.json              # Arquivo de configurações persistentes da aplicação
├── requirements.txt         # Bibliotecas Python (Streamlit, Pandas, Plotly, PySNMP)
└── data/
    └── medicoes.csv         # Base histórica com timestamps, bps, CPU e metadados
```

---

## 3. Métricas Monitoradas, MIBs e OIDs

Conforme exigido pelo PDF da atividade, todas as OIDs consultadas e suportadas estão documentadas formalmente abaixo:

### 3.1. Tráfego de Rede (Entrada e Saída)
* **MIB Utilizada:** `IF-MIB` (RFC 2863 / MIB-II RFC 1213)
* **OIDs Padrão (Contadores de 32 bits):**
  * `ifInOctets` (Bytes recebidos): `1.3.6.1.2.1.2.2.1.10.<ifIndex>`
  * `ifOutOctets` (Bytes transmitidos): `1.3.6.1.2.1.2.2.1.16.<ifIndex>`
* **OIDs de Alta Capacidade (Contadores de 64 bits para interfaces $\ge 1\text{ Gbps}$):**
  * `ifHCInOctets`: `1.3.6.1.2.1.31.1.1.1.6.<ifIndex>`
  * `ifHCOutOctets`: `1.3.6.1.2.1.31.1.1.1.10.<ifIndex>`
* **Identificação da Interface:**
  * `ifDescr`: `1.3.6.1.2.1.2.2.1.2.<ifIndex>`
  * `ifName`: `1.3.6.1.2.1.31.1.1.1.1.<ifIndex>`

### 3.2. Utilização de CPU (%)
O sistema suporta perfis dinâmicos de OID para abranger os principais fabricantes do laboratório:
* **Padrão Multiplataforma (Host Resources MIB - RFC 2790):**
  * `hrProcessorLoad`: `1.3.6.1.2.1.25.3.3.1.2.1`
* **Roteadores Cisco IOS:**
  * `cpmCPUTotal5secRev` (Média de 5 segundos): `1.3.6.1.4.1.9.9.109.1.1.1.1.3.1`
  * `cpmCPUTotal1minRev` (Média de 1 minuto): `1.3.6.1.4.1.9.9.109.1.1.1.1.7.1`
  * `avgBusy1` (Legado): `1.3.6.1.4.1.9.2.1.56.0`
* **Mikrotik RouterOS:**
  * `mtxrProcessorLoad`: `1.3.6.1.4.1.14988.1.1.1.3.1.0`
* **Linux / NET-SNMP:**
  * `ssCpuIdle`: `1.3.6.1.4.1.2021.11.11.0` (o software calcula: $\text{Uso} = 100 - \text{ssCpuIdle}$)

---

## 4. Fórmulas e Tratamento de Contadores (Rollover)

### 4.1. Fórmula Obrigatória de Taxa (bps)
O tráfego de rede é calculado com base na variação de octetos (bytes) e no tempo exato decorrido ($\Delta t$) entre duas leituras sucessivas:

$$\text{Taxa (bps)} = \frac{(\text{Bytes}_{\text{atual}} - \text{Bytes}_{\text{anterior}}) \times 8}{\Delta t}$$

* Onde:
  * $\text{Bytes}_{\text{atual}}$ e $\text{Bytes}_{\text{anterior}}$ são as leituras brutas dos contadores SNMP;
  * O fator $8$ converte bytes em bits;
  * $\Delta t = t_{\text{atual}} - t_{\text{anterior}}$ (em segundos, com precisão de ponto flutuante).

### 4.2. Tratamento de Counter Rollover (32 bits)
Contadores SNMP MIB-II `Counter32` atingem o valor máximo de $2^{32} - 1 = 4.294.967.295$ e voltam a zero. Caso isso ocorra, o cálculo convencional geraria um valor negativo absurdo.

O módulo `snmp_engine.py` trata essa condição da seguinte forma:
```python
if curr_octets >= prev_octets:
    diff = curr_octets - prev_octets
else:
    # O contador estourou e reiniciou
    diff = (4_294_967_296 - prev_octets) + curr_octets

# Se o equipamento foi reiniciado (reboot) ou houve reset de interface:
if diff < 0 or diff > 100_000_000_000:
    diff = 0  # Rejeita valores anômalos e reinicia baseline
```

---

## 5. Sistema de Alertas e Histerese (Debounce)

O sistema implementa regras estritas para notificação:
1. **Seleção de Canais:** Permite selecionar **Pop-up**, **E-mail (SMTP real)** ou **Ambos simultaneamente** via checkboxes.
2. **Prevenção de Tempestade de E-mails (Histerese):** O alarme é disparado **apenas na transição** de estado:
   * $\text{Normal} \rightarrow \text{Excedido}$: Dispara o Pop-up e envia o E-mail.
   * $\text{Excedido} \rightarrow \text{Excedido}$: Mantém o status visual no painel, mas **não inunda** a caixa postal.
   * $\text{Excedido} \rightarrow \text{Normal} \rightarrow \text{Excedido}$: Reativa a notificação quando ocorre novo pico.
   * Existe ainda um tempo de carência configurável (ex.: 5 minutos) caso o administrador queira reenvio periódico se a pane persistir.
3. **Conteúdo Obrigatório da Notificação:**
   * Nome da métrica violada (ex.: Tráfego de Entrada IN, Tráfego de Saída OUT ou Utilização de CPU);
   * Valor medido (em bps e %);
   * Limiar (*threshold*) configurado;
   * Data e hora exatas do evento;
   * IP e identificação da interface do equipamento.

---

## 6. Instalação e Execução Passo a Passo

### Pré-requisitos
* Sistema Operacional: Windows 10 ou 11.
* Python **3.13** instalado (já configurado no ambiente local).

### Como Iniciar o Dashboard
1. Dê dois cliques em **`iniciar_dashboard.bat`**.
2. O script inicializará o ambiente virtual `.venv`, validará as dependências e abrirá automaticamente o navegador em `http://localhost:8501`.

---

### 6.1. Configuração e Execução nos 3 Ambientes Suportados

O sistema opera **100% via SNMP real**, sendo compatível com qualquer uma das três opções abaixo:

#### Opção 1: Roteador Físico de Laboratório (Cisco ou MikroTik)
1. Conecte o cabo de rede Ethernet do computador a uma porta LAN do roteador.
2. Descubra o IP do roteador (ex.: `192.168.88.1` no MikroTik ou `192.168.1.1`/`10.0.0.1` no Cisco).
3. No Dashboard (**Cfg ⚙️**):
   * **IP do Roteador:** Insira o IP do roteador físico.
   * **Porta:** `161` | **Comunidade:** Comunidade do laboratório (ex.: `public`).
   * **Interface (ifIndex):** Clique em *"Descobrir Interfaces"* e selecione a porta conectada.
4. **Gerar Tráfego Real com o Comando PING no CMD:**
   ```cmd
   ping -t -l 6000 192.168.88.1
   ```
   *(Os pacotes ICMP de 6 KB atravessam o cabo físico, elevando os contadores de hardware e a CPU. Ao parar com `Ctrl + C`, o gráfico cai para zero).*

#### Opção 2: MikroTik RouterOS CHR no VirtualBox (Orientação Oficial da Disciplina)
1. Baixe o disco VDI oficial em [mikrotik.com/download](https://mikrotik.com/download).
2. Crie uma VM (Linux 64-bit, 256 MB RAM) anexando o arquivo VDI.
3. Em **Configurações da VM** $\rightarrow$ **Rede**, defina o Adaptador 1 como:
   * **Placa em modo Bridge (Bridged Adapter)** com sua placa Wi-Fi/Ethernet OU
   * **Placa exclusiva de hospedeiro (Host-Only)**.
4. Inicie a VM, faça login como `admin` (sem senha) e consulte o IP:
   ```routeros
   /snmp set enabled=yes
   /snmp community add name=public read-access=yes
   /ip address print
   ```
5. No Dashboard (**Cfg ⚙️**), insira o IP retornado (ex.: `192.168.56.10` ou `192.168.1.X`), porta `161`, comunidade `public` e perfil `MikroTik RouterOS CHR`.
6. **Gerar Tráfego Real com o Comando PING no CMD:**
   ```cmd
   ping -t -l 6000 <IP_DA_VM_VIRTUALBOX>
   ```

#### Opção 3: MikroTik RouterOS CHR via Docker (Ambiente Automatizado Local)
1. Dê dois cliques em **`iniciar_mikrotik_docker.bat`** (ou execute `docker compose up -d`).
2. O script iniciará o container do MikroTik CHR mapeando `161/udp` (SNMP) e `2222/tcp` (SSH), além do MailHog (`8025/tcp`).
3. No Dashboard (**Cfg ⚙️**):
   * **IP do Roteador:** `127.0.0.1` | **Porta:** `161`
   * **Comunidade:** `public` | **Interface (ifIndex):** `2` (`ether1` no RouterOS)
   * **Perfil de CPU:** `MikroTik RouterOS CHR`
4. **Gerar Carga Real no MikroTik:**
   * **Pelo CMD / PowerShell (SSH):**
     ```cmd
     ssh -o StrictHostKeyChecking=no -p 2222 admin@127.0.0.1 ":for i from=1 to=25 do={ :for j from=1 to=3000 do={ :put \"BURST_TEST_STREAM_MIKROTIK_0123456789_ABCDEFGHIJ\" }; :delay 500ms }"
     ```
   * **Ou pelo Dashboard:** Clique no botão da barra lateral **"Gerar Pico no MikroTik (SSH)"**.

---
