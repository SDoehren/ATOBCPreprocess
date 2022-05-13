import pandas as pd
import openpyxl
pd.set_option('display.max_rows', 100)
pd.set_option('display.min_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 200)
from collections import Counter
from os import listdir
from os.path import isfile, join



def importcsvs():
    mypath = r"D:\GitHub\ATOBC\Approved Games"
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]


    SessionsMain = pd.DataFrame(columns=['Date', 'Session', 'Game Number', 'Script', 'Result', 'PlayerCount'])
    RolesMain = pd.DataFrame(columns=['Session', 'Game Number', 'Player', 'Role', 'Notes'])
    EventsMain = pd.DataFrame(columns=['Session', 'Game Number', 'Phase', 'Player', 'Action', 'Target', 'Note'])
    VotesMain = pd.DataFrame(columns=['Session', 'Game Number', 'Vote Number', 'Player', 'Target',
                                      'Total Votes', 'On the Block', 'Executed'])
    PlayerVotesMain = pd.DataFrame(columns=['Session', 'Game Number', 'Vote Number', 'Player', 'Voted'])

    for fstr in onlyfiles:
        print(fstr)
        fstr = f"{mypath}\{fstr}"
        Sessions = pd.read_csv(fstr, usecols=[0, 1, 2, 3, 4, 5])
        Sessions = Sessions.dropna(how="all")
        SessionsMain = pd.concat([SessionsMain, Sessions])

        Roles = pd.read_csv(fstr, usecols=[7, 8, 9, 10, 11, 12])
        Roles.rename(columns={"Session.1": "Session", "Game Number.1": "Game Number"}, inplace=True)
        Roles = Roles.dropna(how="all")
        RolesMain = pd.concat([RolesMain, Roles])

        events = pd.read_csv(fstr, usecols=[14, 15, 16, 17, 18, 19, 20])
        events.rename(columns={"Session.2": "Session", "Game Number.2": "Game Number", "Player.1": "Player"},
                      inplace=True)
        events = events.dropna(how="all")
        EventsMain = pd.concat([EventsMain, events])

        votes = pd.read_csv(fstr, usecols=[22, 23, 24, 25, 26, 27, 28, 29])
        votes.rename(columns={"Session.3": "Session", "Game Number.3": "Game Number", "Player.2": "Player",
                              "Target.1": "Target"}, inplace=True)
        votes = votes.dropna(how="all")
        VotesMain = pd.concat([VotesMain, votes])

        player_votes = pd.read_csv(fstr, usecols=[31, 32, 33, 34, 35, 36, 37])
        player_votes.rename(columns={"Session.4": "Session", "Game Number.4": "Game Number", "Player.3": "Player",
                                    "Vote Number.1": "Vote Number"}, inplace=True)
        player_votes = player_votes.dropna(how="all")
        PlayerVotesMain = pd.concat([PlayerVotesMain, player_votes])

    return SessionsMain, RolesMain, EventsMain, VotesMain, PlayerVotesMain

def importxlsx():
    print("Setup")

    print("Load Sheets")
    SessionsMain, RolesMain, EventsMain, VotesMain, PlayerVotesMain = importcsvs()

    print("Load Finished")

    print("Cleaning and Enhancement")

    intcols = ["Session", "Game Number"]
    SessionsMain[intcols] = SessionsMain[intcols].astype(int)
    SessionsMain['PlayerCount'] = SessionsMain['PlayerCount'].astype(int)
    RolesMain[intcols] = RolesMain[intcols].astype(int)
    EventsMain[intcols] = EventsMain[intcols].astype(int)
    extras = ["Vote Number", 'Total Votes', 'On the Block', 'Executed']

    VotesMain[intcols + extras] = VotesMain[intcols + extras].astype(int)
    PlayerVotesMain[intcols] = PlayerVotesMain[intcols].astype(int)


    RolesMain["Notes"].fillna("", inplace=True)
    EventsMain["Note"].fillna("", inplace=True)
    EventsMain["Target"].fillna("", inplace=True)

    def getgameid(r):
        return f"{int(r['Session'])}-{int(r['Game Number'])}"

    SessionsMain["gameid"] = SessionsMain.apply(getgameid, axis=1)
    RolesMain["gameid"] = RolesMain.apply(getgameid, axis=1)
    EventsMain["gameid"] = EventsMain.apply(getgameid, axis=1)
    VotesMain["gameid"] = VotesMain.apply(getgameid, axis=1)
    PlayerVotesMain["gameid"] = PlayerVotesMain.apply(getgameid, axis=1)

    return SessionsMain, RolesMain, EventsMain, VotesMain, PlayerVotesMain

