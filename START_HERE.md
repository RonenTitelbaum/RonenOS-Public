# Load Ronen OS Public

Copy the following into the GPT chat you want to use. No login is required.

```text
Load Ronen OS Public in read-only mode for my next task.
Public source: https://github.com/RonenTitelbaum/RonenOS-Public

If you can retrieve URLs, first observe the public main commit through
https://api.github.com/repos/RonenTitelbaum/RonenOS-Public/commits/main
Then replace COMMIT below with that exact 40-character SHA and read:
https://raw.githubusercontent.com/RonenTitelbaum/RonenOS-Public/COMMIT/PUBLIC_MANIFEST.json
Read the listed core runtime and PBS workflow, then only the module needed
for my task, all at that same commit. Analysis also needs search.
Verify bytes and SHA-256 only if you actually have that capability.
Do not request a token, login, private repo, or write permission.

If URL retrieval fails or is unavailable, say so plainly. Use the full
RONEN_OS_ANY_GPT.txt snapshot if I have supplied it; label it OFFLINE_SNAPSHOT.
Do not invent a successful GitHub connection, private state, tools, or a
background process. Follow the host's rules and my current task authority.
Give a short load receipt and proceed with the task.
```

Without URL retrieval, copy the full text from
[exports/RONEN_OS_ANY_GPT.txt](exports/RONEN_OS_ANY_GPT.txt) into the chat instead.
That includes the public runtime and modules, so it can work without a connector.
It is a dated snapshot, not a live GitHub connection. Read-only guidance cannot
remove permissions from unrelated tools already attached to a chat.
