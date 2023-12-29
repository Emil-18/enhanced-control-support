<div lang = "nb_no">

# Forbedret kontroll Støtte.
* Forfatter: Emil-18.
* NVDA-kompatibilitet: 2023.1 og utover.
* Last ned: [Stabil versjon](https://github.com/Emil-18/enhanced-control-support/releases/download/v1.0.1/enhancedControlSupport-1.0.1.nvda-addon).

Dette tillegget lar deg bruke noen kontroller som normalt ikke fungerer med NVDA.

Merk:

Når dette tillegget refererer til kontroller, refererer det ikke til individuelle objekter. Du kan for eksempel ikke endre bare listeelementene i en liste til knapper, hele listen vil bli behandlet som én knapp.

Hva som defineres som en kontroll er applikasjonsspesifikk. Knappene i kjør-dialogen, for eksempel, er vær definert som én kontroll. Derimot er alt i Windows 10-kalkulatoren en del av én kontroll, selve vinduet.

Foreløpig støtter tillegget:

* Knapper.
* Avkryssingsbokser.
* Redigerings kontroller.
* Radioknapper.
* Glidebrytere.
* Tekstkontroller.

## Automatisk kontrolltypegjenkjenning.

Når NVDA møter en ukjent kontroll, vil den automatisk prøve å finne ut hvilken type kontroll det er. Hvis funnet, vil den bli rapportert så nært som mulig til det NVDA vanligvis rapporterer når den samhandler med denne typen kontroll.

## Manuell endring av kontrolltype.

Noen ganger, når NVDA ikke rapporterer en kontroll som ukjent, men i stedet som rute, er det umulig å fastslå om kontrollen faktisk er en rute eller ikke. På grunn av dette implementerer tillegget funksjonalitet for å tvinge NVDA til å tolke kontrollen som en annen type.

Du kan også tvinge NVDA til å bruke MSAA eller UIA for å få tilgang til kontrollen. Dette er nyttig hvis NVDA oppfører seg dårlig med tilgjengelighets-grensesnittet den velger på egen hånd.

NVDA bruker vanligvis enten MSAA eller UIA for å få tilgang til kontroller, så en av disse vil være identisk med normal NVDA-oppførsel.

Prøv og forandre tilgjengelighets-grensesnitt hvis:

* NVDAs objektnavigering ikke fungerer som den skal.
* NVDA klarer ikke å følge fokuset, men kontrollen fungerer helt eller delvis med objektnavigering og/eller musesporing.
* NVDA rapporterer feil informasjon om kontrollen.

Du kan gjøre begge disse tingene ved å bruke kombinasjonsboksen for kontrolltype (se nedenfor).

## Arbeide med ukjente kontroller.

Hvis NVDA ikke kan finne ut hva en kontroll er, vil kontrolltypen bli rapportert som "ukjent", og NVDA vil prøve å finne ut hvor fokuset er ved å se på tekstfargene. Merk at kontrollen må støtte les skjerm for at dette skal fungere.

NVDA vil behandle teksten som har minst gjentakende farge i kontrollen som navnet, og både tale og punktskrift vil bli oppdatert når navnet endres, så du bør kunne gjøre ting som å navigere gjennom en liste med piltastene.

Denne oppførselen kan også oppnås i en hvilken som helst kontroll ved å velge "ukjent" i kontrolltype-kombinasjonsboksen (se nedenfor).

Merk:

Når dette tillegget er aktivert, kan du ikke lese all den visuelle teksten i kontrollen i les objekt modus når du lander i en ukjent kontroll som du vanligvis kan.

For å gjenopprette normal NVDA-oppførsel for gjeldende kontroll, velg "Bruk normal NVDA-oppførsel" i kontrolltype-kombinasjonsboksen (se nedenfor).

## Gester:

* NVDA+ALT+C: Åpne dialogboksen som brukes til å endre kontrolltype for den fokuserte kontrollen.
* NVDA+ALT+SHIFT+C:Åpne dialogboksen som brukes til å endre kontrolltype for kontrollen der navigasjonsobjektet befinner seg.
* NVDA+alt+r: Rapporterer kontroll typen der fokuset, hvis det trykkes én gang, eller navigasjonsobjektet, hvis det trykkes to ganger, er plassert.
## innstillinger i dialogboksen for valg av kontrolltype.

* Kontrolltype kombinasjonsboks:
Dette er en kombinasjonsboks som viser alle kontrolltypene du kan velge fra.
Det du velger her, vil kun påvirke kontrollene i applikasjonen du interagerte med da du åpnet dialogen.
Det vil også bare påvirke kontroller som ligner på kontrollen du interagerte med før du åpnet dialogen.
La oss si at du endret OK-knappen i kjør-dialogen til å bli behandlet som en avkryssingsboks.
Nå vil avbryt- og bla gjennom-knappene også rapporteres som avkryssingsbokser, men redigeringsfeltet vil fortsatt rapporteres som et redigeringsfelt, fordi det er en annen type kontroll.
Samme hvis du for eksempel åpner lagringsdialogen i wordpad. Knappene der vil fortsatt bli behandlet som knapper, fordi de er i et annet program enn kjør-dialogen.
* stol på hendelser avkryssingsboks:
Dette er en avkryssingsboks som lar deg velge om NVDA skal stole på hendelser, varsler sendt av kontroller til skjermlesere for å varsle dem om ting som navneendringer, når de samhandler med kontrollen. De fleste egendefinerte kontroller implementerer ikke hendelser riktig, så den er av som standard.
Den vil også bli behandlet som av når NVDA automatisk gjenkjenner en egendefinert kontroll.
Dette vil også bare påvirke kontrollen du interagerte med før du åpnet dialogen.
* Bruk midlertidig normal tilleggsoppførsel for alle kontroller avkryssingsboks:
hvis denne er merket av, vil NVDA bruke normal tilleggsoppførsel for alle kontroller inntil NVDA startes på nytt eller avkryssingsboksen blir ikke avkrysset igjen. Dette er nyttig hvis du har endret en kontroll, men det får NVDA til og ikke fungere til et punkt hvor det er umulig å endre kontrollen tilbake.

## Forandrings log.

### v1.0.1.

Tillegget burde ikke lenger spille av feilmeldings lyder når du bytter tiljengelighets-grensesnitt.

### v1.0.

Første versjon.
</div>