import CharacterJSONprocess
import initimport
import classes as C


SessionsMain, RolesMain, EventsMain, VotesMain, PlayerVotesMain = initimport.importxlsx()
RoleTypesdf = CharacterJSONprocess.getrolesdf()

RoleTypesdict = RoleTypesdf.to_dict("records")
RoleTypesdict = {x['Role']:x['Side'] for x in RoleTypesdict}

for ind, r in SessionsMain.iterrows():
    g = C.Game(r.Date,r.Session,r["Game Number"],r.Script,r.Result,r.PlayerCount)
    for p in RolesMain.loc[(RolesMain["Session"]==g.session) & (RolesMain["Game Number"]==g.game)].to_dict("records"):
        if p['Role'] == "ST":
            g.storytellers.append(p["Player"])
        elif p['Player'] == "Bluff":
            g.demonbluffs.append(p["Role"])
        elif p['Notes'] in ["Good","Evil"]:
            g.addplayer(p["Player"], p['Role'], p['Notes'], p['Notes'])
        else:
            g.addplayer(p["Player"], p['Role'], RoleTypesdict[p['Role']], p['Notes'])

    #print(RolesMain.loc[(RolesMain["Session"]==g.session) & (RolesMain["Game Number"]==g.game)].to_dict("records"))
    #print(RoleTypesdict)

    print(g.getgamestate())
    exit()