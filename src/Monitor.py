#####################################################
#                                                   #
# Título do trabalho: Trabalho de Sockets           #
#         Disciplina: Redes de Computadores PPComp  #
#                                                   #
#####################################################

from datetime import datetime
from Config import *

## Como funciona o Monitor do servidor
# Quando o servidor acabou de ligar, a função é chamada assim:
#
#   RenderMonitor(GetRoomDict(), "Servidor inicializado. Monitor ativo aguardando conexões.")
#
# 1. O RenderMonitor percorre os 15 cômodos cadastrados no ambientes.txt.
# 2. Como nenhum tem dispositivo conectado ainda, a lista active_rooms fica vazia.
# 3. Todos os 15 cômodos vão para a lista idle_rooms.
# 4. Ele imprime a moldura de espera e a lista compacta no rodapé:
#
#   +==================================================================+
#   | MONITOR RESIDENCIAL - SMART HOME                                 |
#   | Status em tempo real | 11/09/2026, 19:30:00                      |
#   +==================================================================+
#   | ULTIMO EVENTO: Servidor inicializado. Monitor ativo aguardando c |
#   +------------------------------------------------------------------+
#   +------------------------------------------------------------------+
#   | NENHUM DISPOSITIVO ATIVO NO MOMENTO                              |
#   | Aguardando conexao de sensores e atuadores...                    |
#   +------------------------------------------------------------------+
#   Ambientes ociosos (15): Sala, Quarto 1, Quarto 2, Quarto 3, Suite etc...
#   +==================================================================+
#
#   Se uma lâmpada for conectada for conectada na sala com ID 1,
#   e logo depois um Sensor de Presença também na Sala (recebe ID 2).
#
#  O GeneralControl recebe os eventos da fila e chama o monitor:
#
#   RenderMonitor(GetRoomDict(), "Sensor de Presença #2 registrado no ambiente [1] Sala")
#
# 1. O cômodo [1] Sala agora tem hasActiveDevices() == True.
# 2. O RenderMonitor desenha um cartão individual exclusivo para a Sala:
#     • Consulta room.temperature: como ainda não há termômetro, imprime -- (Nenhum sensor...).
#     • Consulta room.presence: como ainda não enviou leitura, imprime -- (Nenhum sensor...).
#     • Consulta room.lampQueueList: encontra o ID 1 e o estado inicial [APAGADA].
#     • Consulta room.countDevices() e room.getDeviceIDs(): totaliza 2 dispositivos (#1, #2).
# 3. O cômodo Sala sai da lista de ociosos, restando os outros 14 no rodapé:
#
### Principais Vantagens dessa Implementação:
# 1. Histórico preservado: por não utilizar comandos destrutivos de tela (cls ou clear), o usuário pode rolar o
# terminal e auditar a sequência de comandos que foram disparados na rede.
# 2. ASCII Puro: Funciona em qualquer sistema operacional (Linux, Windows via CMD/PowerShell, macOS, SSH) sem
# risco de ficar estranho ou corromper com caracteres desconhecidos.
# 3. Didático: Fica visualmente evidente na apresentação do trabalho o comportamento das threads e filas
# gerenciando múltiplos cômodos.

WIDTH = 68

def _box_line(text, width=WIDTH):
	inner = width - 4
	if len(text) > inner:
		text = text[:inner]
	return f"| {text.ljust(inner)} |"

def _separator(char='-', width=WIDTH):
	return "+" + char * (width - 2) + "+"

def _double_separator(width=WIDTH):
	return "+" + "=" * (width - 2) + "+"

def RenderMonitor(roomDict, lastEventDesc=""):
	"""
	Renderiza no terminal os cartões em ASCII dos ambientes residenciais
	com seus respectivos indicadores em tempo real.
	"""
	now = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
	lines = []

	lines.append("")
	lines.append(_double_separator())
	lines.append(_box_line("MONITOR RESIDENCIAL - SMART HOME"))
	lines.append(_box_line(f"Status em tempo real | {now}"))
	lines.append(_double_separator())

	if lastEventDesc:
		lines.append(_box_line(f"ULTIMO EVENTO: {lastEventDesc}"))
		lines.append(_separator())

	# Filtrar ambientes que possuem ao menos um dispositivo registrado
	active_rooms = []
	idle_rooms = []

	for roomID in sorted(roomDict.keys(), key=lambda x: int(x) if x.isdigit() else x):
		roomItem = roomDict[roomID]
		if hasattr(roomItem, 'hasActiveDevices') and roomItem.hasActiveDevices():
			active_rooms.append(roomItem)
		elif hasattr(roomItem, 'lampQueueList') and len(roomItem.lampQueueList) > 0:
			active_rooms.append(roomItem)
		else:
			idle_rooms.append(roomItem.roomName)

	if not active_rooms:
		lines.append(_separator())
		lines.append(_box_line("NENHUM DISPOSITIVO ATIVO NO MOMENTO"))
		lines.append(_box_line("Aguardando conexao de sensores e atuadores..."))
		lines.append(_separator())
	else:
		for room in active_rooms:
			lines.append(_separator('-'))
			r_id = str(room.roomID).zfill(2)
			lines.append(_box_line(f"AMBIENTE [{r_id}] - {room.roomName.upper()}"))
			lines.append(_separator('-'))

			# 1. Indicador de Temperatura
			if hasattr(room, 'temperature') and room.temperature is not None:
				sensor_str = f"(Sensor ID: {room.temperatureSensorID})" if getattr(room, 'temperatureSensorID', None) else ""
				lines.append(_box_line(f"[TERMOMETRO]  {room.temperature:.1f} C {sensor_str}"))
			else:
				lines.append(_box_line("[TERMOMETRO]  -- (Nenhum sensor de temperatura registrado)"))

			# 2. Indicador de Presenca
			if hasattr(room, 'presence') and room.presence is not None:
				sensor_str = f"(Sensor ID: {room.presenceSensorID})" if getattr(room, 'presenceSensorID', None) else ""
				p_str = "DETECTADA [!]" if room.presence == PRESENCA_DETECTADA else "NAO DETECTADA"
				lines.append(_box_line(f"[PRESENCA]    {p_str} {sensor_str}"))
			else:
				lines.append(_box_line("[PRESENCA]    -- (Nenhum sensor de presenca registrado)"))

			# 3. Indicador de Lampadas
			lamp_desc = []
			if hasattr(room, 'lampQueueList') and len(room.lampQueueList) > 0:
				for dev_id in sorted(room.lampQueueList.keys()):
					state = getattr(room, 'lampStates', {}).get(dev_id, LUZ_APAGADA)
					state_str = "ACESA" if state == LUZ_ACESA else "APAGADA"
					lamp_desc.append(f"Lampada #{dev_id}: [{state_str}]")
				lines.append(_box_line("[LAMPADAS]    " + " | ".join(lamp_desc)))
			else:
				lines.append(_box_line("[LAMPADAS]    -- (Nenhuma lampada instalada)"))

			# 4. Indicador de Ar-Condicionado
			if hasattr(room, 'airQueueList') and len(room.airQueueList) > 0:
                # lista vazia para acumular as descrições textuais de cada aparelho do cômodo
				air_desc = []
				for dev_id in sorted(room.airQueueList.keys()):
					state = getattr(room, 'airStates', {}).get(dev_id, AR_DESLIGADO)
					state_str = "LIGADO" if state == AR_LIGADO else "DESLIGADO"
					air_desc.append(f"Ar #{dev_id}: [{state_str}]")
                # a _box_line ajusta o espaçamento até atingir exatamente os 68 caracteres definidos no monitor
				lines.append(_box_line("[AR-CONDIC.]  " + " | ".join(air_desc)))
			else:
				lines.append(_box_line("[AR-CONDIC.]  -- (Nenhum ar-condicionado instalado)"))

			# 5. Resumo de dispositivos no ambiente
			total_devs = getattr(room, 'countDevices', lambda: len(room.lampQueueList))()
			dev_ids = getattr(room, 'getDeviceIDs', lambda: list(room.lampQueueList.keys()))()
			ids_str = ", ".join(f"#{d}" for d in sorted(dev_ids)) if dev_ids else "Nenhum"
			lines.append(_box_line(f"[DISPOSITIVOS] Total: {total_devs} | IDs: {ids_str}"))
			lines.append(_separator('-'))

	# Ambientes ociosos (resumo compacto)
	if idle_rooms:
		summary = "Ambientes ociosos (" + str(len(idle_rooms)) + "): " + ", ".join(idle_rooms)
		lines.append("")
		lines.append(summary)

	lines.append(_double_separator())
	lines.append("")

	output = "\n".join(lines)
	print(output)
	return output
