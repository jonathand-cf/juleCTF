#!/app/julespråk
fra os importer environ som miljø
fra unicodedata importer normalize som normaliser

flagg = miljø["FLAGG"] hvis "FLAGG" inni miljø ellers "JUL{test_flagg}"

def sjekk_input(data):
    forbudte_tegn = """abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,"'()[]=🧣"""
    hvis len(data) > 5000:
        returner 0
    for tegn inni normaliser("NFKC", data):
        hvis tegn inni forbudte_tegn:
            returner 0
    returner 1

data = input("Skriv julespråk-programmet du vil kjøre: ").strip()
hvis ikke sjekk_input(data):
    print("Ulovlig input oppdaget!")
ellers:
    resultat = eval(data, {}, {})
    hvis resultat == "Julespråk er favorittspråket mitt!":
        print(f"Gratulerer! Her er flagget ditt: {flagg}")
        print(f"Lengde på løsningen din er: {len(data)}")
    ellers:
        print("Feil resultat, prøv igjen!")
