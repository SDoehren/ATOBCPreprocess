
import pandas as pd
pd.set_option('display.max_rows', 100)
pd.set_option('display.min_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 200)
import numpy as np

def getwinningestplayer(games):
    played = {}
    won = {}
    for gid in games:
        for p in games[gid].playerobjs:
            if p not in played:
                played[p] = 0
                won[p] = 0
            played[p] += 1
            if games[gid].playerobjs[p].win:
                won[p] += 1
    winper = {p:won[p]/played[p] for p in played}
    table = [[p,played[p],won[p],int(np.round(winper[p],2)*100),played[p]>=15] for p in played]
    table.sort(key=lambda x: x[2], reverse=True)
    table.sort(key= lambda x:x[3], reverse=True)
    table.sort(key= lambda x:x[4], reverse=True)
    return table

def getwinningestrole(games):
    played = {}
    won = {}
    for gid in games:
        allroles = [games[gid].playerobjs[p].startingrole for p in games[gid].playerobjs]
        if "Legion" in allroles or "Riot" in allroles:
            continue
        for p in games[gid].playerobjs:
            role = games[gid].playerobjs[p].startingrole

            if role not in played:
                played[role] = 0
                won[role] = 0
            played[role] += 1
            if games[gid].playerobjs[p].win:
                won[role] += 1
    winper = {p:won[p]/played[p] for p in played}
    table = [[p,played[p],won[p],int(np.round(winper[p],2)*100),played[p]>=5] for p in played]
    table.sort(key=lambda x: x[2], reverse=True)
    table.sort(key= lambda x:x[3], reverse=True)
    table.sort(key= lambda x:x[4], reverse=True)
    return table

def getstickiestfingers(games):
    played = {}
    evil = {}
    good = {}
    switch = {}
    for gid in games:
        for p in games[gid].playerobjs:
            if p not in played:
                played[p] = 0
                evil[p] = 0
                good[p] = 0
                switch[p] = 0
            played[p] += 1
            if games[gid].playerobjs[p].startingalignment == "Evil":
                evil[p] += 1
            if games[gid].playerobjs[p].currentalignment == "Good":
                good[p] += 1
            if games[gid].playerobjs[p].currentalignment != games[gid].playerobjs[p].startingalignment:
                switch[p] += 1
    evilper = {p: evil[p] / played[p] for p in played}
    eviltable = [[p, played[p], evil[p], int(np.round(evilper[p], 2) * 100), played[p] >= 15] for p in played]
    eviltable.sort(key=lambda x: x[2], reverse=True)
    eviltable.sort(key=lambda x: x[3], reverse=True)
    eviltable.sort(key=lambda x: x[4], reverse=True)

    goodper = {p: good[p] / played[p] for p in played}
    goodtable = [[p, played[p], good[p], int(np.round(goodper[p], 2) * 100), played[p] >= 15] for p in played]
    goodtable.sort(key=lambda x: x[2], reverse=True)
    goodtable.sort(key=lambda x: x[3], reverse=True)
    goodtable.sort(key=lambda x: x[4], reverse=True)

    switchper = {p: switch[p] / played[p] for p in played}
    switchtable = [[p, played[p], switch[p], int(np.round(switchper[p], 2) * 100), played[p] >= 15] for p in played]
    switchtable.sort(key=lambda x: x[2], reverse=True)
    switchtable.sort(key=lambda x: x[3], reverse=True)
    switchtable.sort(key=lambda x: x[4], reverse=True)

    return eviltable,goodtable,switchtable

def nominations(games):
    played = {}
    evil = {}
    good = {}
    switch = {}
    for gid in games:
        print(games[gid].keys())

def awardpackgen(games):
    awardpack = {}

    winningestplayer = getwinningestplayer(games)
    winners = "|".join([x[0] for x in winningestplayer if x[3]==winningestplayer[0][3] and x[4]])
    pack = {"table":winningestplayer,  "name": "Winningest Player",  "details": "Most Wins",
            "note":"Minimum 15 games to qualify", 'winners':winners,'score':f"{winningestplayer[0][3]}%"}
    awardpack['winningestplayer'] = pack

    winningestrole = getwinningestrole(games)
    winners = "|".join([x[0] for x in winningestrole if x[3]==winningestrole[0][3] and x[4]])
    pack = {"table": winningestrole, 'winners':winners,'score':f"{winningestrole[0][3]}%", "name": "Winningest Role", "details":"Most Wins",
            "note": "Based on starting role, minimum 5 games to qualify, Legion and Riot games excluded."}
    awardpack['winningestrole'] = pack

    stickiestfingers,goodest,switchhitter = getstickiestfingers(games)

    winners = "|".join([x[0] for x in stickiestfingers if x[3] == stickiestfingers[0][3] and x[4]])
    pack = {"table": stickiestfingers, "name": "Sticky Fingers", "details": "Most Times starting as Evil",
            "note": "Minimum 15 games to qualify", 'winners':winners,'score':f"{stickiestfingers[0][3]}%"}
    awardpack['stickyfingers'] = pack

    winners = "|".join([x[0] for x in goodest if x[3] == goodest[0][3] and x[4]])
    pack = {"table": goodest, "name": "Goodest", "details": "Most Times ending as Good",
            "note": "Minimum 15 games to qualify", 'winners':winners,'score':f"{goodest[0][3]}%"}
    awardpack['goodest'] = pack

    winners = "|".join([x[0] for x in switchhitter if x[3] == switchhitter[0][3] and x[4]])
    pack = {"table": switchhitter, "name": "Switch Hitter", "details": "Most Times starting and ending with different alignments",
            "note": "Minimum 15 games to qualify", 'winners':winners,'score':f"{switchhitter[0][3]}%"}
    awardpack['switchhitter'] = pack

    for x in winningestrole:
        print(f"{x[0]}:{x[3]}% (played:{x[1]})")

    return awardpack

if __name__ == '__main__':
    import pickle

    games = pickle.load(open(r'games.p', "rb"))

    awardpackgen(games)