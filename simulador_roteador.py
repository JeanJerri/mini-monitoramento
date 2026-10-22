"""
Simulador de Agente SNMP de Roteador (Cisco 2900 / MIB-II).
Implementa um servidor UDP SNMP v2c de alto desempenho e pura compatibilidade,
ouvindo nas portas UDP 161 (padrão) e 1161 (alternativa), respondendo a consultas
reais de ifInOctets, ifOutOctets, hrProcessorLoad, Cisco CPU e interfaces.
"""
from __future__ import annotations

import math
import random
import socket
import sys
import threading
import time
from typing import Dict, List, Tuple


def encode_asn1_length(length: int) -> bytes:
    """Codifica o comprimento no formato BER."""
    if length < 128:
        return bytes([length])
    len_bytes = []
    temp = length
    while temp > 0:
        len_bytes.insert(0, temp & 0xFF)
        temp >>= 8
    return bytes([0x80 | len(len_bytes)] + len_bytes)


def decode_asn1_length(data: bytes, offset: int) -> Tuple[int, int]:
    """Decodifica comprimento BER. Retorna (comprimento, novo_offset)."""
    b = data[offset]
    if b < 128:
        return b, offset + 1
    num_bytes = b & 0x7F
    val = 0
    for i in range(num_bytes):
        val = (val << 8) | data[offset + 1 + i]
    return val, offset + 1 + num_bytes


def oid_to_tuple(oid_bytes: bytes) -> Tuple[int, ...]:
    """Converte bytes de OID BER para tupla de inteiros."""
    if not oid_bytes:
        return ()
    first = oid_bytes[0]
    subids = [first // 40, first % 40]
    val = 0
    for b in oid_bytes[1:]:
        val = (val << 7) | (b & 0x7F)
        if not (b & 0x80):
            subids.append(val)
            val = 0
    return tuple(subids)


def tuple_to_oid_str(subids: Tuple[int, ...]) -> str:
    return ".".join(str(s) for s in subids)


class RouterState:
    """Estado dinâmico com simulação contínua de tráfego e CPU."""

    def __init__(self) -> None:
        self.start_time = time.time()
        self.last_update = time.time()
        self.in_octets_1 = 125_000_000
        self.out_octets_1 = 48_000_000
        self.in_octets_2 = 32_000_000
        self.out_octets_2 = 14_000_000
        self.stress_mode = False
        self.stress_until = 0.0

    def trigger_stress(self, duration_s: float = 30.0) -> None:
        """Força um pico de sobrecarga por N segundos para demonstrar os alertas."""
        self.stress_until = time.time() + duration_s
        print(f"\n[!] MODO DE ESTRESSE ATIVADO POR {duration_s} SEGUNDOS! Tráfego e CPU em alta.")

    def update(self) -> None:
        now = time.time()
        dt = now - self.last_update
        if dt <= 0:
            return
        self.last_update = now

        t = now - self.start_time
        # Tráfego base: 8 Mbps a 14 Mbps (IN) e 3 Mbps a 7 Mbps (OUT)
        rate_in = 8_000_000 + 4_500_000 * abs(math.sin(t / 14.0)) + random.uniform(0, 1_500_000)
        rate_out = 3_500_000 + 2_500_000 * abs(math.cos(t / 18.0)) + random.uniform(0, 1_000_000)

        # Se pico estiver ativo (salta para ~25-30 Mbps)
        if self.stress_mode or now < self.stress_until:
            rate_in += 18_000_000
            rate_out += 14_000_000

        delta_in = int((rate_in / 8.0) * dt)
        delta_out = int((rate_out / 8.0) * dt)

        # Incremento acumulado com rollover de 32 bits
        self.in_octets_1 = (self.in_octets_1 + delta_in) % 4_294_967_296
        self.out_octets_1 = (self.out_octets_1 + delta_out) % 4_294_967_296
        self.in_octets_2 = (self.in_octets_2 + int(delta_in * 0.4)) % 4_294_967_296
        self.out_octets_2 = (self.out_octets_2 + int(delta_out * 0.4)) % 4_294_967_296

    def get_cpu_load(self) -> int:
        now = time.time()
        t = now - self.start_time
        base_cpu = 28.0 + 32.0 * abs(math.sin(t / 20.0)) + random.uniform(0, 7.0)
        if self.stress_mode or now < self.stress_until:
            base_cpu = 88.0 + random.uniform(0, 9.0)  # Salta para 88% a 97%
        return int(min(99.0, max(5.0, base_cpu)))


state = RouterState()


def get_oid_value(oid_str: str) -> Tuple[int, bytes]:
    """
    Retorna o tipo ASN.1 e os bytes de valor para cada OID consultada.
    Tags:
      0x04: OctetString
      0x02: Integer32
      0x41: Counter32
      0x42: Gauge32
    """
    state.update()

    # sysDescr
    if oid_str.startswith("1.3.6.1.2.1.1.1.0"):
        val = b"MikroTik RouterOS 7.15 (CHR) / Cisco IOS Compatible"
        return 0x04, val

    # sysName
    if oid_str.startswith("1.3.6.1.2.1.1.5.0"):
        val = b"MikroTik-CHR-LabRedes"
        return 0x04, val

    # sysUpTime (TimeTicks em centésimos de segundo desde o boot)
    if oid_str.startswith("1.3.6.1.2.1.1.3.0"):
        uptime_ticks = int((time.time() - state.start_time) * 100) % 4_294_967_296
        return 0x43, uptime_ticks.to_bytes(4, byteorder="big")

    # ifDescr.1
    if oid_str.startswith("1.3.6.1.2.1.2.2.1.2.1"):
        return 0x04, b"ether1 (Link WAN Principal)"

    # ifDescr.2
    if oid_str.startswith("1.3.6.1.2.1.2.2.1.2.2"):
        return 0x04, b"ether2 (Rede Local LAN)"

    # ifInOctets.1 (32 bits)
    if oid_str.startswith("1.3.6.1.2.1.2.2.1.10.1"):
        return 0x41, state.in_octets_1.to_bytes(4, byteorder="big")

    # ifOutOctets.1 (32 bits)
    if oid_str.startswith("1.3.6.1.2.1.2.2.1.16.1"):
        return 0x41, state.out_octets_1.to_bytes(4, byteorder="big")

    # ifInOctets.2
    if oid_str.startswith("1.3.6.1.2.1.2.2.1.10.2"):
        return 0x41, state.in_octets_2.to_bytes(4, byteorder="big")

    # ifOutOctets.2
    if oid_str.startswith("1.3.6.1.2.1.2.2.1.16.2"):
        return 0x41, state.out_octets_2.to_bytes(4, byteorder="big")

    # hrProcessorLoad.1 (Host Resources MIB)
    if oid_str.startswith("1.3.6.1.2.1.25.3.3.1.2"):
        return 0x02, state.get_cpu_load().to_bytes(1, byteorder="big")

    # Cisco cpmCPUTotal5secRev.1 (CISCO-PROCESS-MIB)
    if oid_str.startswith("1.3.6.1.4.1.9.9.109.1.1.1.1.3"):
        return 0x42, state.get_cpu_load().to_bytes(1, byteorder="big")

    # Cisco cpmCPUTotal1minRev.1
    if oid_str.startswith("1.3.6.1.4.1.9.9.109.1.1.1.1.7"):
        return 0x42, state.get_cpu_load().to_bytes(1, byteorder="big")

    # Cisco avgBusy1
    if oid_str.startswith("1.3.6.1.4.1.9.2.1.56"):
        return 0x02, state.get_cpu_load().to_bytes(1, byteorder="big")

    # Mikrotik CPU
    if oid_str.startswith("1.3.6.1.4.1.14988.1.1.1.3"):
        return 0x02, state.get_cpu_load().to_bytes(1, byteorder="big")

    # Linux ssCpuIdle (retorna 100 - CPU)
    if oid_str.startswith("1.3.6.1.4.1.2021.11.11"):
        idle = max(1, 100 - state.get_cpu_load())
        return 0x02, idle.to_bytes(1, byteorder="big")

    # Padrão para OID genérica desconhecida: Counter ou Integer 0
    return 0x02, (0).to_bytes(1, byteorder="big")


def process_snmp_packet(packet: bytes) -> bytes:
    """Decodifica pacote SNMP GET v2c, gera a resposta com as OIDs solicitadas e retorna resposta BER."""
    try:
        # Verifica Sequence tag 0x30
        if packet[0] != 0x30:
            return b""
        total_len, offset = decode_asn1_length(packet, 1)

        # Versão (Integer)
        if packet[offset] != 0x02:
            return b""
        ver_len = packet[offset + 1]
        ver_bytes = packet[offset : offset + 2 + ver_len]
        offset += 2 + ver_len

        # Comunidade (OctetString)
        if packet[offset] != 0x04:
            return b""
        comm_len = packet[offset + 1]
        comm_bytes = packet[offset : offset + 2 + comm_len]
        offset += 2 + comm_len

        # PDU Header
        pdu_tag = packet[offset]
        pdu_len, offset = decode_asn1_length(packet, offset + 1)

        # Somente trata GetRequest (0xa0) e GetNextRequest (0xa1)
        if pdu_tag not in (0xA0, 0xA1):
            return b""

        # Request-ID
        if packet[offset] != 0x02:
            return b""
        req_id_len = packet[offset + 1]
        req_id_bytes = packet[offset : offset + 2 + req_id_len]
        offset += 2 + req_id_len

        # Error-Status (3 bytes) e Error-Index (3 bytes)
        offset += 6

        # VarBindList tag 0x30
        if packet[offset] != 0x30:
            return b""
        vbl_len, offset = decode_asn1_length(packet, offset + 1)
        vbl_end = offset + vbl_len

        out_varbinds = bytearray()

        while offset < vbl_end and offset < len(packet):
            # VarBind tag 0x30
            if packet[offset] != 0x30:
                break
            vb_len, offset = decode_asn1_length(packet, offset + 1)
            vb_end = offset + vb_len

            # OID tag 0x06
            if packet[offset] != 0x06:
                offset = vb_end
                continue
            oid_len, offset = decode_asn1_length(packet, offset + 1)
            raw_oid = packet[offset : offset + oid_len]
            offset += oid_len

            # Identifica a OID
            oid_subids = oid_to_tuple(raw_oid)
            oid_str = tuple_to_oid_str(oid_subids)

            # Para GetNextRequest (Walk) de ifDescr
            if pdu_tag == 0xA1:
                if oid_str == "1.3.6.1.2.1.2.2.1.2":
                    oid_str = "1.3.6.1.2.1.2.2.1.2.1"
                    raw_oid = bytes([0x2B, 0x06, 0x01, 0x02, 0x01, 0x02, 0x02, 0x01, 0x02, 0x01])
                elif oid_str == "1.3.6.1.2.1.2.2.1.2.1":
                    oid_str = "1.3.6.1.2.1.2.2.1.2.2"
                    raw_oid = bytes([0x2B, 0x06, 0x01, 0x02, 0x01, 0x02, 0x02, 0x01, 0x02, 0x02])
                elif oid_str.startswith("1.3.6.1.2.1.2.2.1.2"):
                    # Passou do fim das interfaces (avança para outra MIB)
                    oid_str = "1.3.6.1.2.1.2.2.1.3.1"
                    raw_oid = bytes([0x2B, 0x06, 0x01, 0x02, 0x01, 0x02, 0x02, 0x01, 0x03, 0x01])

            # Obtém o valor
            val_type, val_content = get_oid_value(oid_str)

            # Monta OID chunk
            oid_chunk = bytes([0x06]) + encode_asn1_length(len(raw_oid)) + raw_oid
            val_chunk = bytes([val_type]) + encode_asn1_length(len(val_content)) + val_content

            varbind = bytes([0x30]) + encode_asn1_length(len(oid_chunk) + len(val_chunk)) + oid_chunk + val_chunk
            out_varbinds.extend(varbind)

            offset = vb_end

        # Monta VarBindList
        vbl_packet = bytes([0x30]) + encode_asn1_length(len(out_varbinds)) + out_varbinds

        # GetResponse PDU (tag 0xa2)
        resp_pdu_body = req_id_bytes + b"\x02\x01\x00\x02\x01\x00" + vbl_packet
        resp_pdu = bytes([0xA2]) + encode_asn1_length(len(resp_pdu_body)) + resp_pdu_body

        # Mensagem SNMP completa
        msg_body = ver_bytes + comm_bytes + resp_pdu
        full_msg = bytes([0x30]) + encode_asn1_length(len(msg_body)) + msg_body
        return full_msg

    except Exception:
        return b""


def udp_listener_worker(port: int, stop_event: threading.Event) -> None:
    """Escuta datagramas UDP em uma porta específica."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", port))
        sock.settimeout(0.5)
        print(f"[*] Escutando na porta UDP {port}...")
    except Exception as e:
        print(f"[-] Não foi possível vincular à porta UDP {port}: {e}")
        return

    while not stop_event.is_set():
        try:
            data, addr = sock.recvfrom(4096)
            resp = process_snmp_packet(data)
            if resp:
                sock.sendto(resp, addr)
        except socket.timeout:
            continue
        except Exception:
            pass

    sock.close()
    print(f"[*] Porta {port} encerrada.")


def run_simulator() -> None:
    print("=" * 65)
    print("   SIMULADOR DE ROTEADOR SNMP - LAB DE REDES")
    print("=" * 65)
    print("Emulando Cisco 2900 Series Router com interface GigabitEthernet0/0")
    print("Comunidade SNMP: 'public' | Versão: SNMPv2c\n")

    stop_event = threading.Event()
    threads = []
    for port in [161, 1161]:
        t = threading.Thread(target=udp_listener_worker, args=(port, stop_event), daemon=True)
        t.start()
        threads.append(t)

    print("\nComandos disponíveis no terminal:")
    print("  Digite 'p' e pressione Enter para disparar PICO DE ESTRESSE (30s)")
    print("  Digite 'c' e pressione Enter para consultar status do simulador")
    print("  Pressione Ctrl+C para encerrar o simulador")
    print("-" * 65)

    def input_worker() -> None:
        while not stop_event.is_set():
            try:
                line = sys.stdin.readline().strip().lower()
                if line == "p":
                    state.trigger_stress(30.0)
                elif line == "c":
                    state.update()
                    print(
                        f"[STATUS] Bytes IN: {state.in_octets_1:,} | "
                        f"Bytes OUT: {state.out_octets_1:,} | "
                        f"CPU: {state.get_cpu_load()}%"
                    )
            except Exception:
                break

    in_thread = threading.Thread(target=input_worker, daemon=True)
    in_thread.start()

    try:
        while True:
            time.sleep(1)
            state.update()
    except KeyboardInterrupt:
        print("\n[*] Encerrando o simulador...")
        stop_event.set()
        for t in threads:
            t.join(timeout=1.0)
        print("[*] Simulador finalizado.")


if __name__ == "__main__":
    run_simulator()
