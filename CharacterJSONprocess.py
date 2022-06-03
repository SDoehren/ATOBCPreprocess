import json
import pandas as pd

pd.set_option('display.max_rows', 100)
pd.set_option('display.min_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 200)


def processscript(v):
    if v == '1 - Trouble Brewing':
        return 'Trouble Brewing'
    if v == '2 - Bad Moon Rising':
        return 'Bad Moon Rising'
    if v == '3 - Sects and Violets':
        return 'Sects and Violets'
    if v == '4 - Experimental':
        return 'No Script'
    if v == 'Extras':
        return 'Extras'


def processroletoside(r):
    if r == 'demon':
        return "Evil"
    elif r == 'minion':
        return "Evil"
    elif r == 'outsider':
        return "Good"
    elif r == 'townsfolk':
        return "Good"
    elif r == 'fabled':
        return "Fabled"
    elif r == 'travellers':
        return "Travellers"
    else:
        print(r)


def getrolesdf():
    with open('roles.json') as f:
        d = json.load(f)

    pack = [[r['name'], r['roleType'].capitalize(), processroletoside(r['roleType']), processscript(r['version'])] for r
            in d]
    pack = [["ST", "ST", "ST", "ST"]] + pack
    headers = ["Role", "Type", "Side", "Script"]  # ,"IconURL","PrintURL"]
    df = pd.DataFrame(data=pack, columns=headers)

    return df


rolesingleuse = {"ST": False,
                 "Imp": False,
                 "Baron": False,
                 "Poisoner": False,
                 "Scarlet Woman": True,
                 "Spy": False,
                 "Butler": False,
                 "Drunk": False,
                 "Recluse": False,
                 "Saint": False,
                 "Chef": False,
                 "Empath": False,
                 "Fortune Teller": False,
                 "Investigator": False,
                 "Librarian": False,
                 "Mayor": False,
                 "Monk": False,
                 "Ravenkeeper": False,
                 "Slayer": True,
                 "Soldier": False,
                 "Undertaker": False,
                 "Virgin": True,
                 "Washerwoman": False,
                 "Po": False,
                 "Pukka": False,
                 "Shabaloth": False,
                 "Zombuul": False,
                 "Assassin": True,
                 "Devil's Advocate": False,
                 "Godfather": False,
                 "Mastermind": True,
                 "Goon": False,
                 "Lunatic": False,
                 "Moonchild": False,
                 "Tinker": False,
                 "Chambermaid": False,
                 "Courtier": True,
                 "Exorcist": False,
                 "Fool": True,
                 "Gambler": False,
                 "Gossip": False,
                 "Grandmother": False,
                 "Innkeeper": False,
                 "Minstrel": False,
                 "Pacifist": False,
                 "Professor": True,
                 "Sailor": False,
                 "Tea Lady": False,
                 "Fang Gu": True,
                 "No Dashii": False,
                 "Vigormortis": False,
                 "Vortox": False,
                 "Cerenovus": False,
                 "Evil Twin": False,
                 "Pit-Hag": False,
                 "Witch": False,
                 "Barber": False,
                 "Klutz": False,
                 "Mutant": False,
                 "Sweetheart": False,
                 "Artist": True,
                 "Clockmaker": False,
                 "Dreamer": False,
                 "Flowergirl": False,
                 "Juggler": False,
                 "Mathematician": False,
                 "Oracle": False,
                 "Philosopher": True,
                 "Sage": False,
                 "Savant": False,
                 "Seamstress": True,
                 "Snake Charmer": True,
                 "Town Crier": False,
                 "Riot": False,
                 "Al-Hadikhia": False,
                 "Legion": False,
                 "Leviathan": False,
                 "Lleech": False,
                 "Lil' Monsta": False,
                 "Boomdandy": False,
                 "Goblin": False,
                 "Fearmonger": False,
                 "Widow": False,
                 "Marionette": False,
                 "Mezepheles": True,
                 "Psychopath": False,
                 "Acrobat": False,
                 "Damsel": False,
                 "Golem": True,
                 "Heretic": False,
                 "Politician": False,
                 "Puzzlemaster": True,
                 "Snitch": False,
                 "Amnesiac": False,
                 "Atheist": False,
                 "Balloonist": False,
                 "Bounty Hunter": False,
                 "Cannibal": False,
                 "Cult Leader": False,
                 "Farmer": False,
                 "Fisherman": True,
                 "General": False,
                 "Lycanthrope": False,
                 "Huntsman": True,
                 "Magician": False,
                 "Noble": False,
                 "Pixie": True,
                 "Preacher": False,
                 "Poppy Grower": False,
                 "King": False,
                 "Choirboy": False,
                 "Engineer": True,
                 "Alchemist": False,
                 "Nightwatchman": True,
                 "Angel": False,
                 "Buddhist": False,
                 "Djinn": False,
                 "Doomsayer": False,
                 "Duchess": False,
                 "Fibbin": False,
                 "Fiddler": False,
                 "Hell's Librarian": False,
                 "Revolutionary": False,
                 "Sentinel": False,
                 "Spirit Of Ivory": False,
                 "Storm Catcher": False,
                 "Toymaker": False,
                 "Apprentice": False,
                 "Barista": False,
                 "Beggar": False,
                 "Bishop": False,
                 "Bone Collector": True,
                 "Bureaucrat": False,
                 "Butcher": False,
                 "Deviant": False,
                 "Gangster": False,
                 "Gunslinger": False,
                 "Harlot": False,
                 "Judge": True,
                 "Matron": False,
                 "Scapegoat": False,
                 "Thief": False,
                 "Voudon": False,
                 }

if __name__ == '__main__':
    df = getrolesdf()
    r = list(df.loc[df["Type"] == "Demon"]["Role"])
    r.sort()
    for x in r:
        print(x)
