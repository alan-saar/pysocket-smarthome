#####################################################
#                                                   #
# Título do trabalho: Trabalho de Sockets           #
#         Disciplina: Redes de Computadores PPComp  #
#                                                   #
#####################################################

from Config import *
from ControlItem import *
from Monitor import RenderMonitor
import queue
import threading

def GeneralControl(controlQueue, roomsList, typesList):
	# Dicionário contendo todos os ambientes cadastrados
	# Usamos a lista de ambientes que foi carregada do arquivo de configuração para popular o nosso dicionário de objetos com informações dos ambientes
	for item in roomsList:
		roomID = item['roomID']
		roomName = item['roomName']
		AddRoomItem(RoomItem(roomID, roomName))
	# Dicionário com os tipos carregados da tabela de configuração
	for item in typesList:
		typeID = item['typeID']
		typeCode = item['typeCode']
		typeName = item['typeName']
		AddTypeItem(TypeItem(typeID, typeCode, typeName))

	# Renderiza o estado inicial do monitor
	RenderMonitor(GetRoomDict(), "Servidor inicializado. Monitor ativo aguardando conexões.")

	while True:
		# Aguarda a chegada de um comando na fila
		monitorItem = controlQueue.get()
        # debug removido pois estava poluindo o monitor. Criei uma variável eventDesc no lugar que monta a descrição do que acontedeu (Ex. Lampada #1 Conectada)
        # print(f'Comando chegando na fila do controle do ambiente {monitorItem.roomID}')
		roomItem = GetRoomItem(monitorItem.roomID)
		eventDesc = ""

		# Se encontrou o ambiente na lista, executa o comando
		if roomItem != None:
			# Atende o comando de acordo com o tipo de dispositivo
			# LAMPADA <- Registrar ou desregistrar no sistema
            # a lógica é a mesma, mas inclui uma mensagem explicativa do evento
			if monitorItem.deviceTypeCode == COD_LAMPADA:
				if monitorItem.command == INCLUIR_LAMPADA:
					roomItem.AddLamp(monitorItem.deviceID, monitorItem.lampQueue)
					eventDesc = f"Lâmpada #{monitorItem.deviceID} conectada e registrada no ambiente [{roomItem.roomID}] {roomItem.roomName}"
				elif monitorItem.command == EXCLUIR_LAMPADA:
					roomItem.DelLamp(monitorItem.deviceID)
					eventDesc = f"Lâmpada #{monitorItem.deviceID} desconectada do ambiente [{roomItem.roomID}] {roomItem.roomName}"

			# SENSOR DE PRESENÇA <- Inclusão, remoção ou leitura
            # Expande o tratamento do sensor de presença
            # Antes só acionava roomItem.Sensor(command) para acender ou apar as lâmpadas
            # Agora trata a conexão e desconexão  do sensor e atualiza o atributo UpdatePresense
			elif monitorItem.deviceTypeCode == COD_SENSOR_PRESENCA:
				if monitorItem.command == INCLUIR_DISPOSITIVO:
					roomItem.AddDevice(monitorItem.deviceID, COD_SENSOR_PRESENCA)
					eventDesc = f"Sensor de Presença #{monitorItem.deviceID} registrado no ambiente [{roomItem.roomID}] {roomItem.roomName}"
				elif monitorItem.command == EXCLUIR_DISPOSITIVO:
					roomItem.DelDevice(monitorItem.deviceID)
					eventDesc = f"Sensor de Presença #{monitorItem.deviceID} desconectado do ambiente [{roomItem.roomID}] {roomItem.roomName}"
				else:
					# Leitura recebida
					roomItem.UpdatePresence(monitorItem.deviceID, monitorItem.command)
					roomItem.Sensor(monitorItem.command)
					status_str = "DETECTADA" if int(monitorItem.command) == PRESENCA_DETECTADA else "NÃO DETECTADA"
					eventDesc = f"Presença {status_str} (Sensor #{monitorItem.deviceID}) no ambiente [{roomItem.roomID}] {roomItem.roomName}"

			# TERMÔMETRO <- Inclusão, remoção ou leitura de temperatura
            # Não havia nenhum bloco para controlar o termômetro
            # Agora o termômetro é registrado, e cada leitura enviada atualiza a temperatura do ambiente no Monitor
			elif monitorItem.deviceTypeCode == COD_TERMOMETRO:
				if monitorItem.command == INCLUIR_DISPOSITIVO:
					roomItem.AddDevice(monitorItem.deviceID, COD_TERMOMETRO)
					eventDesc = f"Termômetro #{monitorItem.deviceID} registrado no ambiente [{roomItem.roomID}] {roomItem.roomName}"
				elif monitorItem.command == EXCLUIR_DISPOSITIVO:
					roomItem.DelDevice(monitorItem.deviceID)
					eventDesc = f"Termômetro #{monitorItem.deviceID} desconectado do ambiente [{roomItem.roomID}] {roomItem.roomName}"
				else:
					# Leitura de temperatura recebida
					roomItem.UpdateTemperature(monitorItem.deviceID, monitorItem.command)
                    # mudança par ao ar-condicinado
                    # quando o termômetro envia uma nova leitura para a fila central, além de salvar a temperatura do cômodo,
                    # o servidor agora verifica se há algum aparelho de ar-condicionado instalado no mesmo ambiente para disparar a automação
					temp_val = float(monitorItem.command)
					eventDesc = f"Temperatura lida: {temp_val:.1f} °C (Termômetro #{monitorItem.deviceID}) no ambiente [{roomItem.roomID}] {roomItem.roomName}"
					# Automação Integrada do Ar-Condicionado baseada na temperatura do ambiente
                    # se houver algum ar-condicionado e a temperatura estiver acima do limite manda ligar,
                    # e se estiver frio manda desligar
					if len(roomItem.airQueueList) > 0:
						if temp_val > TEMP_LIMIAR_LIGAR:
							roomItem.SetAirConditioner(AR_LIGADO, TEMP_ALVO_PADRAO)
							eventDesc += f" | [AUTOMAÇÃO] Ar-Condicionado LIGADO (Temp {temp_val:.1f} °C > {TEMP_LIMIAR_LIGAR:.1f} °C)"
						elif temp_val <= TEMP_LIMIAR_DESLIGAR:
							roomItem.SetAirConditioner(AR_DESLIGADO, TEMP_ALVO_PADRAO)
							eventDesc += f" | [AUTOMAÇÃO] Ar-Condicionado DESLIGADO (Temp {temp_val:.1f} °C <= {TEMP_LIMIAR_DESLIGAR:.1f} °C)"

			# AR-CONDICIONADO <- Inclusão ou remoção do atuador
            # trata os eventos de conexão e desconexão dos clientes do tipo Ar-Condicionado que chegam pela fila central
			elif monitorItem.deviceTypeCode == COD_AR_CONDICIONADO:
				if monitorItem.command == INCLUIR_AR_CONDICIONADO:
					roomItem.AddAirConditioner(monitorItem.deviceID, monitorItem.lampQueue)
					eventDesc = f"Ar-Condicionado #{monitorItem.deviceID} conectado e registrado no ambiente [{roomItem.roomID}] {roomItem.roomName}"
				elif monitorItem.command == EXCLUIR_AR_CONDICIONADO:
					roomItem.DelAirConditioner(monitorItem.deviceID)
					eventDesc = f"Ar-Condicionado #{monitorItem.deviceID} desconectado do ambiente [{roomItem.roomID}] {roomItem.roomName}"

			# Outros dispositivos
			elif monitorItem.command == INCLUIR_DISPOSITIVO:
				roomItem.AddDevice(monitorItem.deviceID, monitorItem.deviceTypeCode)
				eventDesc = f"Dispositivo #{monitorItem.deviceID} registrado no ambiente [{roomItem.roomID}] {roomItem.roomName}"
			elif monitorItem.command == EXCLUIR_DISPOSITIVO:
				roomItem.DelDevice(monitorItem.deviceID)
				eventDesc = f"Dispositivo #{monitorItem.deviceID} desconectado do ambiente [{roomItem.roomID}] {roomItem.roomName}"

        # lst = '------------------------------------------------------\n'
        # for roomID, roomItem in GetRoomDict().items():
        #     roomLampList = roomItem.toString()
        #     if roomLampList != None:
        #         lst = lst + roomLampList + '\n'
        # lst = lst + '------------------------------------------------------\n'
        # print(lst)
        #
		# Atualiza a exibição em arte ASCII no terminal
        # Anteriormente era exibido apenas uma lista simples, nem mostrava temperaturas ou presenças
        # ------------------------------------------------------
        # [1] Sala => Lâmpadas> 1
        # ------------------------------------------------------
        # O monitor agora desenha cartões atualizados com os indicadores
		RenderMonitor(GetRoomDict(), eventDesc)
