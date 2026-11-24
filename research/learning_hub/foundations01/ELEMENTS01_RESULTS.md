# ELEMENTS-01 — verified outcome (2026-11-24)
Run https://github.com/Abrasax63/Omega-pub/actions/runs/45386777662
Artifact https://github.com/Abrasax63/Omega-pub/actions/runs/45386777662/artifacts/14917980810
Source 522256bdf3072a25394262adc199c65b1cc892ef. All 80 records and 40 tasks
present; independent local Python ZIP SHA256 and raw file SHA256 agree with
GitHub and report; all row raw and prompt digests checked.
ZIP cd6d902b9ce91bc7489d6c763fc9e86f813f1dc5e2ead2199c29125184040027
raw d612c0fb5a01a35e7c998d3f45395365b074ef0940093a4d0ccc235ac668fd40.
Free strict digits 0/40 valid. Binary forced 40/40 valid, all predict 1.
Membership 16/32 correct, 0/16 both endpoints. Logic 1/8 correct,
balanced accuracy 0.5. Both preregistered signals fail.

Post-hoc exploratory diagnostic: anchored case-insensitive Yes/No word
at beginning of free text, no other extraction. Membership 29/32
extractible, 15/32 correct (4 absent, 11 present), 3/16 pairs both right,
2/16 both inverted. Logic 8/8 extractible, all No, 7/8 correct, balanced
accuracy 0.5. No change to primary strict score. Conditional probability
p(1)/(p(0)+p(1)) averaged .822922 on absent and .823431 on present
membership cases, mean paired contrast .000509, 9/16 positive contrasts.
Mean allowed digit mass .025612 (membership), .013579 (logic). The
binary forced decision is strongly biased and is not an adequate proxy
for natural language response; nevertheless prefix analysis shows no
gain over simple guessing and no established membership capability.
Do not conclude mathematical impossibility for the model.
No gradient, no promotion, no old holdout reused.
Decision: train elementary edge membership only, natural Yes/No target,
paired counterfactual questions, fresh base adapter and fresh held-out
families. Do not launch the composition training or autonomous teacher
until measurable graph-dependent sensitivity is established.
