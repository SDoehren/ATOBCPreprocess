

from collections import Counter as cnt
import numpy as np

def playertable(games,type,quali=15):
    players = {}
    scoreboard = {"Good":0,"Evil":0}

    for gid in games:
        winner = games[gid].result
        scoreboard[winner]+=1
        align = [games[gid].playerobjs[p].currentalignment for p in games[gid].playerobjs]
        align = cnt(align)

        for p in games[gid].playerobjs:
            if p not in players:
                players[p] = {'name': p, 'p': 0, 'w': 0, 'gs': 0, 'gf': 0, 'gw': 0, 'es': 0, 'ef': 0, 'ew': 0}

            players[p]['p'] += 1

            if games[gid].playerobjs[p].startingalignment=="Good":
                players[p]["gs"]+=1
            else:
                players[p]["es"]+=1

            if games[gid].playerobjs[p].currentalignment=="Good":
                players[p]["gf"]+=1
            else:
                players[p]["ef"]+=1

            if games[gid].playerobjs[p].currentalignment==winner:
                if games[gid].playerobjs[p].currentalignment=="Good":
                    players[p]["gw"]+=1
                else:
                    players[p]["ew"]+=1

                players[p]['w'] = players[p]["gw"]+players[p]["ew"]
            #print(games[gid].playerobjs[p].__dict__)


    goodwinper = scoreboard["Good"]/(scoreboard["Good"]+scoreboard["Evil"])
    for p in players:
        xgW = players[p]['gf']*goodwinper
        xeW = players[p]['ef']*(1-goodwinper)
        WARg = players[p]['gw']/(xgW) if xgW>0 else 0
        WARe = players[p]['ew']/(xeW) if xeW>0 else 0

        players[p]["xgW"] = xgW
        players[p]["xeW"] = xeW
        players[p]["xW"] = xgW+xeW
        players[p]["WARg"] = WARg
        players[p]["WARe"] = WARe

    WARgs = [players[p]["WARg"] for p in players if players[p]["p"]>quali]
    adWARgs = {p:players[p]["WARg"]-min(WARgs) for p in players}
    adWARgs = {p:adWARgs[p]/max(adWARgs.values()) if players[p]["p"]>quali else -1 for p in players}

    WARes = [players[p]["WARe"] for p in players if players[p]["p"]>quali]
    adWARes = {p: players[p]["WARe"] - min(WARes) for p in players}
    adWARes = {p: adWARes[p] / max(adWARes.values()) if players[p]["p"] > quali else -1 for p in players}

    for p in players:
        players[p]["WARg"] = adWARgs[p]
        players[p]["WARe"] = adWARes[p]
        players[p]["WAR"] = (adWARes[p]+adWARgs[p])/2 if players[p]["p"]>quali else 0


    codechange = {'p':'Played', 'w':"Wins", 'gs':"Good Starts", 'gf':"Good Finishes", 'gw':"Good Wins",
                  'es':"Evil Starts", 'ef':"Evil Finishes", 'ew':"Good Wins",
                  'xgW':"Expected Good Wins", 'xeW':"Expected Evil Wins", 'xW':"Expected Wins",
                  'WARg':"Good WAR", 'WARe':"Evil WAR", 'WAR':"WAR"}

    editedplayers = {}
    for p in players:
        editedplayers[p] = {}
        for cc in codechange:
            editedplayers[p][f"{type}{codechange[cc]}"] = players[p][cc]
    return editedplayers

def gettabledata(games):
    last25 = list(games.keys())[-25:]
    all = playertable(games,"", quali=15)
    last25 = playertable({gid: games[gid] for gid in games if gid in last25}, "Last 25-", quali=5)

    combined = {}

    roundem = ["Expected Good Wins", "Expected Evil Wins", "Expected Wins", "Good WAR", "Evil WAR", "WAR"]

    for p in last25:
        combined[p] = {**all[p], **last25[p]}

        for r in ["Expected Good Wins", "Expected Evil Wins", "Expected Wins"]:
            for t in ["","Last 25-"]:
                combined[p][f"{t}{r}"] = float(np.round(combined[p][f"{t}{r}"],2))

        for r in ["Good WAR", "Evil WAR", "WAR"]:
            for t in ["","Last 25-"]:
                combined[p][f"{t}{r}"] = float(np.round(combined[p][f"{t}{r}"]*100,2))

        combined[p]["Combined WAR"] = float(np.round((combined[p]["WAR"]+combined[p]["Last 25-WAR"])/2,2))
        if combined[p]["Combined WAR"]<0: combined[p][f"Combined WAR"] = 0

    return combined, list(last25.keys())

if __name__ == '__main__':
    import pickle


    games = pickle.load(open(r'games.p', "rb"))
    gettabledata(games)


