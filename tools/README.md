# Odyssey data tools

`generate_odyssey_csv.py` builds the Odyssey pokedex, regional and matchup CSVs from
the `data.json` published by [epieffe/talrega-dex](https://github.com/epieffe/talrega-dex).
It writes two variants:

* `out/fork/` uses the real `aether` type, and is what ships in `app/src/main/assets/dex/`.
* `out/csv-only/` maps Aether onto the unused `fairy` slot, for importing as a custom
  profile on the upstream app.

`verify_odyssey_csv.py` reimplements the app's CSV parsing and matchup logic, then
checks every one of the 409 dex entries against the raw `data.json` matchup tables.
Both variants must report zero mismatches.

```bash
git clone https://github.com/epieffe/talrega-dex.git
python3 generate_odyssey_csv.py
python3 verify_odyssey_csv.py
```
