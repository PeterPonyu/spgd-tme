# V3 fresh representation-perturbation results

We performed 21 fresh fits of the locked estimator on deterministic 400-spot probes from openST, Xenium (`realgt`), and CosMx BCC (`realgt3`). The reference representation retained all shared genes once, then 75% and 50% random subsets with three prespecified seeds per level. The same retained genes were applied to spots and references, and the reportability threshold remained fixed at 0.80.

The historical-pair decision was stable in all 21 fits. openST remained ABSTAIN at 100%, 75%, and 50% retention (historical cosine means 0.9727, 0.9740, and 0.9663; malignant RMSE means 0.0762, 0.0786, and 0.0846). Xenium `realgt` likewise remained ABSTAIN (cosine means 0.9802, 0.9826, and 0.9790; malignant RMSE means 0.1682, 0.1733, and 0.1699). CosMx BCC `realgt3` remained KEEP (cosine means 0.6037, 0.6121, and 0.5605; malignant RMSE means 0.1220, 0.1229, and 0.1423).

The descriptive all-eligible-neighbor maximum behaved differently in BCC: it remained above threshold at every retention level (0.8247, 0.8413, and 0.8720), with Melanocyte as the maximum in the partial-gene fits. This is evidence that the historical designated pair and the complete-scan maximum answer distinct estimands; it should be reported as a sensitivity analysis rather than silently substituted into the primary operating rule.

These results support representation robustness of the historical KEEP/ABSTAIN calls across substantial gene loss, while also showing a bounded accuracy cost at 50% retention in BCC. They do not establish that every possible gene-selection scheme is stable, and they do not resolve the author-level choice of a single universal neighbor-selection rule.
