#####################################################
#                                                   #
# Título do trabalho: Trabalho de Sockets           #
#         Disciplina: Redes de Computadores PPComp  #
#                                                   #
#####################################################

from Config import *
import queue

# Dicionário com os ambientes catalogados
global roomDict
roomDict = {}
# Dicionário com os tipos catalogados
global typeDict
typeDict = {}


# Objeto que mantém os dados de um ambiente
class RoomItem():
	roomID = ''    # ID do ambiente
	roomName = ''  # Nome do ambiente
	lampQueueList = {}
	#runningStatus = False  # Possui thread monitorando?
	#thread = None          # Objeto da thread
	#eventObject = None     # Objeto de evento para cancelar o timeout

	# Inicializa com ID e Nome do ambiente
	def __init__(self, roomID, roomName):
		self.roomID = roomID
		self.roomName = roomName
		self.lampQueueList = {}
        # LAMPSTATE guarda LUC_ACESA/LUZ_APAGADA. Antes só era guardado a fila da lâmpada
		self.lampStates = {}
        # Já botei dados para um futuro ar condicionado
		self.airQueueList = {}
		self.airStates = {}
        # Ultima temperatura lida (ex. 25.5) e ID do termômetro que enviou a leitura
		self.temperature = None
		self.temperatureSensorID = None
        # Armazena o estado atual do sensor de presença (0 ou 1) e o id do sensor
		self.presence = None
		self.presenceSensorID = None
        # dicionário {deviceID: typeCode} para catalogar todos os dispositivos que estão operando dentro de um cômodo
		self.devices = {}

	# Verifica se o ambiente possui algum dispositivo ativo
    # O monitor usa isso para saber se determinado cômodo tem algum dispositivo ativo.
    # Se false vai colocar no rodapé do monitor que o ambiente está ocioso
	def hasActiveDevices(self):
		return (len(self.lampQueueList) > 0 or
				len(self.airQueueList) > 0 or
				len(self.devices) > 0 or
				self.temperature is not None or
				self.presence is not None)

	# Quantidade total de dispositivos ativos no ambiente (o set é para não contar duas vezes)
	def countDevices(self):
		all_devs = set(self.devices.keys()) | set(self.lampQueueList.keys()) | set(self.airQueueList.keys())
		if self.temperatureSensorID: all_devs.add(self.temperatureSensorID)
		if self.presenceSensorID: all_devs.add(self.presenceSensorID)
		return len(all_devs)

	# Lista de IDs de dispositivos no ambiente (faz o mesmo processo de contar, mas devolve o set como uma lista)
	def getDeviceIDs(self):
		all_devs = set(self.devices.keys()) | set(self.lampQueueList.keys()) | set(self.airQueueList.keys())
		if self.temperatureSensorID: all_devs.add(self.temperatureSensorID)
		if self.presenceSensorID: all_devs.add(self.presenceSensorID)
		return list(all_devs)

	# Gerar a lista de lâmpadas do ambiente em formato texto
	def LampListToString(self):
		deviceList = []
		for deviceID in self.lampQueueList.keys():
			deviceList.append(f'{deviceID}')
		return ', '.join(deviceList)

	# Lista de lâmpadas do ambiente
	def toString(self):
		if len(self.lampQueueList) > 0:
			threadList = 'Lâmpadas> ' + self.LampListToString()
			return f'[{self.roomID}] {self.roomName} => {threadList}'
		return None

	# Incluir nova lâmpada na lista
	def AddLamp(self, deviceID, lampQueue):
		print(f'Adicionando a lâmpada ID={deviceID} no ambiente {self.roomName}')
		self.lampQueueList.update({deviceID: lampQueue})
        # Define que toda lâmpada recém-conectada inicia com estado LUZ_APAGADA
		self.lampStates[deviceID] = LUZ_APAGADA
		self.devices[deviceID] = COD_LAMPADA

	# Remover uma lâmpada da lista
	def DelLamp(self, deviceID):
		print(f'Removendo a lâmpada ID={deviceID} do ambiente {self.roomName}')
        # mudei porque só dar um pop na lista lançava um keyError
		if deviceID in self.lampQueueList:
			self.lampQueueList.pop(deviceID)
		if deviceID in self.lampStates:
			self.lampStates.pop(deviceID)
		if deviceID in self.devices:
			self.devices.pop(deviceID)
		return len(self.lampQueueList)

	# Registra inclusão de outro dispositivo (sensor)
	def AddDevice(self, deviceID, typeCode):
		self.devices[deviceID] = typeCode

	# Remove outro dispositivo (sensor)
    # Reseta os atributos para não ficar nenhum 'fantasma' no monitor
    # Quando o cliente do sensor de presença fecha a janela (Ctrl+C),
    # o servidor chama DelDevice com o Id e o monitor é atualizado
	def DelDevice(self, deviceID):
		if deviceID in self.devices:
			self.devices.pop(deviceID)
		if self.temperatureSensorID == deviceID:
			self.temperature = None
			self.temperatureSensorID = None
		if self.presenceSensorID == deviceID:
			self.presence = None
			self.presenceSensorID = None

	# Atualiza leitura de temperatura
	def UpdateTemperature(self, sensorID, temp):
		self.temperature = float(temp)
		self.temperatureSensorID = sensorID
		self.devices[sensorID] = COD_TERMOMETRO

	# Atualiza leitura de presença
	def UpdatePresence(self, sensorID, presence):
		self.presence = int(presence)
		self.presenceSensorID = sensorID
		self.devices[sensorID] = COD_SENSOR_PRESENCA

	# Se um sensor foi acionado, repassa às lâmpadas e atualiza o estado
	def Sensor(self, command):
		for deviceID, lampQueue in self.lampQueueList.items():
			if lampQueue is not None:
				lampQueue.put(int(command))
			self.lampStates[deviceID] = int(command)

# Objeto contendo os tipos catalogados
class TypeItem():
	typeID = ''    # ID do tipo
	typeCode = ''  # Código do tipo 'L' Lâmpada, 'S' Sensor de presença e 'T' Temperatura
	typeName = ''  # Nome do dispositivo

	def __init__(self, typeID, typeCode, typeName):
		self.typeID = typeID
		self.typeCode = typeCode
		self.typeName = typeName

# Formato da mensagem enviada pela fila para o controle geral
class MonitorItem():
	deviceID = None			# ID do dispositivo
	deviceTypeCode = None	# Código 'L' Lâmpada ou 'S' Sensor de Presença
	roomID = None			# ID do ambiente
	command = None			# Comando
							# Lâmpada:
							#	INCLUIR_LAMPADA / EXCLUIR_LAMPADA
							# Sensor de presença:
							#	PRESENCA_NAO_DETECTADA / PRESENCA_DETECTADA
	lampQueue = None		# Fila para comunicação com a lâmpada

	def __init__(self, deviceID, deviceTypeCode, roomID, command, lampQueue):
		self.deviceID = deviceID
		self.deviceTypeCode = deviceTypeCode
		self.roomID = roomID
		self.command = command
		self.lampQueue = lampQueue

# Incluir um tipo no dicionário
def AddTypeItem(typeItem):
	global typeDict
	typeDict.update({ f'{typeItem.typeID}': typeItem})

# Obter um objeto de tipo pelo ID
def GetTypeItem(typeID):
	global typeDict
	if typeID in typeDict:
		return typeDict[typeID]
	return None

# Obter todo o dicionário de tipos
def GetTypeDict():
	global typeDict
	return typeDict

# Incluir um ambiente no dicionário
def AddRoomItem(roomItem):
	global roomDict
	roomDict.update({ f'{roomItem.roomID}': roomItem})

# Obter um objeto de ambiente pelo ID
def GetRoomItem(roomID):
	global roomDict
	if roomID in roomDict:
		return roomDict[roomID]
	return None

# Obter todo o dicionário de ambientes
def GetRoomDict():
	global roomDict
	return roomDict
