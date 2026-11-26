# True Position series: sources and fact check

Status: **published 2026-11-25 (approved by John) with the items under "Not verified" still open.**
Everything below should still be checked against our own copy of ASME Y14.5 (the edition each print
calls out); fix and republish any video if a check turns up a mistake.

The full ASME standards are paywalled. What was checked, and how:

| Claim used in the videos | Where it was checked | Confidence |
|---|---|---|
| Y14.5-2009 section numbers: 1.4 Fundamental Rules, 2.8 Applicability of Modifiers, 2.9 Screw Threads, Section 4 Datum Reference Frames, Section 7 Tolerances of Location, Appendix B Formulas for Positional Tolerancing | ASME's published table of contents for Y14.5-2009 (asme.org preview PDF) | High |
| Position Ø = 2 × √(Δx² + Δy²); no doubling when there is no Ø (width zone) | Several calculator and training sources agree | High |
| Round zone through the corners of a ±.005 square is Ø.0141 with about 57% more area | Arithmetic: π(.00707)² / (.010)² = 1.57 | High |
| Thread position applies to the pitch cylinder axis unless MAJOR DIA / MINOR DIA is noted under the frame (or next to the datum feature symbol) | gdandtbasics.com position/threads article quoting Y14.5; Eng-Tips threads | Medium-high. 2009 section 2.9 confirmed by the TOC; **2018 paragraph number not found** |
| MMB / LMB / RMB terms introduced in Y14.5-2009; 1994 used MMC/LMC on datum references | Machine Design article on Y14.5-2009; Zeiss comparison table | High |
| Y14.5-2018 removed concentricity and symmetry (A-8.4); use position, runout or profile | Mitutoyo "GD&T and the new ASME Y14.5-2018" (Salsbury, 2019); GeoTol; GD&T Seminars; Tec-Ease | High |
| 2018 renamed the theoretical datum feature simulator "true geometric counterpart" | GeoTol; Made to Measure blog | Medium |
| 2018 default: a rocking datum feature is settled to a single solution that minimizes separation | GeoTol (quotes the standard) | Medium. Only one source |
| MMC/LMC, bonus tolerance and virtual condition rules unchanged in 2018 | GeoTol | Medium |
| Projected zone: Ⓟ after the tolerance, height after the symbol is the minimum height, or a chain line with a dimension; height at least the mating part's max thickness (or stud height) | gdandtbasics.com projected zone page; Goodwin University article | Medium-high. **2009 paragraph (7.4.1?) only from a study guide** |
| Fixed fastener T = (H − F)/2 each part (equal split); floating T = H − F; formulas in Y14.5 Appendix B; fixed formula assumes holes square to the joint | Open Exam Prep study guide; Eng-Tips; Dimensioning and Tolerancing Handbook excerpt | Medium. Appendix B exists per TOC; formula text not read directly |
| MMC on threaded holes gives little real bonus | gdandtbasics.com video summary; GD&T Seminars (Belanger) comment | Medium. Practitioner opinion, not the standard |
| Position to one datum only, single hole = orientation (perpendicularity) control; pattern to one datum controls spacing and orientation, pattern floats | GD&T Seminars "Position with only one datum?"; Eng-Tips | Medium-high |

## Example numbers used (all made up)

- Plate 4.000 × 3.000 × .750, Ø.500–.505 hole at 1.500 / 1.250 basic, position Ø.010 to A B C.
- Datum order example: edge C out of square by .010 over 4.000. B-then-C gives Ø.0045, C-then-B gives Ø.0116 (computed in `tp2_datums.py`).
- MMC example: hole Ø.5035, Δx .005, Δy .0035 → Ø.0122; allowed Ø.0135 at MMC.
- LMC example: hole .400 from an edge; worst-case wall .1425 at every size.
- Threads: 3/8-16 UNC-2B, .750 deep; mating part .500 thick with a Ø.406 clearance hole; position Ø.015 Ⓟ .500.

## Not verified / to check with the standard

1. The 2018 paragraph that carries the screw-thread pitch-cylinder rule.
2. The projected tolerance zone paragraph numbers in 2009 and 2018.
3. The exact Appendix B formula wording.
4. Whether our customers' prints call out 2009, 2018 or 1994.

## Source links

- ASME Y14.5-2009 contents: https://asme.org/getmedia/da2ff89e-067b-4160-8e2e-53e6c7da1d3b/17707.pdf
- Mitutoyo, GD&T and the new ASME Y14.5-2018: https://www.mitutoyo.com/webfoo/wp-content/uploads/ASME_Y14.5-2018_Salsbury.pdf
- GeoTol, 2018 vs 2009: https://geotol.com/symbol/2018-standards/
- Tec-Ease tip 224: https://www.tec-ease.com/gdt-tips-view.php?q=224
- GD&T Seminars, the new 2018 standard: https://gdtseminars.com/2019/05/24/the-new-asme-y14-5-2018-standard/
- GD&T Seminars, position with only one datum: https://gdtseminars.com/2010/05/18/position-with-only-one-datum
- GD&T Seminars, projected tolerance zone: https://gdtseminars.com/2020/02/26/projected-tolerance-zone-equivalent-to-tightening-the-zone/
- GD&T Basics, position on threads: https://www.gdandtbasics.com/position-controlling-threads-on-features/
- GD&T Basics, projected tolerance zone: https://app.gdandtbasics.com/symbol/projected-tolerance-zone
- Goodwin University, projected tolerance zones: https://www.goodwin.edu/enews/faculty-article-projected-tolerance-zones-gdt/
- Machine Design, new Y14.5-2009: https://www.machinedesign.com/learning-resources/basics-of-design/article/21834565/new-asme-y145-2009-standards-for-gdt
- Open Exam Prep, projected zones and fastener formulas: https://open-exam-prep.com/study-guides/asme-gdtp-technologist/ch8/projected-zones-fasteners
