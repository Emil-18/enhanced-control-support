# Forbedret kontrollstøtte.
* Forfatter: Emil-18.
* NVDA -kompatibilitet: 2024.4 og utover.
* Last ned: [Stabil versjon] (https://github.com/emil-18/enhanced-control-support/releases/download/v1.2/enhancedcontrolsupport-1.2.nvda-addon).

Dette tillegget lar deg bruke noen kontroller som normalt ikke fungerer med NVDA. Du kan tvinge NVDA til å tolke en kontroll som en annen type, for eksempel kan en rute tolkes som en avkryssingsboks. Dette kan forbedre rapporteringen av denne kontrollen, for eksempel la NVDA rapportere om den er avkrysset eller ikke. I noen tilfeller vil NVDA også gjenkjenne flere kontroller på egen hånd.

Merk:

Når dette tillegget refererer til kontroller, refererer det ikke til individuelle objekter. Du kan for eksempel ikke endre listeelementene til en liste til knapper, hele listen vil bli behandlet som en knapp.

Det som er definert som en kontroll er applikasjonsspesifikt. Knappene i kjør dialogen for eksempel er ver definert som en kontroll. Derimot er alt i Windows 10 -kalkulatoren en del av en kontroll, selve vinduet.

Foreløpig støtter tillegget:

* Knapper.
* Avkryssingsbokser.
* Rediger kontroller.
* skjerm tekst Redigerkontroller. En type redigeringskontroll der NVDA vil få teksten og innsettingspunktet fra det applikasjonen har skrevet til skjermen, i motsetning til å bruke tilgjengelighets APIer. Les skjerm må fungere i kontrollen for at dette skal fungere.
* Radioknapper.
* Glidebrytere.
* Tekstkontroller.
* Listebokser.
* Fane -kontroller.
## Automatisk gjenkjennelse av kontrolltype.

Når NVDA møter en ukjent kontroll, vil den automatisk prøve å finne ut hvilken type kontroll det er. Hvis det blir funnet, vil det bli rapportert så nært som mulig for hva NVDA normalt rapporterer når du samhandler med den typen kontroll.

## Manuelt endre kontrolltype.

Noen ganger, når NVDA ikke rapporterer en kontroll som ukjent, men i stedet som rute, er det umulig å avgjøre om kontrollen faktisk er en rute eller ikke. På grunn av dette implementerer tillegget funksjonallitet for å tvinge NVDA til å tolke kontrollen som en annen type.

Du kan også tvinge NVDA til å bruke MSAA eller UIA for å få tilgang til kontrollen. Dette er nyttig hvis NVDA oppfører seg dårlig med tilgjengelighets -API den velger på egen hånd.

NVDA bruker normalt enten MSAA eller UIA for å få tilgang til kontroller, så en av disse vil være identisk med normal NVDA -oppførsel.

Prøv å endre tilgjengelighets API hvis:

* NVDAs objektnavigasjon fungerer ikke som den skal.
* NVDA følger ikke fokuset, men kontrollen fungerer delvis eller fullt ut med objektnavigasjon og/eller musesporing.
* NVDA rapporterer feil informasjon om kontrollen.

Du kan gjøre begge disse tingene ved hjelp av kontroll type kombinasjonsboksen (se nedenfor).

## Arbeide med ukjente kontroller.

Hvis NVDA ikke kan finne ut hva en kontroll er, vil den avgjøre kontrolltypen ved å sjekke klassenavnet til kontrollen. For eksempel, hvis klassenavnet inneholder ordet "liste", vil NVDA rapportere kontrollen som en liste, og eventuelle underliggende kontroller som listeelementer. NVDA vil prøve å finne ut hvor fokuset er ved å se på tekstfargene. Merk at kontrollen må støtte les skjerm for at dette skal fungere.

NVDA vil behandle teksten som har den minst gjenntagene fargen i kontrollen som hvor fokuset ligger.

Du kan bruke objektnavigasjon for å navigere mellom tekststykker inne i kontrollen.

Enhver kontroll kan behandles som ukjent ved å velge "ukjent" i kontroll type kombinasjonsboksen (se nedenfor).



Note:

Når dette tillegget er aktivert, kan du ikke lese all den visuelle teksten i kontrollen i les objekt modus når du lander i en ukjent kontroll som du normalt kan.

For å gjenopprette normal NVDA -oppførsel for gjeldende kontroll, velg "Bruk normal NVDA -oppførsel" i kontrolltype -kombinasjonsboksen (se nedenfor).

## Forbedret UIA.

Når dette er valgt fra kontroll type kombinasjonsboksen (se nedenfor), og hvis du er i et tekstfelt, vil NVDA flytte navigasjons -objektet til forslaget som er valgt når de vises.
Merk at dette kan overskrive NVDAs tilpassede støtte for noen kontroller.

## Forbedret skrivestøtte.

I noen kontroller oppfører NVDA seg underlig når du skriver eller sletter tekst, f.eks. Ikke snakke det slettede tegnet/ordet, eller ikke oppdatere blindeskrift. Et eksempel inkluderer hovedredigeringskontrollen i Visual Studio. Forbedret typingstøtteforsøk på å løse disse problemene.
Forbedret skrivestøtte vil bli aktivert automatisk i noen kontroller, men du kan alltid slå den på ved å merke av i avmerkingsboksen "Bruk forbedret skrivestøtte" i velg kontroll type dialogboksen, (se nedenfor).

## gester:

* NVDA+ALT+C: Åpne dialogen som brukes til å endre kontrolltype for den fokuserte kontrollen.
* NVDA+ALT+SHIFT+C: Åpne dialogen som brukes til å endre kontrolltype for kontrollen der navigasjons -objektet er plasert.
* NVDA+ALT+R: Rapporterer typen kontroll der fokuset, hvis det er trykket en gang, eller navigasjonsobjektet, hvis det er trykket to ganger, er plasert.
## Innstillinger for Velg kontrolltype dialogboksen.

* kontroll type kombinasjonsboksen:
Dette er en kombinasjonsboks som viser alle kontrolltypene du kan velge mellom.
Det du velger her, vil bare påvirke kontrollene i applikasjonen du samhandlet med når du åpner dialogen.
Det vil også bare påvirke kontroller som ligner på kontrollen du har samhandlet med før du åpner dialogen.
La oss si at du endret OK -knappen i Kjør dialogen til å bli behandlet som en avkryssingsboks.
Nå vil også avbryt og bla gjennom knappene bli behandlet som avkryssingsbokser, men redigeringsfeltet vil fortsatt bli rapportert som et redigeringsfelt, fordi det er en annen type kontroll.
Samme hvis du for eksempel åpner lagringsdialogen i Word Pad. Knappene der vil fremdeles bli behandlet som knapper, fordi de er i et annet program enn kjør dialogen.
Merk at når du velger "Bruk normal tilleggsoppførsel", vil enhver modifisering du har gjort til kontrollen via dette tillegget bli slettet.
Dette er ikke tilfelle når du velger "Bruk normal NVDA -oppførsel". Du kan for eksempel få kontrollen til å bruke normal NVDA -oppførsel, og fortsatt velge å ikke stole på hendelser.
* Stol på hendelser avkryssingsboks:
Dette er en avkryssingsboks som lar deg velge om NVDA skal stole på hendelser,Varsler sendt av kontroller til skjermlesere for å varsle dem om ting som navnendringer, når de samhandler med kontrollen. De fleste tilpassede kontroller implementerer ikke hendelser riktig, så det er av som standard.
Det vil også bli behandlet som av når NVDA automatisk gjenkjenner en tilpasset kontroll.
* Bruk forbedret skrivestøtte avkryssingsboks:
Dette er en avkryssingsboks som lar deg velge om NVDA skal bruke forbedret skrivestøtte når du samhandler med kontrollen.
Dette er nyttig hvis NVDA oppfører seg underlig når du skriver eller sletter tekst.
* Bruk midlertidig normal tilleggsatferd for alle kontroller:
hvis krysset av, vil NVDA bruke normal tilleggsoppførsel for alle kontroller til NVDA er startet på nytt eller avkryssingsboksen er ikke avkrysset igjen. Dette er nyttig hvis du har endret en kontroll, men det ødelegger NVDA til det punktet hvor det er umulig å endre kontrollen tilbake.
## tilleggsinnstillinger

* Stol på hendelser som standard: Dette er en avkrysningsboks som avgjør om NVDA skal stole på hendelser. Hvis ikke -krysset av, vil NVDA kontinuerlig spørre det fokuserte objektet for dets navn, tilstander osv. Hvis informasjonen er forskjellig fra forrige gang NVDA spurte om det, vil den nye informasjonen bli rapportert.
* Bruk forbedrede metoder for å oppdage hvor fokuset er plasert(eksperimentell): samme som ovenfor, bare for fokus i stedet. Denne innstillingen er som standard av.
## Forandringslogg
### v 1.2
* Lagt til kompatibilitet med NVDA 2025
* Lagt til støtte for listebokser, fanekontroller og skjerm redigerings kontroller.
* Fikset en feil som ødela NVDAs støtte med Word når UIA er aktivert.
* Når forbedret UIA er valgt og et valgt forslag vises, vil navigasjons -objektet bli flyttet til det, i stedet for fokus.
* Støtten for ukjente kontroller er gjort om
    * Du kan nå bruke objektnavigasjon for å gå mellom hvert tekststykke i kontrollen.
    * NVDA vil nå behandle teksten som har de minst tilbakevendende fargene som et eget objekt, snarere enn navnet på kontrollen.
* Lagt til et innstillingspanel med følgende innstillinger. For detaljert informasjon om hva disse innstillingene gjør, sjekk den aktuelle delen av dokumentasjonen.
    * Stol på hendelser som standard
    * Bruk forbedrede metoder for å oppdage hvor fokuset er plasert (eksperimentell)

### v1.1

* Lagt til en ny innstilling kalt "Forbedret UIA"
* Lagt til en ny innstilling for forbedret skrivestøtte. Dette kan slås på for hvilken som helst kontroll via dialogboksen velg kontroll type, men vil være aktivert som standard for visse kontroller
* Fikset noen uiautomasjonsfeil som er til stede i NVDA.
### v1.0.1

Tillegget skal ikke lenger spille feilmeldingslyder når du endrer tilgjengelighets API
### v1.0
 første utgivelse.