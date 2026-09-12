#####################################################
#                                                   #
# Título do trabalho: Trabalho de Sockets           #
#         Disciplina: Redes de Computadores PPComp  #
#                                                   #
#####################################################

from Config import *
from Message import *
from ClientUtil import *
import socket

deviceID = None

####################
# Inicializando... #
####################
if __name__ == '__main__':
	print('Inicializando cliente: Ar-Condicionado Inteligente...')
	try:
		connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		destination = (SERVIDOR, PORTA)
		connection.connect(destination)
	except:
		print(f'Falha ao tentar se conectar com o servidor {SERVIDOR} porta {PORTA}')
		exit()

	device = Device(connection, NUM_AR_CONDICIONADO)
	roomDict = ClientRegister(device)
	if roomDict != None:
		deviceID, roomID, roomName = SelectRoom(device, roomDict)
		if deviceID != None:
			print(f'\n[AR-CONDICIONADO ID={deviceID}] Operando no ambiente [{roomID}] {roomName}')
			print('Aguardando comandos de acionamento do servidor...\n')
			while True:
				print(f'\n==> Ambiente [{roomID}] {roomName}')
				msg = ReceiveMessage(connection, device)
				if msg is None:
					print('Conexão encerrada pelo servidor.')
					break

				if msg.code == MSG_AR_CONDICIONADO:
					print('Comando de climatização recebido do servidor!')
					print('=============================================')
					if msg.action == AR_LIGADO:
						print('         >>> AR-CONDICIONADO LIGADO <<<')
						print(f'          Temperatura Alvo: {msg.targetTemp:.1f} °C')
						print('          Modo: Refrigeração Automática')
					elif msg.action == AR_DESLIGADO:
						print('        >>> AR-CONDICIONADO DESLIGADO <<<')
						print('          Modo: Standby / Desligado')
					else:
						print(f'Ação inválida recebida: {msg.action}')
					print('=============================================')
					
					# Envia confirmação de ação executada para o servidor
					statusMsg = MessageStatus()
					connection.send(statusMsg.pack(deviceID, ACAO_EXECUTADA))
					print('Confirmação [Ação Executada] enviada ao servidor.')
				else:
					print('Mensagem inesperada recebida, código:', msg.code)
		connection.close()
	print('Cliente Ar-Condicionado finalizado.')
