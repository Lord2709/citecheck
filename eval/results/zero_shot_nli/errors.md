# Error analysis: `zero_shot_nli` (dev)

116 errors out of 300 claims.

| bucket | count | meaning |
|---|---|---|
| FALSE_SUPPORT | 15 | Predicted SUPPORT but gold is not SUPPORT (most harmful: false confidence) |
| WRONG_DIRECTION | 23 | SUPPORT <-> CONTRADICT flipped |
| RETRIEVAL_MISS | 15 | Gold paper was not among the k papers judged (retrieval failure, not the verifier's fault) |
| MISSED_BY_VERIFIER | 41 | Gold paper was retrieved but we answered NOT ENOUGH EVIDENCE (abstained or classified neutral) |
| FALSE_CONTRADICT | 22 | Predicted CONTRADICT but gold is NEI |

## FALSE_SUPPORT
Predicted SUPPORT but gold is not SUPPORT (most harmful: false confidence)

**#914** gold `NEI` -> pred `SUPPORT` (conf 0.99)  
claim: PPAR-RXRs can be activated by PPAR ligands.  
gold paper(s): (none, NEI)  
top retrieved: Pharmacological correction of a defect in PPARγ signaling ameliorates disease severity in Cftr-deficient mice  
sentences the verifier saw: Here we show that colonic epithelial cells and whole lung tissue from Cftr-deficient mice show a defect in peroxisome proliferator-activated receptor-gamma (PPAR-gamma, encoded by Pparg) function that contributes to a pathological program of gene expression. | Lipidomic analysis of colonic epithelial cells suggests that this defect results in part from reduced amounts of the endogenous PPAR-gamma ligand 15-keto-prostaglandin E(2) (15-keto-PGE(2)). | Treatment of Cftr-deficient mice with the synthetic PPAR-gamma ligand rosiglitazone partially normalizes the altered gene expression pattern associated with Cftr deficiency and reduces disease severity.  
gold rationale: -  
your category: _______

**#1316** gold `NEI` -> pred `SUPPORT` (conf 0.97)  
claim: Transferred UCB T cells acquire a memory-like phenotype in recipients.  
gold paper(s): (none, NEI)  
top retrieved: Serious infections after unrelated donor transplantation in 136 children: impact of stem cell source.  
sentences the verifier saw: However, it remains unclear whether there are CD4(+) memory T cells committed to the Tfh cell lineage after antigen clearance. | By using adoptive transfer of antigen-specific memory CD4(+) T cell subpopulations in the lymphocytic choriomeningitis virus infection model, we found that there are distinct memory CD4(+) T cell populations with commitment to either Tfh- or Th1-cell lineages. | Our findings indicate that CD4(+) memory T cells "remember" their previous effector lineage after antigen clearance, being poised to reacquire their lineage-specific effector functions upon antigen reencounter.  
gold rationale: -  
your category: _______

**#554** gold `NEI` -> pred `SUPPORT` (conf 0.96)  
claim: Immune complex triggered cell death leads to extracellular release of neutrophil protein HMGB1.  
gold paper(s): (none, NEI)  
top retrieved: Neutrophil extracellular traps: Is immunity the second function of chromatin?  
sentences the verifier saw: Systemic lupus erythematosus (SLE) is a systemic autoimmune disease characterized by a breakdown of tolerance to nuclear antigens and the development of immune complexes. | Here, we show that mature SLE neutrophils are primed in vivo by type I IFN and die upon exposure to SLE-derived anti-ribonucleoprotein antibodies, releasing neutrophil extracellular traps (NETs). | SLE NETs contain DNA as well as large amounts of LL37 and HMGB1, neutrophil proteins that facilitate the uptake and recognition of mammalian DNA by plasmacytoid DCs (pDCs).  
gold rationale: -  
your category: _______

**#300** gold `NEI` -> pred `SUPPORT` (conf 0.95)  
claim: Cytosolic proteins bind to iron-responsive elements on mRNAs coding for DMT1. Cytosolic proteins bind to iron-responsive elements on mRNAs coding for proteins involved in iron uptake.  
gold paper(s): (none, NEI)  
top retrieved: Multiple RNA surveillance pathways limit aberrant expression of iron uptake mRNAs and prevent iron toxicity in S. cerevisiae.  
sentences the verifier saw: Tight regulation of the expression of mRNAs encoding iron uptake proteins is essential to control iron homeostasis and avoid intracellular iron toxicity. | We show that many mRNAs encoding iron uptake or iron mobilization proteins are expressed in iron-replete conditions in the absence of the S. cerevisiae RNase III ortholog Rnt1p or of the nuclear exosome component Rrp6p. | These results show that RNA surveillance through multiple ribonucleolytic pathways plays a role in iron homeostasis in yeast to avoid the potentially toxic effects of the expression of the iron starvation response in iron-replete conditions.  
gold rationale: -  
your category: _______

**#1099** gold `NEI` -> pred `SUPPORT` (conf 0.94)  
claim: Statins decrease blood cholesterol.  
gold paper(s): (none, NEI)  
top retrieved: Pleiotropic effects of statins.  
sentences the verifier saw: Statins are potent inhibitors of cholesterol biosynthesis. | However, the overall benefits observed with statins appear to be greater than what might be expected from changes in lipid levels alone, suggesting effects beyond cholesterol lowering. | Indeed, recent studies indicate that some of the cholesterol-independent or "pleiotropic" effects of statins involve improving endothelial function, enhancing the stability of atherosclerotic plaques, decreasing oxidative stress and inflammation, and inhibiting the thrombogenic response.  
gold rationale: -  
your category: _______

**#1213** gold `NEI` -> pred `SUPPORT` (conf 0.93)  
claim: The deregulated and prolonged activation of monocytes has deleterious effects in inflammatory diseases.  
gold paper(s): (none, NEI)  
top retrieved: CCR2 and CXCR4 regulate peripheral blood monocyte pharmacodynamics and link to efficacy in experimental autoimmune encephalomyelitis  
sentences the verifier saw: BACKGROUND CCR2 plays a key role in regulating monocyte trafficking to sites of inflammation and therefore has been the focus of much interest as a target for inflammatory disease.   
 | METHODS Here we examined the effects of CCR2 blockade with a potent small molecule antagonist to determine the pharmacodynamic consequences on the peripheral blood monocyte compartment in the context of acute and chronic inflammatory processes.   
 | Finally, we show that the pharmacodynamic changes due to CCR2 antagonism were apparent after chronic dosing in mouse experimental autoimmune encephalomyelitis, a model in which CCR2 blockade demonstrated a dramatic reduction in disease severity, manifest in a reduced accumulation of monocytes and other cells in the CNS.   
  
gold rationale: -  
your category: _______

**#1200** gold `NEI` -> pred `SUPPORT` (conf 0.92)  
claim: The binding orientation of the ML-SA1 activator at hTRPML2 is different from the binding orientation of the ML-SA1 activator at hTRPML1.  
gold paper(s): (none, NEI)  
top retrieved: Differential activation of DNA-PK based on DNA strand orientation and sequence bias  
sentences the verifier saw: A series of duplex DNA substrates with site-specific cisplatin–DNA adducts placed in three different orientations on the duplex DNA were prepared. | Terminal biotin modification and streptavidin (SA) blocking was employed to direct DNA-PK binding to the unblocked termini with a specific DNA strand orientation and cisplatin–DNA adduct position. | DNA-PK kinase activity was measured and the results reveal that DNA strand orientation and sequence bias dramatically influence kinase activation, only a portion of which could be attributed to Ku-DNA binding activity.  
gold rationale: -  
your category: _______

**#268** gold `NEI` -> pred `SUPPORT` (conf 0.90)  
claim: Cold exposure increases BAT recruitment.  
gold paper(s): (none, NEI)  
top retrieved: Sestrin2 inhibits uncoupling protein 1 expression through suppressing reactive oxygen species.  
sentences the verifier saw: Uncoupling protein 1 (Ucp1), which is localized in the mitochondrial inner membrane of mammalian brown adipose tissue (BAT), generates heat by uncoupling oxidative phosphorylation. | Upon cold exposure or nutritional abundance, sympathetic neurons stimulate BAT to express Ucp1 to induce energy dissipation and thermogenesis. | Transgenic overexpression of Sestrin2 in adipose tissues inhibited both basal and cold-induced Ucp1 expression in interscapular BAT, culminating in decreased thermogenesis and increased fat accumulation.  
gold rationale: -  
your category: _______

**#834** gold `NEI` -> pred `SUPPORT` (conf 0.87)  
claim: NOX2-independent pathways can generate peroxynitrite by reacting with nitrogen intermediates.  
gold paper(s): (none, NEI)  
top retrieved: Lung Carcinogenesis by Diesel Exhaust Particles and the Carcinogenic Mechanism Via Active Oxygens.  
sentences the verifier saw: Therefore, we measured the end product of NO, nitrate plus nitrite (nitrogen oxide), and examined the relationship between the degree of hypertension and plasma nitrate plus nitrite levels in patients with essential hypertension. | The plasma nitrogen oxide concentration showed significant inverse correlations with both systolic and diastolic blood pressures. | The basal concentration of nitrogen oxide in the plasma was reduced, at least in the peripheral circulation, in individuals with essential hypertension.  
gold rationale: -  
your category: _______

**#956** gold `NEI` -> pred `SUPPORT` (conf 0.86)  
claim: Pleiotropic coupling of GLP-1R to intracellular effectors promotes distinct profiles of cellular signaling.  
gold paper(s): (none, NEI)  
top retrieved: Differential Requirement of the Extracellular Domain in Activation of Class B G Protein-coupled Receptors.  
sentences the verifier saw: G protein-coupled receptors (GPCRs) from the secretin-like (class B) family are key players in hormonal homeostasis and are important drug targets for the treatment of metabolic disorders and neuronal diseases. | In one group, represented by corticotrophin-releasing factor receptor 1 (CRF1R), parathyroid hormone receptor (PTH1R), and pituitary adenylate cyclase activating polypeptide type 1 receptor (PAC1R), the ECD requirement for high affinity hormone binding can be bypassed by induced proximity and mass action effects, whereas in the other group, represented by glucagon receptor (GCGR) and glucagon-like peptide-1 receptor (GLP-1R), the ECD is required for signaling even when the hormone is covalently linked to the TMD. | Furthermore, the activation of GLP-1R by small molecules that interact with the intracellular side of the receptor is dependent on the presence of its ECD, suggesting a direct role of the ECD in GLP-1R activation.  
gold rationale: -  
your category: _______

**#560** gold `NEI` -> pred `SUPPORT` (conf 0.85)  
claim: Immune responses result in the development of inflammatory Th17 cells and anti-inflammatory iTregs.  
gold paper(s): (none, NEI)  
top retrieved: Proinflammatory cytokines underlying the inflammation of Crohn's disease.  
sentences the verifier saw: CD4 T cells play critical roles in mediating adaptive immunity to a variety of pathogens. | They are also involved in autoimmunity, asthma, and allergic responses as well as in tumor immunity. | During TCR activation in a particular cytokine milieu, naive CD4 T cells may differentiate into one of several lineages of T helper (Th) cells, including Th1, Th2, Th17, and iTreg, as defined by their pattern of cytokine production and function.  
gold rationale: -  
your category: _______

**#913** gold `NEI` -> pred `SUPPORT` (conf 0.84)  
claim: PPAR-RXRs are inhibited by PPAR ligands.  
gold paper(s): (none, NEI)  
top retrieved: The Role of PPARγ in Advanced Glycation End Products-Induced Inflammatory Response in Human Chondrocytes  
sentences the verifier saw: RESULTS AGEs could enhance the expression of IL-1, TNF-α, and MMP-13, but the level of PPARγ was decreased in a time- and dose-dependent manner, which was inhibited by anti-RAGE, SB203580 (P38 MAPK specific inhibitor) and SP600125 (a selective inhibitor of JNK). | PPARγ agonist pioglitazone could inhibit the effects of AGEs-induced inflammatory response and PPARγ down-regulation. | In human chondrocytes, AGEs could induce cytosol IκBα degradation and increase the level of nuclear NF-κB p65, which was inhibited by PPARγ agonist pioglitazone.   
  
gold rationale: -  
your category: _______

**#507** gold `NEI` -> pred `SUPPORT` (conf 0.80)  
claim: Helminths interfere with immune system control of macrophages activated by IL-4 favor Mycobacterium tuberculosis replication.  
gold paper(s): (none, NEI)  
top retrieved: Preexisting helminth infection induces inhibition of innate pulmonary anti-tuberculosis defense by engaging the IL-4 receptor pathway  
sentences the verifier saw: The T helper 1 (Th1) cell cytokine IFN-gamma induces autophagy in macrophages to eliminate Mycobacterium tuberculosis. | Here, we report that Th2 cytokines affect autophagy in macrophages and their ability to control intracellular M. tuberculosis. | IL-4 and IL-13 abrogated autophagy and autophagy-mediated killing of intracellular mycobacteria in murine and human macrophages.  
gold rationale: -  
your category: _______

**#350** gold `NEI` -> pred `SUPPORT` (conf 0.77)  
claim: Discrimination between the initiator and elongation tRNAs depends on the translation initiation factor IF3.  
gold paper(s): (none, NEI)  
top retrieved: Large-Scale Movements of IF3 and tRNA during Bacterial Translation Initiation  
sentences the verifier saw: In bacterial translational initiation, three initiation factors (IFs 1-3) enable the selection of initiator tRNA and the start codon in the P site of the 30S ribosomal subunit. | Here, we report 11 single-particle cryo-electron microscopy (cryoEM) reconstructions of the complex of bacterial 30S subunit with initiator tRNA, mRNA, and IFs 1-3, representing different steps along the initiation pathway. | IF3 and tRNA undergo large conformational changes to facilitate the accommodation of the formylmethionyl-tRNA (fMet-tRNA(fMet)) into the P site for start codon recognition.  
gold rationale: -  
your category: _______

**#312** gold `NEI` -> pred `SUPPORT` (conf 0.69)  
claim: De novo assembly of sequence data has more specific contigs than unassembled sequence data.  
gold paper(s): (none, NEI)  
top retrieved: Effects of GC Bias in Next-Generation-Sequencing Data on De Novo Genome Assembly  
sentences the verifier saw: Here we present the Trinity method for de novo assembly of full-length transcripts and evaluate it on samples from fission yeast, mouse and whitefly, whose reference genome is not yet available. | By efficiently constructing and analyzing sets of de Bruijn graphs, Trinity fully reconstructs a large fraction of transcripts, including alternatively spliced isoforms and transcripts from recently duplicated genes. | Compared with other de novo transcriptome assemblers, Trinity recovers more full-length transcripts across a broad range of expression levels, with a sensitivity similar to methods that rely on genome alignments.  
gold rationale: -  
your category: _______


## WRONG_DIRECTION
SUPPORT <-> CONTRADICT flipped

**#100** gold `SUPPORT` -> pred `CONTRADICT` (conf 1.00)  
claim: All hematopoietic stem cells segregate their chromosomes randomly.  
gold paper(s): Haematopoietic stem cells do not asymmetrically segregate chromosomes or retain BrdU  
top retrieved: Haematopoietic stem cells do not asymmetrically segregate chromosomes or retain BrdU  
sentences the verifier saw: In semisyngeneic heterotopic bone marrow transplants the donor or recipient origin of cells of osteogenic and hematopoietic tissues was identified by chromosome markers (T6) and by reverse transplantation into the initial donor line. | This is true for both the proliferating pool and the stem cells of hematopoietic tissue. | A discussion is presented of the interrelationship between determinated osteogenic precursor cells (preosteoblasts) and hematopoietic stem cells (or their descendants) in which osteogenesis is inducible.  
gold rationale: Sequential administration of 5-chloro-2-deoxyuridine and 5-iodo-2-deoxyuridine indicated that all HSCs segregate their chromosomes randomly.  
your category: _______

**#208** gold `SUPPORT` -> pred `CONTRADICT` (conf 1.00)  
claim: CHEK2 is not associated with breast cancer.  
gold paper(s): Linkage Disequilibrium Mapping of       CHEK2: Common Variation and Breast Cancer Risk       
top retrieved: Linkage Disequilibrium Mapping of       CHEK2: Common Variation and Breast Cancer Risk       
sentences the verifier saw: Insulin resistance, hyperinsulinemia, and changes in the signaling of growth hormones and steroid hormones associated with diabetes may affect the risk of breast cancer. | We reviewed epidemiologic studies of the association between type 2 diabetes and risk of breast cancer and the available evidence on the role of hormonal mediators of an association between diabetes and breast cancer. | The combined evidence supports a modest association between type 2 diabetes and the risk of breast cancer, which appears to be more consistent among postmenopausal than among premenopausal women.  
gold rationale: We genotyped these six tagSNPs in 1,577 postmenopausal breast cancer cases and 1,513 population controls, but found no convincing association between any common CHEK2 haplotype and breast cancer risk.  
your category: _______

**#501** gold `SUPPORT` -> pred `CONTRADICT` (conf 0.99)  
claim: Headaches are not correlated with cognitive impairment.  
gold paper(s): Headache, migraine, and structural brain lesions and function: population based Epidemiology of Vascular Ageing-MRI study  
top retrieved: Headache, migraine, and structural brain lesions and function: population based Epidemiology of Vascular Ageing-MRI study  
sentences the verifier saw: Forty-one recurrent tension headache sufferers were randomly assigned to either cognitive-behavioral therapy (administered in a primarily home-based treatment protocol) or to amitriptyline therapy (with dosage individualized at 25, 50, or 75 mg/day). | Cognitive-behavioral therapy and amitriptyline each yielded clinically significant improvements in headache activity, both when improvement was assessed with patient daily recordings (56% and 27% reduction in headache index, respectively), and when improvement was assessed with neurologist ratings of clinical improvement (94% and 69% of patients rated at least moderately improved, respectively). | In instances where differences in treatment effectiveness were observed (headache index, somatic complaints, perceptions of control of headache activity), cognitive-behavioral therapy yielded somewhat more positive outcomes than did amitriptyline.  
gold rationale: Evidence was lacking for cognitive impairment for any headache type with or without brain lesions.   
  
your category: _______

**#808** gold `SUPPORT` -> pred `CONTRADICT` (conf 0.99)  
claim: Most termination events in Okazaki fragments are sequence specific.  
gold paper(s): Quantitative, genome-wide analysis of eukaryotic replication initiation and termination.  
top retrieved: Quantitative, genome-wide analysis of eukaryotic replication initiation and termination.  
sentences the verifier saw: Many fundamental aspects of DNA replication, such as the exact locations where DNA synthesis is initiated and terminated, how frequently origins are used, and how fork progression is influenced by transcription, are poorly understood. | Via the deep sequencing of Okazaki fragments, we comprehensively document replication fork directionality throughout the S. cerevisiae genome, which permits the systematic analysis of initiation, origin efficiency, fork progression, and termination. | Using a strain in which late origins can be induced to fire early, we show that replication termination is a largely passive phenomenon that does not rely on cis-acting sequences or replication fork pausing.  
gold rationale: Via the deep sequencing of Okazaki fragments, we comprehensively document replication fork directionality throughout the S. cerevisiae genome, which permits the systematic analysis of initiation, origin efficiency, fork progression, and termination.  
your category: _______

**#1385** gold `SUPPORT` -> pred `CONTRADICT` (conf 0.99)  
claim: cSMAC formation enhances weak ligand signalling.  
gold paper(s): The stimulatory potency of T cell antigens is influenced by the formation of the immunological synapse.  
top retrieved: The stimulatory potency of T cell antigens is influenced by the formation of the immunological synapse.  
sentences the verifier saw: We describe results showing that a peptide exhibiting many hallmarks of a weak agonist stimulates T cells to proliferate more than the wild-type agonist ligand. | An in silico approach suggested that the inability to form the central supramolecular activation cluster (cSMAC) could underlie the increased proliferation. | This conclusion was supported by experiments that showed that enhancing cSMAC formation reduced stimulatory capacity of the weak peptide.  
gold rationale: This conclusion was supported by experiments that showed that enhancing cSMAC formation reduced stimulatory capacity of the weak peptide.  
your category: _______

**#218** gold `SUPPORT` -> pred `CONTRADICT` (conf 0.99)  
claim: CX3CR1 on the Th2 cells promotes airway inflammation.  
gold paper(s): CX3CR1 is required for airway inflammation by promoting T helper cell survival and maintenance in inflamed lung  
top retrieved: CX3CR1 is required for airway inflammation by promoting T helper cell survival and maintenance in inflamed lung  
sentences the verifier saw: In people with asthma, a fraction of CD4(+) T cells express the CX3CL1 receptor, CX3CR1, and CX3CL1 expression is increased in airway smooth muscle, lung endothelium and epithelium upon allergen challenge. | Transfer of WT CD4(+) T cells into CX3CR1-deficient mice restored the cardinal features of asthma, and CX3CR1-blocking reagents prevented airway inflammation in CX3CR1-deficient recipients injected with WT T(H)2 cells. | CX3CR1-induced survival was also observed for T(H)1 cells upon airway inflammation but not under homeostatic conditions or upon peripheral inflammation.  
gold rationale: Here we found that untreated CX3CR1-deficient mice or wild-type (WT) mice treated with CX3CR1-blocking reagents show reduced lung disease upon allergen sensitization and challenge. | Transfer of WT CD4(+) T cells into CX3CR1-deficient mice restored the cardinal features of asthma, and CX3CR1-blocking reagents prevented airway inflammation in CX3CR1-deficient recipients injected with WT T(H)2 cells. | CX3CR1-induced survival was also observed for T(H)1 cells upon airway inflammation but not under homeostatic conditions or upon peripheral inflammation.  
your category: _______

**#742** gold `SUPPORT` -> pred `CONTRADICT` (conf 0.98)  
claim: Macrolides have no protective effect against myocardial infarction.  
gold paper(s): Antibiotics and risk of subsequent first-time acute myocardial infarction.  
top retrieved: Antibiotics and risk of subsequent first-time acute myocardial infarction.  
sentences the verifier saw: CONTEXT Increasing evidence supports the hypothesis of a causal association between certain bacterial infections and increased risk of developing acute myocardial infarction. | If such a causal association exists, subjects who used antibiotics active against the bacteria, regardless of indication, might be at lower risk of developing acute myocardial infarction than nonusers.   
 | OBJECTIVE To determine whether previous use of antibiotics decreases the risk of developing a first-time acute myocardial infarction.   
  
gold rationale: No effect was found for previous use of macrolides (primarily erythromycin), sulfonamides, penicillins, or cephalosporins.   
  
your category: _______

**#49** gold `SUPPORT` -> pred `CONTRADICT` (conf 0.98)  
claim: ADAR1 binds to Dicer to cleave pre-miRNA.  
gold paper(s): ADAR1 Forms a Complex with Dicer to Promote MicroRNA Processing and RNA-Induced Gene Silencing  
top retrieved: ADAR1 Forms a Complex with Dicer to Promote MicroRNA Processing and RNA-Induced Gene Silencing  
sentences the verifier saw: Drosophila Dicer-2 generates small interfering RNAs (siRNAs) from long double-stranded RNA (dsRNA), whereas Dicer-1 produces microRNAs (miRNAs) from pre-miRNA. | We find that purified Dicer-2 can efficiently cleave pre-miRNA, but that inorganic phosphate and the Dicer-2 partner protein R2D2 inhibit pre-miRNA cleavage. | We show that Dicer-2 is a dsRNA-stimulated ATPase that hydrolyzes ATP to ADP; ATP hydrolysis is required for Dicer-2 to process long dsRNA, but not pre-miRNA.  
gold rationale: In this study, we investigated the interaction of the RNA editing mechanism with the RNA interference (RNAi) machinery and found that ADAR1 forms a complex with Dicer through direct protein-protein interaction. | Most importantly, ADAR1 increases the maximum rate (Vmax) of pre-microRNA (miRNA) cleavage by Dicer and facilitates loading of miRNA onto RNA-induced silencing complexes, identifying a new role of ADAR1 in miRNA processing and RNAi mechanisms.  
your category: _______

**#1089** gold `SUPPORT` -> pred `CONTRADICT` (conf 0.98)  
claim: Smc5/6 engagment drives the activation of SUMO E3 ligase Mms21 by ATP-dependent remolding.  
gold paper(s): ATPase-Dependent Control of the Mms21 SUMO Ligase during DNA Repair  
top retrieved: ATPase-Dependent Control of the Mms21 SUMO Ligase during DNA Repair  
sentences the verifier saw: The Mms21 SUMO ligase docks to the arm region of the Smc5 protein in the Smc5/6 complex; together, they cooperate during recombinational DNA repair. | Here we show that the SUMO ligase and the chromosome disjunction functions of Mms21 depend on its docking to an intact and active Smc5/6 complex, indicating that the Smc5/6-Mms21 complex operates as a large SUMO ligase in vivo. | In spite of the physical distance separating the E3 and the nucleotide-binding domains in Smc5/6, Mms21-dependent sumoylation requires binding of ATP to Smc5, a step that is part of the ligase mechanism that assists Ubc9 function.  
gold rationale: In accordance, scanning force microscopy of the Smc5-Mms21 heterodimer shows that the molecule is physically remodeled in an ATP-dependent manner.  
your category: _______

**#279** gold `SUPPORT` -> pred `CONTRADICT` (conf 0.97)  
claim: Commelina yellow mottle virus' (ComYMV) genome consists of 7489 baise pairs.  
gold paper(s): Properties of Commelina yellow mottle virus's complete DNA sequence, genomic discontinuities and transcript suggest that it is a pararetrovirus.  
top retrieved: Properties of Commelina yellow mottle virus's complete DNA sequence, genomic discontinuities and transcript suggest that it is a pararetrovirus.  
sentences the verifier saw: We have characterized the viral transcript and determined the complete sequence of the genome of Commelina mellow mottle virus (CoYMV), a member of this group. | Analysis of the genome sequence indicates that the genome is 7489 bp in size and that the transcribed strand contains three open reading frames capable of encoding proteins of 23, 15 and 216 kd. | We have demonstrated that a construct containing 1.3 CoYMV genomes is infective when introduced into Commelina diffusa, the host for CoYMV, using Agrobacterium-mediated infection.  
gold rationale: Analysis of the genome sequence indicates that the genome is 7489 bp in size and that the transcribed strand contains three open reading frames capable of encoding proteins of 23, 15 and 216 kd.  
your category: _______

**#183** gold `CONTRADICT` -> pred `SUPPORT` (conf 0.96)  
claim: Bone marrow cells contribute to adult macrophage compartments.  
gold paper(s): Tissue-resident macrophages self-maintain locally throughout adult life with minimal contribution from circulating monocytes.  
top retrieved: Effects of repeated social stress on leukocyte distribution in bone marrow, peripheral blood and spleen  
sentences the verifier saw: Despite accumulating evidence suggesting local self-maintenance of tissue macrophages in the steady state, the dogma remains that tissue macrophages derive from monocytes. | Using parabiosis and fate-mapping approaches, we confirmed that monocytes do not show significant contribution to tissue macrophages in the steady state. | We also found that after bone marrow transplantation, host macrophages retained the capacity to expand when the development of donor macrophages was compromised.  
gold rationale: We also found that after bone marrow transplantation, host macrophages retained the capacity to expand when the development of donor macrophages was compromised.  
your category: _______

**#759** gold `CONTRADICT` -> pred `SUPPORT` (conf 0.96)  
claim: Mathematical models predict that using Artemisinin-based combination therapy over nongametocytocidal drugs have a dramatic impact in reducing malaria transmission.  
gold paper(s): Modelling the Impact of Artemisinin Combination Therapy and Long-Acting Treatments on Malaria Transmission Intensity  
top retrieved: Optimising Strategies for Plasmodium falciparum Malaria Elimination in Cambodia: Primaquine, Mass Drug Administration and Artemisinin Resistance  
sentences the verifier saw: A recent field study in an area of low seasonal transmission in South West Cambodia demonstrated dramatic reductions in malaria parasite prevalence following both mass drug administration (MDA) and high treatment coverage of symptomatic patients with artemisinin-piperaquine plus primaquine. | METHOD AND FINDINGS A mathematical model fitted to the trial results was used to assess the effects of the various components of these interventions, design optimal elimination strategies, and explore their interactions with artemisinin resistance, which has recently been discovered in Western Cambodia. | CONCLUSIONS The key messages of these modelling results for policy makers were: high coverage with ACT treatment can produce a long-term reduction in malaria whereas the impact of MDA is generally only short-term; primaquine enhances the effect of ACT in eliminating malaria and reduces the increase in proportion of artemisinin resistant infections; parasite prevalence is a better surveillance measure for elimination programmes than numbers of symptomatic cases; combinations of interventions are most effective and sustained efforts are crucial for successful elimination.  
gold rationale: An efficacious antimalarial regimen with no specific gametocytocidal properties but a long prophylactic time was estimated to be more effective at reducing transmission than a short-acting ACT in the highest-transmission setting.   
  
your category: _______

**#1336** gold `CONTRADICT` -> pred `SUPPORT` (conf 0.96)  
claim: UCB T cells reduce TCR diversity after transplantation.  
gold paper(s): Quantitative assessment of T-cell repertoire recovery after hematopoietic stem cell transplantation  
top retrieved: Quantitative assessment of T-cell repertoire recovery after hematopoietic stem cell transplantation  
sentences the verifier saw: Delayed T cell recovery and restricted T cell receptor (TCR) diversity after allogeneic hematopoietic stem cell transplantation (allo-HSCT) are associated with increased risks of infection and cancer relapse. | Technical challenges have limited faithful measurement of TCR diversity after allo-HSCT. | After 6 months, cord blood-graft recipients approximated the TCR diversity of healthy individuals, whereas recipients of T cell-depleted peripheral-blood stem cell grafts had 28-fold and 14-fold lower CD4(+) and CD8(+) T cell diversities, respectively.  
gold rationale: After 6 months, cord blood-graft recipients approximated the TCR diversity of healthy individuals, whereas recipients of T cell-depleted peripheral-blood stem cell grafts had 28-fold and 14-fold lower CD4(+) and CD8(+) T cell diversities, respectively.  
your category: _______

**#1163** gold `SUPPORT` -> pred `CONTRADICT` (conf 0.95)  
claim: The DdrB protein from Deinococcus radiodurans is an alternative SSB.  
gold paper(s): The structure of DdrB from Deinococcus: a new fold for single-stranded DNA binding proteins  
top retrieved: The structure of DdrB from Deinococcus: a new fold for single-stranded DNA binding proteins  
sentences the verifier saw: Here, we report the 2.8 A structure of DdrB, a single-stranded DNA (ssDNA) binding protein unique to Deinococcus spp. | Unexpectedly, the crystal structure reveals that DdrB comprises a novel fold that is structurally and topologically distinct from all other single-stranded binding (SSB) proteins characterized to date. | The need for a unique ssDNA binding function in response to severe damage, suggests a distinct role for DdrB which may encompass not only standard SSB protein function in protection of ssDNA, but also more specialized roles in protein recruitment or DNA architecture maintenance.  
gold rationale: Unexpectedly, the crystal structure reveals that DdrB comprises a novel fold that is structurally and topologically distinct from all other single-stranded binding (SSB) proteins characterized to date.  
your category: _______

**#593** gold `SUPPORT` -> pred `CONTRADICT` (conf 0.95)  
claim: Incidence of heart failure decreased by 10% in women since 1979.  
gold paper(s): Trends in heart failure incidence and survival in a community-based population.  
top retrieved: Trends in heart failure incidence and survival in a community-based population.  
sentences the verifier saw: Patients were 4537 Olmsted County residents (57% women; mean [SD] age, 74 [14] years) with a diagnosis of heart failure between 1979 and 2000. | RESULTS The incidence of heart failure was higher among men (378/100 000 persons; 95% confidence interval [CI], 361-395 for men; 289/100 000 persons; 95% CI, 277-300 for women) and did not change over time among men or women. | Survival after heart failure diagnosis was worse among men than women (relative risk, 1.33; 95% CI, 1.24-1.43) but overall improved over time (5-year age-adjusted survival, 43% in 1979-1984 vs 52% in 1996-2000, P<.001).  
gold rationale: RESULTS The incidence of heart failure was higher among men (378/100 000 persons; 95% confidence interval [CI], 361-395 for men; 289/100 000 persons; 95% CI, 277-300 for women) and did not change over time among men or women.  
your category: _______


## RETRIEVAL_MISS
Gold paper was not among the k papers judged (retrieval failure, not the verifier's fault)

**#728** gold `CONTRADICT` -> pred `NEI` (conf 0.99)  
claim: Ly6C hi monocytes have a lower inflammatory capacity than Ly6C lo monocytes.  
gold paper(s): Subpopulations of mouse blood monocytes differ in maturation stage and inflammatory response.  
top retrieved: Origin and functions of tissue macrophages.  
sentences the verifier saw: Recently, it has become evident that most adult tissue macrophages originate during embryonic development and not from circulating monocytes. | This new understanding also prompts reconsideration of the function of circulating monocytes. | Classical Ly6c(hi) monocytes patrol the extravascular space in resting organs, and Ly6c(lo) nonclassical monocytes patrol the vasculature.  
gold rationale: Under inflammatory conditions elicited either by acute infection with Listeria monocytogenes or chronic infection with Leishmania major, there was a significant increase in immature Ly-6C(high) monocytes, resembling the inflammatory left shift of granulocytes. | In addition, acute peritoneal inflammation recruited preferentially Ly-6C(med-high) monocytes.  
your category: _______

**#540** gold `SUPPORT` -> pred `NEI` (conf 0.99)  
claim: Hypothalamic glutamate neurotransmission is crucial to energy balance.  
gold paper(s): Synaptic glutamate release by ventromedial hypothalamic neurons is part of the neurocircuitry that prevents hypoglycemia.  
top retrieved: Leptin regulates glutamate and glucose transporters in hypothalamic astrocytes.  
sentences the verifier saw: Glial cells perform critical functions that alter the metabolism and activity of neurons, and there is increasing interest in their role in appetite and energy balance. | We found that basal and glucose-stimulated electrical activity of hypothalamic proopiomelanocortin (POMC) neurons in mice were altered in the offspring of mothers fed a high-fat diet. | These results demonstrate that whole-organism metabolism alters hypothalamic glial cell activity and suggest that these cells play an important role in the pathology of obesity.  
gold rationale: These mice have hypoglycemia during fasting secondary to impaired fasting-induced increases in the glucose-raising pancreatic hormone glucagon and impaired induction in liver of mRNAs encoding PGC-1alpha and the gluconeogenic enzymes PEPCK and G6Pase.  
your category: _______

**#598** gold `CONTRADICT` -> pred `NEI` (conf 0.98)  
claim: Incidence rates of cervical cancer have increased due to nationwide screening programs based primarily on cytology to detect uterine cervical cancer.  
gold paper(s): Mass screening programmes and trends in cervical cancer in Finland and the Netherlands.  
top retrieved: The effect of mass screening on incidence and mortality of squamous and adenocarcinoma of cervix uteri.  
sentences the verifier saw: OBJECTIVE To describe the efficacy of the Finnish mass screening program for cervical squamous carcinoma and adenocarcinoma, as reflected by changes of incidence and mortality rate.   
 | METHODS Cervical cancer incidence and mortality data were obtained from the Finnish Cancer Registry. | The nationwide mass screening program in Finland was started in the mid-1960s.  
gold rationale: Incidence and mortality rates have declined more in Finland. | The decline in mortality in Finland seems to be almost completely related to the screening programme whereas in the Netherlands it was initially considered to be a natural decline.  
your category: _______

**#1020** gold `SUPPORT` -> pred `NEI` (conf 0.97)  
claim: Rapid up-regulation and higher basal expression of interferon-induced genes increase survival of granule cell neurons that are infected by West Nile virus.  
gold paper(s): Differential innate immune response programs in neuronal subtypes determine susceptibility to infection in the brain by positive stranded RNA viruses  
top retrieved: Beta interferon controls West Nile virus infection and pathogenesis in mice.  
sentences the verifier saw: Studies with mice lacking the common plasma membrane receptor for type I interferon (IFN-αβR(-)(/)(-)) have revealed that IFN signaling restricts tropism, dissemination, and lethality after infection with West Nile virus (WNV) or several other pathogenic viruses. | Consistent with a direct role for IFN-β in control of WNV replication, viral titers in ex vivo cultures of macrophages, dendritic cells, fibroblasts, and cerebellar granule cell neurons, but not cortical neurons, from IFN-β(-)(/)(-) mice were greater than in wild-type cells. | Although detailed immunological analysis revealed no major deficits in the quality or quantity of WNV-specific antibodies or CD8(+) T cells, we observed an altered CD4(+) CD25(+) FoxP3(+) regulatory T cell response, with greater numbers after infection.  
gold rationale: By transducing cortical neurons with genes that were expressed more highly in granule cell neurons, we identified three interferon-stimulated genes (ISGs; Ifi27, Irg1 and Rsad2 (also known as Viperin)) that mediated the antiviral effects against different neurotropic viruses.  
your category: _______

**#1021** gold `CONTRADICT` -> pred `NEI` (conf 0.97)  
claim: Rapid up-regulation and higher basal expression of interferon-induced genes reduce survival of granule cell neurons that are infected by West Nile virus.  
gold paper(s): Differential innate immune response programs in neuronal subtypes determine susceptibility to infection in the brain by positive stranded RNA viruses  
top retrieved: Beta interferon controls West Nile virus infection and pathogenesis in mice.  
sentences the verifier saw: Studies with mice lacking the common plasma membrane receptor for type I interferon (IFN-αβR(-)(/)(-)) have revealed that IFN signaling restricts tropism, dissemination, and lethality after infection with West Nile virus (WNV) or several other pathogenic viruses. | Consistent with a direct role for IFN-β in control of WNV replication, viral titers in ex vivo cultures of macrophages, dendritic cells, fibroblasts, and cerebellar granule cell neurons, but not cortical neurons, from IFN-β(-)(/)(-) mice were greater than in wild-type cells. | Although detailed immunological analysis revealed no major deficits in the quality or quantity of WNV-specific antibodies or CD8(+) T cells, we observed an altered CD4(+) CD25(+) FoxP3(+) regulatory T cell response, with greater numbers after infection.  
gold rationale: By transducing cortical neurons with genes that were expressed more highly in granule cell neurons, we identified three interferon-stimulated genes (ISGs; Ifi27, Irg1 and Rsad2 (also known as Viperin)) that mediated the antiviral effects against different neurotropic viruses.  
your category: _______

**#1221** gold `CONTRADICT` -> pred `NEI` (conf 0.96)  
claim: The genomic aberrations found in matasteses are very similar to those found in the primary tumor.  
gold paper(s): Evolution of metastasis revealed by mutational landscapes of chemically induced skin cancers  
top retrieved: High prevalence of evolutionarily conserved and species-specific genomic aberrations in mouse pluripotent stem cells.  
sentences the verifier saw: We found that genomic aberrations occur frequently in mouse embryonic stem cells of various mouse strains, add in mouse iPSCs of various cell origins and derivation techniques. | Four hotspots of chromosomal aberrations were detected: full trisomy 11 (with a minimally recurrent gain in 11qE2), full trisomy 8, and deletions in chromosomes 10qB and 14qC-14qE. The most recurrent aberration in mouse PSCs, gain 11qE2, turned out to be fully syntenic to the common aberration 17q25 in human PSCs, while other recurrent aberrations were found to be species specific. | Analysis of chromosomal aberrations in 74 samples of rhesus macaque PSCs revealed a gain in chromosome 16q, syntenic to the hotspot in human 17q.  
gold rationale: Shared mutations between primary carcinomas and their matched metastases have the distinct A-to-T signature of the initiating carcinogen dimethylbenzanthracene, but non-shared mutations are primarily G-to-T, a signature associated with oxidative stress.  
your category: _______

**#1368** gold `SUPPORT` -> pred `NEI` (conf 0.96)  
claim: Vitamin D deficiency effects the term of delivery.  
gold paper(s): Association between maternal serum 25-hydroxyvitamin D level and pregnancy and neonatal outcomes: systematic review and meta-analysis of observational studies.  
top retrieved: Vitamin D insufficiency and the blunted PTH response in established osteoporosis: the role of magnesium deficiency  
sentences the verifier saw: Vitamin D insufficiency is common, however within individuals, not all manifest the biochemical effects of PTH excess. | The aims of this study were to compare in patients with established osteoporosis and differing degrees of vitamin D and PTH status : (1) the presence of Mg deficiency using the standard Mg loading test (2) evaluate the effects of Mg loading on the calcium-PTH endocrine axis (3) determine the effects of oral, short term Mg supplementation on the calcium-PTH endocrine axis and bone turnover. | This study confirms that in patients with established osteoporosis, there is also a distinct group with a low vitamin D and a blunted PTH level and that Mg deficiency (as measured by the Mg loading test) is an important contributing factor.  
gold rationale: Insufficient serum levels of 25-OHD were associated with gestational diabetes (pooled odds ratio 1.49, 95% confidence interval 1.18 to 1.89), pre-eclampsia (1.79, 1.25 to 2.58), and small for gestational age infants (1.85, 1.52 to 2.26). | Pregnant women with low serum 25-OHD levels had an increased risk of bacterial vaginosis and low birthweight infants but not delivery by caesarean section.   
 | CONCLUSION Vitamin D insufficiency is associated with an increased risk of gestational diabetes, pre-eclampsia, and small for gestational age infants. | Pregnant women with low 25-OHD levels had an increased risk of bacterial vaginosis and lower birth weight infants, but not delivery by caesarean section.  
your category: _______

**#619** gold `CONTRADICT` -> pred `NEI` (conf 0.95)  
claim: Increased vessel density along with a reduction in fibrosis decreases the efficacy of chemotherapy treatments.  
gold paper(s): Inhibition of Hedgehog signaling enhances delivery of chemotherapy in a mouse model of pancreatic cancer.  
top retrieved: Cell and molecular mechanisms of insulin-induced angiogenesis  
sentences the verifier saw: The appropriate development of new blood vessels, along with their subsequent maturation and differentiation, establishes the foundation for functional wound neovasculature. | Mice skin injected with insulin shows longer vessels with more branches, along with increased numbers of associated alpha-smooth muscle actin-expressing cells, suggesting the appropriate differentiation and maturation of the new vessels. | Our findings strongly suggest that insulin is a good candidate for the treatment of ischaemic wounds and other conditions in which blood vessel development is impaired.  
gold rationale: We tested whether the delivery and efficacy of gemcitabine in the mice could be improved by coadministration of IPI-926, a drug that depletes tumor-associated stromal tissue by inhibition of the Hedgehog cellular signaling pathway. | The combination therapy produced a transient increase in intratumoral vascular density and intratumoral concentration of gemcitabine, leading to transient stabilization of disease.  
your category: _______

**#415** gold `SUPPORT` -> pred `NEI` (conf 0.94)  
claim: Female carriers of the Apolipoprotein E4 (APOE4) allele have increased risk for dementia.  
gold paper(s): Reproductive period and risk of dementia in postmenopausal women.  
top retrieved: Gain of toxic Apolipoprotein E4 effects in Human iPSC-Derived Neurons Is Ameliorated by a Small-Molecule Structure Corrector  
sentences the verifier saw: Using human neurons derived from induced pluripotent stem cells that expressed apolipoprotein E4 (ApoE4), a variant of the APOE gene product and the major genetic risk factor for AD, we demonstrated that ApoE4-expressing neurons had higher levels of tau phosphorylation, unrelated to their increased production of amyloid-β (Aβ) peptides, and that they displayed GABAergic neuron degeneration. | ApoE4 increased Aβ production in human, but not in mouse, neurons. | Converting ApoE4 to ApoE3 by gene editing rescued these phenotypes, indicating the specific effects of ApoE4.  
gold rationale: Risk of dementia associated with a longer reproductive period was most pronounced in APOE epsilon4 carriers (adjusted RR for >39 reproductive years compared with <34 reproductive years, 4.20 [95% CI, 1.97-8.92] for dementia and 3.42 [95% CI, 1.51-7.75] for AD), whereas in noncarriers, no clear association with dementia or AD was observed.   
  
your category: _______

**#1370** gold `CONTRADICT` -> pred `NEI` (conf 0.94)  
claim: Vitamin D deficiency is unrelated to birth weight.  
gold paper(s): Association between maternal serum 25-hydroxyvitamin D level and pregnancy and neonatal outcomes: systematic review and meta-analysis of observational studies.  
top retrieved: Vitamin D: The "sunshine" vitamin.  
sentences the verifier saw: Vitamin D insufficiency affects almost 50% of the population worldwide. | An estimated 1 billion people worldwide, across all ethnicities and age groups, have a vitamin D deficiency (VDD). | This pandemic of hypovitaminosis D can mainly be attributed to lifestyle (for example, reduced outdoor activities) and environmental (for example, air pollution) factors that reduce exposure to sunlight, which is required for ultraviolet-B (UVB)-induced vitamin D production in the skin.  
gold rationale: Pregnant women with low serum 25-OHD levels had an increased risk of bacterial vaginosis and low birthweight infants but not delivery by caesarean section.   
 | Pregnant women with low 25-OHD levels had an increased risk of bacterial vaginosis and lower birth weight infants, but not delivery by caesarean section.  
your category: _______

**#1041** gold `CONTRADICT` -> pred `NEI` (conf 0.86)  
claim: Replacement of histone H2A with H2A.Z slows gene activation in yeasts by stabilizing +1 nucleosomes.  
gold paper(s): Nucleosome stability mediated by histone variants H3.3 and H2A.Z.  
top retrieved: Stepwise Histone Replacement by SWR1 Requires Dual Activation with Histone H2A.Z and Canonical Nucleosome  
sentences the verifier saw: This incorporation is mediated by the conserved SWR1 complex, which replaces histone H2A in canonical nucleosomes with H2A.Z in an ATP-dependent manner. | SWR1-catalyzed H2A.Z replacement in vitro occurs in a stepwise and unidirectional fashion, one H2A.Z-H2B dimer at a time, producing heterotypic nucleosomes as intermediates and homotypic H2A.Z nucleosomes as end products. | These results suggest that the combination of H2A-containing nucleosome and free H2A.Z-H2B dimer acting as both effector and substrate for SWR1 governs the specificity and outcome of the replacement reaction.  
gold rationale: Immunoprecipitation studies of nucleosome core particles (NCPs) show that NCPs that contain both H3.3 and H2A.Z are even less stable than NCPs containing H3.3 and H2A.  
your category: _______

**#212** gold `CONTRADICT` -> pred `NEI` (conf 0.82)  
claim: CR is associated with higher methylation age.  
gold paper(s): Caloric restriction delays age-related methylation drift  
top retrieved: Yeast sirtuins and the regulation of aging.  
sentences the verifier saw: Furthermore, Sir2 has been implicated in mediating the beneficial effects of caloric restriction (CR) on life span, not only in yeast, but also in higher eukaryotes. | While this paradigm has had its share of disagreements and debate, it has also helped rapidly drive the aging research field forward. | This review discusses the function of Sir2 and the Hst homologs in replicative aging and chronological aging, and also addresses how the sirtuins are regulated in response to environmental stresses such as CR.  
gold rationale: Epigenetic information encoded by DNA methylation is tightly regulated, but shows a striking drift associated with age that includes both gains and losses of DNA methylation at various sites. | Twenty-two to 30-year-old rhesus monkeys exposed to 30% caloric restriction since 7-14 years of age showed attenuation of age-related methylation drift compared to ad libitum-fed controls such that their blood methylation age appeared 7 years younger than their chronologic age. | Even more pronounced effects were seen in 2.7-3.2-year-old mice exposed to 40% caloric restriction starting at 0.3 years of age. | Caloric restriction has been shown to increase lifespan in mammals. | Here, the authors provide evidence that age-related methylation drift correlates with lifespan and that caloric restriction in mice and rhesus monkeys results in attenuation of age-related methylation drift.  
your category: _______

**#1088** gold `CONTRADICT` -> pred `NEI` (conf 0.76)  
claim: Silencing of Bcl2 is important for the maintenance and progression of tumors.  
gold paper(s): Antiapoptotic BCL-2 is required for maintenance of a model leukemia.  
top retrieved: Suppression of intestinal neoplasia by deletion of Dnmt3b  
sentences the verifier saw: Aberrant gene silencing accompanied by DNA methylation is associated with neoplastic progression in many tumors that also show global loss of DNA methylation. | Using conditional inactivation of de novo methyltransferase Dnmt3b in Apc(Min/+) mice, we demonstrate that the loss of Dnmt3b has no impact on microadenoma formation, which is considered the earliest stage of intestinal tumor formation. | Interestingly, many large adenomas showed regions with Dnmt3b inactivation, indicating that Dnmt3b is required for initial outgrowth of macroscopic adenomas but is not required for their maintenance.  
gold rationale: Eliminating BCL-2 yielded rapid loss of leukemic cells and significantly prolonged survival, formally validating BCL-2 as a rational target for cancer therapy.  
your category: _______

**#1049** gold `CONTRADICT` -> pred `NEI` (conf 0.75)  
claim: Ribosomopathies have a low degree of cell and tissue specific pathology.  
gold paper(s): Ribosome-Mediated Specificity in Hox mRNA Translation and Vertebrate Tissue Patterning  
top retrieved: Growth control and ribosomopathies.  
sentences the verifier saw: Ribosome biogenesis and protein synthesis are two of the most energy consuming processes in a growing cell. | Recent discoveries of causative mutations and deletions in genes linked to ribosome biogenesis have defined a group of similar pathologies termed ribosomopathies. | In this review, we summarize recent advances in understanding the mechanisms underlying the pathologies of ribosomopathies and discuss the relationship between ribosome production and tumorigenesis.  
gold rationale: Unexpectedly, a ribosomal protein (RP) expression screen reveals dynamic regulation of individual RPs within the vertebrate embryo. | Collectively, these findings suggest that RP activity may be highly regulated to impart a new layer of specificity in the control of gene expression and mammalian development.  
your category: _______

**#756** gold `SUPPORT` -> pred `NEI` (conf 0.54)  
claim: Many proteins in human cells can be post-translationally modified at lysine residues via acetylation.  
gold paper(s): Protein Lysine Acetylated/Deacetylated Enzymes and the Metabolism-Related Diseases  
top retrieved: The growing landscape of lysine acetylation links metabolism and cell signalling  
sentences the verifier saw: Lysine acetylation is a conserved protein post-translational modification that links acetyl-coenzyme A metabolism and cellular signalling. | Recent advances in the identification and quantification of lysine acetylation by mass spectrometry have increased our understanding of lysine acetylation, implicating it in many biological processes through the regulation of protein interactions, activity and localization. | These emerging findings point to new functions for different lysine acylations and deacylating enzymes and also highlight the mechanisms by which acetylation regulates various cellular processes.  
gold rationale: Lysine acetylation is a reversible posttranslational modifcation, an epigenetic phenomenon, referred to as transfer of an acetyl group from acetyl CoA to lysine e- amino group of targeted protein, which is modulated by acetyltransferases (histone/ lysine (K) acetyltransferases, HATs/KATs) and deacetylases (histone/lysine (K) deacetylases, HDACs/KDACs).  
your category: _______


## MISSED_BY_VERIFIER
Gold paper was retrieved but we answered NOT ENOUGH EVIDENCE (abstained or classified neutral)

**#1024** gold `SUPPORT` -> pred `NEI` (conf 1.00)  
claim: Recurrent mutations occur frequently within CTCF anchor sites adjacent to oncogenes.  
gold paper(s): 3D Chromosome Regulatory Landscape of Human Pluripotent Cells.  
top retrieved: 3D Chromosome Regulatory Landscape of Human Pluripotent Cells.  
sentences the verifier saw: To devise this map, we identified transcriptional enhancers and insulators in these cells and placed them within the context of cohesin-associated CTCF-CTCF loops using cohesin ChIA-PET data. | The CTCF-CTCF loops we identified form a chromosomal framework of insulated neighborhoods, which in turn form topologically associating domains (TADs) that are largely preserved during the transition between the naive and primed states. | The CTCF anchor regions we identified are conserved across species, influence gene expression, and are a frequent site of mutations in cancer cells, underscoring their functional importance in cellular regulation.  
gold rationale: The CTCF anchor regions we identified are conserved across species, influence gene expression, and are a frequent site of mutations in cancer cells, underscoring their functional importance in cellular regulation.  
your category: _______

**#852** gold `CONTRADICT` -> pred `NEI` (conf 1.00)  
claim: Non-invasive ventilation use should be decreased if there is inadequate response to conventional treatment.  
gold paper(s): Cost effectiveness of ward based non-invasive ventilation for acute exacerbations of chronic obstructive pulmonary disease: economic analysis of randomised controlled trial.  
top retrieved: Non-invasive ventilation in chronic obstructive pulmonary disease patients: helmet versus facial mask  
sentences the verifier saw: The helmet is a new interface with the potential of increasing the success rate of non-invasive ventilation by improving tolerance. | To perform a physiological comparison between the helmet and the conventional facial mask in delivering non-invasive ventilation in hypercapnic patients with chronic obstructive pulmonary disease. | In 10 patients we evaluated gas exchange, inspiratory effort, patient–ventilator synchrony and patient tolerance after 30 min of non-invasive ventilation delivered either by helmet or facial mask; both trials were preceded by periods of spontaneous unassisted breathing.  
gold rationale: Modelling of these data indicates that a typical UK hospital providing a non-invasive ventilation service will avoid six deaths and three to nine admissions to intensive care units per year, with an associated cost reduction of 12000-53000 pounds sterling per year.   
 | CONCLUSIONS Non-invasive ventilation is a highly cost effective treatment that both reduced total costs and improved mortality in hospital.  
your category: _______

**#718** gold `CONTRADICT` -> pred `NEI` (conf 1.00)  
claim: Low nucleosome occupancy correlates with low methylation levels across species.  
gold paper(s): Dnmt1-Independent CG Methylation Contributes to Nucleosome Positioning in Diverse Eukaryotes  
top retrieved: Dnmt1-Independent CG Methylation Contributes to Nucleosome Positioning in Diverse Eukaryotes  
sentences the verifier saw: Numerous Dnmt5-containing organisms that diverged more than a billion years ago exhibit clustered methylation, specifically in nucleosome linkers. | Clustered methylation occurs at unprecedented densities and directly disfavors nucleosomes, contributing to nucleosome positioning between clusters. | These features constitute a previously unappreciated genome architecture, in which dense methylation influences nucleosome positions, likely facilitating nuclear processes under extreme spatial constraints.  
gold rationale: Clustered methylation occurs at unprecedented densities and directly disfavors nucleosomes, contributing to nucleosome positioning between clusters.  
your category: _______

**#533** gold `SUPPORT` -> pred `NEI` (conf 1.00)  
claim: Hyperfibrinogenemia increases rates of femoropopliteal bypass thrombosis.  
gold paper(s): Influence of smoking and plasma factors on patency of femoropopliteal vein grafts.  
top retrieved: Influence of smoking and plasma factors on patency of femoropopliteal vein grafts.  
sentences the verifier saw: OBJECTIVE To determine the effects of smoking, plasma lipids, lipoproteins, apolipoproteins, and fibrinogen on the patency of saphenous vein femoropopliteal bypass grafts at one year.   
 | DESIGN Prospective study of patients with saphenous vein femoropopliteal bypass grafts entered into a multicentre trial.   
 | PATIENTS 157 Patients (mean age 66.6 (SD 8.2) years), 113 with patent grafts and 44 with occluded grafts one year after bypass.   
  
gold rationale: RESULTS Markers for smoking (blood carboxyhaemoglobin concentration (p less than 0.05) and plasma thiocyanate concentration (p less than 0.01) and plasma concentrations of fibrinogen (p less than 0.001) and apolipoproteins AI (p less than 0.04) and (a) (p less than 0.05) were significantly higher in patients with occluded grafts. | Patency was significantly higher by life table analysis in patients with a plasma fibrinogen concentration below the median than in those with a concentration above (90% v 57%, p less than 0.0002). | CONCLUSIONS Plasma fibrinogen concentration was the most important variable predicting graft occlusion, followed by smoking markers. | A more forceful approach is needed to stop patients smoking; therapeutic measures to improve patency of vein grafts should focus on decreasing plasma fibrinogen concentration rather than serum cholesterol concentration.  
your category: _______

**#48** gold `CONTRADICT` -> pred `NEI` (conf 0.99)  
claim: A total of 1,000 people in the UK are asymptomatic carriers of vCJD infection.  
gold paper(s): Prevalent abnormal prion protein in human appendixes after bovine spongiform encephalopathy epizootic: large scale survey  
top retrieved: Research Letters  
sentences the verifier saw: We report a case of preclinical variant Creutzfeldt-Jakob disease (vCJD) in a patient who died from a non-neurological disorder 5 years after receiving a blood transfusion from a donor who subsequently developed vCJD. | The patient was a heterozygote at codon 129 of PRNP, suggesting that susceptibility to vCJD infection is not confined to the methionine homozygous PRNP genotype. | These findings have major implications for future estimates and surveillance of vCJD in the UK.  
gold rationale: RESULTS Of the 32,441 appendix samples 16 were positive for abnormal PrP, indicating an overall prevalence of 493 per million population (95% confidence interval 282 to 801 per million).  
your category: _______

**#1140** gold `CONTRADICT` -> pred `NEI` (conf 0.99)  
claim: Taking 400mg of α-tocopheryl acetate helps to prevent prostate cancer.  
gold paper(s): Vitamins E and C in the prevention of prostate and total cancer in men: the Physicians' Health Study II randomized controlled trial.  
top retrieved: Vitamins E and C in the prevention of prostate and total cancer in men: the Physicians' Health Study II randomized controlled trial.  
sentences the verifier saw: CONTEXT Many individuals take vitamins in the hopes of preventing chronic diseases such as cancer, and vitamins E and C are among the most common individual supplements. | A large-scale randomized trial suggested that vitamin E may reduce risk of prostate cancer; however, few trials have been powered to address this relationship. | OBJECTIVE To evaluate whether long-term vitamin E or C supplementation decreases risk of prostate and total cancer events among men.   
  
gold rationale: Compared with placebo, vitamin E had no effect on the incidence of prostate cancer (active and placebo vitamin E groups, 9.1 and 9.5 events per 1000 person-years; hazard ratio [HR], 0.97; 95% confidence interval [CI], 0.85-1.09; P = .58) or total cancer (active and placebo vitamin E groups, 17.8 and 17.3 cases per 1000 person-years; HR, 1.04; 95% CI, 0.95-1.13; P = .41). | CONCLUSIONS In this large, long-term trial of male physicians, neither vitamin E nor C supplementation reduced the risk of prostate or total cancer.  
your category: _______

**#982** gold `SUPPORT` -> pred `NEI` (conf 0.99)  
claim: Proteins synthesized at the growth cone are ubiquitinated at a higher rate than proteins from the cell body.  
gold paper(s): Coupled local translation and degradation regulate growth cone collapse  
top retrieved: Coupled local translation and degradation regulate growth cone collapse  
sentences the verifier saw: Here we show that local protein synthesis and degradation are linked events in growth cones. | We find that growth cones exhibit high levels of ubiquitination and that local signalling pathways trigger the ubiquitination and degradation of RhoA, a mediator of Sema3A-induced growth cone collapse. | In addition to RhoA, we find that locally translated proteins are the main targets of the ubiquitin-proteasome system in growth cones.  
gold rationale: We find that growth cones exhibit high levels of ubiquitination and that local signalling pathways trigger the ubiquitination and degradation of RhoA, a mediator of Sema3A-induced growth cone collapse.  
your category: _______

**#532** gold `CONTRADICT` -> pred `NEI` (conf 0.99)  
claim: Hyperfibrinogenemia decreases rates of femoropopliteal bypass thrombosis.  
gold paper(s): Influence of smoking and plasma factors on patency of femoropopliteal vein grafts.  
top retrieved: Influence of smoking and plasma factors on patency of femoropopliteal vein grafts.  
sentences the verifier saw: OBJECTIVE To determine the effects of smoking, plasma lipids, lipoproteins, apolipoproteins, and fibrinogen on the patency of saphenous vein femoropopliteal bypass grafts at one year.   
 | DESIGN Prospective study of patients with saphenous vein femoropopliteal bypass grafts entered into a multicentre trial.   
 | PATIENTS 157 Patients (mean age 66.6 (SD 8.2) years), 113 with patent grafts and 44 with occluded grafts one year after bypass.   
  
gold rationale: RESULTS Markers for smoking (blood carboxyhaemoglobin concentration (p less than 0.05) and plasma thiocyanate concentration (p less than 0.01) and plasma concentrations of fibrinogen (p less than 0.001) and apolipoproteins AI (p less than 0.04) and (a) (p less than 0.05) were significantly higher in patients with occluded grafts. | Patency was significantly higher by life table analysis in patients with a plasma fibrinogen concentration below the median than in those with a concentration above (90% v 57%, p less than 0.0002). | CONCLUSIONS Plasma fibrinogen concentration was the most important variable predicting graft occlusion, followed by smoking markers. | A more forceful approach is needed to stop patients smoking; therapeutic measures to improve patency of vein grafts should focus on decreasing plasma fibrinogen concentration rather than serum cholesterol concentration.  
your category: _______

**#314** gold `SUPPORT` -> pred `NEI` (conf 0.99)  
claim: Deamination of cytidine to uridine on the minus strand of viral DNA results in catastrophic G-to-A mutations in the viral genome.  
gold paper(s): Broad antiretroviral defence by human APOBEC3G through lethal editing of nascent reverse transcripts  
top retrieved: DNA Deamination Mediates Innate Immunity to Retroviral Infection  
sentences the verifier saw: CEM15/APOBEC3G is a cellular protein required for resistance to infection by virion infectivity factor (Vif)-deficient human immunodeficiency virus (HIV). | Here, using a murine leukemia virus (MLV)-based system, we provide evidence that CEM15/APOBEC3G is a DNA deaminase that is incorporated into virions during viral production and subsequently triggers massive deamination of deoxycytidine to deoxyuridine within the retroviral minus (first)-strand cDNA, thus providing a probable trigger for viral destruction. | These findings imply that targeted DNA deamination is a major strategy of innate immunity to retroviruses and likely also contributes to the sequence variation observed in many viruses (including HIV).  
gold rationale: APOBEC3G is closely related to APOBEC1, the central component of an RNA-editing complex that deaminates a cytosine residue in apoB messenger RNA. | Here, we demonstrate that it does, as APOBEC3G exerts its antiviral effect during reverse transcription to trigger G-to-A hypermutation in the nascent retroviral DNA.  
your category: _______

**#5** gold `SUPPORT` -> pred `NEI` (conf 0.98)  
claim: 1/2000 in UK have abnormal PrP positivity.  
gold paper(s): Prevalent abnormal prion protein in human appendixes after bovine spongiform encephalopathy epizootic: large scale survey  
top retrieved: Prevalent abnormal prion protein in human appendixes after bovine spongiform encephalopathy epizootic: large scale survey  
sentences the verifier saw: SAMPLE 32,441 archived appendix samples fixed in formalin and embedded in paraffin and tested for the presence of abnormal prion protein (PrP).   
 | RESULTS Of the 32,441 appendix samples 16 were positive for abnormal PrP, indicating an overall prevalence of 493 per million population (95% confidence interval 282 to 801 per million). | CONCLUSIONS This study corroborates previous studies and suggests a high prevalence of infection with abnormal PrP, indicating vCJD carrier status in the population compared with the 177 vCJD cases to date.  
gold rationale: RESULTS Of the 32,441 appendix samples 16 were positive for abnormal PrP, indicating an overall prevalence of 493 per million population (95% confidence interval 282 to 801 per million).  
your category: _______

**#692** gold `CONTRADICT` -> pred `NEI` (conf 0.98)  
claim: Leuko-increased blood increases infectious complications in red blood cell transfusion.  
gold paper(s): Clinical outcomes following institution of the Canadian universal leukoreduction program for red blood cell transfusions.  
top retrieved: Clinical outcomes following institution of the Canadian universal leukoreduction program for red blood cell transfusions.  
sentences the verifier saw: OBJECTIVE To evaluate clinical outcomes following adoption of a national universal prestorage leukoreduction program for blood transfusions.   
 | DESIGN, SETTING, AND POPULATION Retrospective before-and-after cohort study conducted from August 1998 to August 2000 in 23 academic and community hospitals throughout Canada, enrolling 14 786 patients who received red blood cell transfusions following cardiac surgery or repair of hip fracture, or who required intensive care following a surgical intervention or multiple trauma.   
 | CONCLUSION A national universal leukoreduction program is potentially associated with decreased mortality as well as decreased fever episodes and antibiotic use after red blood cell transfusion in high-risk patients.  
gold rationale: Compared with the control period, the adjusted odds of death following leukoreduction were reduced (odds ratio [OR], 0.87; 95% confidence interval [CI], 0.75-0.99), but serious nosocomial infections did not decrease (adjusted OR, 0.97; 95% CI, 0.87-1.09). | The frequency of posttransfusion fevers decreased significantly following leukoreduction (adjusted OR, 0.86; 95% CI, 0.79-0.94), as did antibiotic use (adjusted OR, 0.90; 95% CI, 0.82-0.99).   
 | CONCLUSION A national universal leukoreduction program is potentially associated with decreased mortality as well as decreased fever episodes and antibiotic use after red blood cell transfusion in high-risk patients.  
your category: _______

**#743** gold `CONTRADICT` -> pred `NEI` (conf 0.98)  
claim: Macrolides protect against myocardial infarction.  
gold paper(s): Antibiotics and risk of subsequent first-time acute myocardial infarction.  
top retrieved: Antibiotics and risk of subsequent first-time acute myocardial infarction.  
sentences the verifier saw: CONTEXT Increasing evidence supports the hypothesis of a causal association between certain bacterial infections and increased risk of developing acute myocardial infarction. | If such a causal association exists, subjects who used antibiotics active against the bacteria, regardless of indication, might be at lower risk of developing acute myocardial infarction than nonusers.   
 | OBJECTIVE To determine whether previous use of antibiotics decreases the risk of developing a first-time acute myocardial infarction.   
  
gold rationale: No effect was found for previous use of macrolides (primarily erythromycin), sulfonamides, penicillins, or cephalosporins.   
  
your category: _______

**#847** gold `CONTRADICT` -> pred `NEI` (conf 0.98)  
claim: New drugs for tuberculosis often do not penetrate the necrotic portion of a tuberculosis lesion in high concentrations.  
gold paper(s): The association between sterilizing activity and drug distribution into tuberculosis lesions  
top retrieved: The association between sterilizing activity and drug distribution into tuberculosis lesions  
sentences the verifier saw: Finding new treatment-shortening antibiotics to improve cure rates and curb the alarming emergence of drug resistance is the major objective of tuberculosis (TB) drug development. | Using a matrix-assisted laser desorption/ionization (MALDI) mass spectrometry imaging suite in a biosafety containment facility, we show that the key sterilizing drugs rifampicin and pyrazinamide efficiently penetrate the sites of TB infection in lung lesions. | We propose an alternative working model to prioritize new antibiotic regimens based on quantitative and spatial distribution of TB drugs in the major lesion types found in human lungs.  
gold rationale: Rifampicin even accumulates in necrotic caseum, a critical lesion site where persisting tubercle bacilli reside.  
your category: _______

**#275** gold `SUPPORT` -> pred `NEI` (conf 0.97)  
claim: Combining phosphatidylinositide 3-kinase and MEK 1/2 inhibitors is effective at treating KRAS mutant tumors.  
gold paper(s): Effective Use of PI3K and MEK Inhibitors to Treat Mutant K-Ras G12D and PIK3CA H1047R Murine Lung Cancers; NVP-BEZ235, a dual PI3K/mTOR inhibitor, prevents PI3K signaling and inhibits the growth of cancer cells with activating PI3K mutations.  
top retrieved: Effective Use of PI3K and MEK Inhibitors to Treat Mutant K-Ras G12D and PIK3CA H1047R Murine Lung Cancers  
sentences the verifier saw: In contrast, mouse lung cancers driven by mutant Kras did not substantially respond to single-agent NVP-BEZ235. | However, when NVP-BEZ235 was combined with a mitogen-activated protein kinase kinase (MEK) inhibitor, ARRY-142886, there was marked synergy in shrinking these Kras-mutant cancers. | These in vivo studies suggest that inhibitors of the PI3K-mTOR pathway may be active in cancers with PIK3CA mutations and, when combined with MEK inhibitors, may effectively treat KRAS mutated lung cancers.  
gold rationale: However, when NVP-BEZ235 was combined with a mitogen-activated protein kinase kinase (MEK) inhibitor, ARRY-142886, there was marked synergy in shrinking these Kras-mutant cancers. | These in vivo studies suggest that inhibitors of the PI3K-mTOR pathway may be active in cancers with PIK3CA mutations and, when combined with MEK inhibitors, may effectively treat KRAS mutated lung cancers. | In summary, NVP-BEZ235 inhibits the PI3K/mTOR axis and results in antiproliferative and antitumoral activity in cancer cells with both wild-type and mutated p110-alpha.  
your category: _______

**#1266** gold `SUPPORT` -> pred `NEI` (conf 0.97)  
claim: The risk of breast cancer among parous women increases with placental weight of pregnancies, and this association is strongest for premenopausal breast cancer.  
gold paper(s): Pregnancy characteristics and maternal risk of breast cancer.  
top retrieved: Pregnancy characteristics and maternal risk of breast cancer.  
sentences the verifier saw: OBJECTIVE To examine associations between indirect markers of hormonal exposures, such as placental weight and other pregnancy characteristics, and maternal risk of developing breast cancer.   
 | A high birth weight (> or =4000 g) in 2 successive births was associated with an increased risk of breast cancer before but not after adjusting for placental weight and other covariates (adjusted hazard ratio, 1.10; 95% CI, 0.76-1.59).   
 | CONCLUSIONS Placental weight is positively associated with maternal risk of breast cancer.  
gold rationale: Compared with women who had placentas weighing less than 500 g in 2 consecutive pregnancies, the risk of breast cancer was increased among women whose placentas weighed between 500 and 699 g in their first pregnancy and at least 700 g in their second pregnancy (or vice versa) (adjusted hazard ratio, 1.82; 95% confidence interval [CI], 1.07-3.08), and the corresponding risk was doubled among women whose placentas weighed at least 700 g in both pregnancies (adjusted hazard ratio, 2.05; 95% CI, 1.15-3.64). | CONCLUSIONS Placental weight is positively associated with maternal risk of breast cancer.  
your category: _______


## FALSE_CONTRADICT
Predicted CONTRADICT but gold is NEI

**#1100** gold `NEI` -> pred `CONTRADICT` (conf 1.00)  
claim: Statins increase blood cholesterol.  
gold paper(s): (none, NEI)  
top retrieved: Pleiotropic effects of statins.  
sentences the verifier saw: Statins decrease hepatic cholesterol biosynthesis and may therefore lower the risk of cholesterol gallstones by reducing the cholesterol concentration in the bile. | OBJECTIVE To study the association between the use of statins, fibrates, or other lipid-lowering agents and the risk of incident gallstone disease followed by cholecystectomy.   
 | RESULTS A total of 27,035 patients with cholecystectomy and 106,531 matched controls were identified, including 2396 patients and 8868 controls who had statin use.  
gold rationale: -  
your category: _______

**#1292** gold `NEI` -> pred `CONTRADICT` (conf 1.00)  
claim: There is no association between HNF4A mutations and diabetes risks.  
gold paper(s): (none, NEI)  
top retrieved: Macrosomia and Hyperinsulinaemic Hypoglycaemia in Patients with Heterozygous Mutations in the HNF4A Gene  
sentences the verifier saw: Background  Macrosomia is associated with considerable neonatal and maternal morbidity. | The increased rate of macrosomia in the offspring of pregnant women with diabetes and in congenital hyperinsulinaemia is mediated by increased foetal insulin secretion. | We assessed the in utero and neonatal role of two key regulators of pancreatic insulin secretion by studying birthweight and the incidence of neonatal hypoglycaemia in patients with heterozygous mutations in the maturity-onset diabetes of the young (MODY) genes HNF4A (encoding HNF-4α) and HNF1A/TCF1 (encoding HNF-1α), and the effect of pancreatic deletion of Hnf4a on foetal and neonatal insulin secretion in mice.  
gold rationale: -  
your category: _______

**#354** gold `NEI` -> pred `CONTRADICT` (conf 1.00)  
claim: Downregulation and mislocalization of Scribble prevents cell transformation and mammary tumorigenesis.  
gold paper(s): (none, NEI)  
top retrieved: Deregulation of Scribble Promotes Mammary Tumorigenesis and Reveals a Role for Cell Polarity in Carcinoma  
sentences the verifier saw: Here, we demonstrate that depletion of Scribble in mammary epithelia disrupts cell polarity, blocks three-dimensional morphogenesis, inhibits apoptosis, and induces dysplasia in vivo that progress to tumors after long latency. | Like depletion, mislocalization of Scribble from cell-cell junction was sufficient to promote cell transformation. | Interestingly, spontaneous mammary tumors in mice and humans possess both downregulated and mislocalized Scribble.  
gold rationale: -  
your category: _______

**#213** gold `NEI` -> pred `CONTRADICT` (conf 0.99)  
claim: CRP is not predictive of postoperative mortality following Coronary Artery Bypass Graft (CABG) surgery.  
gold paper(s): (none, NEI)  
top retrieved: Preoperative C-reactive protein predicts long-term mortality and hospital length of stay after primary, nonemergent coronary artery bypass grafting.  
sentences the verifier saw: We examine the value of preoperative CRP levels less than 10 mg/l for predicting long-term, all-cause mortality and hospital length of stay in surgical patients undergoing primary, nonemergent coronary artery bypass graft-only surgery.   
 | METHODS We examined the association between preoperative CRP levels stratified into four categories (< 1, 1-3, 3-10, and > 10 mg/l), and 7-yr all-cause mortality and hospital length of stay in 914 prospectively enrolled primary, nonemergent coronary artery bypass graft-only surgical patients using a proportional hazards regression model.   
 | CONCLUSION We demonstrate that preoperative CRP levels as low as 3 mg/l are associated with increased long-term mortality and extended hospital length of stay in relatively lower-acuity patients undergoing primary, nonemergent coronary artery bypass graft-only surgery.  
gold rationale: -  
your category: _______

**#649** gold `NEI` -> pred `CONTRADICT` (conf 0.99)  
claim: Integrating classroom-based collaborative learning with Web-based collaborative learning leads to subpar class performance  
gold paper(s): (none, NEI)  
top retrieved: Update of the FANTOM web resource: high resolution transcriptome of diverse cell types in mammals  
sentences the verifier saw: It is becoming “a truth universally acknowledged” that the education of undergraduate medical students will be enhanced through the use of computer assisted learning. | A “leading edge” virtual campus is likely to attract good students  Achieves the ultimate goal of higher education —The goal is to link people into learning communities. | Computer applications, especially the internet and world wide web, are an extremely efficient way of doing this2  Expands pedagogical horizons —The most controversial argument for … RETURN TO TEXT  
gold rationale: -  
your category: _______

**#269** gold `NEI` -> pred `CONTRADICT` (conf 0.98)  
claim: Cold exposure reduces BAT recruitment.  
gold paper(s): (none, NEI)  
top retrieved: Sestrin2 inhibits uncoupling protein 1 expression through suppressing reactive oxygen species.  
sentences the verifier saw: Uncoupling protein 1 (Ucp1), which is localized in the mitochondrial inner membrane of mammalian brown adipose tissue (BAT), generates heat by uncoupling oxidative phosphorylation. | Upon cold exposure or nutritional abundance, sympathetic neurons stimulate BAT to express Ucp1 to induce energy dissipation and thermogenesis. | Transgenic overexpression of Sestrin2 in adipose tissues inhibited both basal and cold-induced Ucp1 expression in interscapular BAT, culminating in decreased thermogenesis and increased fat accumulation.  
gold rationale: -  
your category: _______

**#1278** gold `NEI` -> pred `CONTRADICT` (conf 0.97)  
claim: The treatment of cancer patients with co-IR blockade does not cause any adverse autoimmune events.  
gold paper(s): (none, NEI)  
top retrieved: In vitro characterization of the anti-PD-1 antibody nivolumab, BMS-936558, and in vivo toxicology in non-human primates.  
sentences the verifier saw: The introduction of immune-checkpoint blockade in the cancer therapy led to a paradigm change of the management of late stage cancers. | A network of microRNAs directly and indirectly controls the expression of checkpoint receptors and several microRNAs can target multiple checkpoint molecules, mimicking the therapeutic effect of a combined immune checkpoint blockade. | In this review, we will describe the microRNAs that control the expression of immune checkpoints and we will present four specific issues of the immune checkpoint therapy in cancer: (1) imprecise therapeutic indication, (2) difficult response evaluation, (3) numerous immunologic adverse-events, and (4) the absence of response to immune therapy.  
gold rationale: -  
your category: _______

**#198** gold `NEI` -> pred `CONTRADICT` (conf 0.96)  
claim: CCL19 is absent within dLNs.  
gold paper(s): (none, NEI)  
top retrieved: Chemokine-like receptor 1 (CMKLR1) and chemokine (C-C motif) receptor-like 2 (CCRL2); two multifunctional receptors with unusual properties.  
sentences the verifier saw: The mammalian gastrointestinal tract harbors a microbial community with metabolic activity critical for host health, including metabolites that can modulate effector functions of immune cells. | Mice treated with vancomycin have an altered microbiome and metabolite profile, exhibit exacerbated T helper type 2 cell (Th2) responses, and are more susceptible to allergic lung inflammation. | In addition, DCs exposed to SCFAs activate T cells less robustly, are less motile in response to CCL19 in vitro, and exhibit a dampened ability to transport inhaled allergens to lung draining nodes.  
gold rationale: -  
your category: _______

**#1332** gold `NEI` -> pred `CONTRADICT` (conf 0.95)  
claim: Tumor necrosis factor alpha (TNF-α) and interleukin-1 (IL-1) are pro-inflammatory cytokines that inhibit IL-6 and IL-10.  
gold paper(s): (none, NEI)  
top retrieved: Downloaded from  
sentences the verifier saw: Physical activity induces a subclinical inflammatory response, mediated in part by leukocytes, and manifested by elevated concentrations of circulating proinflammatory cytokines, including interleukin (IL)-1β, IL-6, and tumor necrosis factor-α (TNF-α). | Ten healthy [peak oxygen uptake = 48.8 ± 6.5 (SD) ml · kg−1 · min−1] but untrained men [age = 25 ± 5 (SD) yr] undertook 3 h of exercise (cycling and inclined walking) at 60–65% peak oxygen uptake. | Circulating leukocyte subset counts were elevated during and 2 h postexercise but returned to normal within 24 h. Plasma concentrations of IL-1β, IL-6, and TNF-α peaked at the end of exercise and remained elevated at 2 h (IL-6) and up to 24 h (IL-1β and TNF-α) postexercise.  
gold rationale: -  
your category: _______

**#527** gold `NEI` -> pred `CONTRADICT` (conf 0.95)  
claim: Homozygous deletion of murine Sbds gene from osterix-expressing mesenchymal stem and progenitor cells (MPCs) prevents oxidative stress.  
gold paper(s): (none, NEI)  
top retrieved: Bone progenitor dysfunction induces myelodysplasia and secondary leukemia  
sentences the verifier saw: By examining how mesenchymal osteolineage cells modulate haematopoiesis, here we show that deletion of Dicer1 specifically in mouse osteoprogenitors, but not in mature osteoblasts, disrupts the integrity of haematopoiesis. | Examining gene expression altered in osteoprogenitors as a result of Dicer1 deletion showed reduced expression of Sbds, the gene mutated in Schwachman-Bodian-Diamond syndrome-a human bone marrow failure and leukaemia pre-disposition condition. | Deletion of Sbds in mouse osteoprogenitors induced bone marrow dysfunction with myelodysplasia.  
gold rationale: -  
your category: _______

**#72** gold `NEI` -> pred `CONTRADICT` (conf 0.92)  
claim: Activator-inhibitor pairs are provided dorsally by Admpchordin.  
gold paper(s): (none, NEI)  
top retrieved: Localization and requirement for Myosin II at the dorsal-ventral compartment boundary of the Drosophila wing.  
sentences the verifier saw: It is unable to signal dorsally because of inhibition by Chordin. | By transplanting dorsal or ventral wild-type grafts into ADMP/BMP2/4/7-depleted hosts, we demonstrate that both poles serve as signaling centers that can induce histotypic differentiation over considerable distances. | We conclude that dorsal and ventral BMP signals and their extracellular antagonists expressed under opposing transcriptional regulation provide a molecular mechanism for embryonic self-regulation.  
gold rationale: -  
your category: _______

**#785** gold `NEI` -> pred `CONTRADICT` (conf 0.90)  
claim: Microarray results from culture-amplified mixtures of serotypes correlate poorly with microarray results from uncultured mixtures.  
gold paper(s): (none, NEI)  
top retrieved: Empirical Bayesian models for analysing molecular serotyping microarrays  
sentences the verifier saw: Over 90 different serotypes exist, and nasopharyngeal carriage of multiple serotypes is common. | CONCLUSIONS Most methods were able to detect the dominant serotype in a sample, but many performed poorly in detecting the minor serotype populations. | Microarray with a culture amplification step was the top-performing method.  
gold rationale: -  
your category: _______

**#691** gold `NEI` -> pred `CONTRADICT` (conf 0.89)  
claim: Leukemia associated Rho guanine nucleotide-exchange factor represses RhoA in response to SRC activation.  
gold paper(s): (none, NEI)  
top retrieved: The Rho GEFs LARG and GEF-H1 regulate the mechanical response to force on integrins  
sentences the verifier saw: Polyploidization can precede the development of aneuploidy in cancer. | Using primary cells, we demonstrate that the guanine exchange factors GEF-H1 and ECT2, which are often overexpressed in cancer and are essential for RhoA activation during cytokinesis, must be downregulated for Mk polyploidization. | Furthermore, we have shown that the mechanism by which polyploidization is prevented in Mks lacking Mkl1, which is mutated in megakaryocytic leukemia, is via elevated GEF-H1 expression; shRNA-mediated GEF-H1 knockdown alone rescues this ploidy defect.  
gold rationale: -  
your category: _______

**#587** gold `NEI` -> pred `CONTRADICT` (conf 0.86)  
claim: In transgenic mice harboring green florescent protein under the control of the Sox2 promoter, less than ten percent of the cells with green florescent colocalize with cell proliferation markers.  
gold paper(s): (none, NEI)  
top retrieved: Visualization of cell cycle in mouse embryos with Fucci2 reporter directed by Rosa26 promoter.  
sentences the verifier saw: To aid in the investigation of these issues, we developed strains of transgenic mice in which a green fluorescent protein (GFP) is expressed in the ureteric bud under the control of the Hoxb7 promoter. | In these mice, GFP is expressed in every branch of the ureteric bud throughout renal development, and in its derivative epithelia in the adult kidney. | These mice represent an extremely powerful tool to characterize the normal patterns of ureteric bud morphogenesis and to investigate the response of the bud to growth factors, matrix elements, and other agents that regulate its growth and branching.  
gold rationale: -  
your category: _______

**#1344** gold `NEI` -> pred `CONTRADICT` (conf 0.84)  
claim: Up-regulation of the p53 pathway and related molecular events casues cancer resistance and results in a significantly shortened lifespan marked by senescent cells and accelerated organismal aging.  
gold paper(s): (none, NEI)  
top retrieved: Senescence and aging: the critical roles of p53  
sentences the verifier saw: The process of aging results in a host of changes at the cellular and molecular levels, which include senescence, telomere shortening, and changes in gene expression. | Epigenetic patterns also change over the lifespan, suggesting that epigenetic changes may constitute an important component of the aging process. | Together, these observations point to the existence of two phenomena that both contribute to age-related DNA methylation changes: epigenetic drift and the epigenetic clock.  
gold rationale: -  
your category: _______


## Your taxonomy (fill in after reading >= 20 errors)

| category | count | example ids | fix idea |
|---|---|---|---|
| | | | |
