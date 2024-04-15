import os
import json
import random

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

def is_coordinate_in_list(coord_list, target_coord):
    for coord in coord_list:
        if coord == target_coord:
            return True
    return False


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
    Prints a MQTT message to stdout (used as a callback for subscribe).
    :param client: the client itself
    :param userdata: userdata is set when initiating the client, here it is userdata=None
    :param msg: the message with topic and payload
    """
    if msg.topic == "games/TestLobby/Player1/game_state":
        # Decode the message payload from bytes to string using UTF-8 and load into JSON
        game_state = json.loads(msg.payload.decode('utf-8'))
        print("Game State Decoded Successfully")

        walls = game_state.get("walls", [])
        coins = [game_state.get(f"coin{i + 1}", []) for i in range(3) if game_state.get(f"coin{i + 1}", [])]
        position = game_state["currentPosition"]
        if len(coins) != 0:
            coins = coins[0]
            next_move = find_coin(position, coins, walls)
        else:
            next_move = move_random(position, walls)
        print(f"Next Move: {next_move}")
        client.publish(f"games/{lobby_name}/{player_1}/move", next_move)
    if msg.topic == "games/TestLobby/Player2/game_state":
        # Decode the message payload from bytes to string using UTF-8 and load into JSON
        game_state = json.loads(msg.payload.decode('utf-8'))
        print("Game State Decoded Successfully")

        walls = game_state.get("walls", [])
        coins = [game_state.get(f"coin{i + 1}", []) for i in range(3) if game_state.get(f"coin{i + 1}", [])]
        position = game_state["currentPosition"]
        if len(coins) != 0:
            coins = coins[0]
            next_move = find_coin(position, coins, walls)
        else:
            next_move = move_random(position, walls)
        print(f"Next Move: {next_move}")
        client.publish(f"games/{lobby_name}/{player_2}/move", next_move)
    if msg.topic == "games/TestLobby/Player3/game_state":
        # Decode the message payload from bytes to string using UTF-8 and load into JSON
        game_state = json.loads(msg.payload.decode('utf-8'))
        print("Game State Decoded Successfully")

        walls = game_state.get("walls", [])
        coins = [game_state.get(f"coin{i + 1}", []) for i in range(3) if game_state.get(f"coin{i + 1}", [])]
        position = game_state["currentPosition"]
        if len(coins) != 0:
            coins = coins[0]
            next_move = find_coin(position, coins, walls)
        else:
            next_move = move_random(position, walls)
        print(f"Next Move: {next_move}")
        client.publish(f"games/{lobby_name}/{player_3}/move", next_move)
    if msg.topic == "games/TestLobby/Player4/game_state":
        # Decode the message payload from bytes to string using UTF-8 and load into JSON
        game_state = json.loads(msg.payload.decode('utf-8'))
        print("Game State Decoded Successfully")

        walls = game_state.get("walls", [])
        coins = [game_state.get(f"coin{i + 1}", []) for i in range(3) if game_state.get(f"coin{i + 1}", [])]
        position = game_state["currentPosition"]
        if len(coins) != 0:
            coins = coins[0]
            next_move = find_coin(position, coins, walls)
        else:
            next_move = move_random(position, walls)
        print(f"Next Move: {next_move}")
        client.publish(f"games/{lobby_name}/{player_4}/move", next_move)


def find_coin(position, coins, walls):
    nearest_coin = None
    min_distance = float('inf')
    # sleeep half a second
    time.sleep(0.5)
    for coin in coins:
        dist = abs(coin[0] - position[0]) + abs(coin[1] - position[1])
        if dist < min_distance:
            nearest_coin = coin
            min_distance = dist

    # Calculate move direction towards the nearest coin
    if nearest_coin:
        y_diff = nearest_coin[0] - position[0]
        x_diff = nearest_coin[1] - position[1]

        if x_diff != 0:
            if x_diff > 0:
                if not is_coordinate_in_list(walls, [position[0], position[1] + 1]):
                    return "RIGHT"  # Move right if not blocked and the coin is to the right in x-coordinate
            elif x_diff < 0:
                if not is_coordinate_in_list(walls, [position[0], position[1] - 1]):
                    return "LEFT"
            else:
                if not is_coordinate_in_list(walls, [position[0] + 1, position[1]]):
                    return "DOWN"  # Move down if not blocked and the coin is lower in y-coordinate
                elif y_diff < 0:
                    if not is_coordinate_in_list(walls, [position[0] - 1, position[1]]):
                        return "UP"
        if y_diff != 0:
            if y_diff > 0:
                if not is_coordinate_in_list(walls, [position[0] + 1, position[1]]):
                    return "DOWN"  # Move down if not blocked and the coin is lower in y-coordinate
            elif y_diff < 0:
                if not is_coordinate_in_list(walls, [position[0] - 1, position[1]]):
                    return "UP"
            else:
                if x_diff > 0:
                    if not is_coordinate_in_list(walls, [position[0], position[1] + 1]):
                        return "RIGHT"  # Move right if not blocked and the coin is to the right in x-coordinate
                elif x_diff < 0:
                    if not is_coordinate_in_list(walls, [position[0], position[1] - 1]):
                        return "LEFT"

        directions = [
            ("DOWN", [position[0] + 1, position[1]]),
            ("UP", [position[0] - 1, position[1]]),
            ("RIGHT", [position[0], position[1] + 1]),
            ("LEFT", [position[0], position[1] - 1])
        ]

        # Shuffle the list to randomize the order of direction checking
        random.shuffle(directions)

        # Check each direction in the shuffled list
        for direction, new_position in directions:
            if not is_coordinate_in_list(walls, new_position):
                return direction

def move_random(position, walls):
    # target = [4, 4]
    # y_diff = target[0] - position[0]
    # x_diff = target[1] - position[1]
    #
    # # Prioritize moving towards the target y-coordinate (vertical movement)
    # if y_diff != 0:
    #     if y_diff > 0 and not is_coordinate_in_list(walls, [position[0] + 1, position[1]]):
    #         return "DOWN"  # Move downwards if not blocked and the center is below
    #     elif y_diff < 0 and not is_coordinate_in_list(walls, [position[0] - 1, position[1]]):
    #         return "UP"    # Move upwards if not blocked and the center is above
    #
    # # If vertical movement is not needed or blocked, try moving horizontally
    # if x_diff != 0:
    #     if x_diff > 0 and not is_coordinate_in_list(walls, [position[0], position[1] + 1]):
    #         return "RIGHT"  # Move to the right if not blocked and the center is to the right
    #     elif x_diff < 0 and not is_coordinate_in_list(walls, [position[0], position[1] - 1]):
    #         return "LEFT"   # Move to the left if not blocked and the center is to the left
    # else:
    #     if not is_coordinate_in_list(walls, [position[0] + 1, position[1]]):
    #         return "DOWN"
    #     elif not is_coordinate_in_list(walls, [position[0] - 1, position[1]]):
    #         return "UP"
    #     elif not is_coordinate_in_list(walls, [position[0], position[1]+1]):
    #         return "RIGHT"
    #     elif not is_coordinate_in_list(walls, [position[0], position[1]-1]):
    #         return "LEFT"

    # while(1):
    #     x = random.randint(1, 4)
    #     if x == 1:
    #         if not is_coordinate_in_list(walls, [position[0] + 1, position[1]]):
    #             return "DOWN"
    #     elif x == 2:
    #         if not is_coordinate_in_list(walls, [position[0] - 1, position[1]]):
    #              return "UP"
    #     elif x == 3:
    #         if not is_coordinate_in_list(walls, [position[0], position[1] + 1]):
    #             return "RIGHT"
    #     elif x == 4:
    #         if not is_coordinate_in_list(walls, [position[0], position[1] - 1]):
    #             return "LEFT"
    time.sleep(0.5)
    directions = [
        ("DOWN", [position[0] + 1, position[1]]),
        ("UP", [position[0] - 1, position[1]]),
        ("RIGHT", [position[0], position[1] + 1]),
        ("LEFT", [position[0], position[1] - 1])
    ]

    # Shuffle the list to randomize the order of direction checking
    random.shuffle(directions)

    # Check each direction in the shuffled list
    for direction, new_position in directions:
        if not is_coordinate_in_list(walls, new_position):
            return direction



if __name__ == '__main__':
    load_dotenv(dotenv_path='credentials.env')

    broker_address = os.environ.get('BROKER_ADDRESS')
    broker_port = int(os.environ.get('BROKER_PORT'))
    username = os.environ.get('USER_NAME')
    password = os.environ.get('PASSWORD')

    client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="Player1", userdata=None,
                         protocol=paho.MQTTv5)

    # enable TLS for secure connection
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    # set username and password
    client.username_pw_set(username, password)
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect(broker_address, broker_port)

    # setting callbacks, use separate functions like above for better visibility
    client.on_subscribe = on_subscribe  # Can comment out to not print when subscribing to new topics
    client.on_message = on_message
    client.on_publish = on_publish  # Can comment out to not print when publishing to topics

    lobby_name = "TestLobby"
    player_1 = "Player1"
    player_2 = "Player2"
    player_3 = "Player3"
    player_4 = "Player4"

    client.subscribe(f"games/{lobby_name}/lobby")
    client.subscribe(f'games/{lobby_name}/+/game_state')
    client.subscribe(f'games/{lobby_name}/scores')

    client.publish("new_game", json.dumps({'lobby_name': lobby_name,
                                           'team_name': 'ATeam',
                                           'player_name': player_1}))

    client.publish("new_game", json.dumps({'lobby_name':lobby_name,
                                            'team_name':'ATeam',
                                            'player_name' : player_2}))

    client.publish("new_game", json.dumps({'lobby_name':lobby_name,
                                        'team_name':'BTeam',
                                        'player_name' : player_3}))
    client.publish("new_game", json.dumps({'lobby_name': lobby_name,
                                           'team_name': 'BTeam',
                                           'player_name': player_4}))

    time.sleep(1)  # Wait a second to resolve game start
    client.publish(f"games/{lobby_name}/start", "START")
    # client.publish(f"games/{lobby_name}/{player_1}/move", "UP")
    # client.publish(f"games/{lobby_name}/{player_2}/move", "DOWN")
    # client.publish(f"games/{lobby_name}/{player_3}/move", "DOWN")
    # client.publish(f"games/{lobby_name}/start", "STOP")

    client.loop_forever()