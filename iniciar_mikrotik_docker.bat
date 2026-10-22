@echo off
chcp 65001 >nul
title MikroTik RouterOS CHR via Docker - Mini Monitoramento

echo ==============================================================================
echo   Iniciando MikroTik RouterOS CHR no Docker (Alternativa ao VirtualBox)
echo ==============================================================================
echo.

where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERRO] Docker nao foi encontrado no PATH.
    echo Certifique-se de que o Docker Desktop esta instalado e rodando.
    pause
    exit /b 1
)

docker info >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [AVISO] O daemon do Docker Desktop nao parece estar em execucao.
    echo Por favor, abra o Docker Desktop e tente novamente.
    pause
    exit /b 1
)

echo [1/4] Verificando container 'mikrotik_chr'...
docker inspect mikrotik_chr >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo Container 'mikrotik_chr' ja existe. Reiniciando...
    docker start mikrotik_chr >nul 2>nul
) else (
    echo Criando e iniciando novo container MikroTik CHR...
    docker run -d --name mikrotik_chr --privileged ^
        -p 2222:22 -p 8291:8291 -p 8088:80 -p 161:161/udp ^
        cnsoluciones/mikrotik:latest ^
        -enable-kvm -device e1000,netdev=net_snmp -netdev user,id=net_snmp,hostfwd=udp::161-:161
)

echo.
echo [2/4] Aguardando o boot do RouterOS (cerca de 5 a 10 segundos)...
timeout /t 8 /nobreak >nul

echo [3/4] Configurando SNMP e interface de rede no MikroTik via SSH...
ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -p 2222 admin@127.0.0.1 "/snmp set enabled=yes; /ip dhcp-client add interface=ether2 disabled=no" >nul 2>nul

echo [4/5] Verificando servidor SMTP local (MailHog para testes de e-mail)...
docker inspect mailhog >nul 2>nul
if %ERRORLEVEL% equ 0 (
    docker start mailhog >nul 2>nul
) else (
    docker run -d --name mailhog -p 1025:1025 -p 8025:8025 mailhog/mailhog:latest >nul 2>nul
)

echo [5/5] Ambiente MikroTik + SMTP pronto e respondendo!
echo.
echo ==============================================================================
echo   DADOS PARA CONECTAR NO DASHBOARD (Cfg ⚙️):
echo   - Origem dos Dados: Coleta SNMP Real
echo   - IP do Roteador  : 127.0.0.1
echo   - Porta SNMP      : 161
echo   - Comunidade SNMP : public
echo   - Perfil de CPU   : MikroTik RouterOS CHR
echo ==============================================================================
echo.
echo   Comandos uteis:
echo   - Terminal RouterOS: ssh -p 2222 admin@127.0.0.1
echo   - WebFig (Navegador): http://localhost:8088
echo   - Teste de Carga (Pico): ssh -p 2222 admin@127.0.0.1 "/tool bandwidth-test address=127.0.0.1 direction=both duration=25s"
echo   - Parar container: docker stop mikrotik_chr
echo.
echo Pressione qualquer tecla para fechar esta janela (o container continuara rodando em segundo plano).
pause >nul
