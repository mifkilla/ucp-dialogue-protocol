# UCP experiments: evidence and reproduction

English is the primary edition · [Русская версия](README.ru.md) · [Main protocol](../README.md)

This directory contains two small repair pilots and a continuity comparison of UCP-related instructions, memory and execution checks. They examine observable behavior in synthetic tasks. Their results do not establish general effectiveness, consciousness, or reliability across models and environments.

**Continuity study:** [implementation and commands](continuity/README.md) · [results](continuity/RESULTS.md) · [fixed plan](continuity/PLAN.md) · [evidence archive](data/continuity-03.zip). Ordinary and structured memory each passed 36/36 episodes; no advantage was demonstrated. The following reproduction section describes the two earlier repair pilots; continuity has its own commands and frozen inputs.

## Read in three steps

1. **Read the findings and their limits:** [Pilot results](PILOT_RESULTS.md) separates completed observations, comparisons, and unresolved questions. Use that report for the results of both pilots.
2. **Understand what was checked:** [Debugging and operational checks](DEBUGGING.md) explains the checks, failure categories, and distinction between a model's proposed action and an action allowed by an external control.
3. **Inspect or reproduce the evidence:** download [Pilot 01](data/pilot-01.zip) and [Pilot 02](data/pilot-02.zip), verify them against [SHA-256 checksums](data/SHA256SUMS.txt), and follow the local commands below.

| Bundle | Main use | Local check |
|---|---|---|
| Pilot 01 | Compare instruction conditions on a frozen set of synthetic cases | `python -m unittest test_runner -v` |
| Pilot 02 | Inspect a follow-up execution loop and its operational checks | `python -m unittest test_loop -v` |

The archives preserve the plans, source code, fixtures, raw model answers, event records, hashes, analyses, and reports used to document each pilot. Each ZIP has a flat root: its Python files and subdirectories appear directly in the extraction folder. Consult the included plan before interpreting a run.

## Which protocol and model were tested?

The protocol input was frozen from [UCP commit `796ffe9`](https://github.com/mifkilla/ucp-dialogue-protocol/tree/796ffe9). The README subsequently received editorial changes for clarity. These pilots do not validate that updated wording as a newly tested intervention.

Historical instruction texts remain in the archives as experimental inputs, including any phrasing later changed in the public invitation. They document what a run received; the [current main protocol](../README.md) is the place to read the present invitation.

The fixtures are synthetic, and the publication contains no API key. Both pilots used the same inherited model backend. This is not a comparison across independently selected models. Recorded seeds control case ordering, not model generation; they do not guarantee identical new answers. The result reports describe the measured scope and remaining uncertainties.

## Check the saved evidence locally

Use Python and PowerShell. Start at the repository root. Extract into a new directory outside the repository so that local analysis cannot overwrite the published bundles. No API key or model access is needed for these unit tests or for rescoring the saved answers.

First, compare the printed hashes with `experiments/data/SHA256SUMS.txt`:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath 'experiments/data/pilot-01.zip', 'experiments/data/pilot-02.zip'
Get-Content -LiteralPath 'experiments/data/SHA256SUMS.txt'
```

Then extract and check each pilot:

```powershell
$repo = (Get-Location).Path
$verificationRoot = Join-Path $env:TEMP ('ucp-verification-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $verificationRoot | Out-Null

Expand-Archive -LiteralPath (Join-Path $repo 'experiments/data/pilot-01.zip') -DestinationPath (Join-Path $verificationRoot 'pilot-01')
Set-Location -LiteralPath (Join-Path $verificationRoot 'pilot-01')
python -m unittest test_runner -v
python analyze.py

Expand-Archive -LiteralPath (Join-Path $repo 'experiments/data/pilot-02.zip') -DestinationPath (Join-Path $verificationRoot 'pilot-02')
Set-Location -LiteralPath (Join-Path $verificationRoot 'pilot-02')
python -m unittest test_loop -v
python analyze.py

Set-Location -LiteralPath $repo
```

`python analyze.py` scores existing saved answers and writes analysis in the extracted copy. It does not generate new model answers. Compare its output with the included reports; distinguish a successful calculation from a claim about how a future run will behave.

**Do not run `prepare.py` or `freeze_holdout.py` on a completed bundle.** Preparation and freezing belong to creating a new experiment and can replace the inputs or manifests needed to interpret the archived run. A new generation run requires a separate working directory, an explicit design, and its own model configuration and evidence record.
