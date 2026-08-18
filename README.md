# Stacked Queries (`stacked-queries`)

**Category:** sql injection · **Difficulty:** hard · **Points:** 400

Stacked queries let you INSERT a row you can later SELECT for the seed.

## Run it

```bash
docker build -t sparflag/stacked-queries .
# `deca-ai start stacked-queries` (or the web UI) prints the docker run line with your
# SPARFLAG_SERVER + SPARFLAG_INSTANCE_TOKEN
```

## Recover the flag

The delivery blob is Fernet ciphertext. Discover the key seed, derive the Fernet key, then decrypt.

The plaintext flag is never written to disk or served — only the encoded delivery blob
is. When you have it:

```bash
deca-ai submit stacked-queries 'sparflag{...}'
```

## Hints

- Does the driver allow multiple statements?
- Write the seed into a readable table, then fetch it.
