import re


# qui carichiamo il file che contiene le abbreviazioni; il metodo .strip() delle stringhe, elimina la testa e la coda
# delle stringhe; elimina, cioè, i caratteri di spazio e a capo che si trovano all'inizio e alla fine di una stringa
abbrv = [i.strip() for i in open("lista_abbreviazioni_it.txt")]

# questa funzione ha il compito di rimpiazzare alcuni pattern con degli spazi (anche se questa è una definizione molto
# generica); l'idea è quella di "aggiustare" la stringa in input, in modo da ottenere una tokenizzazione che, dopo 
# le dovute operazioni, debba solo prendere in considerazione lo spazio come separatore

def tokenizza_apostr_punct(stringa):
    # il carattere underscore è un po' problemamtico, dato che è riconosciuto dalla wildcard "\w" nelle RegEx;
    # per elimianre il problema, si può sostituirlo, prima di fare altre operazioni, con uno spazio;
    # non dovrebbe comportare perdita di informazione;
    # il risultato di questa sostituzione, che come in altri casi è dato dall'uso di re.sub(), è una stringa;
    # in questa prima fase, quindi, sostituiamo questo carattere e assegnamo la stringa risultante a var0
    var0 = re.sub("_", " ", stringa)
    
    # per trattare il problema dell'apostrofo, dobbiamo utilizzare un range di caratteri (denotato tra []) e 
    # individuare alcuni gruppi di caratteri (usando le tonde ()) per separare il carattere prima dell'apostrofo
    # l'apostrofo stesso e la vocale dopo; 
    # ecco come si "legge" l'espressione regolare: ad ogni istanza di un carattere che risponde al range [LlDdNnCcMmTtSsVvhr]
    # SEGUITO DAL caratere single quote o apostrofo tipografico ['’], SEGUITO DA un carattere compreso nel range
    # [AEIOUhaeiouèìòàù], SOSTITUISCI CON quel primo carattere, un single quote (così facendo normalizziamo le istanze in 
    # cui il testo contiene un apostrofo diverso da quello che vogliamo, come quello tipografico ’), uno spazio e il terzo 
    # carattere (il terzo "catch" o gruppo); assegnamo a var1 il risultato
    var1 = re.sub(r"([LlDdNnCcMmTtSsVvhr])['’]([AEIOUhaeiouèìòàù])", r"\1' \2", var0)
    
    # il testo contiene molte righe che iniziano con due segni meno "--"; vengono utilizzati nel testo per introdurre
    # dei dialoghi; dobbiamo sostituirli con uno spazio, altrimenti ci ritroveremmo cose come "--Ecco", che dovremmo
    # considerare dei tokens diversi da "Ecco"
    vardash = re.sub("--", " ", var1)
    
    # dobbiamo risolvere il problema delle parole che sono precedute da una punteggiature come "(vedi", "«anche", etc.
    # questa punteggiatura deve essere separata dalla parola, se non vogliamo avere dei tokens inconsistenti
    # per farlo, definiamo un range di punteggiatura che potremmo trovare prima di una parola; il primo gruppo:
    # (["«\(\[\{])
    # è un po' difficile da leggere, ma significa: "raggruppa (con parentesi tonda) il range di caratteri (denotato
    # dall quadre alle due estremità) che comprende questi caratteri "«([{]", seguito da un carattere alfanumerico 
    # (denotato da "\w"); per poter denotare il primo gruppo, però, in alcuni casi dobbiamo usare il backslah, che significa
    # "interpreta in modo letterale il carattere successivo"; nel caso del pattern "\(", stiamo denotando la parentesi 
    # tonda come carattere letterale, senza usare il suo significato di "raggruppamento"; Inoltre stiamo usando un modo
    # un po' diverso di denotare una stringa: non stiamo usando il single quote o il double quote, ma stiamo usando 
    # tre double quote prima e dopo la stringa; questo perché all'interno di questa stringa è possibile inserire 
    # anche il carattere di double quote intesi in modo letterale; in caso contrario, Python non saprebbe come interpretare
    # la stringa "ahdsj"sadkjasj", perché non sarebbe in grado di capire dove inizia e dove finisce; provare per credere:
    # provate ad assegnare a eseguire in un'altra cella questa assegnazione di variabile:
    # strng = "ahdsj"sadkjasj"
    # vederete che python vi restituirà un errore; al contrario, l'operazione
    # strng = """ahdsj"sadkjasj"""
    # non darà nessun problema
    varpunct_ini = re.sub(r"""([“"«\(\[\{])(\w)""", r"\1 \2", vardash)
    
    #qui risolviamo lo stesso problema, ma per i caratteri di chiusura di parentesi, come "anno)", me", città»
    varpunct_fine = re.sub(r"""([\w0-9\.,;:!\?])([\)\]\}"”»])""", r"\1 \2", varpunct_ini)
    
    # qui stiamo usando un carattere speciale, l'accento circonflesso ^, che ha due significati nelle RegEx:
    # QUANDO è fuori da un range (NON tra parentesi quadre) significa "inizio riga";
    # QUANDO è all'interno di un range, denota il complemento (o contrario, se volete) di un range; nel caso
    # ([^\.]), significa: il gruppo che corrisponde a tutti i caratteri che NON SONO il punto letterale (e non il 
    # punto usato come wildcard delle espressioni regolari)
    some_other_punct = re.sub("([^\.])(\.\.+)([^\.])?", r"\1 \2 \3", varpunct_fine)
    
    # finalmente possiamo prenderci cura della punteggiatura di separazione di fras; questa espressione regolare 
    # sostituisce tutte le istanze di caratteri alfanumerici seguiti da un simbolo di punteggiatura compreso nel range
    # [\.,;:\!\?] con il primo carattere, uno spazio e quel simbolo di punteggiatura
    var2 = re.sub(r"(\w)([\.…,;:\!\?])",  r"\1 \2", some_other_punct)
    
    # a questo punto possiamo restituire la lista delle stringhe che dovrebbe corrispondere alle nostre parole
    return var2.split()

# Questa funzione ci servirà per trattare alcuni casi particolari, come le abbreviazioni, gli indirizzi url o i 
# nomi dei file, prima di mandare alcune parti del testo da tokenizzare alla funzione tokenizza_apostr_punct()



def tokenizza(testo):
    # qui stiamo utilizzando un metodo del modulo re, re.compile(), che consente di compilare una RegEx e assegnare
    # il valore di questa compilazione ad una variabile, in questo caso "urls"; il pattern riconosce le stringhe che
    # iniziano per "http", che POSSONO essere seguite -utlizzando la wildcard "?"- da 0 o una istanza di "s" (e quindi abbiamo un match sia nel caso
    # in cui un'indirizzo inizi per "http" o "https"), seguite da "://" e da www. e che sono seguite da qualsiasi carattere
    # che NON sia comprenso nel range o spazio o nuova riga. NB: la parte che tratta https:// è seguita sempe da "?",
    # il che vuol dire che questo match può esserci oppure no; in questo modo, siamo in grado di riconoscere sia
    # www.gutenberg.org, che hhtp://www.gutenberg.org; il formato della url che possiamo trovare nel testo dipende
    # dalla preferenza di chi lo ha scritto, ma la nostra RegEx deve essere in grado di addattarsi ad entrambi i pattern
    
    urls =re.compile(r"((http)s?://)?www\.[^\s\n]+")
    
    # questa RegEx individua tutte le istanze di indirizzi espressi come https://gutenberg.org; non vogliamo
    # includere questo pattern nella RegEx precedente, perché otterremmo una espressione troppo generica, che 
    # ci darebbe dei falsi risultati
    just_http_url = re.compile("https?://[^\s\n]+")
    
    # qui creiamo una lista vuota, che ospiterà i tokens
    out_ = []
    
    # qui vogliamo "splittare" la riga iniziale, in una lista di righe, usando il parametro "nuova riga" come separatore
    # si tratta di una list-comprehension, che include un if; significa: restituisci ogni "riga" all'interno della lista
    # ottenuta usando testo.split("\n") SE la riga non è uguale ad una stringa vuota ""; così facendo elimiamo tutte quelle
    # stringhe che non contengono nulla
    frasi = [riga for riga in testo.split("\n") if riga !=""]
    
    # iniziamo un ciclo for sulla lista di frasi (NB: il concetto di frase, in questo caso, è un'approssimazione)
    for frase in frasi:
        # otteniamo una lista temporanea, dividendo la stringa usando lo spazio come parametro
        temp = frase.split(" ")
        # con un altro ciclo for, iniziamo a verificare se la stringa ottenuta deve essere passata a 
        # tokenizza_apostr_punct() oppure no;
        for parola in temp:
            # SE il pattern in urls viene trovato nella stringa, allora la aggiungiamo alla lista out_; in altri termini,
            # se il token è un indirizzo html, non tentiamo di tokenizzarlo, ma lo inseriamo nella lista così com'è
            if urls.search(parola):
                out_.append(parola)
            
            # SE la stringa è di tipo "http://repubblica.it", cioè senza un www, facciamo la stessa cosa: lo inseriamo 
            # nella lista come token usando il metodo append
            elif just_http_url.search(parola):
                out_.append(parola)
                
            # SE il pattern [#@] (o hashatg o chiocciola) è all'interno della stringa, allora lo consideriamo un oggetto
            # da non tokenizzare (potrebbe essere un indirizzo email o un hashtag di twitter, ad esempio)
            elif re.search(r"[@#]", parola):
                out_.extend(tokenizza_apostr_punct(parola))
                
            # SE il patter contiene cose del tipo "file.txt" o "file.zip", allora non lo tokeniziamo, ma facciamo un append    
            elif re.search(r"\.(txt|pdf|doc|docx|zip)$", parola):
                out_.append(parola)
                
            # SE il token si trova nella lista delle abbreviazioni, allora non tokeniziamo, ma facciamo un append
            elif parola in abbrv:
                out_.append(parola)
                
            # SE tutte le condizioni precedenti non si verificano, allora tokenizziamo al stringa; prendiamo il caso in cui 
            # la stringa sia "quest'anno.": in questo caso, tokenizza_apostr_punct ci restituirebbe la LISTA (NB:LISTA)
            # ["quest'", "anno", "."], composta da tre stringhe; a questo punto non possiamo fare append, perché ci troveremmo
            # con una lista, out_, che contiene sia stringhe che liste di stringhe; per ssere sicuri che la lista finale contenga
            # solo stringhe, anziché usare .append(), usiamo .extend() che prende tutti gli elementi della lista che gli
            # gli passiamo come argomento e li aggiunge ad una lista 
            else:
                out_.extend(tokenizza_apostr_punct(parola))
            
    # una volta terminate tutte le operazioni, restituiamo la lista dei tokens out_   
    return out_

