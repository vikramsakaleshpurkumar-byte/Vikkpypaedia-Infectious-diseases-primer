# Vikkypaedia · Pediatric Infectious Diseases

Open **index.html** in a desktop browser. No server, sign-in, network connection, or installation is required. Keep the folder structure intact. The ZIP contains the same portable course.

Source attribution and permissions are documented in [Source credits](SOURCE_CREDITS.md). The reference has 1,178 PDF pages; all 168 content chapters are included.

## Included

- Reader: all source chapters with five source-extracted study pillars, paragraph page references, images, and links to complete raw Markdown.
- Pathogen atlas: etiology, epidemiology, and diagnostic excerpts for every chapter.
- Clinical feature explorer: 32 searchable feature tags. Results reflect text matches, not a validated differential diagnosis or a probability estimate.
- Treatment matrix: 809 paragraph excerpts, including 82 with detected dose units. Ages, dose limits, route, and duration must be checked in the original source context.
- 1,310 section recall cards with progress saved in this browser, chapter / pathway scopes, and Anki TSV export.
- 196 quizzes: 168 automated passage-recognition questions and 28 authored diagnostic vignettes. They are labeled separately and have source references. No independent specialist item review has been performed.
- 1,452 extracted image placements, caption reveal self-test, chapter filters, and full-size viewing.
- 83 geometry-detected tables rendered as images and converted to Markdown. Other source tables remain in the raw page text; they were not silently converted into invented structured data.

## How to study

1. Choose a pathway or a chapter. Read the five study pillars, then the source content.
2. Explain the clinical pattern aloud and work through its flashcards.
3. Use the visual spotter with captions hidden.
4. Complete authored vignettes and source-recognition quizzes; open source references after answering.
5. Revisit cards marked Needs review. Import `anki_pediatric_infectious_diseases.tsv` into Anki as Basic notes (field 1 Front, field 2 Back, field 3 Tags).

## Fidelity and limits

The reader is a structured extraction, not a facsimile. Raw Markdown retains small-font material and page markers; the clinical reader excludes captions from the clinical paragraphs and displays images separately. Some compound words may retain extraction artifacts. Multi-panel figures can share captions; 36 image placements have no automatically matched caption and explicitly point to their source page. A rendered crop may include source labels. Clinical answers should be checked against the original PDF. Chapter numbering and page boundaries come from the embedded bookmarks, cross-checked against the printed contents and the 14-page offset.

The six pathways are course editorial groupings; the source book itself is alphabetical. No genetics / OMIM atlas is fabricated for this infectious disease text. Flashcards are source-extracted prompts; the automated quiz items are passage-recognition exercises rather than independently authored board questions. Progress storage depends on browser settings and stays on the device.

This is a private, edition-based learning course. Source details, permissions, and update references are kept in [Source credits](SOURCE_CREDITS.md).

## Build provenance

Built 21 October 2026 from the user-specified downloaded PDF. The two detailed supplied skill documents are byte-identical; the third is a shorter description of the same pipeline. The supplied Nelson examples, paths, counts, account names, publication steps, and force-push commands were treated as reference material. No remote repository or public website was created or modified.

See `BUILD_REPORT.md`, `build/verification.json`, and `build/source_metadata.json` for coverage and checks. Reproduction scripts are in `build/`; they require Python and PyMuPDF 1.26.7, and the source PDF path must be adapted for another machine.

Original PDF buttons open the existing Downloads file at its PDF page. The source PDF is not included in this package. Move/update those links if the source file changes location.

## Private course branding

The interface and Anki export use neutral Pediatric Infectious Diseases branding. Original credits, copyright notices, and clinical attributions are retained in reference material. The original source file is unchanged.
