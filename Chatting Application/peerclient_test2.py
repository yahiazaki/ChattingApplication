import unittest
import socket
import DB






class TestPeerMain(unittest.TestCase):
    def setUp(self):
        # ip address of the server
        self.host = '127.0.0.1'
        # port number of the server
        self.port = 55555
        # tcp socket connection to server
        self.tcpClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpClientSocket.connect((self.host, self.port))


    def test_login_scenario(self):
        Credentials = 'Login' + 'mazen123' + '12345' + 'mazen' + 'GROUP' + '/join' + 'General'
        self.tcpClientSocket.send(Credentials.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "Register/Login")




    def test_Register(self):

        Credentials= 'Register'+ 'ahmed123'+ '123456'+ 'ahmed'+'GROUP'+'/join'+'Sports'
        self.tcpClientSocket.send(Credentials.encode('utf-8'))
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "Register/Login")

    def test_create(self):

        Credentials = 'Login' + 'aly123' + '12345' + 'aly' + 'GROUP'+'/create'+'main1'
        self.tcpClientSocket.send(Credentials.encode('utf-8'))
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "Register/Login")

    def test_create2(self):
        Credentials = 'Register' + 'ibrahim123' + '12349' + 'ibrahim' + 'GROUP' + '/create' + 'newroom'
        self.tcpClientSocket.send(Credentials.encode('utf-8'))
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "Register/Login")


    def test_join1(self):

        Credentials = 'Register' + 'mahmoud123' + '123458' + 'mahmoud' + 'GROUP'+'/join'+'Music'
        self.tcpClientSocket.send(Credentials.encode('utf-8'))
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "Register/Login")


    def test_join2(self):

        Credentials = 'Register' + 'mohamed123' + '12347' + 'mohamed' + 'GROUP'+'/join'+'sports'
        self.tcpClientSocket.send(Credentials.encode('utf-8'))
        response = self.tcpClientSocket.recv(1024).decode()
        self.assertEqual(response, "Register/Login")














if __name__ == "__main__":
    unittest.main()