# Debian-paket

Ett paket per röst byggs först från en fullständig, hashbunden release-manifest:

```sh
python3 tools/build_deb.py \
  --voice anton \
  --source /sökväg/till/anton \
  --manifest manifests/anton-release.json \
  --output packages/asterisk-prompt-sv-anton.deb
```

Byggverktyget kräver exakt filkarta, kontrollerar SHA-256 för varje WAV och
kräver mono PCM16 i 48 kHz. Paketet installerar ljuden under
`/usr/share/asterisk/sounds/sv`.

Kontrollera innehållet på Debian eller Ubuntu med:

```sh
dpkg-deb --contents packages/asterisk-prompt-sv-anton.deb
dpkg-deb --info packages/asterisk-prompt-sv-anton.deb
```

## RPM

På Fedora, RHEL och andra RPM-baserade system byggs motsvarande paket med:

```sh
python3 tools/build_rpm.py \
  --voice anton \
  --source /sökväg/till/anton \
  --manifest manifests/anton-release.json \
  --output packages/asterisk-prompt-sv-anton.rpm
```

Även RPM-byggaren kräver samma exakta filkarta, SHA-256-värden och WAV-format.

## Tarball

För manuella Asterisk-installationer kan samma verifierade filuppsättning
packas utan systempaket:

```sh
python3 tools/build_tar_gz.py \
  --voice anton \
  --source /sökväg/till/anton \
  --manifest manifests/anton-release.json \
  --output packages/asterisk-prompt-sv-anton.tar.gz
```
