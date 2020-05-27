import math
import matplotlib.pyplot as plt

class TirageImpossible(Exception):
    pass

"""
retourne la valeur de la combinatoire de k éléments parmi n
"""
def combi(n,k):
    if k>n or k<0:
        raise TirageImpossible()
    if k==0 or k==n:
        return 1
    else:
        if k<=n/2:
            return n/k*combi(n-1,k-1)
        else:
            k2 = n-k
            return n/k2*combi(n-1,k2-1)

"""
retourne la probabilité d'avoir X cartes cibles en main parmi un deck de total cartes après avoir piocher X cartes
"""
def hypergeo(total,pioche,nbrCarteCible,nbrCarteCibleMain):
    proba = combi(nbrCarteCible,nbrCarteCibleMain)*combi(total-nbrCarteCible,pioche-nbrCarteCibleMain)/combi(total,pioche)
    return proba

"""
retourne la probabilité d'avoir un nombres de cartes cibles entre 2 valeurs en main parmi un deck de total cartes après avoir piocher X cartes
"""
def hypergeoInt(total,pioche,nbrCarteCible,minCarteCible,maxCarteCible):
    proba = 0
    for i in range(minCarteCible,maxCarteCible+1):
        proba += hypergeo(total,pioche,nbrCarteCible,i)
    return proba

def analyseProb(total,nbrCarteCible,pioche):
    analyse = {}
    for i in range(0,min(pioche,nbrCarteCible)+1):
        analyse[i] = round(hypergeo(total,pioche,nbrCarteCible,i)*100,2)    
    return analyse

def analyseProbImg(total,nbrCarteCible,pioche,fileName):
    analyse = analyseProb(total,nbrCarteCible,pioche)
    nom = []
    valeur = []
    for i in analyse.keys():
        nom.append(str(i))
        valeur.append(analyse[i]) 
    plt.figure()
    plt.plot()
    plt.title("répartition de probabilité d'un tirage de {} cartes\nparmi {} dont {} cartes recherchées".format(pioche,total,nbrCarteCible))
    plt.bar(nom,valeur)
    plt.savefig(fileName)


def main():
    try:
        analyseProbImg(60,24,13,"teststring.png")
    except TirageImpossible:
        print("Tirage impossible à faire !")

if __name__ == "__main__":
    main()