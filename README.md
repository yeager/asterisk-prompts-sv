# Svenska röstprompter för Asterisk och FreePBX

[English](#swedish-voice-prompts-for-asterisk-and-freepbx)

Det här projektet tillhandahåller moderna svenska röstprompter för Asterisk
och FreePBX. Paketet är ett fritt, granskningsbart alternativ till äldre
svenska ljudpaket och behåller den filstruktur som Asterisk använder.

Två svenska röster finns tillgängliga:

- Anton – Warm, Confident & Friendly
- Louise – Calm & Clear Narration

Varje ljudfil bygger på ett granskat svenskt manus. Kandidater lyssnas igenom
och får hashbundna godkännanden innan de paketeras. Version 0.1.0 innehåller
855 godkända WAV-filer för vardera röst.

## Hämta paket

Hämta den röst och det paketformat som passar din installation från
[releaserna](https://github.com/yeager/asterisk-prompts-sv/releases):

- [Anton 0.1.0](https://github.com/yeager/asterisk-prompts-sv/releases/tag/v0.1.0-anton)
- [Louise 0.1.0](https://github.com/yeager/asterisk-prompts-sv/releases/tag/v0.1.0-louise)

Varje release innehåller följande format:

- `asterisk-prompt-sv-<röst>.deb` för Debian och Ubuntu
- `asterisk-prompt-sv-<röst>.rpm` för RPM-baserade distributioner
- `asterisk-prompt-sv-<röst>.tar.gz` för manuell installation
- en fil med SHA-256-kontrollsummor

Debian- och RPM-paketen installerar ljuden under
`/usr/share/asterisk/sounds/sv`. Kontrollera alltid filens SHA-256-värde
mot kontrollsummefilen i samma release före installation.

## Licens och kontakt

Ljud, manus och dokumentation publiceras under
[CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/deed.sv), om
inte en fil uttryckligen anger något annat. Återanvändning kräver
attribuering och att bearbetningar delas under samma licens.

Ljuden har skapats med ElevenLabs. Jag har en ElevenLabs Pro-prenumeration,
vilket medger den avsedda vidareanvändningen och distributionen enligt
ElevenLabs villkor.

Kontakt: Daniel Nylander

---

# Swedish voice prompts for Asterisk and FreePBX

[Svenska](#svenska-röstprompter-för-asterisk-och-freepbx)

This project provides modern Swedish voice prompts for Asterisk and FreePBX.
It is a freely licensed and reviewable alternative to older Swedish sound
sets, while preserving the directory layout expected by Asterisk.

Two Swedish voices are available:

- Anton – Warm, Confident & Friendly
- Louise – Calm & Clear Narration

Every audio file is based on a reviewed Swedish script. Candidates are
listened to and receive hash-bound approvals before they are packaged.
Version 0.1.0 contains 855 approved WAV files for each voice.

## Download packages

Download the voice and package format that suit your installation from the
[releases](https://github.com/yeager/asterisk-prompts-sv/releases):

- [Anton 0.1.0](https://github.com/yeager/asterisk-prompts-sv/releases/tag/v0.1.0-anton)
- [Louise 0.1.0](https://github.com/yeager/asterisk-prompts-sv/releases/tag/v0.1.0-louise)

Each release provides:

- `asterisk-prompt-sv-<voice>.deb` for Debian and Ubuntu
- `asterisk-prompt-sv-<voice>.rpm` for RPM-based distributions
- `asterisk-prompt-sv-<voice>.tar.gz` for manual installation
- a SHA-256 checksum file

The Debian and RPM packages install the sounds in
`/usr/share/asterisk/sounds/sv`. Always verify the file's SHA-256 checksum
against the checksum file in the same release before installation.

## License and contact

The audio, scripts and documentation are published under
[CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/), unless a
file explicitly states otherwise. Reuse requires attribution and that
adaptations are shared under the same license.

The audio was created with ElevenLabs. I have an ElevenLabs Pro subscription,
which permits the intended reuse and distribution under ElevenLabs' terms.

Contact: Daniel Nylander
