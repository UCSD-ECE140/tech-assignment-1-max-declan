import os
import json
from dotenv import load_dotenv

import paho.mqtt.client as paho
from paho import mqtt
import time

from enum import Enum


class Moveset(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)


# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    """
        Prints the result of the connection with a reasoncode to stdout ( used as callback for connect )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param flags: these are response flags sent by the broker
        :param rc: stands for reasonCode, which is a code for the connection result
        :param properties: can be used in MQTTv5, but is optional
    """
    print("CONNACK received with code %s." % rc)


# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    """
        Prints mid to stdout to reassure a successful publish ( used as callback for publish )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param properties: can be used in MQTTv5, but is optional
    """
    print("mid: " + str(mid))


# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    """
        Prints a reassurance for successfully subscribing
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param granted_qos: this is the qos that you declare when subscribing, use the same one for publishing
        :param properties: can be used in MQTTv5, but is optional
    """
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    """
        Prints a mqtt message to stdout ( used as callback for subscribe )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param msg: the message with topic and payload
    """

    try:
        print(f"Received message on {msg.topic} with QoS {msg.qos}")

        # Decode the message payload using explicit UTF-8 encoding
        game_state = json.loads(msg.payload.decode('utf-8'))
        print("Game State Decoded:", game_state)

        player_position = tuple(game_state["currentPosition"])
        coins = [tuple(game_state[coin]) for coin in ["coin1", "coin2", "coin3"] if game_state[coin]]
        walls = [tuple(wall) for wall in game_state["walls"]]

        print("Player Position:", player_position)
        print("Coins:", coins)
        print("Walls:", walls)

        # Decide the next move based on the current game state
        next_move = decide_next_move(player_position, coins, walls)
        print("Decided Move:", next_move)

        # Ensure the next_move is a string, as MQTT expects the payload to be a string or bytes
        if next_move:
            client.publish(f"games/{lobby_name}/{player_1}/move", next_move)
        else:
            print("No valid move was calculated.")

    except Exception as e:
        print(f"An error occurred while processing the message: {e}")

    print("End of message processing.")

    # Make sure to set up your MQTT client with the correct callbacks
    client = mqtt.Client()
    client.on_message = on_message
    client.connect("mqtt_broker_address", 1883, 60)  # Update with your MQTT broker's address and port
    client.subscribe("games/TestLobby/Player1/game_state", qos=1)
    client.loop_forever()  # Start the network loop


def calculate_distance(start, end):
    # Using Manhattan distance for grid movement
    return abs(start[0] - end[0]) + abs(start[1] - end[1])

def is_path_blocked(start, end, walls):
    # Check if there's a straight line path to the coin without walls blocking
    # This function assumes walls are a list of tuples (x, y)
    if start[0] == end[0]:  # same row
        for y in range(min(start[1], end[1]) + 1, max(start[1], end[1])):
            if (start[0], y) in walls:
                return True
    elif start[1] == end[1]:  # same column
        for x in range(min(start[0], end[0]) + 1, max(start[0], end[0])):
            if (x, start[1]) in walls:
                return True
    return False

def get_direction(start, goal):
    # Determine the simple step direction to move towards the goal
    if goal[0] > start[0]:
        return "RIGHT"
    elif goal[0] < start[0]:
        return "LEFT"
    elif goal[1] > start[1]:
        return "DOWN"
    elif goal[1] < start[1]:
        return "UP"

def decide_next_move(player_position, coins, walls):
    # Move towards the nearest accessible coin
    best_coin = None
    min_distance = float('inf')

    for coin in coins:
        if not is_path_blocked(player_position, coin, walls):
            distance = calculate_distance(player_position, coin)
            if distance < min_distance:
                min_distance = distance
                best_coin = coin

    if best_coin:
        # Determine the direction to move towards the best coin
        return get_direction(player_position, best_coin)

    # If no accessible coin, move towards the middle of the grid
    grid_center = [5, 5]  # Example center for a 10x10 grid
    return get_direction(player_position, grid_center)


if __name__ == '__main__':
    load_dotenv(dotenv_path='credentials.env')
    
    broker_address = os.environ.get('BROKER_ADDRESS')
    broker_port = int(os.environ.get('BROKER_PORT'))
    username = os.environ.get('USER_NAME')
    password = os.environ.get('PASSWORD')

    client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="Player1", userdata=None, protocol=paho.MQTTv5)
    
    # enable TLS for secure connection
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    # set username and password
    client.username_pw_set(username, password)
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect(broker_address, broker_port)

    # setting callbacks, use separate functions like above for better visibility
    client.on_subscribe = on_subscribe # Can comment out to not print when subscribing to new topics
    client.on_message = on_message
    client.on_publish = on_publish # Can comment out to not print when publishing to topics

    lobby_name = "TestLobby"
    player_1 = "Player1"
    # player_2 = "Player2"
    # player_3 = "Player3"

    client.subscribe(f"games/{lobby_name}/lobby")
    client.subscribe(f'games/{lobby_name}/+/game_state')
    client.subscribe(f'games/{lobby_name}/scores')

    client.publish("new_game", json.dumps({'lobby_name':lobby_name,
                                            'team_name':'ATeam',
                                            'player_name' : player_1}))
    
    # client.publish("new_game", json.dumps({'lobby_name':lobby_name,
    #                                         'team_name':'BTeam',
    #                                         'player_name' : player_2}))
    #
    # client.publish("new_game", json.dumps({'lobby_name':lobby_name,
    #                                     'team_name':'BTeam',
    #                                     'player_name' : player_3}))

    time.sleep(1) # Wait a second to resolve game start
    client.publish(f"games/{lobby_name}/start", "START")
    # client.publish(f"games/{lobby_name}/{player_1}/move", "UP")
    # client.publish(f"games/{lobby_name}/{player_2}/move", "DOWN")
    # client.publish(f"games/{lobby_name}/{player_3}/move", "DOWN")
    # client.publish(f"games/{lobby_name}/start", "STOP")


    client.loop_forever()
