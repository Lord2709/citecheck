# Error analysis: `lexical` (dev)

133 errors out of 300 claims.

| bucket | count | meaning |
|---|---|---|
| FALSE_SUPPORT | 21 | Predicted SUPPORT but gold is not SUPPORT (most harmful: false confidence) |
| WRONG_DIRECTION | 36 | SUPPORT <-> CONTRADICT flipped |
| RETRIEVAL_MISS | 15 | Gold paper was not among the k papers judged (retrieval failure, not the verifier's fault) |
| MISSED_BY_VERIFIER | 48 | Gold paper was retrieved but we answered NOT ENOUGH EVIDENCE (abstained or classified neutral) |
| FALSE_CONTRADICT | 13 | Predicted CONTRADICT but gold is NEI |

## FALSE_SUPPORT
Predicted SUPPORT but gold is not SUPPORT (most harmful: false confidence)

**#623** gold `NEI` -> pred `SUPPORT` (conf 0.83)  
claim: Individuals with low serum vitamin D concentrations have increased risk of multiple sclerosis.  
gold paper(s): (none, NEI)  
top retrieved: Low serum vitamin D is associated with high risk of diabetes in Korean adults.  
sentences the verifier saw: A low vitamin D level has been associated with increased risk of diabetes mellitus, but the association has not been confirmed in Asians. | Compared to individuals with a sufficient serum 25(OH)D concentration ≥75 nmol/L, the OR (95% CI) for diabetes mellitus were 1.73 (1.09-2.74), 1.30 (0.91-1.84), and 1.40 (0.99-1.98) for serum 25(OH)D concentrations <25, 25 to <50, and 50 to <75 nmol/L, respectively, after multiple adjustments (P-trend < 0.0001). | In conclusion, a low serum vitamin D concentration is associated with a high risk of diabetes mellitus in Korean adults and the concentration is inversely associated with insulin resistance in those who are overweight or obese.  
gold rationale: -  
your category: _______

**#410** gold `NEI` -> pred `SUPPORT` (conf 0.79)  
claim: Febrile seizures increase the threshold for development of epilepsy.  
gold paper(s): (none, NEI)  
top retrieved: Febrile seizures in the developing brain result in persistent modification of neuronal excitability in limbic circuits  
sentences the verifier saw: Febrile (fever-induced) seizures affect 3–5% of infants and young children. | Despite the high incidence of febrile seizures, their contribution to the development of epilepsy later in life has remained controversial. | Combining a new rat model of complex febrile seizures and patch clamp techniques, we determined that hyperthermia-induced seizures in the immature rat cause a selective presynaptic increase in inhibitory synaptic transmission in the hippocampus that lasts into adulthood.  
gold rationale: -  
your category: _______

**#644** gold `NEI` -> pred `SUPPORT` (conf 0.79)  
claim: Insulin increases risk of severe kidney failure.  
gold paper(s): (none, NEI)  
top retrieved: Diabetes treatments and risk of amputation, blindness, severe kidney failure, hyperglycaemia, and hypoglycaemia: open cohort study in primary care  
sentences the verifier saw: OBJECTIVE To assess the risks of amputation, blindness, severe kidney failure, hyperglycaemia, and hypoglycaemia in patients with type 2 diabetes associated with prescribed diabetes drugs, particularly newer agents including gliptins or glitazones (thiazolidinediones).   
 | MAIN OUTCOME MEASURES First recorded diagnoses of amputation, blindness, severe kidney failure, hyperglycaemia, and hypoglycaemia recorded on patients' primary care, mortality, or hospital records. | Although the numbers of patients prescribed gliptin monotherapy or glitazones monotherapy were relatively low, there were significantly increased risks of severe kidney failure compared with metformin monotherapy (adjusted hazard ratio 2.55, 95% confidence interval 1.13 to 5.74).  
gold rationale: -  
your category: _______

**#268** gold `NEI` -> pred `SUPPORT` (conf 0.77)  
claim: Cold exposure increases BAT recruitment.  
gold paper(s): (none, NEI)  
top retrieved: Sestrin2 inhibits uncoupling protein 1 expression through suppressing reactive oxygen species.  
sentences the verifier saw: Uncoupling protein 1 (Ucp1), which is localized in the mitochondrial inner membrane of mammalian brown adipose tissue (BAT), generates heat by uncoupling oxidative phosphorylation. | Upon cold exposure or nutritional abundance, sympathetic neurons stimulate BAT to express Ucp1 to induce energy dissipation and thermogenesis. | Transgenic overexpression of Sestrin2 in adipose tissues inhibited both basal and cold-induced Ucp1 expression in interscapular BAT, culminating in decreased thermogenesis and increased fat accumulation.  
gold rationale: -  
your category: _______

**#312** gold `NEI` -> pred `SUPPORT` (conf 0.73)  
claim: De novo assembly of sequence data has more specific contigs than unassembled sequence data.  
gold paper(s): (none, NEI)  
top retrieved: Effects of GC Bias in Next-Generation-Sequencing Data on De Novo Genome Assembly  
sentences the verifier saw: Data on the genome sizes and the phylogeny of Genlisea suggest that this is a derived state within the genus. | RESULTS Here we report sequencing and de novo draft assembly of G. aurea genome. | The assembly consists of 10,687 contigs of the total length of 43.4 Mb and includes 17,755 complete and partial protein-coding genes.  
gold rationale: -  
your category: _______

**#914** gold `NEI` -> pred `SUPPORT` (conf 0.73)  
claim: PPAR-RXRs can be activated by PPAR ligands.  
gold paper(s): (none, NEI)  
top retrieved: Pharmacological correction of a defect in PPARγ signaling ameliorates disease severity in Cftr-deficient mice  
sentences the verifier saw: Here we show that colonic epithelial cells and whole lung tissue from Cftr-deficient mice show a defect in peroxisome proliferator-activated receptor-gamma (PPAR-gamma, encoded by Pparg) function that contributes to a pathological program of gene expression. | Lipidomic analysis of colonic epithelial cells suggests that this defect results in part from reduced amounts of the endogenous PPAR-gamma ligand 15-keto-prostaglandin E(2) (15-keto-PGE(2)). | Treatment of Cftr-deficient mice with the synthetic PPAR-gamma ligand rosiglitazone partially normalizes the altered gene expression pattern associated with Cftr deficiency and reduces disease severity.  
gold rationale: -  
your category: _______

**#975** gold `NEI` -> pred `SUPPORT` (conf 0.73)  
claim: Primary pro-inflammatory cytokines induce secondary pro- and anti-inflammatory mediators.  
gold paper(s): (none, NEI)  
top retrieved: High-Density Lipoproteins Exert Pro-inflammatory Effects on Macrophages via Passive Cholesterol Depletion and PKC-NF-κB/STAT1-IRF1 Signaling.  
sentences the verifier saw: Here we show overt pro-inflammatory effects of HDL-mediated passive cholesterol depletion and lipid raft disruption in murine and human primary macrophages in vitro. | These pro-inflammatory effects were confirmed in vivo in peritoneal macrophages from apoA-I transgenic mice, which have elevated HDL levels. | Expression analysis, ChIP-PCR, and combinatorial pharmacological and genetic intervention studies unveiled that both native and reconstituted HDL enhance Toll-like-receptor-induced signaling by activating a PKC-NF-κB/STAT1-IRF1 axis, leading to increased inflammatory cytokine expression.  
gold rationale: -  
your category: _______

**#1099** gold `NEI` -> pred `SUPPORT` (conf 0.73)  
claim: Statins decrease blood cholesterol.  
gold paper(s): (none, NEI)  
top retrieved: Pleiotropic effects of statins.  
sentences the verifier saw: Statins decrease hepatic cholesterol biosynthesis and may therefore lower the risk of cholesterol gallstones by reducing the cholesterol concentration in the bile. | OBJECTIVE To study the association between the use of statins, fibrates, or other lipid-lowering agents and the risk of incident gallstone disease followed by cholecystectomy.   
 | CONCLUSION Long-term use of statins was associated with a decreased risk of gallstones followed by cholecystectomy.  
gold rationale: -  
your category: _______

**#213** gold `NEI` -> pred `SUPPORT` (conf 0.72)  
claim: CRP is not predictive of postoperative mortality following Coronary Artery Bypass Graft (CABG) surgery.  
gold paper(s): (none, NEI)  
top retrieved: Preoperative C-reactive protein predicts long-term mortality and hospital length of stay after primary, nonemergent coronary artery bypass grafting.  
sentences the verifier saw: We examine the value of preoperative CRP levels less than 10 mg/l for predicting long-term, all-cause mortality and hospital length of stay in surgical patients undergoing primary, nonemergent coronary artery bypass graft-only surgery.   
 | METHODS We examined the association between preoperative CRP levels stratified into four categories (< 1, 1-3, 3-10, and > 10 mg/l), and 7-yr all-cause mortality and hospital length of stay in 914 prospectively enrolled primary, nonemergent coronary artery bypass graft-only surgical patients using a proportional hazards regression model.   
 | CONCLUSION We demonstrate that preoperative CRP levels as low as 3 mg/l are associated with increased long-term mortality and extended hospital length of stay in relatively lower-acuity patients undergoing primary, nonemergent coronary artery bypass graft-only surgery.  
gold rationale: -  
your category: _______

**#232** gold `NEI` -> pred `SUPPORT` (conf 0.71)  
claim: Cataract and trachoma are the primary cause of blindness in Southern Sudan.  
gold paper(s): (none, NEI)  
top retrieved: The Burden of Trachoma in Ayod County of Southern Sudan  
sentences the verifier saw: BACKGROUND Blindness due to trachoma is avoidable through Surgery, Antibiotics, Facial hygiene and Environmental improvements (SAFE). | Recent surveys have shown trachoma to be a serious cause of blindness in Southern Sudan. | The high prevalence of active trachoma and trichiasis confirms the severe burden of blinding trachoma found in other post-conflict areas of Southern Sudan.  
gold rationale: -  
your category: _______

**#535** gold `NEI` -> pred `SUPPORT` (conf 0.71)  
claim: Hypertension is frequently observed in type 1 diabetes patients.  
gold paper(s): (none, NEI)  
top retrieved: Prevention of Type 2 Diabetes Mellitus Through Inhibition of the Renin-Angiotensin System  
sentences the verifier saw: The importance of protecting the body from hyperglycemia cannot be overstated; the direct and indirect effects on the human vascular tree are the major source of morbidity and mortality in both type 1 and type 2 diabetes. | It is responsible for ∼ 10,000 new cases of blindness every year in the United States alone.1 The risk of developing diabetic retinopathy or other microvascular complications of diabetes depends on both the duration and the severity of hyperglycemia. | Development of diabetic retinopathy in patients with type 2 diabetes was found to be related to both severity of hyperglycemia and presence of hypertension in the U.K. Prospective Diabetes Study (UKPDS), and most patients with type 1 diabetes develop evidence of retinopathy within 20 years of diagnosis.2,3 Retinopathy may begin to develop as early as 7 years before the diagnosis of diabetes in patients with type 2 diabetes.1 There are several proposed pathological mechanisms by which diabetes may lead …  
gold rationale: -  
your category: _______

**#1279** gold `NEI` -> pred `SUPPORT` (conf 0.70)  
claim: The treatment of cancer patients with co-IR blockade precipitates adverse autoimmune events.  
gold paper(s): (none, NEI)  
top retrieved: In vitro characterization of the anti-PD-1 antibody nivolumab, BMS-936558, and in vivo toxicology in non-human primates.  
sentences the verifier saw: The programmed death-1 (PD-1) receptor serves as an immunologic checkpoint, limiting bystander tissue damage and preventing the development of autoimmunity during inflammatory responses. | In patients with cancer, the expression of PD-1 on tumor-infiltrating lymphocytes and its interaction with the ligands on tumor and immune cells in the tumor microenvironment undermine antitumor immunity and support its rationale for PD-1 blockade in cancer immunotherapy. | Nivolumab treatment did not induce adverse immune-related events when given to cynomolgus macaques at high concentrations, independent of circulating anti-nivolumab antibodies where observed.  
gold rationale: -  
your category: _______

**#552** gold `NEI` -> pred `SUPPORT` (conf 0.69)  
claim: IgA plasma cells that are specific for transglutaminase 2 accumulate in the duodenal mucosa on commencement of a gluten-free diet.  
gold paper(s): (none, NEI)  
top retrieved: High abundance of plasma cells secreting transglutaminase 2–specific IgA autoantibodies with limited somatic hypermutation in celiac disease intestinal lesions  
sentences the verifier saw: Celiac disease is an immune-mediated disorder in which mucosal autoantibodies to the enzyme transglutaminase 2 (TG2) are generated in response to the exogenous antigen gluten in individuals who express human leukocyte antigen HLA-DQ2 or HLA-DQ8 (ref. | We assessed in a comprehensive and nonbiased manner the IgA anti-TG2 response by expression cloning of the antibody repertoire of ex vivo–isolated intestinal antibody-secreting cells (ASCs). | We found that TG2-specific plasma cells are markedly expanded within the duodenal mucosa in individuals with active celiac disease.  
gold rationale: -  
your category: _______

**#517** gold `NEI` -> pred `SUPPORT` (conf 0.68)  
claim: High levels of copeptin decrease risk of diabetes.  
gold paper(s): (none, NEI)  
top retrieved: Changes in plasma copeptin, the c-terminal portion of arginine vasopressin during water deprivation and excess in healthy subjects.  
sentences the verifier saw: A low vitamin D level has been associated with increased risk of diabetes mellitus, but the association has not been confirmed in Asians. | Our objective was to examine the association of serum 25-hydroxyvitamin D [25(OH)D] levels with insulin resistance and diabetes mellitus in Korean adults based on a large population-based survey. | In conclusion, a low serum vitamin D concentration is associated with a high risk of diabetes mellitus in Korean adults and the concentration is inversely associated with insulin resistance in those who are overweight or obese.  
gold rationale: -  
your category: _______

**#554** gold `NEI` -> pred `SUPPORT` (conf 0.66)  
claim: Immune complex triggered cell death leads to extracellular release of neutrophil protein HMGB1.  
gold paper(s): (none, NEI)  
top retrieved: Neutrophil extracellular traps: Is immunity the second function of chromatin?  
sentences the verifier saw: Systemic lupus erythematosus (SLE) is a systemic autoimmune disease characterized by a breakdown of tolerance to nuclear antigens and the development of immune complexes. | Here, we show that mature SLE neutrophils are primed in vivo by type I IFN and die upon exposure to SLE-derived anti-ribonucleoprotein antibodies, releasing neutrophil extracellular traps (NETs). | SLE NETs contain DNA as well as large amounts of LL37 and HMGB1, neutrophil proteins that facilitate the uptake and recognition of mammalian DNA by plasmacytoid DCs (pDCs).  
gold rationale: -  
your category: _______


## WRONG_DIRECTION
SUPPORT <-> CONTRADICT flipped

**#179** gold `SUPPORT` -> pred `CONTRADICT` (conf 0.90)  
claim: Birth-weight is positively associated with breast cancer.  
gold paper(s): Birth Size and Breast Cancer Risk: Re-analysis of Individual Participant Data from 32 Studies; Role of birthweight in the etiology of breast cancer.; Intrauterine factors and risk of breast cancer: a systematic review and meta-analysis of current evidence.; Intrauterine environments and breast cancer risk: meta-analysis and systematic review  
top retrieved: Pregnancy characteristics and maternal risk of breast cancer.  
sentences the verifier saw: OBJECTIVE To examine associations between indirect markers of hormonal exposures, such as placental weight and other pregnancy characteristics, and maternal risk of developing breast cancer.   
 | A high birth weight (> or =4000 g) in 2 successive births was associated with an increased risk of breast cancer before but not after adjusting for placental weight and other covariates (adjusted hazard ratio, 1.10; 95% CI, 0.76-1.59).   
 | CONCLUSIONS Placental weight is positively associated with maternal risk of breast cancer.  
gold rationale: Birth weight was positively associated with breast cancer risk in studies based on birth records (pooled relative risk [RR] per one standard deviation [SD] [= 0.5 kg] increment in birth weight: 1.06; 95% confidence interval [CI] 1.02-1.09) and parental recall when the participants were children (1.02; 95% CI 0.99-1.05), but not in those based on adult self-reports, or maternal recall during the woman's adulthood (0.98; 95% CI 0.95-1.01) (p for heterogeneity between data sources = 0.003). | Relative to women who weighed 3.000-3.499 kg, the risk was 0.96 (CI 0.80-1.16) in those who weighed < 2.500 kg, and 1.12 (95% CI 1.00-1.25) in those who weighed > or = 4.000 kg (p for linear trend = 0.001) in birth record data. | CONCLUSIONS This pooled analysis of individual participant data is consistent with birth size, and in particular birth length, being an independent correlate of breast cancer risk in adulthood. | The majority of studies identified a positive link between birthweight and premenopausal, but not postmenopausal, breast cancer. | The relative risk estimate for breast cancer comparing women with high birthweight to women with low birthweight combining all studies including both pre- and postmenopausal breast cancer was 1.23 (95% confidence interval 1.13-1.34). | Increased risk of breast cancer was noted with increased birthweight (relative risk [RR] 1.15 [95% CI 1.09-1.21]), birth length (1.28 [1.11-1.48]), higher maternal age (1.13 [1.02-1.25]), and paternal age (1.12 [1.05-1.19]). | RESULTS We found that heavier birth weights were associated with increased breast cancer risk, with studies involving five categories of birth weight identifying odds ratios (ORs) of 1.24 (95% confidence interval [CI] 1.04 to 1.48) for 4,000 g or more and 1.15 (95% CI 1.04 to 1.26) for 3,500 g to 3,999 g, relative to a birth weight of 2,500 to 2,599 g. These studies provided no support for a J-shaped relationship of birthweight to risk. | CONCLUSION Our findings provide some support for the hypothesis that in utero exposures reflective of higher endogenous hormone levels could affect risk for development of breast cancer in adulthood.  
your category: _______

**#327** gold `SUPPORT` -> pred `CONTRADICT` (conf 0.90)  
claim: Deletion of αvβ8 does not result in a spontaneous inflammatory phenotype.  
gold paper(s): Integrin αvβ8-Mediated TGF-β Activation by Effector Regulatory T Cells Is Essential for Suppression of T-Cell-Mediated Inflammation  
top retrieved: Integrin αvβ8-Mediated TGF-β Activation by Effector Regulatory T Cells Is Essential for Suppression of T-Cell-Mediated Inflammation  
sentences the verifier saw: Here we show that effector Treg cells express high amounts of the integrin αvβ8, which enables them to activate latent transforming growth factor-β (TGF-β). | Treg-cell-specific deletion of integrin αvβ8 did not result in a spontaneous inflammatory phenotype, suggesting that this pathway is not important in Treg-cell-mediated maintenance of immune homeostasis. | However, Treg cells lacking expression of integrin αvβ8 were unable to suppress pathogenic T cell responses during active inflammation.  
gold rationale: Treg-cell-specific deletion of integrin αvβ8 did not result in a spontaneous inflammatory phenotype, suggesting that this pathway is not important in Treg-cell-mediated maintenance of immune homeostasis.  
your category: _______

**#338** gold `CONTRADICT` -> pred `SUPPORT` (conf 0.90)  
claim: Dexamethasone decreases risk of postoperative bleeding.  
gold paper(s): Dexamethasone and risk of nausea and vomiting and postoperative bleeding after tonsillectomy in children: a randomized trial.  
top retrieved: Dexamethasone and risk of nausea and vomiting and postoperative bleeding after tonsillectomy in children: a randomized trial.  
sentences the verifier saw: children who received placebo had bleeding compared with 6 of 53 (11%; 95% CI, 4%-23%), 2 of 51 (4%; 95% CI, 0.5%-13%), and 12 of 50 (24%; 95% CI, 13%-38%) who received dexamethasone at 0.05, 0.15, and 0.5 mg/kg, respectively (P = .003). | Dexamethasone, 0.5 mg/kg, was associated with the highest bleeding risk (adjusted relative risk, 6.80; 95% CI, 1.77-16.5). | CONCLUSION In this study of children undergoing tonsillectomy, dexamethasone decreased the risk of PONV dose dependently but was associated with an increased risk of postoperative bleeding.   
  
gold rationale: Two of 53 (4%; 95% CI, 0.5%-13%) | children who received placebo had bleeding compared with 6 of 53 (11%; 95% CI, 4%-23%), 2 of 51 (4%; 95% CI, 0.5%-13%), and 12 of 50 (24%; 95% CI, 13%-38%) who received dexamethasone at 0.05, 0.15, and 0.5 mg/kg, respectively (P = .003). | Dexamethasone, 0.5 mg/kg, was associated with the highest bleeding risk (adjusted relative risk, 6.80; 95% CI, 1.77-16.5). | CONCLUSION In this study of children undergoing tonsillectomy, dexamethasone decreased the risk of PONV dose dependently but was associated with an increased risk of postoperative bleeding.   
  
your category: _______

**#597** gold `SUPPORT` -> pred `CONTRADICT` (conf 0.90)  
claim: Incidence rates of cervical cancer have decreased.  
gold paper(s): Effect of screening on cervical cancer mortality in England and Wales: analysis of trends with an age period cohort model.; The effect of mass screening on incidence and mortality of squamous and adenocarcinoma of cervix uteri.; Mass screening programmes and trends in cervical cancer in Finland and the Netherlands.  
top retrieved: The effect of mass screening on incidence and mortality of squamous and adenocarcinoma of cervix uteri.  
sentences the verifier saw: OBJECTIVE To describe the efficacy of the Finnish mass screening program for cervical squamous carcinoma and adenocarcinoma, as reflected by changes of incidence and mortality rate.   
 | METHODS Cervical cancer incidence and mortality data were obtained from the Finnish Cancer Registry. | Thus, it might be possible to decrease the incidence of cervical adenocarcinoma.  
gold rationale: The number of women dying from cervical cancer in 1997 was 7% lower than in 1996 and has fallen by over 25% since 1992.1 Such rapid change must be at least partly due to cervical screening, although strong cohort effects have caused large fluctuations in cervical mortality in the past.2 We modelled mortality data, taking into account the effects of age and year of birth and looking for trends in time within four age groups to estimate the beneficial effects of cervical screening.   | RESULTS The mean incidence of cervical carcinoma in the early 1960s was 15.4 per 10(5) woman-years. | In 1991, it was only 2.7 per 10(5) woman-years. | Incidence and mortality rates have declined more in Finland.  
your category: _______

**#1137** gold `CONTRADICT` -> pred `SUPPORT` (conf 0.90)  
claim: TNFAIP3 is a tumor suppressor in glioblastoma.  
gold paper(s): Targeting A20 Decreases Glioma Stem Cell Survival and Tumor Growth  
top retrieved: Targeting A20 Decreases Glioma Stem Cell Survival and Tumor Growth  
sentences the verifier saw: Glioblastomas are deadly cancers that display a functional cellular hierarchy maintained by self-renewing glioblastoma stem cells (GSCs). | We determined that A20 (TNFAIP3), a regulator of cell survival and the NF-kappaB pathway, is overexpressed in GSCs relative to non-stem glioblastoma cells at both the mRNA and protein levels. | Although inactivating mutations in A20 in lymphoma suggest A20 can act as a tumor suppressor, similar point mutations have not been identified through glioma genomic sequencing: in fact, our data suggest A20 may function as a tumor enhancer in glioma through promotion of GSC survival.  
gold rationale: The tumorigenic potential of GSCs was decreased with A20 targeting, resulting in increased survival of mice bearing human glioma xenografts. | Although inactivating mutations in A20 in lymphoma suggest A20 can act as a tumor suppressor, similar point mutations have not been identified through glioma genomic sequencing: in fact, our data suggest A20 may function as a tumor enhancer in glioma through promotion of GSC survival.  
your category: _______

**#380** gold `SUPPORT` -> pred `CONTRADICT` (conf 0.83)  
claim: Enhanced early production of inflammatory chemokines improves viral control in the lung.  
gold paper(s): Memory CD4+ T cells induce innate responses independently of pathogen  
top retrieved: Memory CD4+ T cells induce innate responses independently of pathogen  
sentences the verifier saw: We found that the response of memory, but not naive, CD4+ T cells enhances production of multiple innate inflammatory cytokines and chemokines (IICs) in the lung and that, during influenza infection, this leads to early control of virus. | Memory CD4+ T cell–induced IICs and viral control require cognate antigen recognition and are optimal when memory cells are either T helper type 1 (TH1) or TH17 polarized but are independent of interferon-γ (IFN-γ) and tumor necrosis factor-α (TNF-α) production and do not require activation of conserved pathogen recognition pathways. | This represents a previously undescribed mechanism by which memory CD4+ T cells induce an early innate response that enhances immune protection against pathogens.  
gold rationale: We found that the response of memory, but not naive, CD4+ T cells enhances production of multiple innate inflammatory cytokines and chemokines (IICs) in the lung and that, during influenza infection, this leads to early control of virus.  
your category: _______

**#1270** gold `CONTRADICT` -> pred `SUPPORT` (conf 0.82)  
claim: The risk of male prisoners harming themselves is ten times that of female prisoners.  
gold paper(s): Self-harm in prisons in England and Wales: an epidemiological study of prevalence, risk factors, clustering, and subsequent suicide  
top retrieved: Self-harm in prisons in England and Wales: an epidemiological study of prevalence, risk factors, clustering, and subsequent suicide  
sentences the verifier saw: FINDINGS 139,195 self-harm incidents were recorded in 26,510 individual prisoners between 2004 and 2009; 5-6% of male prisoners and 20-24% of female inmates self-harmed every year. | Self-harm rates were more than ten times higher in female prisoners than in male inmates. | Risk factors for suicide after self-harm in male prisoners were older age and a previous self-harm incident of high or moderate lethality; in female inmates, a history of more than five self-harm incidents within a year was associated with subsequent suicide.   
  
gold rationale: FINDINGS 139,195 self-harm incidents were recorded in 26,510 individual prisoners between 2004 and 2009; 5-6% of male prisoners and 20-24% of female inmates self-harmed every year. | Self-harm rates were more than ten times higher in female prisoners than in male inmates.  
your category: _______

**#51** gold `CONTRADICT` -> pred `SUPPORT` (conf 0.80)  
claim: ALDH1 expression is associated with better breast cancer outcomes.  
gold paper(s): ALDH1 is a marker of normal and malignant human mammary stem cells and a predictor of poor clinical outcome.  
top retrieved: ALDH1 is a marker of normal and malignant human mammary stem cells and a predictor of poor clinical outcome.  
sentences the verifier saw: Overexpression of PD-L1 in cancers such as gastric cancer, hepatocellular carcinoma, renal cell carcinoma, esophageal cancer, pancreatic cancer, ovarian cancer, and bladder cancer is associated with poor clinical outcomes. | In contrast, PD-L1 expression correlates with better clinical outcomes in breast cancer and merkel cell carcinoma. | The prognostic value of PD-L1 expression in lung cancer, colorectal cancer, and melanoma is controversial.  
gold rationale: In a series of 577 breast carcinomas, expression of ALDH1 detected by immunostaining correlated with poor prognosis.  
your category: _______

**#922** gold `CONTRADICT` -> pred `SUPPORT` (conf 0.80)  
claim: Patients in stable partnerships have a faster progression from HIV to AIDS.  
gold paper(s): Stable partnership and progression to AIDS or death in HIV infected patients receiving highly active antiretroviral therapy: Swiss HIV cohort study.  
top retrieved: Stable partnership and progression to AIDS or death in HIV infected patients receiving highly active antiretroviral therapy: Swiss HIV cohort study.  
sentences the verifier saw: OBJECTIVES To explore the association between a stable partnership and clinical outcome in HIV infected patients receiving highly active antiretroviral therapy (HAART).   
 | In an analysis stratified by previous antiretroviral therapy and clinical stage when starting HAART (US Centers for Disease Control and Prevention group A, B, or C), the adjusted hazard ratio for progression to AIDS or death was 0.79 (95% confidence interval 0.63 to 0.98) for participants with a stable partnership compared with those without. | CONCLUSIONS A stable partnership is associated with a slower rate of progression to AIDS or death in HIV infected patients receiving HAART.  
gold rationale: In an analysis stratified by previous antiretroviral therapy and clinical stage when starting HAART (US Centers for Disease Control and Prevention group A, B, or C), the adjusted hazard ratio for progression to AIDS or death was 0.79 (95% confidence interval 0.63 to 0.98) for participants with a stable partnership compared with those without. | CONCLUSIONS A stable partnership is associated with a slower rate of progression to AIDS or death in HIV infected patients receiving HAART.  
your category: _______

**#163** gold `SUPPORT` -> pred `CONTRADICT` (conf 0.79)  
claim: Bariatric surgery has a positive impact on mental health.  
gold paper(s): Mental Health Conditions Among Patients Seeking and Undergoing Bariatric Surgery: A Meta-analysis.  
top retrieved: Mental Health Conditions Among Patients Seeking and Undergoing Bariatric Surgery: A Meta-analysis.  
sentences the verifier saw: Health-related psychological and psychosocial variables have been increasingly considered as important outcome variables of bariatric surgery. | However, the long-term impact of bariatric surgery on psychological and psychosocial functioning is largely unclear. | Corresponding to the considerable weight loss after bariatric surgery, important aspects of mental health improved significantly during the 4-year follow-up period.  
gold rationale: Bariatric surgery was, however, consistently associated with postoperative decreases in the prevalence of depression (7 studies; 8%-74% decrease) and the severity of depressive symptoms (6 studies; 40%-70% decrease).   
 | Moderate-quality evidence supports an association between bariatric surgery and lower rates of depression postoperatively.  
your category: _______

**#536** gold `SUPPORT` -> pred `CONTRADICT` (conf 0.79)  
claim: Hypocretin neurones induce panicprone state in rats.  
gold paper(s): A KEY ROLE FOR OREXIN IN PANIC ANXIETY  
top retrieved: A KEY ROLE FOR OREXIN IN PANIC ANXIETY  
sentences the verifier saw: In a rat model of panic disorder, chronic inhibition of GABA synthesis in the dorsomedial-perifornical hypothalamus of rats produces anxiety-like states and a similar vulnerability to sodium lactate-induced cardioexcitatory responses. | The dorsomedial-perifornical hypothalamus is enriched in neurons containing orexin (ORX, also known as hypocretin), which have a crucial role in arousal, vigilance and central autonomic mobilization, all of which are key components of panic. | Here we show that activation of ORX-synthesizing neurons is necessary for developing a panic-prone state in the rat panic model, and either silencing of the hypothalamic gene encoding ORX (Hcrt) with RNAi or systemic ORX-1 receptor antagonists blocks the panic responses.  
gold rationale: Here we show that activation of ORX-synthesizing neurons is necessary for developing a panic-prone state in the rat panic model, and either silencing of the hypothalamic gene encoding ORX (Hcrt) with RNAi or systemic ORX-1 receptor antagonists blocks the panic responses.  
your category: _______

**#613** gold `SUPPORT` -> pred `CONTRADICT` (conf 0.79)  
claim: Increased microtubule acetylation repairs LRRK2 Roc-COR domain mutation induced locomotor deficits.  
gold paper(s): Increasing microtubule acetylation rescues axonal transport and locomotor deficits caused by LRRK2 Roc-COR domain mutations  
top retrieved: Increasing microtubule acetylation rescues axonal transport and locomotor deficits caused by LRRK2 Roc-COR domain mutations  
sentences the verifier saw: Defective microtubule-based axonal transport is hypothesized to contribute to Parkinson's disease, but whether LRRK2 mutations affect this process to mediate pathogenesis is not known. | Here we find that LRRK2 containing pathogenic Roc-COR domain mutations (R1441C, Y1699C) preferentially associates with deacetylated microtubules, and inhibits axonal transport in primary neurons and in Drosophila, causing locomotor deficits in vivo. | In vitro, increasing microtubule acetylation using deacetylase inhibitors or the tubulin acetylase αTAT1 prevents association of mutant LRRK2 with microtubules, and the deacetylase inhibitor trichostatin A (TSA) restores axonal transport.  
gold rationale: In vitro, increasing microtubule acetylation using deacetylase inhibitors or the tubulin acetylase αTAT1 prevents association of mutant LRRK2 with microtubules, and the deacetylase inhibitor trichostatin A (TSA) restores axonal transport.  
your category: _______

**#1180** gold `SUPPORT` -> pred `CONTRADICT` (conf 0.79)  
claim: The PRR MDA5 is a sensor of RNA virus infection.  
gold paper(s): Immune signaling by RIG-I-like receptors.  
top retrieved: Loss of DExD/H box RNA helicase LGP2 manifests disparate antiviral responses.  
sentences the verifier saw: Double-stranded RNA (dsRNA) produced during viral replication is believed to be the critical trigger for activation of antiviral immunity mediated by the RNA helicase enzymes retinoic acid-inducible gene I (RIG-I) and melanoma differentiation-associated gene 5 (MDA5). | We showed that influenza A virus infection does not generate dsRNA and that RIG-I is activated by viral genomic single-stranded RNA (ssRNA) bearing 5'-phosphates. | These results identify RIG-I as a ssRNA sensor and potential target of viral immune evasion and suggest that its ability to sense 5'-phosphorylated RNA evolved in the innate immune system as a means of discriminating between self and nonself.  
gold rationale: The RIG-I-like receptors (RLRs) RIG-I, MDA5, and LGP2 play a major role in pathogen sensing of RNA virus infection to initiate and modulate antiviral immunity.  
your category: _______

**#1385** gold `SUPPORT` -> pred `CONTRADICT` (conf 0.79)  
claim: cSMAC formation enhances weak ligand signalling.  
gold paper(s): The stimulatory potency of T cell antigens is influenced by the formation of the immunological synapse.  
top retrieved: The stimulatory potency of T cell antigens is influenced by the formation of the immunological synapse.  
sentences the verifier saw: We describe results showing that a peptide exhibiting many hallmarks of a weak agonist stimulates T cells to proliferate more than the wild-type agonist ligand. | An in silico approach suggested that the inability to form the central supramolecular activation cluster (cSMAC) could underlie the increased proliferation. | This conclusion was supported by experiments that showed that enhancing cSMAC formation reduced stimulatory capacity of the weak peptide.  
gold rationale: This conclusion was supported by experiments that showed that enhancing cSMAC formation reduced stimulatory capacity of the weak peptide.  
your category: _______

**#1144** gold `CONTRADICT` -> pred `SUPPORT` (conf 0.78)  
claim: Taxation of sugar-sweetened beverages had no effect on the incidence rate of type II diabetes in India.  
gold paper(s): Averting Obesity and Type 2 Diabetes in India through Sugar-Sweetened Beverage Taxation: An Economic-Epidemiologic Modeling Study  
top retrieved: Averting Obesity and Type 2 Diabetes in India through Sugar-Sweetened Beverage Taxation: An Economic-Epidemiologic Modeling Study  
sentences the verifier saw: BACKGROUND Taxing sugar-sweetened beverages (SSBs) has been proposed in high-income countries to reduce obesity and type 2 diabetes. | However, acceleration in SSB consumption trends consistent with industry marketing models would be expected to increase the impact efficacy of taxation, averting 4.2% of prevalent overweight/obesity (95% CI 2.5-10.0%) and 2.5% (95% CI 1.0-2.8%) of incident type 2 diabetes from 2014-2023. | CONCLUSION Sustained SSB taxation at a high tax rate could mitigate rising obesity and type 2 diabetes in India among both urban and rural subpopulations.  
gold rationale: The 20% SSB tax was anticipated to reduce overweight and obesity prevalence by 3.0% (95% CI 1.6%-5.9%) and type 2 diabetes incidence by 1.6% (95% CI 1.2%-1.9%) among various Indian subpopulations over the period 2014-2023, if SSB consumption continued to increase linearly in accordance with secular trends. | However, acceleration in SSB consumption trends consistent with industry marketing models would be expected to increase the impact efficacy of taxation, averting 4.2% of prevalent overweight/obesity (95% CI 2.5-10.0%) and 2.5% (95% CI 1.0-2.8%) of incident type 2 diabetes from 2014-2023. | CONCLUSION Sustained SSB taxation at a high tax rate could mitigate rising obesity and type 2 diabetes in India among both urban and rural subpopulations.  
your category: _______


## RETRIEVAL_MISS
Gold paper was not among the k papers judged (retrieval failure, not the verifier's fault)

**#475** gold `SUPPORT` -> pred `NEI` (conf 0.90)  
claim: Glycolysis is one of the primary glycometabolic pathways in cells.  
gold paper(s): Vesicular Glycolysis Provides On-Board Energy for Fast Axonal Transport  
top retrieved: Metabolic interplay between glycolysis and mitochondrial oxidation: The reverse Warburg effect and its therapeutic implication.  
sentences the verifier saw: Aerobic glycolysis, i.e., the Warburg effect, may contribute to the aggressive phenotype of hepatocellular carcinoma. | However, increasing evidence highlights the limitations of the Warburg effect, such as high mitochondrial respiration and low glycolysis rates in cancer cells. | Aerobic glycolysis may also occur in the stromal compartment that surrounds the tumor; thus, the stromal cells feed the cancer cells with lactate and this interaction prevents the creation of an acidic condition in the tumor microenvironment.  
gold rationale: We demonstrate that glycolysis provides ATP for the FAT of vesicles.  
your category: _______

**#1382** gold `CONTRADICT` -> pred `NEI` (conf 0.48)  
claim: aPKCz causes tumour enhancement by affecting glutamine metabolism.  
gold paper(s): Control of Nutrient Stress-Induced Metabolic Reprogramming by PKCζ in Tumorigenesis  
top retrieved: Glutamine supports pancreatic cancer growth through a Kras-regulated metabolic pathway  
sentences the verifier saw: Indeed, the spectrum of glutamine-dependent tumours and the mechanisms whereby glutamine supports cancer metabolism remain areas of active investigation. | Here we report the identification of a non-canonical pathway of glutamine use in human pancreatic ductal adenocarcinoma (PDAC) cells that is required for tumour growth. | Furthermore, we establish that the reprogramming of glutamine metabolism is mediated by oncogenic KRAS, the signature genetic alteration in PDAC, through the transcriptional upregulation and repression of key metabolic enzymes in this pathway.  
gold rationale: Interestingly, the loss of PKCζ in mice results in enhanced intestinal tumorigenesis and increased levels of these two metabolic enzymes, whereas patients with low levels of PKCζ have a poor prognosis. | Taken together, this demonstrates that PKCζ is a critical metabolic tumor suppressor in mouse and human cancer.  
your category: _______

**#1020** gold `SUPPORT` -> pred `NEI` (conf 0.45)  
claim: Rapid up-regulation and higher basal expression of interferon-induced genes increase survival of granule cell neurons that are infected by West Nile virus.  
gold paper(s): Differential innate immune response programs in neuronal subtypes determine susceptibility to infection in the brain by positive stranded RNA viruses  
top retrieved: Beta interferon controls West Nile virus infection and pathogenesis in mice.  
sentences the verifier saw: Studies with mice lacking the common plasma membrane receptor for type I interferon (IFN-αβR(-)(/)(-)) have revealed that IFN signaling restricts tropism, dissemination, and lethality after infection with West Nile virus (WNV) or several other pathogenic viruses. | Consistent with a direct role for IFN-β in control of WNV replication, viral titers in ex vivo cultures of macrophages, dendritic cells, fibroblasts, and cerebellar granule cell neurons, but not cortical neurons, from IFN-β(-)(/)(-) mice were greater than in wild-type cells. | Although detailed immunological analysis revealed no major deficits in the quality or quantity of WNV-specific antibodies or CD8(+) T cells, we observed an altered CD4(+) CD25(+) FoxP3(+) regulatory T cell response, with greater numbers after infection.  
gold rationale: By transducing cortical neurons with genes that were expressed more highly in granule cell neurons, we identified three interferon-stimulated genes (ISGs; Ifi27, Irg1 and Rsad2 (also known as Viperin)) that mediated the antiviral effects against different neurotropic viruses.  
your category: _______

**#1021** gold `CONTRADICT` -> pred `NEI` (conf 0.45)  
claim: Rapid up-regulation and higher basal expression of interferon-induced genes reduce survival of granule cell neurons that are infected by West Nile virus.  
gold paper(s): Differential innate immune response programs in neuronal subtypes determine susceptibility to infection in the brain by positive stranded RNA viruses  
top retrieved: Beta interferon controls West Nile virus infection and pathogenesis in mice.  
sentences the verifier saw: Studies with mice lacking the common plasma membrane receptor for type I interferon (IFN-αβR(-)(/)(-)) have revealed that IFN signaling restricts tropism, dissemination, and lethality after infection with West Nile virus (WNV) or several other pathogenic viruses. | Consistent with a direct role for IFN-β in control of WNV replication, viral titers in ex vivo cultures of macrophages, dendritic cells, fibroblasts, and cerebellar granule cell neurons, but not cortical neurons, from IFN-β(-)(/)(-) mice were greater than in wild-type cells. | Although detailed immunological analysis revealed no major deficits in the quality or quantity of WNV-specific antibodies or CD8(+) T cells, we observed an altered CD4(+) CD25(+) FoxP3(+) regulatory T cell response, with greater numbers after infection.  
gold rationale: By transducing cortical neurons with genes that were expressed more highly in granule cell neurons, we identified three interferon-stimulated genes (ISGs; Ifi27, Irg1 and Rsad2 (also known as Viperin)) that mediated the antiviral effects against different neurotropic viruses.  
your category: _______

**#385** gold `SUPPORT` -> pred `NEI` (conf 0.43)  
claim: Epigenetic modulating agents (EMAs) modulate antitumor immune response in a cancer model system.  
gold paper(s): Epigenetic Therapy Ties MYC Depletion to Reversing Immune Evasion and Treating Lung Cancer  
top retrieved: Augmenting Antitumor Immune Responses with Epigenetic Modifying Agents  
sentences the verifier saw: Epigenetic silencing of immune-related genes is a striking feature of the cancer genome that occurs in the process of tumorigenesis. | The potential reversal of immunosuppression by epigenetic modulation is therefore a promising and versatile therapeutic approach to reinstate endogenous immune recognition and tumor lysis. | Pre-clinical studies have identified multiple elements of the immune system that can be modulated by epigenetic mechanisms and result in improved antigen presentation, effector T-cell function, and breakdown of suppressor mechanisms.  
gold rationale: Use of this combination treatment schema in mouse models of NSCLC reverses tumor immune evasion and modulates T cell exhaustion state towards memory and effector T cell phenotypes.  
your category: _______

**#540** gold `SUPPORT` -> pred `NEI` (conf 0.43)  
claim: Hypothalamic glutamate neurotransmission is crucial to energy balance.  
gold paper(s): Synaptic glutamate release by ventromedial hypothalamic neurons is part of the neurocircuitry that prevents hypoglycemia.  
top retrieved: Leptin regulates glutamate and glucose transporters in hypothalamic astrocytes.  
sentences the verifier saw: Glial cells perform critical functions that alter the metabolism and activity of neurons, and there is increasing interest in their role in appetite and energy balance. | We found that basal and glucose-stimulated electrical activity of hypothalamic proopiomelanocortin (POMC) neurons in mice were altered in the offspring of mothers fed a high-fat diet. | These results demonstrate that whole-organism metabolism alters hypothalamic glial cell activity and suggest that these cells play an important role in the pathology of obesity.  
gold rationale: These mice have hypoglycemia during fasting secondary to impaired fasting-induced increases in the glucose-raising pancreatic hormone glucagon and impaired induction in liver of mRNAs encoding PGC-1alpha and the gluconeogenic enzymes PEPCK and G6Pase.  
your category: _______

**#1370** gold `CONTRADICT` -> pred `NEI` (conf 0.43)  
claim: Vitamin D deficiency is unrelated to birth weight.  
gold paper(s): Association between maternal serum 25-hydroxyvitamin D level and pregnancy and neonatal outcomes: systematic review and meta-analysis of observational studies.  
top retrieved: Vitamin D: The "sunshine" vitamin.  
sentences the verifier saw: Vitamin D insufficiency affects almost 50% of the population worldwide. | An estimated 1 billion people worldwide, across all ethnicities and age groups, have a vitamin D deficiency (VDD). | This pandemic of hypovitaminosis D can mainly be attributed to lifestyle (for example, reduced outdoor activities) and environmental (for example, air pollution) factors that reduce exposure to sunlight, which is required for ultraviolet-B (UVB)-induced vitamin D production in the skin.  
gold rationale: Pregnant women with low serum 25-OHD levels had an increased risk of bacterial vaginosis and low birthweight infants but not delivery by caesarean section.   
 | Pregnant women with low 25-OHD levels had an increased risk of bacterial vaginosis and lower birth weight infants, but not delivery by caesarean section.  
your category: _______

**#598** gold `CONTRADICT` -> pred `NEI` (conf 0.41)  
claim: Incidence rates of cervical cancer have increased due to nationwide screening programs based primarily on cytology to detect uterine cervical cancer.  
gold paper(s): Mass screening programmes and trends in cervical cancer in Finland and the Netherlands.  
top retrieved: The effect of mass screening on incidence and mortality of squamous and adenocarcinoma of cervix uteri.  
sentences the verifier saw: OBJECTIVE To describe the efficacy of the Finnish mass screening program for cervical squamous carcinoma and adenocarcinoma, as reflected by changes of incidence and mortality rate.   
 | METHODS Cervical cancer incidence and mortality data were obtained from the Finnish Cancer Registry. | The nationwide mass screening program in Finland was started in the mid-1960s.  
gold rationale: Incidence and mortality rates have declined more in Finland. | The decline in mortality in Finland seems to be almost completely related to the screening programme whereas in the Netherlands it was initially considered to be a natural decline.  
your category: _______

**#415** gold `SUPPORT` -> pred `NEI` (conf 0.40)  
claim: Female carriers of the Apolipoprotein E4 (APOE4) allele have increased risk for dementia.  
gold paper(s): Reproductive period and risk of dementia in postmenopausal women.  
top retrieved: Gain of toxic Apolipoprotein E4 effects in Human iPSC-Derived Neurons Is Ameliorated by a Small-Molecule Structure Corrector  
sentences the verifier saw: Using human neurons derived from induced pluripotent stem cells that expressed apolipoprotein E4 (ApoE4), a variant of the APOE gene product and the major genetic risk factor for AD, we demonstrated that ApoE4-expressing neurons had higher levels of tau phosphorylation, unrelated to their increased production of amyloid-β (Aβ) peptides, and that they displayed GABAergic neuron degeneration. | ApoE4 increased Aβ production in human, but not in mouse, neurons. | Converting ApoE4 to ApoE3 by gene editing rescued these phenotypes, indicating the specific effects of ApoE4.  
gold rationale: Risk of dementia associated with a longer reproductive period was most pronounced in APOE epsilon4 carriers (adjusted RR for >39 reproductive years compared with <34 reproductive years, 4.20 [95% CI, 1.97-8.92] for dementia and 3.42 [95% CI, 1.51-7.75] for AD), whereas in noncarriers, no clear association with dementia or AD was observed.   
  
your category: _______

**#1049** gold `CONTRADICT` -> pred `NEI` (conf 0.39)  
claim: Ribosomopathies have a low degree of cell and tissue specific pathology.  
gold paper(s): Ribosome-Mediated Specificity in Hox mRNA Translation and Vertebrate Tissue Patterning  
top retrieved: Growth control and ribosomopathies.  
sentences the verifier saw: Ribosome biogenesis and protein synthesis are two of the most energy consuming processes in a growing cell. | Recent discoveries of causative mutations and deletions in genes linked to ribosome biogenesis have defined a group of similar pathologies termed ribosomopathies. | In this review, we summarize recent advances in understanding the mechanisms underlying the pathologies of ribosomopathies and discuss the relationship between ribosome production and tumorigenesis.  
gold rationale: Unexpectedly, a ribosomal protein (RP) expression screen reveals dynamic regulation of individual RPs within the vertebrate embryo. | Collectively, these findings suggest that RP activity may be highly regulated to impart a new layer of specificity in the control of gene expression and mammalian development.  
your category: _______

**#1221** gold `CONTRADICT` -> pred `NEI` (conf 0.39)  
claim: The genomic aberrations found in matasteses are very similar to those found in the primary tumor.  
gold paper(s): Evolution of metastasis revealed by mutational landscapes of chemically induced skin cancers  
top retrieved: High prevalence of evolutionarily conserved and species-specific genomic aberrations in mouse pluripotent stem cells.  
sentences the verifier saw: We found that genomic aberrations occur frequently in mouse embryonic stem cells of various mouse strains, add in mouse iPSCs of various cell origins and derivation techniques. | Four hotspots of chromosomal aberrations were detected: full trisomy 11 (with a minimally recurrent gain in 11qE2), full trisomy 8, and deletions in chromosomes 10qB and 14qC-14qE. The most recurrent aberration in mouse PSCs, gain 11qE2, turned out to be fully syntenic to the common aberration 17q25 in human PSCs, while other recurrent aberrations were found to be species specific. | Analysis of chromosomal aberrations in 74 samples of rhesus macaque PSCs revealed a gain in chromosome 16q, syntenic to the hotspot in human 17q.  
gold rationale: Shared mutations between primary carcinomas and their matched metastases have the distinct A-to-T signature of the initiating carcinogen dimethylbenzanthracene, but non-shared mutations are primarily G-to-T, a signature associated with oxidative stress.  
your category: _______

**#212** gold `CONTRADICT` -> pred `NEI` (conf 0.37)  
claim: CR is associated with higher methylation age.  
gold paper(s): Caloric restriction delays age-related methylation drift  
top retrieved: Yeast sirtuins and the regulation of aging.  
sentences the verifier saw: Furthermore, Sir2 has been implicated in mediating the beneficial effects of caloric restriction (CR) on life span, not only in yeast, but also in higher eukaryotes. | While this paradigm has had its share of disagreements and debate, it has also helped rapidly drive the aging research field forward. | This review discusses the function of Sir2 and the Hst homologs in replicative aging and chronological aging, and also addresses how the sirtuins are regulated in response to environmental stresses such as CR.  
gold rationale: Epigenetic information encoded by DNA methylation is tightly regulated, but shows a striking drift associated with age that includes both gains and losses of DNA methylation at various sites. | Twenty-two to 30-year-old rhesus monkeys exposed to 30% caloric restriction since 7-14 years of age showed attenuation of age-related methylation drift compared to ad libitum-fed controls such that their blood methylation age appeared 7 years younger than their chronologic age. | Even more pronounced effects were seen in 2.7-3.2-year-old mice exposed to 40% caloric restriction starting at 0.3 years of age. | Caloric restriction has been shown to increase lifespan in mammals. | Here, the authors provide evidence that age-related methylation drift correlates with lifespan and that caloric restriction in mice and rhesus monkeys results in attenuation of age-related methylation drift.  
your category: _______

**#261** gold `SUPPORT` -> pred `NEI` (conf 0.37)  
claim: Chronic aerobic exercise alters endothelial function, improving vasodilating mechanisms mediated by NO.  
gold paper(s): Endothelium-mediated relaxation of porcine collateral-dependent arterioles is improved by exercise training.; Vasodilator responses of coronary resistance arteries of exercise-trained pigs.  
top retrieved: Exercise training-induced adaptations in the coronary circulation.  
sentences the verifier saw: Aerobic exercise training induces an increase in coronary blood flow capacity that is associated with altered control of coronary vascular resistance and, therefore, coronary blood flow. | Also, there is evidence that the mode, frequency, and intensity of exercise training bouts and duration of training may influence the adaptive changes in endothelial function. | Although much remains to be studied, evidence clearly indicates that chronic exercise alters the phenotype of coronary endothelial and vascular smooth muscle cells and that plasticity of these cells plays a role in adaptation of the cardiovascular system in exercise training.  
gold rationale: Relaxation to the endothelium-dependent vasodilator bradykinin was decreased (P<0.05) in arterioles isolated from collateral-dependent LCx versus nonoccluded LAD regions of SED animals. | CONCLUSIONS These data indicate that exercise training enhances bradykinin-mediated relaxation of collateral-dependent LCx arterioles isolated after chronic coronary occlusion, most likely because of effects on ecNOS mRNA expression and increased production of NO. | CONCLUSIONS These results suggest that exercise training enhances bradykinin-induced vasodilation through increased endothelium-derived relaxing factor/nitric oxide production by the L-arginine/nitric oxide synthase pathway.  
your category: _______

**#619** gold `CONTRADICT` -> pred `NEI` (conf 0.37)  
claim: Increased vessel density along with a reduction in fibrosis decreases the efficacy of chemotherapy treatments.  
gold paper(s): Inhibition of Hedgehog signaling enhances delivery of chemotherapy in a mouse model of pancreatic cancer.  
top retrieved: Cell and molecular mechanisms of insulin-induced angiogenesis  
sentences the verifier saw: The appropriate development of new blood vessels, along with their subsequent maturation and differentiation, establishes the foundation for functional wound neovasculature. | Mice skin injected with insulin shows longer vessels with more branches, along with increased numbers of associated alpha-smooth muscle actin-expressing cells, suggesting the appropriate differentiation and maturation of the new vessels. | Our findings strongly suggest that insulin is a good candidate for the treatment of ischaemic wounds and other conditions in which blood vessel development is impaired.  
gold rationale: We tested whether the delivery and efficacy of gemcitabine in the mice could be improved by coadministration of IPI-926, a drug that depletes tumor-associated stromal tissue by inhibition of the Hedgehog cellular signaling pathway. | The combination therapy produced a transient increase in intratumoral vascular density and intratumoral concentration of gemcitabine, leading to transient stabilization of disease.  
your category: _______

**#873** gold `CONTRADICT` -> pred `NEI` (conf 0.37)  
claim: Obesity is determined solely by environmental factors.  
gold paper(s): Genetics of obesity in adult adoptees and their biological siblings.; Familial obesity and leanness.; The body-mass index of twins who have been reared apart.; An adoption study of human obesity.; Genetic analysis of human obesity in an Italian sample.  
top retrieved: Effect of age, sex, and sites on the cellularity of the adipose tissue in mice and rats rendered obese by a high-fat diet.  
sentences the verifier saw: Cell size and number of parametrial fat pads were determined in Swiss mice made obese by means of a high-fat diet (40% lard w/w) given ad lib. | This difference is due solely to an increase in fat cell size. | After weaning, until the 18th wk, the two groups differed with a striking fat cell enlargement seen in the obese group.  
gold rationale: In full siblings body mass index (kg/m2) significantly increased with weight of the adoptees. | Body mass index of the half siblings showed a steady but weaker increase across the four weight groups of adoptees. | In contrast with the findings in half siblings and (previously) the natural parents there was a striking, significant increase in body mass index between full siblings of overweight and obese adoptees. | The degree of fatness in adults living in the same environment appears to be influenced by genetic factors independent of sex, which may include polygenic as well as major gene effects on obesity. | Suspected familial obesity was observed in 2.4 percent and 6 percent respectively of random and hyperlipidemic recall group whites. | Nearly all subjects with familial obesity or leanness had no overt metabolic or pharmacological explanations for their body habitus. | We conclude that genetic influences on body-mass index are substantial, whereas the childhood environment has little or no influence. | There was a strong relation between the weight class of the adoptees and the body-mass index of their biologic parents - for the mothers, P less than 0.0001; for the fathers, P less than 0.02. | Cumulative distributions of the body-mass index of parents showed similar results; there was a strong relation between the body-mass index of biologic parents and adoptee weight class and no relation between the index of adoptive parents and adoptee weight class. | We conclude that genetic influences have an important role in determining human fatness in adults, whereas the family environment alone has no apparent effect. | Our conclusions are that genetic factors are certainly present. | Several analyses suggest the presence of a dominant major gene with weak effect.  
your category: _______


## MISSED_BY_VERIFIER
Gold paper was retrieved but we answered NOT ENOUGH EVIDENCE (abstained or classified neutral)

**#3** gold `SUPPORT` -> pred `NEI` (conf 0.90)  
claim: 1,000 genomes project enables mapping of genetic sequence variation consisting of rare variants with larger penetrance effects than common variants.  
gold paper(s): Rare Variants Create Synthetic Genome-Wide Associations  
top retrieved: Rare Variants Create Synthetic Genome-Wide Associations  
sentences the verifier saw: Genome-wide association studies (GWAS) have now identified at least 2,000 common variants that appear associated with common diseases or related traits (http://www.genome.gov/gwastudies), hundreds of which have been convincingly replicated. | We also illustrate the behavior of synthetic associations in real datasets by showing that rare causal mutations responsible for both hearing loss and sickle cell anemia create genome-wide significant synthetic associations, in the latter case extending over a 2.5-Mb interval encompassing scores of "blocks" of associated variants. | In conclusion, uncommon or rare genetic variants can easily create synthetic associations that are credited to common variants, and this possibility requires careful consideration in the interpretation and follow up of GWAS signals.  
gold rationale: We propose as an alternative explanation that variants much less common than the associated one may create "synthetic associations" by occurring, stochastically, more often in association with one of the alleles at the common site versus the other allele. | We show that they are not only possible, but inevitable, and that under simple but reasonable genetic models, they are likely to account for or contribute to many of the recently identified signals reported in genome-wide association studies. | In conclusion, uncommon or rare genetic variants can easily create synthetic associations that are credited to common variants, and this possibility requires careful consideration in the interpretation and follow up of GWAS signals.  
your category: _______

**#718** gold `CONTRADICT` -> pred `NEI` (conf 0.90)  
claim: Low nucleosome occupancy correlates with low methylation levels across species.  
gold paper(s): Dnmt1-Independent CG Methylation Contributes to Nucleosome Positioning in Diverse Eukaryotes  
top retrieved: Dnmt1-Independent CG Methylation Contributes to Nucleosome Positioning in Diverse Eukaryotes  
sentences the verifier saw: Numerous Dnmt5-containing organisms that diverged more than a billion years ago exhibit clustered methylation, specifically in nucleosome linkers. | Clustered methylation occurs at unprecedented densities and directly disfavors nucleosomes, contributing to nucleosome positioning between clusters. | These features constitute a previously unappreciated genome architecture, in which dense methylation influences nucleosome positions, likely facilitating nuclear processes under extreme spatial constraints.  
gold rationale: Clustered methylation occurs at unprecedented densities and directly disfavors nucleosomes, contributing to nucleosome positioning between clusters.  
your category: _______

**#115** gold `CONTRADICT` -> pred `NEI` (conf 0.50)  
claim: Anthrax spores can be disposed of easily after they are dispersed.  
gold paper(s): Secondary aerosolization of viable Bacillus anthracis spores in a contaminated US Senate Office.  
top retrieved: Secondary aerosolization of viable Bacillus anthracis spores in a contaminated US Senate Office.  
sentences the verifier saw: CONTEXT Bioterrorist attacks involving letters and mail-handling systems in Washington, DC, resulted in Bacillus anthracis (anthrax) spore contamination in the Hart Senate Office Building and other facilities in the US Capitol's vicinity.   
 | OBJECTIVE To provide information about the nature and extent of indoor secondary aerosolization of B anthracis spores.   
 | DESIGN Stationary and personal air samples, surface dust, and swab samples were collected under semiquiescent (minimal activities) and then simulated active office conditions to estimate secondary aerosolization of B anthracis spores.  
gold rationale: More than 80% of the B anthracis particles collected on stationary monitors were within an alveolar respirable size range of 0.95 to 3.5 micro m.   CONCLUSIONS Bacillus anthracis spores used in a recent terrorist incident reaerosolized under common office activities.  
your category: _______

**#42** gold `CONTRADICT` -> pred `NEI` (conf 0.49)  
claim: A high microerythrocyte count raises vulnerability to severe anemia in homozygous alpha (+)- thalassemia trait subjects.  
gold paper(s): Increased Microerythrocyte Count in Homozygous α+-Thalassaemia Contributes to Protection against Severe Malarial Anaemia  
top retrieved: GENOTYPING OF THALASSEMIA IN MICROCYTIC HYPOCHROMIC ANEMIA PATIENTS FROM SOUTHWEST REGION OF IRAN  
sentences the verifier saw: Methodology: In total out of 850, 340 subjects with microcytic hypochromic anemia [MCV<80fl; MCH<27pg] from Southwest part of Iran, were studied in Research Center of Thalassemia and Hemoglobinopathies (RCTH) which is the only center working on hematology and oncology in Southwest (Khuzestan) region of Iran. | These include 325 individuals: 171 with Beta-thalassemia trait, 88 with Alpha-thalassemia trait, 13 with thalassemia major, 11 with hemoglobin variants (HbS, HbC, and HbD Punjab ) and 42 with iron-deficiency anemia. | There was statistically significant difference between Beta-thalassemia trait and Beta-thalassemia Major in case of MCV (p- value = 0.25) and MCH (P–value =0.23) indices, and also MCH index between Beta-thalassemia trait and Hb Variants (P-value = 0.04).  
gold rationale: Individuals homozygous for alpha(+)-thalassaemia have microcytosis and an increased erythrocyte count. | We estimated that the haematological profile in children homozygous for alpha(+)-thalassaemia reduces the risk of SMA during acute malaria compared to children of normal genotype (relative risk 0.52; 95% confidence interval [CI] 0.24-1.12, p = 0.09).   
 | CONCLUSIONS The increased erythrocyte count and microcytosis in children homozygous for alpha(+)-thalassaemia may contribute substantially to their protection against SMA.  
your category: _______

**#636** gold `SUPPORT` -> pred `NEI` (conf 0.49)  
claim: Inositol lipid 3-phosphatase PTEN converts Ptdlns(3,4)P 2 into phosphatidylinositol 4-phosphate.  
gold paper(s): PTEN Regulates PI(3,4)P2 Signaling Downstream of Class I PI3K  
top retrieved: The isolation and characterization of a cDNA encoding phospholipid-specific inositol polyphosphate 5-phosphatase.  
sentences the verifier saw: It is a highly basic protein (pI = 8.8) and has the greatest affinity toward phosphatidylinositol 3,4,5-trisphosphate of known 5-phosphatases. | The K(m) is 0.65 micrometer, 1/10 that of SHIP (5.95 micrometer), another 5-phosphatase that hydrolyzes phosphatidylinositol 3,4,5-trisphosphate. | Remarkably SHIP, a 5-phosphatase previously characterized as hydrolyzing only substrates with d-3 phosphates, also readily hydrolyzed phosphatidylinositol 4,5-bisphosphate in the presence of n-octyl beta-glucopyranoside but not cetyltriethylammonium bromide.  
gold rationale: Here we show that PTEN also functions as a PI(3,4)P2 3-phosphatase, both in vitro and in vivo.  
your category: _______

**#1320** gold `CONTRADICT` -> pred `NEI` (conf 0.49)  
claim: Transplanted human glial progenitor cells are incapable of forming a neural network with host animals' neurons.  
gold paper(s): Forebrain engraftment by human glial progenitor cells enhances synaptic plasticity and learning in adult mice.  
top retrieved: Neurons derived from reprogrammed fibroblasts functionally integrate into the fetal brain and improve symptoms of rats with Parkinson's disease.  
sentences the verifier saw: Here, we show that iPS cells can be efficiently differentiated into neural precursor cells, giving rise to neuronal and glial cell types in culture. | Upon transplantation into the fetal mouse brain, the cells migrate into various brain regions and differentiate into glia and neurons, including glutamatergic, GABAergic, and catecholaminergic subtypes. | Furthermore, iPS cells were induced to differentiate into dopamine neurons of midbrain character and were able to improve behavior in a rat model of Parkinson's disease upon transplantation into the adult brain.  
gold rationale: Long-term potentiation (LTP) was sharply enhanced in the human glial chimeric mice, as was their learning, as assessed by Barnes maze navigation, object-location memory, and both contextual and tone fear conditioning.  
your category: _______

**#48** gold `CONTRADICT` -> pred `NEI` (conf 0.47)  
claim: A total of 1,000 people in the UK are asymptomatic carriers of vCJD infection.  
gold paper(s): Prevalent abnormal prion protein in human appendixes after bovine spongiform encephalopathy epizootic: large scale survey  
top retrieved: Research Letters  
sentences the verifier saw: We report a case of preclinical variant Creutzfeldt-Jakob disease (vCJD) in a patient who died from a non-neurological disorder 5 years after receiving a blood transfusion from a donor who subsequently developed vCJD. | The patient was a heterozygote at codon 129 of PRNP, suggesting that susceptibility to vCJD infection is not confined to the methionine homozygous PRNP genotype. | These findings have major implications for future estimates and surveillance of vCJD in the UK.  
gold rationale: RESULTS Of the 32,441 appendix samples 16 were positive for abnormal PrP, indicating an overall prevalence of 493 per million population (95% confidence interval 282 to 801 per million).  
your category: _______

**#521** gold `SUPPORT` -> pred `NEI` (conf 0.47)  
claim: High-sensitivity cardiac troponin T (HSCT-T) dosage may not be diagnostic if the onset of symptoms occurs less than 3 hours before acute myocardial injury (AMI).  
gold paper(s): Diagnostic accuracy of single baseline measurement of Elecsys Troponin T high-sensitive assay for diagnosis of acute myocardial infarction in emergency department: systematic review and meta-analysis  
top retrieved: Diagnostic accuracy of single baseline measurement of Elecsys Troponin T high-sensitive assay for diagnosis of acute myocardial infarction in emergency department: systematic review and meta-analysis  
sentences the verifier saw: OBJECTIVE To obtain summary estimates of the accuracy of a single baseline measurement of the Elecsys Troponin T high-sensitive assay (Roche Diagnostics) for the diagnosis of acute myocardial infarction in patients presenting to the emergency department.   
 | STUDY SELECTION Studies were included if they evaluated the diagnostic accuracy of a single baseline measurement of Elecsys Troponin T high-sensitive assay for the diagnosis of acute myocardial infarction in patients presenting to the emergency department with suspected acute coronary syndrome.    | CONCLUSIONS The results indicate that a single baseline measurement of the Elecsys Troponin T high-sensitive assay could be used to rule out acute myocardial infarction if lower cut-off values such as 3 ng/L or 5 ng/L are used.  
gold rationale: However, this method should be part of a comprehensive triage strategy and may not be appropriate for patients who present less than three hours after symptom onset.  
your category: _______

**#729** gold `SUPPORT` -> pred `NEI` (conf 0.47)  
claim: Lymphadenopathy is observed in knockin mouse lacking the SHP-2 MAPK pathway.  
gold paper(s): Dissection of signaling cascades through gp130 in vivo: reciprocal roles for STAT3- and SHP2-mediated signals in immune responses.  
top retrieved: Control of CNS Cell-Fate Decisions by SHP-2 and Its Dysregulation in Noonan Syndrome  
sentences the verifier saw: In this regard, genetic mutations resulting in constitutive activation of the protein tyrosine phosphatase SHP-2 cause Noonan Syndrome (NS), which is associated with learning disabilities and mental retardation. | Here, we demonstrate that genetic knockdown of SHP-2 in cultured cortical precursors or in the embryonic cortex inhibited basal neurogenesis and caused enhanced and precocious astrocyte formation. | Neural cell-fate decisions were similarly perturbed in a mouse knockin model that phenocopies human NS.  
gold rationale: The SHP2 signal-deficient mice (gp130F759/F759 were born normal but displayed splenomegaly and lymphadenopathy and an enhanced acute phase reaction.  
your category: _______

**#967** gold `SUPPORT` -> pred `NEI` (conf 0.47)  
claim: Pretreatment with the Arp2/3 inhibitor CK-666 affects lamelliopodia formation.  
gold paper(s): Arp2/3 complex inhibition radically alters lamellipodial actin architecture, suspended cell shape, and the cell spreading process  
top retrieved: Characterization of two classes of small molecule inhibitors of Arp2/3 complex  
sentences the verifier saw: However, questions remain regarding the relative contributions of Arp2/3 complex versus other mechanisms of actin filament nucleation to processes such as path finding by neuronal growth cones; this is because of the lack of simple methods to inhibit Arp2/3 complex reversibly in living cells. | CK-0944636 binds between Arp2 and Arp3, where it appears to block movement of Arp2 and Arp3 into their active conformation. | Two inhibitors with different mechanisms of action provide a powerful approach for studying the Arp2/3 complex in living cells.  
gold rationale: Using light and electron microscopy, we demonstrate that Arp2/3 complex inhibition via the drug CK666 dramatically altered LP actin architecture, slowed centripetal flow, drove a lamellipodial-to-filopodial shape change in suspended cells, and induced a novel actin structural organization during cell spreading.  
your category: _______

**#982** gold `SUPPORT` -> pred `NEI` (conf 0.47)  
claim: Proteins synthesized at the growth cone are ubiquitinated at a higher rate than proteins from the cell body.  
gold paper(s): Coupled local translation and degradation regulate growth cone collapse  
top retrieved: Coupled local translation and degradation regulate growth cone collapse  
sentences the verifier saw: Here we show that local protein synthesis and degradation are linked events in growth cones. | We find that growth cones exhibit high levels of ubiquitination and that local signalling pathways trigger the ubiquitination and degradation of RhoA, a mediator of Sema3A-induced growth cone collapse. | In addition to RhoA, we find that locally translated proteins are the main targets of the ubiquitin-proteasome system in growth cones.  
gold rationale: We find that growth cones exhibit high levels of ubiquitination and that local signalling pathways trigger the ubiquitination and degradation of RhoA, a mediator of Sema3A-induced growth cone collapse.  
your category: _______

**#1259** gold `SUPPORT` -> pred `NEI` (conf 0.46)  
claim: The relationship between a breast cancer patient's capacity to metabolize tamoxifen and treatment outcome is dependent on the patient's genetic make-up.  
gold paper(s): Association between CYP2D6 polymorphisms and outcomes among women with early stage breast cancer treated with tamoxifen.  
top retrieved: Influence of CYP2D6 Polymorphisms on Serum Levels of Tamoxifen Metabolites in Spanish Women with Breast Cancer  
sentences the verifier saw: BACKGROUND Estrogen receptor-positive breast cancer tumors depend on estrogen signaling for their growth and replication and can be treated by anti-estrogen therapy with tamoxifen. | The study objective was to investigate the impact of genetic polymorphisms in CYP2D6 and CYP2C19 on the pharmacokinetics of tamoxifen and its metabolites in Spanish women with estrogen receptor-positive breast cancer who were candidates for tamoxifen therapy.   
 | All poor metabolizers in this series were *4/*4, and their endoxifen and 4-hydroxy tamoxifen levels were 25% lower than those of extensive metabolizers.  
gold rationale: Compared with extensive metabolizers, there was a significantly increased risk of recurrence for heterozygous extensive/intermediate metabolizers (time to recurrence adjusted hazard ratio [HR], 1.40; 95% confidence interval [CI], 1.04-1.90) and for poor metabolizers (time to recurrence HR, 1.90; 95% CI, 1.10-3.28). | Compared with extensive metabolizers, those with decreased CYP2D6 activity (heterozygous extensive/intermediate and poor metabolism) had worse event-free survival (HR, 1.33; 95% CI, 1.06-1.68) and disease-free survival (HR, 1.29; 95% CI, 1.03-1.61), but there was no significant difference in overall survival (HR, 1.15; 95% CI, 0.88-1.51).   
 | CONCLUSION Among women with breast cancer treated with tamoxifen, there was an association between CYP2D6 variation and clinical outcomes, such that the presence of 2 functional CYP2D6 alleles was associated with better clinical outcomes and the presence of nonfunctional or reduced-function alleles with worse outcomes.  
your category: _______

**#5** gold `SUPPORT` -> pred `NEI` (conf 0.43)  
claim: 1/2000 in UK have abnormal PrP positivity.  
gold paper(s): Prevalent abnormal prion protein in human appendixes after bovine spongiform encephalopathy epizootic: large scale survey  
top retrieved: Prevalent abnormal prion protein in human appendixes after bovine spongiform encephalopathy epizootic: large scale survey  
sentences the verifier saw: SAMPLE 32,441 archived appendix samples fixed in formalin and embedded in paraffin and tested for the presence of abnormal prion protein (PrP).   
 | RESULTS Of the 32,441 appendix samples 16 were positive for abnormal PrP, indicating an overall prevalence of 493 per million population (95% confidence interval 282 to 801 per million). | CONCLUSIONS This study corroborates previous studies and suggests a high prevalence of infection with abnormal PrP, indicating vCJD carrier status in the population compared with the 177 vCJD cases to date.  
gold rationale: RESULTS Of the 32,441 appendix samples 16 were positive for abnormal PrP, indicating an overall prevalence of 493 per million population (95% confidence interval 282 to 801 per million).  
your category: _______

**#133** gold `SUPPORT` -> pred `NEI` (conf 0.43)  
claim: Assembly of invadopodia is triggered by focal generation of phosphatidylinositol-3,4-biphosphate and the activation of the nonreceptor tyrosine kinase Src.  
gold paper(s): Sequential signals toward podosome formation in NIH-src cells  
top retrieved: Sequential signals toward podosome formation in NIH-src cells  
sentences the verifier saw: The expression of various phosphoinositide-binding domains revealed that the podosomes in Src-transformed NIH3T3 (NIH-src) cells are enriched with PtdIns(3,4)P2, suggesting an important role of this phosphoinositide in podosome formation. | Live-cell imaging analysis revealed that Src-expression stimulated podosome formation at focal adhesions of NIH3T3 cells after PtdIns(3,4)P2 accumulation. | These results indicate that augmentation of the N-WASP-Arp2/3 signal was accomplished on the platform of Tks5/FISH-Grb2 complex at focal adhesions, which is stabilized by PtdIns(3,4)P2.  
gold rationale: The expression of various phosphoinositide-binding domains revealed that the podosomes in Src-transformed NIH3T3 (NIH-src) cells are enriched with PtdIns(3,4)P2, suggesting an important role of this phosphoinositide in podosome formation. | Live-cell imaging analysis revealed that Src-expression stimulated podosome formation at focal adhesions of NIH3T3 cells after PtdIns(3,4)P2 accumulation.  
your category: _______

**#141** gold `SUPPORT` -> pred `NEI` (conf 0.43)  
claim: Auditory entrainment is strengthened when people see congruent visual and auditory information.  
gold paper(s): Congruent Visual Speech Enhances Cortical Entrainment to Continuous Auditory Speech in Noise-Free Conditions.  
top retrieved: Congruent Visual Speech Enhances Cortical Entrainment to Continuous Auditory Speech in Noise-Free Conditions.  
sentences the verifier saw: When incongruent auditory and visual information is presented concurrently, it can hinder a listener's perception and even cause him or her to perceive information that was not presented in either modality. | Finally, our data suggest that neural entrainment to the speech envelope is inhibited when the auditory and visual streams are incongruent both temporally and contextually.    | Studying how the brain uses this timing relationship to combine information from continuous auditory and visual speech has traditionally been methodologically difficult.  
gold rationale: UNLABELLED Congruent audiovisual speech enhances our ability to comprehend a speaker, even in noise-free conditions. | When incongruent auditory and visual information is presented concurrently, it can hinder a listener's perception and even cause him or her to perceive information that was not presented in either modality. | We demonstrate that the cortical representation of the speech envelope is enhanced by the presentation of congruent audiovisual speech in noise-free conditions. | Finally, our data suggest that neural entrainment to the speech envelope is inhibited when the auditory and visual streams are incongruent both temporally and contextually.    | SIGNIFICANCE STATEMENT Seeing a speaker's face as he or she talks can greatly help in understanding what the speaker is saying. | Specifically, we show that the brain's representation of auditory speech is enhanced when the accompanying visual speech signal shares the same timing.  
your category: _______


## FALSE_CONTRADICT
Predicted CONTRADICT but gold is NEI

**#13** gold `NEI` -> pred `CONTRADICT` (conf 0.80)  
claim: 5% of perinatal mortality is due to low birth weight.  
gold paper(s): (none, NEI)  
top retrieved: Perinatal mortality in rural China: retrospective cohort study.  
sentences the verifier saw: This study aimed to identify the determinants of neonatal mortality in Indonesia, for a nationally representative sample of births from 1997 to 2002.   
 | RESULTS At the community level, the odds of neonatal death was significantly higher for infants from East Java (OR = 5.01, p = 0.00), and for North, Central and Southeast Sulawesi and Gorontalo combined (OR = 3.17, p = 0.03) compared to the lowest neonatal mortality regions of Bali, South Sulawesi and Jambi provinces. | Low birth weight and short birth interval infants as well as perinatal health services factors, such as the availability of skilled birth attendance and postnatal care utilization should be taken into account when planning the interventions to reduce neonatal mortality in Indonesia.  
gold rationale: -  
your category: _______

**#269** gold `NEI` -> pred `CONTRADICT` (conf 0.77)  
claim: Cold exposure reduces BAT recruitment.  
gold paper(s): (none, NEI)  
top retrieved: Sestrin2 inhibits uncoupling protein 1 expression through suppressing reactive oxygen species.  
sentences the verifier saw: In two genetic mouse knockout models (apolipoprotein E(-/-) [ApoE(-/-)] and LDL receptor(-/-) [Ldlr(-/-)] mice), persistent cold exposure stimulated atherosclerotic plaque growth by increasing lipid deposition. | Deletion of uncoupling protein 1 (UCP1), a key mitochondrial protein involved in thermogenesis in brown adipose tissue (BAT), in the ApoE(-/-) strain completely protected mice from the cold-induced atherosclerotic lesions. | Cold acclimation markedly reduced plasma levels of adiponectin, and systemic delivery of adiponectin protected ApoE(-/-) mice from plaque development.  
gold rationale: -  
your category: _______

**#1292** gold `NEI` -> pred `CONTRADICT` (conf 0.77)  
claim: There is no association between HNF4A mutations and diabetes risks.  
gold paper(s): (none, NEI)  
top retrieved: Macrosomia and Hyperinsulinaemic Hypoglycaemia in Patients with Heterozygous Mutations in the HNF4A Gene  
sentences the verifier saw: Background  Macrosomia is associated with considerable neonatal and maternal morbidity. | The increased rate of macrosomia in the offspring of pregnant women with diabetes and in congenital hyperinsulinaemia is mediated by increased foetal insulin secretion. | We assessed the in utero and neonatal role of two key regulators of pancreatic insulin secretion by studying birthweight and the incidence of neonatal hypoglycaemia in patients with heterozygous mutations in the maturity-onset diabetes of the young (MODY) genes HNF4A (encoding HNF-4α) and HNF1A/TCF1 (encoding HNF-1α), and the effect of pancreatic deletion of Hnf4a on foetal and neonatal insulin secretion in mice.  
gold rationale: -  
your category: _______

**#354** gold `NEI` -> pred `CONTRADICT` (conf 0.73)  
claim: Downregulation and mislocalization of Scribble prevents cell transformation and mammary tumorigenesis.  
gold paper(s): (none, NEI)  
top retrieved: Deregulation of Scribble Promotes Mammary Tumorigenesis and Reveals a Role for Cell Polarity in Carcinoma  
sentences the verifier saw: Here, we demonstrate that depletion of Scribble in mammary epithelia disrupts cell polarity, blocks three-dimensional morphogenesis, inhibits apoptosis, and induces dysplasia in vivo that progress to tumors after long latency. | Like depletion, mislocalization of Scribble from cell-cell junction was sufficient to promote cell transformation. | Interestingly, spontaneous mammary tumors in mice and humans possess both downregulated and mislocalized Scribble.  
gold rationale: -  
your category: _______

**#870** gold `NEI` -> pred `CONTRADICT` (conf 0.73)  
claim: Obesity decreases life quality.  
gold paper(s): (none, NEI)  
top retrieved: Psychological Outcome 4 Years after Restrictive Bariatric Surgery  
sentences the verifier saw: Extreme obesity is associated with severe psychiatric and somatic comorbidity and impairment of psychosocial functioning. | The aim of this study was to evaluate the relationship between the course of weight and psychological variables including depression, anxiety, health-related quality of life (HRQOL), and self-esteem up to 4 years after obesity surgery. | Statistical analysis revealed significant improvements in depressive symptoms, physical dimension of quality of life, and self-esteem with peak improvements 1 year after surgery.  
gold rationale: -  
your category: _______

**#907** gold `NEI` -> pred `CONTRADICT` (conf 0.73)  
claim: PGE 2 promotes intestinal tumor growth by altering the expression of tumor suppressing and DNA repair genes.  
gold paper(s): (none, NEI)  
top retrieved: Prostaglandin E2 promotes intestinal tumor growth via DNA methylation  
sentences the verifier saw: Although aberrant DNA methylation is considered to be one of the key ways by which tumor-suppressor and DNA-repair genes are silenced during tumor initiation and progression, the mechanisms underlying DNA methylation alterations in cancer remain unclear. | Here we show that prostaglandin E(2) (PGE(2)) silences certain tumor-suppressor and DNA-repair genes through DNA methylation to promote tumor growth. | These findings uncover a previously unrecognized role for PGE(2) in the promotion of tumor progression.  
gold rationale: -  
your category: _______

**#1213** gold `NEI` -> pred `CONTRADICT` (conf 0.73)  
claim: The deregulated and prolonged activation of monocytes has deleterious effects in inflammatory diseases.  
gold paper(s): (none, NEI)  
top retrieved: CCR2 and CXCR4 regulate peripheral blood monocyte pharmacodynamics and link to efficacy in experimental autoimmune encephalomyelitis  
sentences the verifier saw: Prolonged release of interleukin-1β (IL-1β) from activated microglia has a deleterious effect on hippocampal neurons and is implicated in the impaired neurogenesis and cognitive dysfunction associated with aging, Alzheimer's disease and depression. | This study assessed the effect of IL-1β on the proliferation and differentiation of embryonic rat hippocampal NPCs in vitro. | The present results emphasise the consequences of an inflammatory environment during NPC development, and indicate that strategies to inhibit IL-1β signalling may be necessary to facilitate effective cell transplantation approaches or in conditions where endogenous hippocampal neurogenesis is impaired.  
gold rationale: -  
your category: _______

**#1175** gold `NEI` -> pred `CONTRADICT` (conf 0.71)  
claim: The PPR MDA5 has two N-terminal CARD domains.  
gold paper(s): (none, NEI)  
top retrieved: Cytosolic viral sensor RIG-I is a 5'-triphosphate-dependent translocase on double-stranded RNA.  
sentences the verifier saw: Two N-terminal caspase activation and recruitment domains (CARDs) transmit the signal, and the regulatory domain prevents signaling in the absence of viral RNA. | However, the function of the DExH box helicase domain that is also required for activity is less clear. | Using single-molecule protein-induced fluorescence enhancement, we discovered a robust adenosine 5'-triphosphate-powered dsRNA translocation activity of RIG-I. The CARDs dramatically suppress translocation in the absence of 5'-triphosphate, and the activation by 5'-triphosphate triggers RIG-I to translocate preferentially on dsRNA in cis.  
gold rationale: -  
your category: _______

**#1332** gold `NEI` -> pred `CONTRADICT` (conf 0.71)  
claim: Tumor necrosis factor alpha (TNF-α) and interleukin-1 (IL-1) are pro-inflammatory cytokines that inhibit IL-6 and IL-10.  
gold paper(s): (none, NEI)  
top retrieved: Downloaded from  
sentences the verifier saw: Physical activity induces a subclinical inflammatory response, mediated in part by leukocytes, and manifested by elevated concentrations of circulating proinflammatory cytokines, including interleukin (IL)-1β, IL-6, and tumor necrosis factor-α (TNF-α). | Ten healthy [peak oxygen uptake = 48.8 ± 6.5 (SD) ml · kg−1 · min−1] but untrained men [age = 25 ± 5 (SD) yr] undertook 3 h of exercise (cycling and inclined walking) at 60–65% peak oxygen uptake. | Circulating leukocyte subset counts were elevated during and 2 h postexercise but returned to normal within 24 h. Plasma concentrations of IL-1β, IL-6, and TNF-α peaked at the end of exercise and remained elevated at 2 h (IL-6) and up to 24 h (IL-1β and TNF-α) postexercise.  
gold rationale: -  
your category: _______

**#1278** gold `NEI` -> pred `CONTRADICT` (conf 0.70)  
claim: The treatment of cancer patients with co-IR blockade does not cause any adverse autoimmune events.  
gold paper(s): (none, NEI)  
top retrieved: In vitro characterization of the anti-PD-1 antibody nivolumab, BMS-936558, and in vivo toxicology in non-human primates.  
sentences the verifier saw: The programmed death-1 (PD-1) receptor serves as an immunologic checkpoint, limiting bystander tissue damage and preventing the development of autoimmunity during inflammatory responses. | In patients with cancer, the expression of PD-1 on tumor-infiltrating lymphocytes and its interaction with the ligands on tumor and immune cells in the tumor microenvironment undermine antitumor immunity and support its rationale for PD-1 blockade in cancer immunotherapy. | Nivolumab treatment did not induce adverse immune-related events when given to cynomolgus macaques at high concentrations, independent of circulating anti-nivolumab antibodies where observed.  
gold rationale: -  
your category: _______

**#411** gold `NEI` -> pred `CONTRADICT` (conf 0.68)  
claim: Febrile seizures reduce the threshold for development of epilepsy.  
gold paper(s): (none, NEI)  
top retrieved: Febrile seizures in the developing brain result in persistent modification of neuronal excitability in limbic circuits  
sentences the verifier saw: Febrile (fever-induced) seizures affect 3–5% of infants and young children. | Despite the high incidence of febrile seizures, their contribution to the development of epilepsy later in life has remained controversial. | Combining a new rat model of complex febrile seizures and patch clamp techniques, we determined that hyperthermia-induced seizures in the immature rat cause a selective presynaptic increase in inhibitory synaptic transmission in the hippocampus that lasts into adulthood.  
gold rationale: -  
your category: _______

**#700** gold `NEI` -> pred `CONTRADICT` (conf 0.68)  
claim: Localization of PIN1 in the Arabidopsis embryo does not require VPS9a  
gold paper(s): (none, NEI)  
top retrieved: Local, Efflux-Dependent Auxin Gradients as a Common Module for Plant Organ Formation  
sentences the verifier saw: Here, we show that organ formation in Arabidopsis involves dynamic gradients of the signaling molecule auxin with maxima at the primordia tips. | These gradients are mediated by cellular efflux requiring asymmetrically localized PIN proteins, which represent a functionally redundant network for auxin distribution in both aerial and underground organs. | PIN1 polar localization undergoes a dynamic rearrangement, which correlates with establishment of auxin gradients and primordium development.  
gold rationale: -  
your category: _______

**#702** gold `NEI` -> pred `CONTRADICT` (conf 0.68)  
claim: Localization of PIN1 in the roots of Arabidopsis does not require VPS9a  
gold paper(s): (none, NEI)  
top retrieved: Local, Efflux-Dependent Auxin Gradients as a Common Module for Plant Organ Formation  
sentences the verifier saw: This is largely dependent on the ability of plants to form new organs, such as lateral roots, leaves, and flowers during postembryonic development. | These gradients are mediated by cellular efflux requiring asymmetrically localized PIN proteins, which represent a functionally redundant network for auxin distribution in both aerial and underground organs. | PIN1 polar localization undergoes a dynamic rearrangement, which correlates with establishment of auxin gradients and primordium development.  
gold rationale: -  
your category: _______


## Your taxonomy (fill in after reading >= 20 errors)

| category | count | example ids | fix idea |
|---|---|---|---|
| | | | |
