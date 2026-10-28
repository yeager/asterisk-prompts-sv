# Svenska röstprompter för Asterisk och FreePBX

Det här projektet samlar svenska röstprompter för Asterisk och FreePBX. Målet
är ett modernt, fritt och granskningsbart alternativ till äldre svenska
ljudpaket.

Två svenska ElevenLabs-röster används:

- Anton – Warm, Confident & Friendly
- Louise – Calm & Clear Narration

Varje ljudfil hör ihop med ett granskat svenskt manus och behåller den
filstruktur som Asterisk förväntar sig. Ljuden tas fram som separata
WAV-filer och kontrolleras innan de paketeras i de format som behövs för
Asterisk och FreePBX.

## Status

Arbetet sker i tydliga steg:

1. Manus granskas och normaliseras på svenska.
2. Röstkandidater skapas separat för Anton och Louise.
3. Ljuden lyssnas igenom och godkänns med hashbundna beslut.
4. Godkända ljud konverteras, paketeras och funktionstestas i Asterisk/FreePBX.

Endast filer som har passerat hela kedjan ska läggas i en release.

| Röst | Status |
| --- | --- |
| Louise | 855 ljud är lyssningsgodkända och paketerade i version 0.1.0. |
| Anton | 855 ljud är lyssningsgodkända och paketerade i version 0.1.0. |

För Debian och Ubuntu blir releasen ett paket per röst:

- `asterisk-prompt-sv-anton.deb`
- `asterisk-prompt-sv-louise.deb`
- `asterisk-prompt-sv-anton.rpm`
- `asterisk-prompt-sv-louise.rpm`
- `asterisk-prompt-sv-anton.tar.gz`
- `asterisk-prompt-sv-louise.tar.gz`

Se [docs/DEBIAN.md](docs/DEBIAN.md) för paketering och kontroll.

## Planerad struktur

```text
sounds/
  anton/sv/
  louise/sv/
manifests/
packages/
docs/
```

## Licens och attributering

Ljud, manus och dokumentation i projektet publiceras under
[CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/deed.sv), om
inte en fil uttryckligen anger något annat. Återanvändning kräver
attribuering och att bearbetningar delas under samma licens.

Ljuden har skapats med ElevenLabs. Jag har en ElevenLabs Pro-prenumeration,
vilket medger den avsedda vidareanvändningen och distributionen enligt
ElevenLabs villkor.

## Kontakt

Daniel Nylander
