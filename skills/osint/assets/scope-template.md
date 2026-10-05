# Scope Note

Reference copy of what `scope_note.py` renders into `<case>/scope.md`. Every `{brace}` field is
filled from its flag; a field you did not supply renders as `{not_stated}`, printing the literal
string `— NOT STATED —`. A field is never dropped and never guessed.

## Subject

{subject}

Must have: the discriminator that makes this the subject asked about, in one line.
Must not have: the similar thing it must not be confused with, in one line.

## Objective

{objective}

Decision this feeds: {decision}

What would settle it: {settle}

Both lines turn a search into an investigation: without a decision the work produces material
nobody asked for, and without a settling condition there is no way to call the question
answered. Written from a bare identifier, the note shows the unfilled fields as gaps, not blanks:

    Decision this feeds: — NOT STATED —
    What would settle it: — NOT STATED —
    Jurisdiction: — NOT STATED —

## In bounds

{in_bounds}

## Interactive probing

{interactive}

Interactive probing means querying a service that answers anyone — WHOIS, RDAP, a
certificate-transparency log, a search engine, a public paste — never a non-public surface.

## Out of bounds

{out_of_bounds}

## Jurisdiction

{jurisdiction}

A jurisdictional limit is recorded as a limit on the finding, not resolved by guessing.

## Stop conditions

The investigation halts and the work returns to the user for a decision when:

- anything requires authentication, a credential, a paid account, or a login.
- anything needs a warrant, a court order, or the cooperation of a service operator.
- any request would identify a private individual at their home or at their workplace.
- any pivot would leave the in-bounds list written above.

If the only answer to "is this allowed" is "I was authorised", stop and ask.