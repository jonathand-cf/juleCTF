n = 129044391092593358836413150444361449599586999672529961565676352574292420115748392669398411631596462334207482029115762256598167083787272273235753887121460000204841987429108754581244050136422971333516670803761495895794590247032120330844282728979335161028352231858221965500756138501790763250064894184931481083351
e = 65537
ct = 26475173276039843627709084403029130584817765758751327772557330551581345025072651271091414974772432261412987133577999917453363955648278471643948326901873147633545220698573650987989184280888860727616302931219207995314567671325830416277180499008620481681424487555385100213836758914694754525664097074976299260521

leaked = (
    "hhlhhhlllhhllhhhlhhlhhhhhhhhlhhhllhhlhhhllhhhhllhlhhhlhlhlhlllhlhllhllllhhllllhlhlhhlhhllhhlhlhhhh"
    "llhllhlhhhhhlllhhhlllhlhhllhhlhllhhhhlhllhhhhhlhlhhlllllhlhhlhllhllhllhhhhllhhlhhhhhhhhhlhllhhhll"
    "hlllhlhllllhllhlhhlhhllhhhlhhlllllllhhhhhlhhhlhlhllllllhlhlhhlhlhlhhhllhhlllhlhhlllllhlllhhlhhhhl"
    "hlhhhhlhhhlhhhhllhlllhlhhhlhlhhlhllhhlhhlhllllhhllhlhlllhhhhlhhlhllllhllhlhlhhhhlhhhlhlhhllllhll"
    "hhhhhhllhhhlllhhhlllhlhlhhhlhhhhlhlhlhlhlhllhlhhlllhlhllhhlhlhllllllhlhhhhlllhhhhhhllllhhhhhllhhl"
    "hlhhlhllhhlhllhhllllhlhhhlh"
)

q = int(leaked.replace("h", "1").replace("l", "0"), 2)
q = n // q
phi = (q - 1) * (q - 1)
d = pow(e, -1, phi)
m = pow(ct, d, n)

plaintext = m.to_bytes((m.bit_length() + 7) // 8, "big")
print(plaintext.decode().strip())
