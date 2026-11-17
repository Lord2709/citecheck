# P05: written test on binary-exploitation claims (2026-11-17)

An outside participant (a student who reads security papers, not on the team) built a test paragraph on purpose,
ran it on the live site, and wrote down for every citation what CiteCheck said and what they think is right. Their
document, as written, with their name and the file's metadata removed. Screenshots of the run:
`P05_2026-11-17_results_1.png`, `P05_2026-11-17_results_2.png` (the site as it was before the update of 2026-11-17,
14:10 ET).

## The test paragraph they pasted

Stack-based buffer overflows occur when a program writes more data into a stack-allocated buffer than the buffer can
accommodate, potentially overwriting adjacent variables, saved frame pointers, or return addresses [1]. In traditional
stack-smashing attacks, an attacker may redirect execution by overwriting a saved return address with an
attacker-controlled address [1]. Address Space Layout Randomization (ASLR) randomizes the locations of memory regions,
making it more difficult to predict the addresses required for successful exploitation [2]. ASLR completely prevents
buffer overflow attacks by ensuring that memory addresses can never be predicted [2]. Stack canaries are values placed
on the stack to detect certain forms of stack corruption before a function returns [3]. Stack canaries protect against
all memory corruption vulnerabilities, including heap-based use-after-free attacks [3]. Data Execution Prevention (DEP)
restricts execution from memory pages that are not marked executable [4]. Return-oriented programming (ROP) allows
attackers to construct computations using instruction sequences already present in executable memory [5]. ROP attacks
require the attacker to inject new executable shellcode into the stack before execution can begin [5]. Position
Independent Executables (PIEs) allow executable code to be loaded at different virtual addresses when ASLR is enabled
[2].

References

[1] Aleph One. Smashing the Stack for Fun and Profit. Phrack 1996. https://phrack.org/issues/49/14
[2] Shacham et al. On the Effectiveness of Address-Space Randomization. ACM CCS 2004. doi:10.1145/1030083.1030124
[3] Cowan et al. StackGuard: Automatic Adaptive Detection and Prevention of Buffer-Overflow Attacks. USENIX Security 1998.
[4] Microsoft. Data Execution Prevention. Microsoft Learn. https://learn.microsoft.com/en-us/windows/win32/memory/data-execution-prevention
[5] Shacham. The Geometry of Innocent Flesh on the Bone: Return-into-libc without Function Calls (on the x86). ACM CCS 2007. doi:10.1145/1315245.1315313

## Their results

"I tested CiteCheck with 10 claims related to binary exploitation. I intentionally included a mixture of correct and
incorrect statements to see how well it handles verification."

| # | Claim (shortened) | CiteCheck | Their assessment |
|---|---|---|---|
| 1 | Stack overflows overwrite adjacent memory | Could not check | Retrieval failure |
| 2 | Return-address overwrite redirects execution | Could not check | Retrieval failure |
| 3 | ASLR randomizes memory locations | Not enough evidence | Arguably supported |
| 4 | ASLR completely prevents exploitation | Not enough evidence | Should be contradicted |
| 5 | Stack canaries detect stack corruption | Not enough evidence | Wrong paper retrieved |
| 6 | Stack canaries prevent all memory corruption | Not enough evidence | Wrong paper retrieved; claim false |
| 7 | DEP restricts execution | Could not check | Retrieval failure |
| 8 | ROP reuses existing instructions | Supported | Correct |
| 9 | ROP requires injected shellcode | Not enough evidence | Should be contradicted |
| 10 | PIE enables executable relocation under ASLR | Not enough evidence | Reasonable if using abstract only |

## Their feedback (verbatim)

"The citation extraction worked well, and I liked how it displayed the evidence sentences and explained the
verification process. But I noticed a few issues:

1. Contradiction detection: Some clearly incorrect statements were classified as "Not enough evidence" instead of
   "Contradicted." For example, I included a claim saying ASLR completely prevents buffer overflow attacks, but the
   cited paper explicitly discusses bypassing ASLR. The same happened with a false claim that ROP requires injected
   shellcode.
2. Reference matching: For the StackGuard paper by Cowan et al. (1998), the tool retrieved a completely different paper
   from 2007. It looks like the matching algorithm might be relying too much on title similarity without sufficiently
   checking the author and year.
3. Source retrieval: The tool couldn't check the Phrack article or Microsoft documentation because it couldn't find
   them through Crossref, even though I provided direct URLs. A fallback for retrieving content directly from URLs would
   help.
4. Confidence scores: Some incorrect classifications were assigned confidence scores of 0.99 or higher. I know the
   report mentions that the scores aren't calibrated, but it might be worth checking the NLI model's class predictions
   and confidence calculations.
5. Abstract-only verification: The report says zero papers were read in full. This limits verification for claims that
   are supported in the full paper but not explicitly discussed in the abstract.

One positive thing is that even when the verdict was incorrect, the evidence CiteCheck displayed was often relevant
enough for me to spot the problem myself. That's a useful feature.

Overall, I think the citation extraction and explanation features are working well. I'd prioritize fixing
contradiction detection and reference matching first, since those directly affect the reliability of the verdicts.

Also, I tested this on cybersecurity literature rather than biomedical papers, so I understand the results might differ
from the SciFact benchmark mentioned on the site."
