
import pandas as pd
pd.set_option('display.max_rows', 100)
pd.set_option('display.min_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 200)
import numpy as np
from itertools import combinations

def standardsort(l):
    l.sort(key=lambda x: x[2], reverse=True)
    l.sort(key=lambda x: x[3], reverse=True)
    l.sort(key=lambda x: x[4], reverse=True)
    return l

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
    table = standardsort(table)

    winners = " | ".join([x[0] for x in table if x[3] == table[0][3] and x[4]])
    pack = {"table": table, "name": "Winningest Player", "details": "Most Wins",
            "note": "Minimum 15 games to qualify", 'winners': winners, 'score': f"{table[0][3]}%",
            'suffix': "%",
            "scorecalc": "Won/Games Played"}

    return {'winningestplayer':pack}

def getwinningestrole(games):
    played = {}
    won = {}
    for gid in games:
        allroles = [games[gid].playerobjs[p].startingrole for p in games[gid].playerobjs]
        if "Legion" in allroles or "Riot" in allroles:
            continue
        for p in games[gid].playerobjs:
            role = games[gid].playerobjs[p].startingrole
            if games[gid].playerobjs[p].startingalignment == "Evil":
                if role not in played:
                    played[role] = 0
                    won[role] = 0
                played[role] += 1
                if games[gid].playerobjs[p].win:
                    won[role] += 1
    winper = {p:won[p]/played[p] for p in played}
    table = [[p,played[p],won[p],int(np.round(winper[p],2)*100),played[p]>=5] for p in played]
    table = standardsort(table)

    winners = " | ".join([x[0] for x in table if x[3] == table[0][3] and x[4]])
    pack = {"table": table, 'winners': winners, 'score': f"{table[0][3]}%", "name": "Winningest Role",
            "details": "Most Wins",
            "note": "Based on starting role, minimum 5 games to qualify, Legion and Riot games excluded.",
            'suffix': "%",
            "scorecalc": "Won/Games Played"}

    return {'winningestrole':pack}

def getroleawards(games):
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
    stickiestfingers = standardsort(eviltable)

    goodper = {p: good[p] / played[p] for p in played}
    goodtable = [[p, played[p], good[p], int(np.round(goodper[p], 2) * 100), played[p] >= 15] for p in played]
    goodest = standardsort(goodtable)

    switchper = {p: switch[p] / played[p] for p in played}
    switchtable = [[p, played[p], switch[p], int(np.round(switchper[p], 2) * 100), played[p] >= 15] for p in played]
    switchhitter = standardsort(switchtable)

    winners = " | ".join([x[0] for x in stickiestfingers if x[3] == stickiestfingers[0][3] and x[4]])
    stickiestfingerspack = {"table": stickiestfingers, "name": "Sticky Fingers", "details": "Most Times starting as Evil",
            "note": "Minimum 15 games to qualify", 'winners': winners, 'score': f"{stickiestfingers[0][3]}%",
            'suffix': "%",
            "scorecalc": "Start as Evil/Games Played"}

    winners = " | ".join([x[0] for x in goodest if x[3] == goodest[0][3] and x[4]])
    goodestpack = {"table": goodest, "name": "Goodest", "details": "Most Times ending as Good",
            "note": "Minimum 15 games to qualify", 'winners': winners, 'score': f"{goodest[0][3]}%", 'suffix': "%",
            "scorecalc": "Ends as Good/Games Played"}

    winners = " | ".join([x[0] for x in switchhitter if x[3] == switchhitter[0][3] and x[4]])
    switchhitterpack = {"table": switchhitter, "name": "Switch Hitter",
            "details": "Most Times starting and ending with different alignments",
            "note": "Minimum 15 games to qualify", 'winners': winners, 'suffix': "%", 'score': f"{switchhitter[0][3]}%",
            "scorecalc": "Start and Finish Alignment Different/Games Played"}

    return {'stickyfingers':stickiestfingerspack,'goodest':goodestpack,'switchhitter':switchhitterpack}

def nominationawards(games):
    played = {}
    nomopportunity = {}
    noms = {}
    selfnom = {}
    novotenom = {}
    demonhunter = {}
    demonhunteroppo = {}
    whome = {}
    earlybird = {}
    theworm = {}

    for gid in games:
        for p in games[gid].playerobjs:

            if p not in played:
                played[p] = 0
                selfnom[p] = 0
                nomopportunity[p] = 0
                novotenom[p] = 0
                noms[p] = 0
                demonhunter[p] = 0
                demonhunteroppo[p] = 0
                whome[p] = 0
                earlybird[p] = 0
                theworm[p] = 0

            played[p] += 1

        phase = ""
        demons = []
        living = []
        good = []
        newday = True
        for e in games[gid].events:
            if e.phase != phase:
                phase = e.phase
                living = [p for p in e.playerpack if e.playerpack[p]['alive']]
                demons = [p for p in e.playerpack if e.playerpack[p]['currenttype'] == 'Demon']
                good = [pl for pl in e.playerpack if e.playerpack[p]['currentalignment'] == 'Good']

                if "D" in phase:
                    for p in living:
                        nomopportunity[p] += 1
                        if p in good and len(demons)>0:
                            demonhunteroppo[p] += 1
                    newday = True

            if e.nomination != []:
                player,target,pack = e.nomination


                noms[player] += 1
                if target != 'Storyteller':
                    whome[target] += 1

                if newday:
                    earlybird[player] += 1
                    if target != 'Storyteller':
                        theworm[target] += 1
                    newday=False

                if player == target:
                    selfnom[player] += 1
                if len(demons) > 0:
                    if player in [p for p in e.playerpack if e.playerpack[p]['currentalignment'] == 'Good']:
                        if target in demons and player in good:
                            demonhunter[player] += 1

                if pack is None:
                    novotenom[player] += 1
                else:
                    livingvotes,deadvotes,votesreceived,ontheblock,votepack = pack

            #self.player,self.targetlist[0],[livingvotes,deadvotes,votesreceived,votedetails['On the Block'] == 1,votepack]

    PACK = {}

    nomsper = {p: noms[p] / nomopportunity[p] for p in played}
    nomstable = [[p, nomopportunity[p], noms[p], nomsper[p], played[p] >= 15] for p in played]
    nomstable = standardsort(nomstable)
    nomstable = [[x[0], x[1], x[2], int(np.round(x[3], 2) * 100), x[4]] for x in nomstable]

    winners = " | ".join([x[0] for x in nomstable if x[3] == nomstable[0][3] and x[4]])
    nomspack = {"table": nomstable, "name": "Finger Pointer",
                        "details": "Most likely to nominate",
                        "note": "Minimum 15 games to qualify", 'winners': winners, 'suffix': "%",
                        'score': f"{nomstable[0][3]}%",
                        "scorecalc": "Nominations/Days Started Alive"}
    PACK['fingerpointer'] = nomspack


    selfper = {p: selfnom[p] / nomopportunity[p] for p in played}
    selftable = [[p, nomopportunity[p], selfnom[p], selfper[p], played[p] >= 15] for p in played]
    selftable = standardsort(selftable)
    selftable = [[x[0], x[1], x[2], int(np.round(x[3], 2) * 100), x[4]] for x in selftable]

    winners = " | ".join([x[0] for x in selftable if x[3] == selftable[0][3] and x[4]])
    pickmepack = {"table": selftable, "name": "Pick Me",
                "details": "Most likely to nominate self",
                "note": "Minimum 15 games to qualify", 'winners': winners, 'suffix': "%",
                'score': f"{selftable[0][3]}%",
                "scorecalc": "Self Nominations/Days Started Alive"}
    PACK['pickme'] = pickmepack

    earlybirdper = {p: earlybird[p] / nomopportunity[p] for p in played}
    earlybirdtable = [[p, nomopportunity[p], earlybird[p], earlybirdper[p], played[p] >= 15] for p in played]
    earlybirdtable = standardsort(earlybirdtable)
    earlybirdtable = [[x[0], x[1], x[2], int(np.round(x[3], 2) * 100), x[4]] for x in earlybirdtable]

    winners = " | ".join([x[0] for x in earlybirdtable if x[3] == earlybirdtable[0][3] and x[4]])
    earlybirdpack = {"table": earlybirdtable, "name": "The Early Goose",
                  "details": "Most likely to nominate first",
                  "note": "Minimum 15 games to qualify", 'winners': winners, 'suffix': "%",
                  'score': f"{earlybirdtable[0][3]}%",
                  "scorecalc": "First Nominations of Day/Days Started Alive"}
    PACK['earlygoose'] = earlybirdpack

    thewormper = {p: theworm[p] / nomopportunity[p] for p in played}
    thewormtable = [[p, nomopportunity[p], theworm[p], thewormper[p], played[p] >= 15] for p in played]
    thewormtable = standardsort(thewormtable)
    thewormtable = [[x[0], x[1], x[2], int(np.round(x[3], 2) * 100), x[4]] for x in thewormtable]

    winners = " | ".join([x[0] for x in thewormtable if x[3] == thewormtable[0][3] and x[4]])
    thewormpack = {"table": thewormtable, "name": "The Mint Vine",
                     "details": "Most likely to be nominated first",
                     "note": "Minimum 15 games to qualify", 'winners': winners, 'suffix': "%",
                     'score': f"{thewormtable[0][3]}%",
                     "scorecalc": "Day Where First Nominated/Days Started Alive"}
    PACK['themint'] = thewormpack

    novoteper = {p: novotenom[p] / noms[p] if noms[p]>0 else 0 for p in played}
    novotetable = [[p, noms[p], novotenom[p], novoteper[p], played[p] >= 15] for p in played]
    novotetable = standardsort(novotetable)
    novotetable = [[x[0], x[1], x[2], int(np.round(x[3], 2) * 100), x[4]] for x in novotetable]

    winners = " | ".join([x[0] for x in novotetable if x[3] == novotetable[0][3] and x[4]])
    novotepack = {"table": novotetable, "name": "No Vote For You",
                   "details": "Most likely not to trigger a vote when nominating",
                   "note": "Minimum 15 games to qualify", 'winners': winners, 'suffix': "%",
                   'score': f"{novotetable[0][3]}%",
                   "scorecalc": "Nominations Where No Vote Occured/Nominations"}
    PACK['novote'] = novotepack

    demonhunterper = {p: demonhunter[p] / demonhunteroppo[p] if demonhunteroppo[p] > 0 else 0 for p in played}
    demonhuntertable = [[p, demonhunteroppo[p], demonhunter[p], demonhunterper[p], played[p] >= 15] for p in played]
    demonhuntertable = standardsort(demonhuntertable)
    demonhuntertable = [[x[0], x[1], x[2], int(np.round(x[3], 2) * 100), x[4]] for x in demonhuntertable]

    winners = " | ".join([x[0] for x in demonhuntertable if x[3] == demonhuntertable[0][3] and x[4]])
    demonhunterpack = {"table": demonhuntertable, "name": "Demon Hunter",
                  "details": "Most likely nominate the Demon",
                  "note": "Minimum 15 games to qualify", 'winners': winners, 'suffix': "%",
                  'score': f"{demonhuntertable[0][3]}%",
                  "scorecalc": "Nominations of Demon/Days Started Alive as Good"}
    PACK['demonhunter'] = demonhunterpack

    whomeper = {p: whome[p] / played[p] if played[p] > 0 else 0 for p in played}
    whometable = [[p, played[p], whome[p], whomeper[p], played[p] >= 15] for p in played]
    whometable = standardsort(whometable)
    whometable = [[x[0], x[1], x[2], np.round(x[3], 2), x[4]] for x in whometable]

    winners = " | ".join([x[0] for x in whometable if x[3] == whometable[0][3] and x[4]])
    whomepack = {"table": whometable, "name": "Who, me?",
                       "details": "Most likely to be nominated",
                       "note": "Minimum 15 games to qualify", 'winners': winners, 'suffix': "",
                       'score': f"{whometable[0][3]}",
                       "scorecalc": "Time Nominated/Games Played"}
    PACK['whome'] = whomepack


    i = 1
    for x in thewormtable:
        pass #if x[4]:print(f"{i}-{x[0]}:{x[3]}% ({x[2]}/{x[1]} opportunies)")
        i+=1

    return PACK

def pairsawards(games):
    PACK = {}
    players = []

    for gid in games:
        for p in games[gid].playerobjs:
            players.append(p)

    players = list(set(players))
    players.sort()
    pairs = combinations(players,2)
    pairs = list(pairs)

    played = {p:0 for p in pairs}
    wins = {p:0 for p in pairs}
    teamedup = {p:0 for p in pairs}
    teamedupgood = {p:0 for p in pairs}
    teamedupevil = {p:0 for p in pairs}
    evilwins = {p:0 for p in pairs}

    for gid in games:
        winner = games[gid].result
        for pair in pairs:
            if all([p in games[gid].playerobjs for p in pair]):
                played[pair] += 1
                if games[gid].playerobjs[pair[0]].currentalignment == games[gid].playerobjs[pair[1]].currentalignment:
                    teamedup[pair] += 1
                    if games[gid].playerobjs[pair[0]].currentalignment=="Good":
                        teamedupgood[pair] += 1
                    else:
                        teamedupevil[pair] += 1

                    if games[gid].playerobjs[pair[0]].currentalignment == winner:
                        wins[pair] += 1

                    if games[gid].playerobjs[pair[0]].currentalignment == winner and winner == "Evil":
                        evilwins[pair] += 1

    teamedupper = {p: teamedup[p] / played[p] if played[p] > 0 else 0 for p in played}
    teameduptable = [[p, played[p], teamedup[p], teamedupper[p], played[p] >= 10] for p in played]
    teameduptable = standardsort(teameduptable)
    teameduptable = [[f"{x[0][0]} & {x[0][1]}", x[1], x[2], np.round(x[3]*100, 2), x[4]] for x in teameduptable if x[1]>7]

    winners = " | ".join([x[0] for x in teameduptable if x[3] == teameduptable[0][3] and x[4]])
    BFFpack = {"table": teameduptable, "name": "Bestest Buds",
                 "details": "Most likely to team up based on finshing alignment",
                 "note": "Minimum 10 games where both players played to qualify", 'winners': winners, 'suffix': "%",
                 'score': f"{teameduptable[0][3]}%",
                 "scorecalc": "Times Teamed Up/Opportunities to Team Up"}
    PACK['bestestbuds'] = BFFpack

    dynamper = {p: wins[p] / teamedup[p] if teamedup[p] > 0 else 0 for p in played}
    dynamtable = [[p, teamedup[p], wins[p], dynamper[p], teamedup[p] >= 10] for p in played]
    dynamtable = standardsort(dynamtable)
    dynamtable = [[f"{x[0][0]} & {x[0][1]}", x[1], x[2], np.round(x[3] * 100, 2), x[4]] for x in dynamtable if x[1]>7]

    winners = " | ".join([x[0] for x in dynamtable if x[3] == dynamtable[0][3] and x[4]])
    dynampack = {"table": dynamtable, "name": "Dynamic Duo",
               "details": "Most likely to team up and win",
               "note": "Minimum 10 games as a team based on finshing alignment", 'winners': winners, 'suffix': "%",
               'score': f"{dynamtable[0][3]}%",
               "scorecalc": "Win on Same Team/Times Teamed Up"}
    PACK['dynamicduo'] = dynampack

    i = 1
    for x in dynamtable:
        pass#if x[4]:print(f"{i}-{x[0]}:{x[3]}% ({x[2]}/{x[1]} opportunies)")
        i += 1

    return PACK


def awardpackgen(games,eligible):

    winningestplayerpack = getwinningestplayer(games)

    winningestrolepack = getwinningestrole(games)

    rolepack = getroleawards(games)

    nominationpack = nominationawards(games)

    pairspack = pairsawards(games)

    awardpack = {**winningestplayerpack, **winningestrolepack, **rolepack, **nominationpack, **pairspack}
    print([x for x in awardpack])


    for a in awardpack:
        awardpack[a]['title']=a

        if a in ["bestestbuds",'dynamicduo']:
            awardpack[a]['table'] = [x for x in awardpack[a]['table'] if x[0].split(" & ")[0] in eligible and x[0].split(" & ")[1] in eligible]
        elif a not in ['winningestrole']:
            awardpack[a]['table'] = [x for x in awardpack[a]['table'] if x[0] in eligible]

        scores = [x[3] for x in awardpack[a]['table'] if x[4]]

        rank = 0
        lastscore = 99
        for ind in range(len(awardpack[a]['table'])):
            if awardpack[a]['table'][ind][1]==0:
                rank = ind+1
            elif awardpack[a]['table'][ind][2]/awardpack[a]['table'][ind][1]<lastscore:
                rank = ind+1
            awardpack[a]['table'][ind].append(rank)

        awardpack[a]['average']=np.round(sum(scores)/len(scores),2)

    ###Not all that glitters

    return awardpack

if __name__ == '__main__':
    import pickle

    games = pickle.load(open(r'games.p', "rb"))

    awardpackgen(games,['Jordan', 'Weaver', 'Piranha', 'Electra', 'Lycan', 'Sam', 'Permzilla', 'Lyra', 'Tanfana', 'Tim', 'Dice', 'Kani', 'Jon', 'Amy', 'Shaun', 'Frosty', 'Stephen', 'Planck', 'Billy', 'Lyphoon', 'Nara', 'KK'])
