/* Coverage grid for the artificial-organisms page.
   rows = behavioral processes / phenomena; cols = artificial-organism approaches.
   The principles are all long established; the grid asks only who has reproduced
   each one with THAT SPECIFIC AO approach.
   A cell is 'lab' (our AO does it), 'field' (another research group's AO of the
   same approach does it), 'both', or open (no AO of this approach has yet).

   Sources: integrated-principles = the molecular-dynamics-algorithm-ao repo (only
   ours exists). MPR = mpr-aos (ours is the only MPR AO). ETBD = our etbd-aos plus
   McDowell and colleagues' ETBD AOs (field). Q-learning = our q-learning-aos plus
   other groups' RL/Q-learning agent implementations (field); several need augmented
   variants (latent-cause or distributional RL), noted on hover.
*/
window.AOGRID = {
  cols: [
    { id: 'qlearning', label: 'Q-learning' },
    { id: 'mpr', label: 'MPR' },
    { id: 'etbd', label: 'ETBD' },
    { id: 'integrated', label: 'Integrated-principles' },
  ],
  groups: [
    { label: 'Respondent', rows: [
      ['resp_acq', 'Acquisition'],
      ['resp_ext', 'Extinction'],
      ['spont', 'Spontaneous recovery'],
      ['stimgen', 'Stimulus generalization'],
      ['peakshift', 'Generalization gradient & peak shift'],
      ['discrim', 'Discrimination'],
      ['blocking', 'Blocking'],
      ['overshadow', 'Overshadowing'],
      ['renewal', 'Renewal (ABA)'],
      ['reacq', 'Rapid reacquisition'],
      ['second_order', 'Second-order conditioning'],
      ['cond_inhib', 'Conditioned inhibition'],
    ]},
    { label: 'Operant', rows: [
      ['op_acq', 'Acquisition'],
      ['op_ext', 'Extinction'],
      ['schedules', 'FR / VR / FI / VI schedule signatures'],
      ['pree', 'Partial-reinforcement extinction effect'],
      ['threeterm', 'Three-term stimulus control'],
      ['matching', 'Matching (concurrent + concatenated GML)'],
      ['momentum', 'Behavioral momentum'],
      ['contrast', 'Behavioral contrast'],
      ['punishment', 'Punishment'],
      ['avoidance', 'Avoidance / negative reinforcement'],
      ['reinstatement', 'Reinstatement'],
      ['timing', 'Interval timing'],
      ['vigor', 'Vigor / response rate & bout structure'],
    ]},
    { label: 'Choice, dynamics, & quantitative laws', rows: [
      ['risk', 'Risk-sensitive foraging / energy-budget rule'],
      ['resurgence', 'Resurgence'],
      ['rpasym', 'Reinforcement–punishment asymmetry'],
      ['skew', 'Higher-moment (skew) effects'],
      ['single_alt', "Single-alternative response rate (Herrnstein's hyperbola)"],
      ['magnitude', 'Reinforcer magnitude effects'],
      ['discounting', 'Delay discounting / impulsive choice'],
      ['prob_disc', 'Probability discounting'],
      ['variability', 'Behavioral variability'],
      ['choice_dyn', 'Choice dynamics / preference tracking'],
      ['demand', 'Demand / behavioral economics (unit price)'],
      ['foraging', 'Optimal foraging / patch-leaving (MVT)'],
    ]},
  ],
  // lab[col] = '*' (all rows) or [rowId, ...]. A row in both lab and field shows as 'both'.
  lab: {
    // molecular-dynamics-algorithm-ao repo audit
    integrated: ['resp_acq', 'resp_ext', 'spont', 'stimgen', 'peakshift', 'discrim', 'blocking',
      'overshadow', 'renewal', 'reacq', 'op_acq', 'op_ext', 'schedules', 'pree', 'threeterm',
      'matching', 'momentum', 'contrast', 'punishment', 'risk', 'resurgence', 'rpasym', 'skew',
      'magnitude', 'discounting', 'prob_disc', 'demand', 'timing', 'foraging', 'vigor'],
    qlearning: ['matching', 'op_acq', 'op_ext', 'resurgence', 'choice_dyn'],
    mpr: ['single_alt', 'matching', 'choice_dyn'],
    etbd: ['matching'],
  },
  // field[col] = [rowId, ...] (another research group's AO of this approach has demonstrated it)
  field: {
    qlearning: ['resp_acq', 'resp_ext', 'spont', 'stimgen', 'discrim', 'blocking', 'overshadow',
      'renewal', 'reacq', 'op_acq', 'op_ext', 'pree', 'threeterm', 'matching', 'punishment',
      'rpasym', 'single_alt', 'magnitude', 'discounting', 'risk', 'choice_dyn',
      'reinstatement', 'avoidance', 'timing', 'vigor', 'second_order', 'cond_inhib'],
    mpr: [],
    etbd: ['op_acq', 'op_ext', 'matching', 'punishment', 'rpasym', 'resurgence',
      'single_alt', 'magnitude', 'discounting', 'variability', 'choice_dyn', 'reinstatement', 'vigor'],
  },
  // notes[rowId|colId] shown on hover
  notes: {
    // Q-learning (lab repo)
    'matching|qlearning': 'q-learning-aos, verified: GML on concurrent VI VI (a ≈ 0.63, R² ≈ 0.999). Matching is a property of melioration (softmax), not maximization (greedy responds ~50/50).',
    'op_acq|qlearning': 'q-learning-aos: allocation rises from indifference toward the matching equilibrium as values are learned (run_acquisition_demo).',
    'op_ext|qlearning': 'q-learning-aos: target value decays and allocation falls back toward indifference. Caveat: gamma=0 myopic decay (the "unlearning" mechanism the field flags as phenomenologically wrong).',
    'choice_dyn|qlearning': 'q-learning-aos: reversal learning; allocation tracks the reversal after a lag (run_reversal_demo).',
    'resurgence|qlearning': 'q-learning-aos reproduces resurgence in a 3-phase design. Notable: the field has no dedicated RL model of resurgence (Resurgence-as-Choice is behavior-analytic), so this is closer to a field-first than a replication.',
    'rpasym|qlearning': 'Asymmetric +/- prediction-error scaling; distributional RL predicts diverse optimistic/pessimistic channels, confirmed in dopamine (Dabney et al., 2020, Nature).',
    'discounting|qlearning': 'Plain TD discounts exponentially; hyperbolic discounting is recovered only with a distribution of γ micro-agents (Kurth-Nelson & Redish, 2009). A recognized misfit, then a fix.',
    'spont|qlearning': 'Not reproduced by plain TD (unlearning cannot return a CR); recovered by latent-cause inference (Gershman, Blei & Niv, 2010).',
    'renewal|qlearning': 'ABA renewal needs state-classification / latent-cause RL; the clearest "plain TD fails" case (Redish et al., 2007).',
    'reinstatement|qlearning': 'Reinstatement of an extinguished response by unsignaled reinforcer exposure; latent-state RL (Redish et al., 2007; Gershman et al., 2010).',
    'avoidance|qlearning': 'Active avoidance / negative reinforcement via actor-critic RL, resolving two-factor theory (Maia, 2010).',
    'timing|qlearning': 'CR / interval-timing topography via TD with microstimuli (Ludvig, Sutton & Kehoe, 2008).',
    'vigor|qlearning': 'Free-operant response rate and bout-and-pause microstructure (Niv et al., 2007 average-reward vigor; Yamada & Kanemura, 2020).',
    'second_order|qlearning': 'Second-order conditioning reproduced by plain TD (Sutton & Barto, 1990).',
    'cond_inhib|qlearning': 'Conditioned inhibition via TD with a nonnegativity constraint (Sutton & Barto, 1990).',
    // MPR (lab repo)
    'single_alt|mpr': "mpr-aos: single VR/VI target rates conform to McDowell's generalized hyperbola (VR R²=1.00, VI R²=0.99) — Herrnstein's single-alternative hyperbola (manuscript, Figs 2 & 4).",
    'single_alt|integrated': 'Open for the integrated organism: it builds FR/VR/FI/VI rate signatures, not the Herrnstein single-alternative hyperbola (a deliberate scope choice).',
    'matching|mpr': "mpr-aos: concurrent VR/VI allocation fit by Baum's generalized matching law (R²=0.95/0.96), with undermatching (manuscript, Figs 6 & 8).",
    'choice_dyn|mpr': 'mpr-aos: preference tracks relative reinforcement via per-alternative coupling with a changeover delay; includes an MPR + Q-learning hybrid (manuscript, Figs 6-9).',
    'schedules|mpr': 'Open as an AO: our mpr-aos ran only the molar VR/VI rate functions, not the FI-scallop / FR-break-run microstructure, and no other MPR artificial organism exists.',
    // ETBD (literature review)
    'matching|etbd': 'Established for ETBD in the field: concurrent RI RI AOs fit the GML at pVAF 0.97-1.00 with undermatching emergent (McDowell, Caron, Kulubekova & Berg, 2008, JEAB). Our etbd-aos reproduces it (a ≈ 0.60).',
    'op_acq|etbd': 'Virtual organisms acquire responding on RI schedules from a random population (McDowell, 2004, JEAB).',
    'op_ext|etbd': 'Extinction by mutating behavior out of the reinforced class (Kulubekova & McDowell, 2008).',
    'punishment|etbd': 'Punishment as mutation out of the punished class; suppresses the punished alternative (McDowell & Klapes, 2019, JEAB).',
    'rpasym|etbd': 'Punishment efficacy is asymmetric by reinforcement context (McDowell & Klapes, 2019, JEAB).',
    'resurgence|etbd': 'AOs reproduce target-response recurrence when alternative reinforcement is downshifted (~86.7% vs ~87.5% in live animals; Falligant, Klapes & Hagopian, 2022).',
    'reinstatement|etbd': 'Response-dependent reinstatement of an extinguished response reproduced by ETBD AOs (McDowell group, 2025).',
    'single_alt|etbd': "Single RI schedules emergently produce Herrnstein's hyperbola (McDowell, 2004, JEAB).",
    'magnitude|etbd': 'Response rate is a joint function of reinforcement rate and magnitude (McDowell, 2021, JEAB).',
    'discounting|etbd': 'AOs produce hyperbolic delay-discounting curves matching pigeon, rat, and human data (Higginbotham et al., 2025, Perspectives on Behavior Science).',
    'variability|etbd': 'Variability scales with the mutation rate and reinforcement (Popa & McDowell, 2016, JEAB). Not variability reinforced as an operant.',
    'choice_dyn|etbd': 'AOs track local shifts in reinforcer ratios across successive reinforcers (Kulubekova & McDowell, 2013, JEAB).',
    'vigor|etbd': 'Log-survivor inter-response-time bout structure under interval schedules (Kulubekova & McDowell, 2008).',
    'schedules|etbd': 'Left open for ETBD: it uses RI/RR analogs and reproduces rates and concurrent preference, but not the FI-scallop / FR-break-and-run molecular signatures.',
    // Integrated (molecular-dynamics repo)
    'magnitude|integrated': 'Demonstrated as the amount term of the concatenated matching law (allocation tracks relative amount, a ≈ 0.97; emergent). A standalone single-operant magnitude effect remains a gap.',
    'discounting|integrated': 'Demonstrated as the delay term of the concatenated matching law (hyperbolic). The smaller-sooner vs larger-later self-control procedure remains a gap.',
    'prob_disc|integrated': 'Probability discounting as the probability term of the concatenated matching law (emergent; exp013).',
    'demand|integrated': 'Demand / unit price: consumption falls as response cost rises (emergent; exp016).',
    'timing|integrated': 'Interval timing via a pluggable SET/BeT/LeT module, plus temporal stimulus control / food anticipation (exp017, exp064).',
    'foraging|integrated': 'Optimal foraging / patch-leaving (marginal value theorem) and the Charnov functional response (exp020, exp021; emergent).',
    'vigor|integrated': 'Free-operant response rates and the post-reinforcement pause (FR > VR) under schedules (exp018).',
    'resurgence|integrated': 'Resurgence as model mimicry; part of the resurgence study (four processes, one phenomenon).',
    'risk|integrated': 'Risk-sensitive foraging follows from the energy-budget rule (Caraco, 1980; Stephens & Krebs, 1986).',
  },
};
