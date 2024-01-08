# test_PeerClient.py

import unittest
import PeerClient
from unittest.mock import Mock,patch
from PeerClient import *

class TestIsValidChatroom(unittest.TestCase):
    def setUp(self):
        # create a mock client object
        self.client = unittest.mock.Mock()
        # create a mock input function
        self.input = unittest.mock.Mock()
        # create a mock print function
        self.print = unittest.mock.Mock()
        # create a mock username
        #client.username = "Alice"







    def test_valid_input(self):
        # test if the function returns True for a valid input
        input_text = "/join room1"
        available_chatrooms = ["room1", "room2", "room3"]
        expected_output = True
        actual_output = PeerClient.is_valid_chatroom(input_text, available_chatrooms)
        self.assertEqual(expected_output, actual_output)

    def test_invalid_input(self):
        # test if the function returns False for an invalid input
        input_text = "/join room4"
        available_chatrooms = ["room1", "room2", "room3"]
        expected_output = False
        actual_output = PeerClient.is_valid_chatroom(input_text, available_chatrooms)
        self.assertEqual(expected_output, actual_output)


#################################################################
    def test_handle_room(self):
        # test the case when the user chooses to connect to a private chatroom
        self.input.side_effect = [1, "person_name : Bob"]
        PeerClient.handle_room("person online", 0)
        # check that the client sent the correct messages
        self.client.send.assert_has_calls([unittest.mock.call(b'PRIVATE'), unittest.mock.call(b'person_name : Bob')])
        # check that the input function was called with the correct prompts
        self.input.assert_has_calls([unittest.mock.call(), unittest.mock.call()])
        # check that the print function was called with the correct messages
        self.print.assert_has_calls([unittest.mock.call("1. connect to a private chatroom\n2. connect to a group chatroom\n"), unittest.mock.call("person online"), unittest.mock.call("Please enter the name of the person you want to chat with this format person_name : <name>")])

        # test the case when the user chooses to connect to a group chatroom
        self.input.side_effect = [2, "/join test_room"]
        PeerClient.handle_room("test_room", 0)
        # check that the client sent the correct messages
        self.client.send.assert_has_calls([unittest.mock.call(b'GROUP'), unittest.mock.call(b'/join test_room')])
        # check that the input function was called with the correct prompts
        self.input.assert_has_calls([unittest.mock.call(), unittest.mock.call()])
        # check that the print function was called with the correct messages
        self.print.assert_has_calls([unittest.mock.call("1. connect to a private chatroom\n2. connect to a group chatroom\n"), unittest.mock.call("\nAvailable Chatrooms. To choose a chatroom, enter /join test_room ,\n to create a chatroom enter /create <name> \n to leave enter /leave: \n")])

        # test the case when the user enters an invalid choice
        self.input.side_effect = [3]
        PeerClient.handle_room("", 0)
        # check that the print function was called with the correct messages
        self.print.assert_has_calls([unittest.mock.call("1. connect to a private chatroom\n2. connect to a group chatroom\n"), unittest.mock.call("invalid choice")])
###################################################################################################################
    @patch('Registry.msg')
    @patch('Registry.choice')
    def test_handle_room(self, mock_choice, mock_msg):
        # set the mock arguments to some values
        mock_choice.return_value = 1
        mock_msg.return_value = 'some message'
        # call the function with the mock arguments
        PeerClient.handle_room(mock_msg, mock_choice)
        self.assertEqual(mock_choice,1)




    def tearDown(self):
        # delete the mock objects
        del self.client
        del self.input
        del self.print


if __name__ == '__main__':
    unittest.main()
