# Never silently swallow exceptions

Standing order, all projects, all languages: never write a catch/except that discards the error and does nothing. No `except: pass`, no `except Exception: pass`, no empty `catch {}` / `catch (e) {}`, no ignoring an error value you were handed back.

Silent swallowing turns a failure into an invisible one. The thing you were guarding against still happened, but now there is no signal, no log, no diagnostic. It is the single most common way a real bug hides inside a green test run. (Concrete case that prompted this order: a tier-2 eval teardown used `except: pass` on every delete and discarded the return, so a failed fixture wipe left synthetic data live in a real workspace with zero trace.)

When you catch, do at least one of:
- **Handle it** meaningfully (fall back, retry, translate to a domain error).
- **Surface it** (logger / print / structured error / a failure sentinel the caller or CI gate can see) with enough context to diagnose.
- **Re-raise** (`raise`, or `raise NewError(...) from e`).

Catch the **narrowest** exception type you actually expect. Don't blanket-catch `Exception` / `BaseException` just to make an error go away.

Genuinely-ignorable cases exist (best-effort cleanup where a failure truly does not matter). They are rare and must be made **explicit**: catch the specific type and leave a one-line comment saying why it is safe to ignore (`except FileNotFoundError: pass  # already gone`), never a bare silent pass. If you cannot state why it is safe, it is not.

This applies to code you write AND code you review: flag a silent swallow as a finding.

**In review it is a request-changes, not a nit.** Do not soften it because the rest of the change is excellent, because the swallowed case looks genuinely harmless, or because it is three lines against two thousand. The standard is absolute rather than proportionate to the risk in any one instance, and grading it by instance is exactly how it survives: every individual occurrence looks tolerable and the class never goes away. Blocking on it also costs the author almost nothing, since the fix is narrowing a type and moving a comment. **Caught 2026-08-19**, when an otherwise outstanding pull request was written up as approve-with-a-nit over a `try: conn.read_only = True / except Exception: pass`, and the principal's correction was "we never do that." Note the aggravating detail: it sat inside a guard built to stop controls reporting success without proving anything, and a silently-failed assertion is precisely that.
