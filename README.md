# minion-vocabulary

Vocabulary packs for [Minion](https://github.com/studiolxd/minion): TOML
files that say what applications exist, what to call them in Spanish, and
what a spoken phrase should do. Minion's `«Actualizar vocabulario…»` menu
item (and `minion packs update` from the terminal) downloads the latest
release of this repository into
`~/Library/Application Support/Minion/vocabulary/`, alongside anything you
have written there yourself.

## What a pack is

A pack is one `.toml` file under `packs/`. Everything it may contain is
data — a name, some phrases, one of four things to do — never a script:
Minion refuses to run anything from a file that may have been downloaded.

```toml
category = "macOS"

[[apps]]
name = "Finder"                  # shown in the log and the catalogue
bundle_id = "com.apple.finder"   # from /Applications/X.app/Contents/Info.plist
aliases = ["finder", "fainder", "el buscador", "archivos"]

[[commands]]
name = "copiar"                  # stable identifier, shown in the log
phrases = ["copia esto"]         # accents and case do not matter
keys = "cmd-c"                   # what to press

[[sites]]
name = "gmail"                   # said on its own, after an opening verb
url = "https://mail.google.com"
```

- `category` names the group in Minion's «Qué puedo decirle» catalogue.
  Optional — the file name is used when it is missing.
- An `[[apps]]` entry needs `name`, `bundle_id` and `aliases` — every way
  Minion should recognise the app being asked for.
- A `[[commands]]` entry needs `name`, `phrases`, and **exactly one** of:
  - `keys = "cmd-shift-b"` — a keystroke, written as it reads on a menu
  - `action = "volume:up"` — one of Minion's own named actions (the closed
    list lives in `minion/src/vocabulary.rs`, `NAMED_ACTIONS`)
  - `text = "un saludo"` — type this into whatever has focus
  - `url = "https://…"` — open this page
  - Add `bundles = ["com.some.app"]` to make it contextual: the command
    then only exists while that application is in front, and it beats a
    global command claiming the same phrase.
- Unknown keys are refused — a misspelled key invalidates the *whole
  file*, which Minion reports in its log and skips, leaving the rest of
  the vocabulary untouched.

See `packs/macos.toml` for the full schema, written out in comments, and
`packs/community/adobe.toml` for a minimal third-party pack.

## Contributing

Pull requests welcome. A few rules, because a pack here is downloaded and
trusted by other people's microphones:

1. **Alias what the recogniser actually wrote, not what you'd guess.**
   Spanish speech recognisers turn English app names into surprising
   things — "Chrome" becomes "cromo", "Safari" becomes "so fuddy". Do not
   invent a spelling from how you imagine it sounds: run Minion, say the
   name, read `~/Library/Logs/minion.log` for the `unknown  «…»` line it
   left, and use exactly that. `minion learn` does this for you from the
   log.
2. **A contextual command (`bundles = […]`) needs a verified shortcut.**
   Press it inside the real application first. A guessed keystroke that
   does the wrong thing is worse than no command at all.
3. **One pack, one subject.** Group by application family or use case
   (`packs/community/adobe.toml`, not one file per app), the same way the
   built-in packs are split by `macos`, `browsers`, `office`, `media`,
   `dev`, `apps`, `sites`.
4. **No scripts, no runtime interpolation.** If what you want to do is not
   expressible as `keys`, one of the named `action`s, `text` or `url`,
   it belongs in Minion's own code, not a vocabulary file.
5. Run the validator locally before opening a pull request:
   `python3 scripts/validate.py`. CI runs the same check and regenerates
   `manifest.toml` on every push to `main`.

## The manifest and releases

`manifest.toml` lists every pack under `packs/` with its SHA-256 and the
release version. Minion downloads a release's `manifest.toml` and
`packs.zip`, checks each file's hash against the manifest before unzipping
anything, and never removes a file in your own vocabulary folder that
this manifest does not mention.

`.github/workflows/validate.yml` regenerates the manifest and checks that
every pack parses as TOML on each push to `main`; a maintainer cuts a
release (`packs.zip` + `manifest.toml`) by hand when the packs here are
ready to ship.
