import re
REPO='/Users/jonsnow/homepage'
tpl=open(f'{REPO}/paper/AgentMD.html').read()
PRE = tpl.split('    <header class="hero">')[0]
POST= '  </main>' + tpl.split('  </main>',1)[1]

def hero(cover,eyebrow,h1,authors,badge,year,pdf,jlabel,jurl):
    return (f'    <header class="hero"><img class="cover" src="../assets/covers/{cover}" alt="{h1.split(":")[0]}">\n'
      f'      <div><div class="eyebrow">{eyebrow}</div><h1>{h1}</h1>\n'
      f'        <div class="authors">{authors}</div>\n'
      f'        <div class="venue"><span class="badge">{badge}</span> {year}</div>\n'
      f'        <div class="links"><a class="primary" href="../assets/papers/{pdf}" target="_blank" rel="noopener">PDF</a>\n'
      f'          <a href="{jurl}" target="_blank" rel="noopener">{jlabel}</a></div></div>'
      f'<div class="hero-disc">These slides were generated with the help of AI and may contain errors.</div></header>\n')
def fig(src,cap,cls='',style=''):
    c=f' {cls}' if cls else ''; st=f'style="{style}" ' if style else ''
    alt=re.sub(r'<[^>]+>','',cap)[:120]
    return f'<figure class="fig{c}"><img {st}src="../assets/figures/auto/{src}" alt="{alt}"><figcaption>{cap}</figcaption></figure>'
def table(headers,rows,note='',best=None,wrap=False):
    th=''.join(f'<th style="text-align:{"left" if i==0 else "right"}">{h}</th>' for i,h in enumerate(headers))
    tb=''
    for r in rows:
        cls=' class="best"' if best and r[0]==best else ''
        td=''.join(f'<td style="text-align:{"left" if i==0 else "right"}">{c}</td>' for i,c in enumerate(r))
        tb+=f'<tr{cls}>{td}</tr>'
    n=f'<div class="tnote">{note}</div>' if note else ''
    w=' wrap' if wrap else ''
    return f'<div class="tbl-wrap"><table class="utbl{w}"><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>{n}'
def stats(pairs):
    return '<div class="stats">'+''.join(f'<div class="stat"><div class="num">{n}</div><div class="lbl">{l}</div></div>' for n,l in pairs)+'</div>'
def sl(sid,kind,title,bullets,disp='',note=''):
    b='<ul class="highlights">'+''.join(f'<li>{x}</li>' for x in bullets)+'</ul>' if bullets else ''
    n=f'<div class="cnote">{note}</div>' if note else ''
    return (f'    <section class="slide" id="{sid}"><div class="kick"><span class="n">00</span>{kind}</div>'
            f'<h2>{title}</h2><div class="body">{b}{disp}{n}</div></section>\n')
def summ(rows):
    tb=''.join(f'<tr><td class="slab">{k}</td><td class="sval">{v}</td></tr>' for k,v in rows)
    return f'<div class="tbl-wrap"><table class="stbl"><tbody>{tb}</tbody></table></div>'
def build(fname,title,accent,heroargs,slides):
    pre=PRE.replace('<title>AgentMD &mdash; Qiao Jin</title>', f'<title>{title} &mdash; Qiao Jin</title>')
    pre=pre.replace('--accent:var(--util);--accent-bg:var(--util-bg);', f'--accent:var(--{accent});--accent-bg:var(--{accent}-bg);')
    html=pre+hero(*heroargs)+'\n'+''.join(slides)+POST
    n=[0]
    html=re.sub(r'<div class="kick"><span class="n">\d+</span>',
                lambda _:(n.__setitem__(0,n[0]+1) or f'<div class="kick"><span class="n">{n[0]:02d}</span>'), html)
    open(f'{REPO}/paper/{fname}','w').write(html)
    print(f'  {fname:<20} {len(slides)} slides, {len(html)//1024} KB')

NC='Nature Communications'; NPJ='npj Digital Medicine'
S=lambda u,t: f'<span class="src"><a class="srcref" href="{u}" target="_blank" rel="noopener">{t}</a>.</span>'

# ───────────────────────────── AI Scientists
u='https://www.nature.com/articles/s41467-025-63913-1'
build('AIScientist.html','Risks of AI Scientists','eval',
 ('AIScientist.png','AI Safety &middot; Perspective','Risks of AI Scientists: Prioritizing Safeguarding Over Autonomy',
  'Xiangru Tang, <b>Qiao Jin</b>, Kunlun Zhu, Tongxin Yuan, Yichi Zhang, Wangchunshu Zhou, Meng Qu, Yilun Zhao, Jian Tang, Zhuosheng Zhang, Arman Cohan, Dov Greenbaum, Zhiyong Lu, Mark Gerstein',
  NC,'2025','AIScientist.pdf','Journal',u),
 [sl('motivation','Motivation','Autonomy in a lab is not autonomy in a chatbot',
   ['Language-model agents already design and execute experiments across disciplines.',
    'When the output is a physical substance rather than text, a wrong step has physical consequences.',
    'Every stage of a real workflow carries its own plausible failure mode.'],
   fig('AISCI_fig1.png','A six-step antibody-synthesis workflow, each step paired with the incorrect action an agent might take and the risk it creates. '+S(u,'Fig. 1'))),
  sl('risks','Risks','Risk depends on intent, domain and reach',
   ['<b>User intent</b> &mdash; directly malicious, malicious by indirection, or simply unintended.',
    '<b>Scientific domain</b> &mdash; chemical, biological, radiological, physical, informational and emerging-tech risks differ sharply in worst case.',
    '<b>Environment</b> &mdash; harm can land on nature, on human health, or on the social and economic order.'],
   fig('AISCI_fig3.png','The three axes along which the paper classifies the risks of AI scientists. '+S(u,'Fig. 3a&ndash;c'))),
  sl('causes','Causes','Where the vulnerabilities actually come from',
   ['<b>Data insufficiency</b> &mdash; missing safety-domain knowledge, weak sources, little human feedback.',
    '<b>Planning limits</b> &mdash; long-horizon risk blindness, dead loops, poor multi-task planning.',
    '<b>Tool and model limits</b> &mdash; unregulated tool use, factual error, jailbreak exposure.',
    '<b>No measurement</b> &mdash; few detection methods and no regulation of agent interactions.'],
   fig('AISCI_fig4.png','The structure of an LLM-based scientific agent, with the vulnerability each component introduces. '+S(u,'Fig. 4'))),
  sl('framework','Framework','Safeguarding takes three parties, not one',
   ['Human regulation, agent alignment and agent regulation have to operate together.',
    'Aligning the agent cannot substitute for regulating what it is permitted to touch.',
    'The environment is a participant in the loop, not a passive backdrop.'],
   fig('AISCI_fig2.png','The triadic safeguarding framework: human regulation, agent alignment and agent regulation. '+S(u,'Fig. 2'),'m')),
  sl('safeguards','Safeguards','What exists today &mdash; and what does not',
   ['Content evaluation and safety alignment are comparatively mature for plain LLMs.',
    'Agent-level mechanisms &mdash; risk detection, memory, external tool use &mdash; are far thinner.',
    'Extra safety training helps, but too much of it degrades scientific usefulness.'],
   fig('AISCI_fig5.png','Existing work on safeguarding LLMs and agents, by category. '+S(u,'Fig. 5'))),
  sl('summary','Summary','Risks of AI scientists at a glance',
   [], summ([('Background','LLM agents increasingly conduct science autonomously.'),
             ('Problem','Their vulnerabilities had not been examined systematically.'),
             ('Approach','A perspective mapping risk by intent, domain and environmental reach.'),
             ('Results','A triadic safeguarding framework, and a survey of what protection exists.'),
             ('Conclusion','Build the benchmarks and rules before autonomy outpaces them.')]))])

# ───────────────────────────── BioNLP
u='https://www.nature.com/articles/s41467-025-56989-2'
build('BioNLP.html','BioNLP Benchmark','eval',
 ('BioNLP.png','Medical AI Evaluation &middot; BioNLP Benchmark','Benchmarking Large Language Models for Biomedical Natural Language Processing',
  'Qingyu Chen, Yan Hu, Xueqing Peng, Qianqian Xie, <b>Qiao Jin</b>, Aidan Gilson, Maxwell B. Singer, Xuguang Ai, Po-Ting Lai, Zhizheng Wang, Vipina K. Keloth, Kalpana Raja, Jimin Huang, Huan He, Fongci Lin, Jingcheng Du, Rui Zhang, W. Jim Zheng, Ron A. Adelman, Zhiyong Lu, Hua Xu',
  NC,'2025','BioNLP.pdf','Journal',u),
 [sl('motivation','Motivation','Do LLMs actually do biomedical NLP well?',
   ['Biomedical NLP exists because nobody can read the literature by hand &mdash; COVID-19 alone added ~10,000 articles a month.',
    'LLMs clearly help in general domains, but their standing on biomedical tasks was untested at scale.',
    'Earlier evaluations mostly probed GPT-3.5, on few tasks, reporting F1 without qualitative review.']),
  sl('method','Method','Four LLMs, twelve benchmarks, six applications',
   ['GPT and LLaMA representatives evaluated zero-shot, few-shot and fine-tuned.',
    'Compared head-to-head against traditional fine-tuning of BERT and BART.',
    'Scored beyond accuracy: inconsistency, missing information, hallucination and cost per 100 instances.']),
  sl('result','Result','Traditional fine-tuning still wins most tasks',
   ['Fine-tuned BERT and BART lead zero- and few-shot LLMs across most of the 12 benchmarks.',
    'The gap is widest on extraction-style tasks, where labelled data still pays off.'],
   table(['Approach','Macro-average across 12 benchmarks'],
         [['Fine-tuned BERT / BART (SOTA)','0.65'],['Best zero- or few-shot LLM','0.50']],
         'Roughly 15 points separate the two across the benchmark suite. Source: '+S(u,'Nature Communications 16:3280'),
         best='Fine-tuned BERT / BART (SOTA)')),
  sl('result-2','Result','But LLMs win where reasoning matters',
   ['Closed-source LLMs excel at reasoning-heavy work such as medical question answering.',
    'On summarization, GPT-4 wins clearly on readability but trails a fine-tuned BART on completeness.'],
   fig('BIONLP_fig3.png','Qualitative evaluation on PubMed text summarization: GPT-4 against GPT-3.5 and against a fine-tuned BART, judged on accuracy, completeness and readability. '+S(u,'Fig. 3'))),
  sl('recommend','Recommendation','Which tool for which task',
   ['For extraction, fine-tuned BERT models remain the top choice.',
    'For summarization and simplification, closed-source LLMs lead if the context fits.',
    'Advanced prompt engineering pays off mainly on reasoning and semantic-understanding tasks.'],
   fig('BIONLP_fig4.png','Task-by-task recommendations for using LLMs in biomedical NLP. '+S(u,'Fig. 4'))),
  sl('summary','Summary','BioNLP benchmarking at a glance',
   [], summ([('Background','Biomedical NLP automates curation of an unreadable literature.'),
             ('Problem','How well LLMs perform on real BioNLP tasks was untested at scale.'),
             ('Approach','Four LLMs across 12 benchmarks and six applications, versus fine-tuned BERT/BART.'),
             ('Results','Fine-tuning leads on most tasks (0.65 vs 0.50); LLMs lead on reasoning.'),
             ('Conclusion','Choose the tool by task &mdash; and evaluate quality, not just F1.')]))])

# ───────────────────────────── BriefContext
u='https://www.nature.com/articles/s41746-025-01651-w'
build('BriefContext.html','BriefContext','util',
 ('BriefContext.png','AI for Evidence Utilization &middot; Long Context','Leveraging Long Context in Retrieval Augmented Language Models for Medical Question Answering',
  'Gongbo Zhang, Zihan Xu, <b>Qiao Jin</b>, Fangyi Chen, Yilu Fang, Yi Liu, Justin F. Rousseau, Ziyang Xu, Zhiyong Lu, Chunhua Weng, Yifan Peng',
  NPJ,'2025','BriefContext.pdf','Journal',u),
 [sl('motivation','Motivation','RAG loses the answer in the middle',
   ['Retrieval grounds a medical answer in real literature &mdash; but only if the model reads the right passage.',
    'Models attend to the start and end of a long context and skim the middle: the &ldquo;lost-in-the-middle&rdquo; problem.',
    'So the answer can sit in the retrieved set and still be missed.']),
  sl('method','Method','Map-reduce over the retrieved context',
   ['BriefContext splits retrieved documents into smaller contexts, answers within each, then reduces the partial answers.',
    'A preflight check predicts, before generation, whether a query is at risk.',
    'No weight changes &mdash; it wraps any LLM backbone.'],
   fig('BRIEF_fig1.png','The BriefContext workflow: context map, per-partition answering, and reduce. '+S(u,'Fig. 1'))),
  sl('result','Result','Accuracy holds as the context grows',
   ['Vanilla RAG degrades as more documents are packed into the prompt.',
    'BriefContext stays flat or improves across four different backbones as top-k rises.',
    'Gains are largest exactly where vanilla RAG fails &mdash; key evidence buried mid-context.'],
   fig('BRIEF_fig5.png','Medical QA accuracy against the number of retrieved documents, for Llama3-70B, Llama2-70B, Mixtral-7x8b and GPT-3.5-turbo. '+S(u,'Fig. 5'))),
  sl('result-2','Result','It wins more often than it loses',
   ['Head-to-head against vanilla RAG, BriefContext wins far more comparisons than it loses.',
    'The margin widens as the retrieved set grows from top-k 8 to top-k 16.'],
   fig('BRIEF_fig4.png','Win / tie / lose counts for BriefContext against vanilla RAG at two retrieval depths. '+S(u,'Fig. 4'))),
  sl('result-3','Result','A preflight check predicts the failure',
   ['The check flags queries likely to suffer lost-in-the-middle before any answer is generated.',
    'It is deliberately cautious &mdash; it would rather re-plan than let a failure through.'],
   stats([('92.6%','recall predicting a<br>lost-in-the-middle case'),('50.2%','precision'),('35.7%','of true negatives<br>correctly filtered')]),
   'Low precision is the intended trade: a false alarm costs one extra map-reduce pass, a miss costs a wrong answer.'),
  sl('summary','Summary','BriefContext at a glance',
   [], summ([('Background','RAG keeps medical answers current and grounded.'),
             ('Problem','Evidence buried mid-context gets skimmed and missed.'),
             ('Approach','A map-reduce strategy over partitioned context, plus a preflight check.'),
             ('Results','Accuracy holds as context grows; failures predicted at 92.6% recall.'),
             ('Conclusion','The fix is how context is arranged, not the model weights.')]))])

# ───────────────────────────── DDx
u='https://www.nature.com/articles/s41746-025-01556-8'
PMC='<a class="ref own" href="https://www.nature.com/articles/s41597-023-02814-8" target="_blank" rel="noopener">PMC-Patients</a>'
build('DDx.html','Lab Results and Differential Diagnosis','eval',
 ('ddx.png','Medical AI Evaluation &middot; Differential Diagnosis','Impact of Lab Results on Large Language Model Generated Differential Diagnoses',
  'Balu Bhasuran, <b>Qiao Jin</b>, Yuzhang Xie, Carl Yang, Karim Hanna, Jennifer Costa, Cindy Shavor, Wenshan Han, Zhiyong Lu, Zhe He',
  NPJ,'2025','ddx.pdf','Journal',u),
 [sl('motivation','Motivation','Does giving a model the labs change the diagnosis?',
   ['Differential diagnosis is how clinicians separate conditions that present alike.',
    'Most LLM diagnosis studies feed a narrative vignette &mdash; symptoms and history, but no lab values.',
    'Real workups turn on the labs, so the open question is whether they change what the model concludes.']),
  sl('method','Method','Fifty case reports, five models, labs on and off',
   [f'Vignettes were built from 50 randomly selected {PMC} case reports.',
    'Each was run with and without lab data through five LLMs.',
    'Outputs were scored for exact and lenient accuracy against the true diagnosis.'],
   fig('DDX_fig1.png','The evaluation pipeline, from case report to scored differential. '+S(u,'Fig. 1'))),
  sl('cohort','Cohort','What the fifty cases cover',
   ['The cases span twelve medical categories, weighted toward gastrointestinal, infectious and endocrine disease.',
    'That spread keeps the benchmark from measuring one specialty in disguise.'],
   fig('DDX_fig2.png','Distribution of diseases across medical categories in the 50-case set. '+S(u,'Fig. 2'))),
  sl('result','Result','GPT-4 leads, but the field is close',
   ['With lab data, GPT-4 tops Top-1 accuracy; Mixtral and Claude-2 close much of the gap further down the list.',
    'Every model improves as the list lengthens from Top-1 to Top-10.'],
   table(['Model (with lab data)','Top-1','Top-5','Top-10'],
     [['Llama-2','0.52','0.54','0.54'],['Claude-2','0.50','0.58','0.58'],['Mixtral','0.52','0.60','0.58'],
      ['GPT-3.5','0.44','0.54','0.53'],['GPT-4','0.55','0.57','0.60']],
     'Exact-match accuracy. GPT-4 reaches 0.79 lenient accuracy at Top-5. Source: '+S(u,'Table 4'), best='GPT-4')),
  sl('result-2','Result','Lab data lifts accuracy by up to 30%',
   ['Across all five models, adding lab values raises both exact and lenient accuracy.',
    'The improvement is statistically significant (Holm-adjusted p &lt; 0.05), with GPT-4 and Mixtral gaining most.'],
   fig('DDX_fig3.png','Accuracy and lenient accuracy with and without lab tests, for each model across Top-1, Top-5 and Top-10. '+S(u,'Fig. 3'))),
  sl('result-3','Result','The gain holds as the list lengthens',
   ['Accuracy trends upward for every model as more differentials are allowed.',
    'The lab-informed curves sit above the lab-free ones throughout, not just at Top-1.'],
   fig('DDX_fig4.png','Accuracy and linear trend for the five LLMs with lab test data. '+S(u,'Fig. 4'))),
  sl('summary','Summary','Lab results and DDx at a glance',
   [], summ([('Background','Differential diagnosis separates conditions that look alike.'),
             ('Problem','LLM diagnosis studies usually omit the lab data clinicians rely on.'),
             ('Approach','50 case reports as vignettes, five LLMs, with and without labs.'),
             ('Results','Labs improved accuracy by up to 30%; GPT-4 reached 0.55 Top-1 and 0.79 lenient.'),
             ('Conclusion','Structured lab data is not a detail &mdash; it changes the diagnosis.')]))])

# ───────────────────────────── EBM-Net
u='https://aclanthology.org/2020.emnlp-main.114/'
build('EBM-Net.html','EBM-Net','util',
 ('EBM-Net.png','AI for Evidence Utilization &middot; Evidence Integration','Predicting Clinical Trial Results by Implicit Evidence Integration',
  '<b>Qiao Jin</b>, Chuanqi Tan, Mosha Chen, Xiaozhong Liu, Songfang Huang','EMNLP','2020','EBM-Net.pdf','Proceedings',u),
 [sl('motivation','Motivation','Most clinical trials fail &mdash; expensively',
   ['Trials are the evidence base of medicine, and they carry enormous cost and risk.',
    'One study reports that about <b>86.2%</b> of clinical trials fail to meet their goals.',
    'If a proposal&rsquo;s likely result could be estimated beforehand, trial design could be prioritized before the spend.']),
  sl('task','Task','A new task: Clinical Trial Result Prediction',
   ['The model reads a PICO-formatted proposal &mdash; Population, Intervention, Comparison, Outcome &mdash; with its background.',
    'It predicts how the intervention group compares with the comparison group on the measured outcome.'],
   fig('EBM_fig1.png','The CTRP task: a structured trial proposal in, a directional result out. '+S(u,'Fig. 1'))),
  sl('method','Method','Learning from evidence nobody labelled',
   ['Structured clinical evidence is prohibitively costly to annotate at scale.',
    '12 million comparative sentences from PubMed and PMC implicitly contain PICOs and their results.',
    'Reversing an example flips its label, giving free adversarial supervision for the direction of a comparison.'],
   fig('EBM_fig2.png','Comparative language-model pre-training: disentangle the result from implicit evidence, then predict it. '+S(u,'Fig. 2'))),
  sl('result','Result','Large gains over biomedical baselines',
   ['EBM-Net beats BioBERT by <b>10.7%</b> relative 3-way macro-F1 on the Evidence Integration benchmark.',
    'It also degrades least under the adversarial split, where the comparison direction is reversed.'],
   table(['Model','Accuracy','F1 (3-way)','F1 (2-way)'],
     [['Majority class','41.76','19.64','&ndash;'],['BoW + logistic regression','43.73','41.04','35.84'],
      ['MeSH ontology','38.55','36.33','31.01'],['BioBERT','55.96','54.33','51.98'],
      ['EBM-Net (ours)','61.35','60.15','59.42']],
     'Standard Evidence Integration split, all percentages. Source: '+S(u,'Table 2'), best='EBM-Net (ours)')),
  sl('result-2','Result','More pre-training evidence keeps helping',
   ['Performance rises log-linearly with the amount of implicit evidence used for pre-training.',
    'The advantage over BioBERT holds at every fine-tuning budget, including zero-shot.'],
   fig('EBM_fig3.png','Left: macro-F1 against pre-training size. Right: macro-F1 against the share of fine-tuning data used. '+S(u,'Fig. 3'))),
  sl('result-3','Result','The model learns real comparisons',
   ['Representations cluster by the direction of the result rather than by surface wording.',
    'That separation is what lets the model generalize to unseen interventions.'],
   fig('EBM_fig4.png','t-SNE of EBM-Net representations on the Evidence Integration test set, coloured by true label. '+S(u,'Fig. 4'),'m')),
  sl('summary','Summary','EBM-Net at a glance',
   [], summ([('Background','Clinical trials guide practice but cost enormously and often fail.'),
             ('Problem','Predicting a result needs structured evidence too expensive to annotate.'),
             ('Approach','Pre-train on 12M sentences of implicit evidence from PubMed and PMC.'),
             ('Results','+10.7% relative macro-F1 over BioBERT, and validated on COVID-19 trials.'),
             ('Conclusion','The literature already holds the supervision &mdash; it just needs disentangling.')]))])
print('done')
