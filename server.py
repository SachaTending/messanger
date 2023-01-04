import json

from PyQt6 import QtCore, QtNetwork, QtWebSockets
from PyQt6.QtWidgets import QApplication

last = {
    "user": "System",
    "msg": "Welcome! You first here!"
}

class MyServer(QtCore.QObject):
    def __init__(self, parent):
        super(QtCore.QObject, self).__init__(parent)
        self.clients = []
        self.server = QtWebSockets.QWebSocketServer(parent.serverName(), parent.secureMode(), parent)
        if self.server.listen(QtNetwork.QHostAddress("localhost"), 1302):
            print('Connected: '+self.server.serverName()+' : '
                  +self.server.serverAddress().toString()+':'+str(self.server.serverPort()))
        else:
            print('error')
            QApplication.quit()
        self.server.newConnection.connect(self.onNewConnection)
        self.clientConnection = None
        print(self.server.isListening())

    def onNewConnection(self):
        sock = self.server.nextPendingConnection()
        sock.textMessageReceived.connect(lambda msg: self.processTextMessage(sock, msg))

        sock.binaryMessageReceived.connect(lambda msg: self.processBinaryMessage(sock, msg))
        sock.disconnected.connect(lambda: self.socketDisconnected(sock))

        print("newClient")
        self.clients.append(sock)

    def processTextMessage(self, sock: QtWebSockets.QWebSocket, message):
        data = json.loads(message)
        print(f"[{data['user']}]: {data['msg']}")
        last = data
        if self.clientConnection:
            for client in self.clients:
                # if client!= self.clientConnection:
                client.sendTextMessage(message)
            # self.clientConnection.sendTextMessage(message)

    def processBinaryMessage(self, sock: QtWebSockets.QWebSocket, message):
        print("b:",message)
        if self.clientConnection:
            self.clientConnection.sendBinaryMessage(message)

    def socketDisconnected(self, sock: QtWebSockets.QWebSocket):
        if sock:
            self.clients.remove(sock)
            sock.deleteLater()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    serverObject = QtWebSockets.QWebSocketServer('My Socket', QtWebSockets.QWebSocketServer.SslMode(1))
    server = MyServer(serverObject)
    serverObject.closed.connect(app.quit)
    print(f"Exit code: {app.exec()}")