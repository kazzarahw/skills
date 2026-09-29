# Media Investigation

End-to-end workflow to establish where and when a photo or video was captured and whether it is authentic — evidentiary handling, metadata extraction, reverse image search for provenance, visual geolocation, chronolocation from shadows, and manipulation checks, ending in a location finding with a stated confidence radius.

## Contents
- [Step 1 — Authorized Scope](#step-1--authorized-scope)
- [Step 2 — Secure a Pristine Copy](#step-2--secure-a-pristine-copy)
- [Step 3 — Metadata](#step-3--metadata)
- [Step 4 — Provenance](#step-4--provenance)
- [Step 5 — Visual Geolocation](#step-5--visual-geolocation)
- [Step 6 — Chronolocation](#step-6--chronolocation)
- [Step 7 — Authenticity](#step-7--authenticity)
- [Step 8 — Decide Whether the Claim Is Corroborated](#step-8--decide-whether-the-claim-is-corroborated)
- [Step 9 — Express the Finding](#step-9--express-the-finding)
- [Key Tools](#key-tools)
- [Gotchas](#gotchas)
- [Pivots](#pivots)

## Step 1 — Authorized Scope

State, in writing, before you open the file:

- **Subject** — what the media is, and who appears in or is affected by it.
- **Objective** — verification, disinformation research, missing persons, threat assessment, due diligence, litigation support, or showing someone their own exposure. If you cannot name a legitimate objective, stop.
- **In and out of bounds** — specifically: are you permitted to publish a precise coordinate, or only a region? Is face search permitted? Is anyone in the frame a private individual?
- **Jurisdiction** — yours, the subject's, and the platform's. Precise historical location data about an identifiable person is regulated personal data in most of them.
- **Publication floor** — decide now what precision you will publish, before you know the answer. Geolocating a private individual's home from their own photos is the mechanic of stalking regardless of your intent, and conflict imagery can make the people in frame a target. Rounding a coordinate is a decision to make cold.

**Done when** subject, objective, bounds, jurisdiction and publication floor are written down in the case file.

## Step 2 — Secure a Pristine Copy

Everything downstream is worthless if you contaminate the original.

- Work from the file, not a screenshot of it. For platform video, pull the best rendition with `yt-dlp` and keep the sidecar JSON.
- Hash it immediately and record the hash: `sha256sum evidence.jpg`. A second algorithm costs nothing and pre-empts an argument.
- Set the original read-only, store it unmodified, and do all work on copies. Name derivatives so the transform is legible: `evidence_crop-sign.png`, `evidence_flop.jpg`.
- Record provenance of your own acquisition: the URL, the timestamp you fetched it, who gave it to you, and the platform it came from. Archive the source page before it changes.
- Note whether the file is an original capture, a platform re-encode, or a screenshot. This single fact determines which later tests are valid at all, and you will need it in the report.

**Done when** the original is hashed, read-only, and its acquisition path recorded, and every subsequent step is operating on a named copy.

## Step 3 — Metadata

Run metadata extraction before any transformation. Cropping, rotating, upscaling or even opening the file in some editors rewrites tags.

Prioritise: GPS coordinates and `GPSHPositioningError`; `GPSImgDirection`, which gives you the camera's bearing and lets you reproduce the exact view; `GPSDateStamp`/`GPSTimeStamp` in UTC as the only timezone-anchored clock; the timestamp triplet; device make, model and serial; the software chain; and the embedded thumbnail for comparison against the main image.

If GPS is present you have a **lead**, not an answer. It is a writable field. Continue to step 5 and verify it visually; a metadata coordinate that a visual check confirms is a far stronger finding than either alone.

**Done when** metadata is extracted and recorded, or confirmed absent — and you have written "no EXIF present" rather than "EXIF removed".

## Step 4 — Provenance

Run reverse image search. For video, extract keyframes first and search several of them.

You are looking for an earlier appearance, a different caption, a photographer credit, and a date you can corroborate independently through archives. Open the match pages and read them — the caption on the earliest copy frequently names the place outright, which collapses steps 5 and 6 into a verification exercise instead of a search.

If the media is older than the claim, or from a different country than the claim, you have your answer and it is a stronger answer than a coordinate.

**Done when** you have either an earliest-known publication with its date and caption, or a documented null across at least three engines including crops and a mirrored search.

## Step 5 — Visual Geolocation

Inventory clues before searching, rank them by geographic specificity, fix the country from language, plates, driving side and road markings, then narrow to a site and confirm in satellite and street-level imagery.

If step 3 gave you coordinates, do this anyway as an independent test rather than navigating straight to the coordinate and confirming what you were told. Use `GPSImgDirection` to reproduce the camera bearing and check that the view matches what a camera at that position pointing that way would see. A bearing that points at a blank wall means the coordinate is wrong.

**Done when** you have a candidate location with a stated radius and a written list of the specific features you matched — or a documented region-only result with the reason you could not narrow further.

## Step 6 — Chronolocation

Shadow azimuth for the sun's bearing, shadow-length ratio for its elevation, then solve against a sun-position calculator for the confirmed location. Expect two date bands, not one, and break the tie with foliage, snow, crop stage, or a dated object in frame. Corroborate against a weather archive and note which station you used and how far away it is.

Reconcile the result against the metadata timestamps from step 3. Agreement between an unanchored EXIF datetime and an independently derived sun position is one of the strongest corroborations available in this whole workflow, because the two have no common failure mode.

**Done when** you have a time-of-day range and a date band, each graded, with the discriminator you used named — or an explicit statement that the date remains two-banded.

## Step 7 — Authenticity

At minimum: the physical-consistency checks — shadow convergence across multiple objects, reflection geometry, perspective and scale — and the internal-consistency sweep against your own step 5 findings.

The specific failure this step is here to catch: you have just geolocated a scene that was assembled from two photographs, or generated. A composite geolocates beautifully and means nothing. If shadow convergence fails or an element carries no optical signature, your location finding applies to the background plate only, and you must say so.

**Done when** manipulation and synthesis are assessed, each graded, with signal-level tests either run or explicitly marked invalid for the copy you hold.

## Step 8 — Decide Whether the Claim Is Corroborated

Lay the independent lines of evidence side by side and ask what agrees.

The standard: **three mutually independent non-transient features** matching reference imagery makes a location. Independence is the requirement people fudge. Three photographs of the same sign is one feature. A building footprint, a utility pole line and a ridgeline profile are three. Metadata GPS plus a visual match plus a sun-position-consistent shadow are three, and they are independent because forging all three coherently is hard.

Then run the falsification test you should have written in step 5: name the single observation that would kill your candidate, go look for it, and record that you did. A finding nobody tried to break is not a finding.

Grade the composite honestly:

- **Confirmed** — three independent features align, the falsification test was run and failed to break it, and no line of evidence contradicts another.
- **Probable** — two independent features, or three with one resting on undated or low-resolution reference imagery.
- **Region only** — country or province established, no site. A respectable result.
- **Excluded** — you can affirmatively rule out the claimed location. Needs only one hard contradiction, and is often more useful than finding the true site.
- **Unresolved** — say so. An honest gap beats a confident guess that gets rebutted.

**Done when** each of location, time and authenticity carries a grade and the evidence it rests on, and any contradiction between lines of evidence is stated rather than reconciled away.

## Step 9 — Express the Finding

- **Coordinates plus a radius in metres, always.** A bare six-decimal coordinate claims sub-metre precision you do not have. Derive the radius from what actually bounds you: `GPSHPositioningError` if the finding rests on metadata, the resolution of the reference imagery if it rests on a satellite match, the size of the area consistent with your matched features if it rests on visual work.
- **Camera position and bearing, separately from the subject's position.** These are different places and reports routinely conflate them.
- **Time as a range in local clock time**, saying whether you converted from solar time and what offset you applied.
- **Date as one or two bands**, naming the discriminator that dropped the second — or reporting both if nothing did.
- **The specific features you matched**, listed, with links to the reference imagery and its capture dates.
- **Your assumptions**: assumed object heights, ground flatness, which reference bearing you used, which weather station.
- **Apply the publication floor from step 1.** If it says region-only, round the coordinate before it leaves your notes, not after someone asks.

**Done when** the finding is written with a radius, a grade, its matched features and its assumptions, at the precision step 1 authorised.

## Key Tools

| Tool | Purpose | Cost |
|---|---|---|
| `ExifTool` | Metadata extraction | Free |
| `yt-dlp` | Video download | Free |
| `ffprobe` | Video analysis | Free |
| Google Lens | Visual search | Free |
| Yandex Images | Reverse image search | Free |
| TinEye | Reverse image search | Free |
| Baidu | Reverse image search (China) | Free |
| PimEyes | Facial recognition search | Freemium |
| Forensically | Image forensics | Free |
| FotoForensics | Image forensics | Free |
| InVid | Video verification | Free |
| SunCalc | Sun position calculator | Free |
| MoonCalc | Moon position calculator | Free |
| Google Maps | Mapping and street view | Free |
| Google Earth Pro | Satellite imagery | Free |
| OpenStreetMap | Collaborative mapping | Free |
| Mapillary | Street-level imagery | Free |
| Wayback Machine | Historical web content | Free |
| Geohints | Geolocation hints | Free |
| GeoSolver | Geolocation from images | Free |
| Picarta | AI geolocation | Free |
| Deepware | Deepfake detection | Free |

## Gotchas

- **Every filter has a base-rate problem.** Run six forensic tools on an authentic photograph and something will look anomalous. Anomaly is the normal condition of real images.
- **The platform did it.** Resizing, re-encoding, chroma subsampling and metadata stripping produce artifacts people attribute to manipulation. Establish processing history before interpreting any artifact.
- **You will be handed the worst copy** — a screenshot of a repost of a crop. Most signal-level analysis is invalid on it, and the honest report says so.
- **"Not manipulated" is not a finding.** Absence of detected manipulation is a statement about your tests, not about the image.
- **A real photo can be entirely misleading.** Selective framing, staged scenes and a true image with a false caption all pass every forensic test.
- **Debunking amplifies.** A detailed refutation spreads the original claim — an editorial judgement worth making deliberately. Material is also sometimes seeded to be discovered and debunked, or to see who investigates.
- **Identification from resemblance** is the highest-consequence error here — "this is person Z because they look alike" is not a finding.
- **ELA is mostly used wrongly.** Error level analysis responds to content, so edges and texture light up while flat sky and skin go dark, meaning every image has "suspicious bright regions". One re-save destroys it. It cannot localise a modern edit. Use it as one weak input, only on least-processed files, never as the basis of a published claim.
- **AI detector tools** false-positive on compressed, resized, upscaled, heavily edited and low-light real photographs, false-negative against generators newer than their training data, and are adversarially fragile. Run more than one, treat them as a weak signal, never publish a conclusion resting on one.

## Pivots

| What you got | Send to |
|---|---|
| Earlier copies, credits, original caption | Image provenance |
| Editing chain, device, timestamps | Metadata investigation |
| Location and date verification | Geolocation workflow |
| Deleted or altered source pages | Archive recovery |
| Publishing or seeding domain | Domain investigation |
| Accounts amplifying the media | Username investigation, social media analysis |
| Coordinated network behind the spread | Link analysis |
| Named individuals in or credited on the media | People investigation |
