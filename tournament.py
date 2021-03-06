"""This module includes functions to simulate a tournament between players."""

import time
from multiprocessing import Pool
from os import cpu_count

import draights


def create_roundrobin_schedule(players):
    schedule = []

    if len(players) % 2 == 1:
        players.append(None)

    mid = len(players) // 2
    for i in range(len(players) - 1):
        left = players[:mid]
        right = players[mid:]
        right.reverse()

        if i % 2 == 1:
            schedule.extend(list(zip(left, right)))
        else:
            schedule.extend(list(zip(right, left)))

        players.insert(1, players.pop())

    return schedule + list(tuple(reversed(match)) for match in schedule)


RESULT_BYE = 2


def play_match(players):
    if any(player is None for player in players):
        return RESULT_BYE

    print("Playing {0} - {1}".format(players[0][0].name, players[1][0].name))

    t = time.process_time()
    game = draights.Game((players[0][0], players[1][0]), False)
    _, winner = game.run()
    t = time.process_time() - t

    result = "draw"
    if 0 <= winner <= 1:
        result = players[winner][0].name

    print("{0} - {1}: {2} in {3}".format(players[0][0].name, players[1][0].name,
                                         result, t))

    return winner


def play_roundrobin_tournament(players, num_sets=1, win_points=1,
                               draw_points=0.5, loss_points=0):
    """Simulate a double round robin tournament with all players.

    The total number of matches played will be

        len(players) * (len(players) - 1) * num_sets

    :param players: a list of PlayerConfig objects.
    :param num_sets: the amount of times that players will play against each
        other. (In sets of two: each player plays as white once)
    :param win_points: the amount of points that will be assigned for a win to
        the winning player.
    :param draw_points: the amount of points that will be assigned to both
        players in case of a draw.
    :param loss_points: the amount of points that will be assigned to a player
        in case of a loss.
    """

    t = time.time()

    players = [[player, 0] for player in players]

    matches = create_roundrobin_schedule(players[:])
    matches = matches * num_sets
    print("Playing {0} matches".format(sum(
        match[0] is not None and match[1] is not None for match in matches)))
    with Pool(processes=cpu_count() - 2 or 1) as pool:
        results = pool.map(play_match, matches)

    for i in range(len(results)):
        if 0 <= results[i] <= 1:
            matches[i][results[i]][1] += win_points
            matches[i][not results[i]][1] += loss_points
        elif results[i] == -1:
            matches[i][0][1] += draw_points
            matches[i][1][1] += draw_points

    t = time.time() - t
    print("Tournament finished in {0} seconds".format(t))

    return players
