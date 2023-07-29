import os

with open('train') as train:
    data = list()
    tracks_stat = dict()
    lines = train.readlines()
    for line in lines:
        user = list()
        tracks = line.strip().split(' ')
        for track in tracks:
            if track not in tracks_stat:
                tracks_stat[track] = 0
            tracks_stat[track] += 1
            user.append(track)
        data.append(user)
    print(len(data), len(tracks_stat))
    print(tracks_stat)