# Ronen OS Public

A portable Ronen OS integration for GPT chats on any subscription tier, with a
public GitHub backbone and a plain-text fallback. Tool availability and limits
still depend on the chat/account. This project does not unlock paid features.

**Start:** open [START_HERE.md](START_HERE.md). For a chat without URL retrieval,
paste [RONEN_OS_ANY_GPT.txt](exports/RONEN_OS_ANY_GPT.txt) into that chat, then give
it your task. The text is self-contained; attaching it is optional.

## What is shared

| Part | Purpose |
| --- | --- |
| core/runtime.md | Public workflow, privacy and source-loading rules |
| modules/search.md | Source discovery, coverage and evidence rules |
| modules/analysis.md | Reproducible analysis and uncertainty rules |
| workflows/pbs.md | One bounded, verified step at a time |
| templates/handoff.md | Empty continuation template |
| PUBLIC_MANIFEST.json | Explicit document allowlist with byte counts and SHA-256 |
| exports/RONEN_OS_ANY_GPT.txt | Generated offline snapshot for paste/attachment |
| tools/read_public.py | Optional standard-library, GET-only pinned reader |

This is a curated public edition, not the complete private OS. Two reusable
policy files are copied byte-for-byte from the reviewed upstream snapshot.
The public runtime and PBS workflow are adaptations, not claims to reproduce
the private runtime. See [PUBLICATION_REVIEW.json](PUBLICATION_REVIEW.json).

Personal preferences, private state, credentials, finances, contacts, device
details, trading records, research datasets, handoffs and old Git history are
excluded. References in copied modules to non-exported tools/files are context,
not available capabilities. This reader never needs the private repository.

## Read-only access

Readers use anonymous HTTPS GET and receive no token or GitHub write tools.
The separate public repository is the privacy boundary. A prompt or folder
name inside a private repository would not enforce that separation. Connecting
an owner's broad GitHub account separately is outside this integration.

Observe public main once, then read the manifest and documents at that exact
40-character commit. Hash verification detects inconsistent or modified bytes;
it is not a cryptographic proof that a maintainer is trustworthy.

## Optional verified CLI

Python 3.10+ and internet access are sufficient. No packages or credentials:

```bash
python tools/read_public.py --commit PUBLIC_COMMIT_SHA
python tools/read_public.py --commit PUBLIC_COMMIT_SHA --module analysis
```

The reader prints the core/workflow/template and the selected module. Analysis
also includes its search prerequisite. An explicit commit is mandatory; there
is no implicit latest mode, private fallback, arbitrary URL or write endpoint.

## Maintaining this public edition

Edit only this clean public repository. Review every proposed export for both
personal information and secrets; scanners are secondary checks. Never mirror
the private repository, its Git history or a recursive folder automatically.
The fixed allowlist in tools/build_public.py must be reviewed before extension.
Only exact reviewed upstream bytes may be copied; update their source digests
and provenance deliberately. Missing or changed source bytes fail the build.

```bash
python tools/build_public.py
python tools/build_public.py --check
python -m unittest discover -s tests -v
```

Publication needs a reviewed diff and passing checks. Consumers observe a fresh
commit on the next load; an existing chat is not updated automatically. Revoking
a public URL cannot recall copies already downloaded. No automated export or
background synchronization is installed.

## Official product references

Reviewed 12 November 2026:

- [Use ChatGPT](https://learn.chatgpt.com/docs/use-chatgpt): context can be
  supplied through text/files and supported tools; plugin availability varies.
- [About GitHub repositories](https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories):
  public repository contents and their history are accessible on the internet.

These references describe host capabilities and visibility. They do not prove
this prompt was tested on every subscription, model, device or language.
