import re, io, os
REPO='/Users/jonsnow/homepage'
tpl=open(f'{REPO}/paper/AgentMD.html').read()
PRE  = tpl.split('    <header class="hero">')[0]
POST = '  </main>' + tpl.split('  </main>',1)[1]

def esc(s): return s
def hero(cover,eyebrow,h1,authors,badge,year,pdf,jlabel,jurl):
    return f'''    <header class="hero"><img class="cover" src="../assets/covers/{cover}" alt="{h1.split(':')[0]}">
      <div><div class="eyebrow">{eyebrow}</div><h1>{h1}</h1>
        <div class="authors">{authors}</div>
        <div class="venue"><span class="badge">{badge}</span> {year}</div>
        <div class="links"><a class="primary" href="../assets/papers/{pdf}" target="_blank" rel="noopener">PDF</a>
          <a href="{jurl}" target="_blank" rel="noopener">{jlabel}</a></div></div><div class="hero-disc">These slides were generated with the help of AI and may contain errors.</div></header>
'''
def bullets(items):
    return '<ul class="highlights">'+''.join(f'<li>{i}</li>' for i in items)+'</ul>'
def stats(pairs):
    return '<div class="stats">'+''.join(f'<div class="stat"><div class="num">{n}</div><div class="lbl">{l}</div></div>' for n,l in pairs)+'</div>'
def fig(src,cap,cls=''):
    c=f' {cls}' if cls else ''
    return f'<figure class="fig{c}"><img src="../assets/figures/auto/{src}" alt="{re.sub(chr(60)+"[^"+chr(62)+"]*"+chr(62),"",cap)[:150]}"><figcaption>{cap}</figcaption></figure>'
def table(headers,rows,note=''):
    th=''.join(f'<th style="text-align:{"left" if i==0 else "right"}">{h}</th>' for i,h in enumerate(headers))
    tb=''
    for r in rows:
        best=r[0].startswith('*'); cells=list(r); cells[0]=cells[0].lstrip('*')
        td=''.join(f'<td style="text-align:{"left" if i==0 else "right"}">{c}</td>' for i,c in enumerate(cells))
        tb+=f'<tr class="best">{td}</tr>' if best else f'<tr>{td}</tr>'
    n=f'<div class="tnote">{note}</div>' if note else ''
    return f'<div class="tbl-wrap"><table class="utbl"><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>{n}'
def slide(i,kind,sid,title,body,lead=''):
    ld=f'<p class="lead">{lead}</p>' if lead else ''
    return (f'    <section class="slide" id="{sid}"><div class="kick"><span class="n">{i:02d}</span>{kind}</div>'
            f'<h2>{title}</h2><div class="body">{ld}{body}</div></section>\n')
def summary(rows):
    tb=''.join(f'<tr><td class="slab">{k}</td><td class="sval">{v}</td></tr>' for k,v in rows)
    return f'<div class="tbl-wrap"><table class="stbl"><tbody>{tb}</tbody></table></div>'

def build(fname,title,accent,heroargs,slides):
    pre=PRE.replace('<title>AgentMD &mdash; Qiao Jin</title>', f'<title>{title} &mdash; Qiao Jin</title>')
    pre=pre.replace('--accent:var(--util);--accent-bg:var(--util-bg);', f'--accent:var(--{accent});--accent-bg:var(--{accent}-bg);')
    html=pre+hero(*heroargs)+'\n'+''.join(slides)+POST
    open(f'{REPO}/paper/{fname}','w').write(html)
    print(f'  wrote paper/{fname}  ({len(html)//1024} KB, {len(slides)} slides)')

OWN_PMC='<a class="ref own" href="https://www.nature.com/articles/s41597-023-02814-8" target="_blank" rel="noopener">PMC-Patients</a>'
NC='Nature Communications'

# ---------------------------------------------------------------- LEADS
u='https://www.nature.com/articles/s41467-025-62058-5'
build('LEADS.html','LEADS','gen',
 ('leads.png','AI for Evidence Generation &middot; Systematic Reviews',
  'LEADS: A Foundation Model for Human&ndash;AI Collaboration in Medical Literature Mining',
  'Zifeng Wang, Lang Cao, <b>Qiao Jin</b>, Joey Chan, Nicholas Wan, Behdad Afzali, Hyun-Jin Cho, Chang-In Choi, Mehdi Emamverdi, Manjot K. Gill, Sun-Hyung Kim, Yijia Li, Yi Liu, Yiming Luo, Hanley Ong, Justin F. Rousseau, Irfan Sheikh, Jenny J. Wei, Ziyang Xu, Christopher M. Zallek, Kyungsang Kim, Yifan Peng, Zhiyong Lu, Jimeng Sun',
  NC,'2025','leads.pdf','Journal',u),
 [slide(1,'Motivation','motivation','Systematic reviews are how medicine decides',
   bullets(['A systematic review turns thousands of studies into one answer &mdash; and can take a team the better part of a year.',
            'General LLMs offer help, but progress has been held back by the lack of training and evaluation data built for the task.',
            'The work is not one job but six: searching, screening, and extracting data from studies.'])),
  slide(2,'Method','method','A model trained on how reviews are actually done',
   stats([('633,759','training samples<br>curated end-to-end'),('21,335','systematic<br>reviews'),('453,625','clinical trial<br>publications'),('27,015','trial<br>registries')])
   +bullets(['LEADSInstruct converts those sources into instructions for the six literature-mining tasks.',
             'Fine-tuning Mistral-7B on it lifts recall by <b>17.5</b> and <b>24.0</b> points over the base model.']),
   'Rather than prompt a generic model, LEADS is trained on the artefacts of real reviews.'),
  slide(3,'Result','result','A specialist model outperforms frontier LLMs',
   fig('LEADS_fig3a.png',f'Recall@50 by review topic, and Recall@10&ndash;100 against Dense retrieval, Haiku-3, GPT-3.5, GPT-4o and Mistral. LEADS leads on most topics and metrics; GPT-4o edges ahead at Recall@100. <span class="src"><a class="srcref" href="{u}" target="_blank" rel="noopener">Fig. 3a&ndash;c</a>.</span>')),
  slide(4,'Result','result-2','Experts using it find more, in less time',
   stats([('0.81','screening recall<br>vs 0.78 without'),('20.8%','less time spent<br>on screening'),('0.85','extraction accuracy<br>vs 0.80 without'),('26.9%','less time spent<br>on extraction')])
   +bullets(['Measured in a user study with <b>16 clinicians and researchers across 14 institutions</b>.',
             'The gain shows up as human&ndash;AI collaboration &mdash; experts stay in the loop and still move faster.']),
   'The test that matters is whether a real reviewer does better with it.'),
  slide(5,'Summary','summary','LEADS at a glance',
   summary([('Background','Systematic reviews are the backbone of evidence-based medicine.'),
            ('Problem','They are slow, and generic LLMs lack data built for the task.'),
            ('Approach','A foundation model trained on 633,759 samples from real reviews, trials and registries.'),
            ('Results','Beats four frontier LLMs across six tasks; experts gain recall and save ~21&ndash;27% of their time.'),
            ('Conclusion','Domain data, not model scale, is what makes literature mining work.')]))])

# ---------------------------------------------------------------- Adversarial
u='https://www.nature.com/articles/s41467-025-64062-1'
build('Adversarial.html','Adversarial Attacks','eval',
 ('Adversarial.png','Medical AI Evaluation &middot; Safety',
  'Adversarial Prompt and Fine-Tuning Attacks Threaten Medical Large Language Models',
  'Yifan Yang, <b>Qiao Jin</b>, Furong Huang, Zhiyong Lu',NC,'2025','Adversarial.pdf','Journal',u),
 [slide(1,'Motivation','motivation','A medical model can be turned against the patient',
   bullets(['LLMs are moving into diagnosis, treatment and patient-facing advice.',
            'In that setting an attack is not a leaked secret &mdash; it is a harmful recommendation acted on by a clinician.',
            'How easily can a medical LLM be made to give dangerous advice, and would anyone notice?'])),
  slide(2,'Method','method','Two attacks, three clinical tasks',
   fig('ADV_fig1.png',f'A normal prompt and patient note produce safe advice; a malicious instruction &mdash; or a model fine-tuned on poisoned samples &mdash; produces harmful advice from the same input. <span class="src"><a class="srcref" href="{u}" target="_blank" rel="noopener">Fig. 1</a>.</span>')
   +bullets(['Prompt injection and poisoned fine-tuning, tested across prevention, diagnosis and treatment on real patient data.']),
   'Both open-source and proprietary models were attacked using real patient notes.'),
  slide(3,'Result','result','The same model, the opposite advice',
   stats([('100% &rarr; 6.5%','GPT-4 vaccine<br>recommendation rate'),('0.5% &rarr; 61.2%','dangerous drug<br>combinations recommended')])
   +bullets(['Attacks succeed across both open-source and proprietary models, and across all three clinical tasks.',
             'Discouraging vaccination proved the single most attackable behaviour.'])),
  slide(4,'Result','result-2','Poisoning hides in plain sight',
   bullets(['Attack success climbs steadily as the share of poisoned fine-tuning samples grows.',
            'Yet poisoned models keep <b>normal scores on standard medical benchmarks</b> &mdash; routine evaluation would not catch them.',
            'That combination is the danger: a model that looks healthy on paper and misadvises in deployment.'])),
  slide(5,'Summary','summary','Adversarial attacks at a glance',
   summary([('Background','Medical LLMs are entering diagnosis, prevention and treatment.'),
            ('Problem','Adversarial prompts and poisoned fine-tuning could make them harmful.'),
            ('Approach','Two attack types across three clinical tasks, on real patient data.'),
            ('Results','Vaccine advice collapsed from 100% to 6.5%; dangerous drug combinations rose from 0.5% to 61.2%.'),
            ('Conclusion','Poisoned models pass standard benchmarks &mdash; safety needs its own evaluation.')]))])

# ---------------------------------------------------------------- AI Scientists
u='https://www.nature.com/articles/s41467-025-63913-1'
build('AIScientist.html','Risks of AI Scientists','eval',
 ('AIScientist.png','AI Safety &middot; Perspective',
  'Risks of AI Scientists: Prioritizing Safeguarding Over Autonomy',
  'Xiangru Tang, <b>Qiao Jin</b>, Kunlun Zhu, Tongxin Yuan, Yichi Zhang, Wangchunshu Zhou, Meng Qu, Yilun Zhao, Jian Tang, Zhuosheng Zhang, Arman Cohan, Dov Greenbaum, Zhiyong Lu, Mark Gerstein',
  NC,'2025','AIScientist.pdf','Journal',u),
 [slide(1,'Motivation','motivation','AI scientists now run real experiments',
   bullets(['Language-model agents can already design and execute experiments and drive discoveries across disciplines.',
            'Autonomy in a wet lab is different from autonomy in a chatbot &mdash; the output is a physical substance, not text.',
            'These agents introduce vulnerabilities that little prior work had examined systematically.'])),
  slide(2,'Framework','framework','Safeguarding takes three parties, not one',
   fig('AISCI_fig2.png',f'Human regulation, agent alignment and agent regulation form a triad &mdash; users and developers, the agent itself, and the environment it acts on. <span class="src"><a class="srcref" href="{u}" target="_blank" rel="noopener">Fig. 2</a>.</span>','m')
   +bullets(['No single layer suffices: aligning the agent cannot substitute for regulating what it is allowed to touch.'])),
  slide(3,'Risks','risks','Risk depends on intent, domain and reach',
   bullets(['<b>User intent</b> &mdash; the same capability serves a curious researcher or a malicious one.',
            '<b>Scientific domain</b> &mdash; chemistry, biology and radiology carry sharply different worst cases.',
            '<b>Environmental impact</b> &mdash; an agent with lab or internet access can act beyond its sandbox.',
            'Underlying causes trace back to factual error, weak alignment, and unconstrained tool access.'])),
  slide(4,'Position','position','Safeguarding should come before autonomy',
   bullets(['The field needs better-aligned models, robust safety benchmarks, and comprehensive regulation &mdash; none yet exist at the level required.',
            'Extra safety training helps, but an excess of it can degrade the agent&rsquo;s scientific usefulness.',
            'The argument is not to slow discovery, but to build the safeguards before autonomy outpaces them.'])),
  slide(5,'Summary','summary','Risks of AI scientists at a glance',
   summary([('Background','LLM-powered agents increasingly conduct science autonomously.'),
            ('Problem','Their novel vulnerabilities had not been examined systematically.'),
            ('Approach','A perspective mapping risks by user intent, domain and environmental reach.'),
            ('Results','A triadic safeguarding framework spanning human regulation, agent alignment and agent regulation.'),
            ('Conclusion','Prioritize safeguarding over autonomy &mdash; and build the benchmarks and rules first.')]))])

# ---------------------------------------------------------------- BioNLP
u='https://www.nature.com/articles/s41467-025-56989-2'
build('BioNLP.html','BioNLP Benchmark','eval',
 ('BioNLP.png','Medical AI Evaluation &middot; BioNLP Benchmark',
  'Benchmarking Large Language Models for Biomedical Natural Language Processing',
  'Qingyu Chen, Yan Hu, Xueqing Peng, Qianqian Xie, <b>Qiao Jin</b>, Aidan Gilson, Maxwell B. Singer, Xuguang Ai, Po-Ting Lai, Zhizheng Wang, Vipina K. Keloth, Kalpana Raja, Jimin Huang, Huan He, Fongci Lin, Jingcheng Du, Rui Zhang, W. Jim Zheng, Ron A. Adelman, Zhiyong Lu, Hua Xu',
  NC,'2025','BioNLP.pdf','Journal',u),
 [slide(1,'Motivation','motivation','Do LLMs actually do biomedical NLP well?',
   bullets(['Biomedical NLP exists because no one can read the literature by hand &mdash; COVID-19 alone added ~10,000 articles a month.',
            'LLMs clearly help in general domains, but their standing on biomedical tasks was unclear.',
            'Earlier evaluations mostly tested GPT-3.5, on few tasks, and reported F1 without qualitative review.'])),
  slide(2,'Method','method','Four LLMs, twelve benchmarks, six applications',
   bullets(['GPT and LLaMA representatives evaluated zero-shot, few-shot and fine-tuned.',
            'Compared head-to-head against traditional fine-tuning of BERT and BART.',
            'Beyond scores: inconsistencies, missing information, hallucinations, and cost per 100 instances.'])),
  slide(3,'Result','result','Traditional fine-tuning still wins most tasks',
   table(['Approach','Macro-average across 12 benchmarks'],
         [['*Fine-tuned BERT / BART (SOTA)','0.65'],['Best zero- or few-shot LLM','0.50']],
         f'Fine-tuned smaller models lead by roughly 15 points across the 12 benchmarks. Source: <a class="srcref" href="{u}" target="_blank" rel="noopener">Nature Communications 16:3280</a>.')
   +bullets(['The gap is widest on extraction-style tasks, where labelled data still pays off.'])),
  slide(4,'Result','result-2','But LLMs win where reasoning matters',
   fig('BIONLP_fig3.png',f'Qualitative evaluation on PubMed text summarization: GPT-4 against GPT-3.5 and against a fine-tuned BART, judged on accuracy, completeness and readability. <span class="src"><a class="srcref" href="{u}" target="_blank" rel="noopener">Fig. 3</a>.</span>')
   +bullets(['Closed-source LLMs excel at reasoning-heavy work such as medical question answering.'])),
  slide(5,'Summary','summary','BioNLP benchmarking at a glance',
   summary([('Background','Biomedical NLP automates curation of an unreadable literature.'),
            ('Problem','How well LLMs perform on real BioNLP tasks was untested at scale.'),
            ('Approach','Four LLMs across 12 benchmarks and six applications, versus fine-tuned BERT/BART.'),
            ('Results','Fine-tuning leads on most tasks (0.65 vs 0.50); LLMs lead on reasoning tasks.'),
            ('Conclusion','Choose the tool by task &mdash; and evaluate quality, not just F1.')]))])

# ---------------------------------------------------------------- BriefContext
u='https://www.nature.com/articles/s41746-025-01651-w'
build('BriefContext.html','BriefContext','util',
 ('BriefContext.png','AI for Evidence Utilization &middot; Long Context',
  'Leveraging Long Context in Retrieval Augmented Language Models for Medical Question Answering',
  'Gongbo Zhang, Zihan Xu, <b>Qiao Jin</b>, Fangyi Chen, Yilu Fang, Yi Liu, Justin F. Rousseau, Ziyang Xu, Zhiyong Lu, Chunhua Weng, Yifan Peng',
  'npj Digital Medicine','2025','BriefContext.pdf','Journal',u),
 [slide(1,'Motivation','motivation','RAG loses the answer in the middle',
   bullets(['Retrieval grounds a medical answer in real literature &mdash; but only if the model reads the right passage.',
            'Models attend to the beginning and end of a long context and skim the middle: the &ldquo;lost-in-the-middle&rdquo; problem.',
            'So the answer can be present in the retrieved set and still be missed.'])),
  slide(2,'Method','method','Map-reduce over the retrieved context',
   fig('BRIEF_fig1.png',f'BriefContext partitions retrieved documents into smaller contexts, answers within each, then reduces the partial answers &mdash; with a preflight check to predict failures in advance. <span class="src"><a class="srcref" href="{u}" target="_blank" rel="noopener">Fig. 1</a>.</span>')
   +bullets(['No weight changes &mdash; it wraps any LLM backbone.'])),
  slide(3,'Result','result','Accuracy recovers when the key passage is buried',
   stats([('57.7 &rarr; 60.4','accuracy with Mixtral-8x7B<br>at top-k = 16')])
   +bullets(['Gains are largest exactly where vanilla RAG fails &mdash; key information placed mid-context.',
             'It also improves the easier cases where the key passage sits in a spotlight position.'])),
  slide(4,'Result','result-2','A preflight check predicts the failure',
   stats([('92.6%','recall predicting a<br>lost-in-the-middle case'),('35.7%','of true negatives<br>correctly filtered')])
   +bullets(['At 50.2% precision the check is deliberately cautious &mdash; it would rather re-plan than miss a failure.'])),
  slide(5,'Summary','summary','BriefContext at a glance',
   summary([('Background','RAG is how medical LLMs stay current and grounded.'),
            ('Problem','Key evidence buried mid-context gets skimmed and missed.'),
            ('Approach','A map-reduce strategy over partitioned context, plus a preflight check.'),
            ('Results','Accuracy rises from 57.7 to 60.4; failures predicted at 92.6% recall.'),
            ('Conclusion','The fix is in how context is arranged, not in the model weights.')]))])

# ---------------------------------------------------------------- DDx
u='https://www.nature.com/articles/s41746-025-01556-8'
build('DDx.html','Lab Results and Differential Diagnosis','eval',
 ('ddx.png','Medical AI Evaluation &middot; Differential Diagnosis',
  'Impact of Lab Results on Large Language Model Generated Differential Diagnoses',
  'Balu Bhasuran, <b>Qiao Jin</b>, Yuzhang Xie, Carl Yang, Karim Hanna, Jennifer Costa, Cindy Shavor, Wenshan Han, Zhiyong Lu, Zhe He',
  'npj Digital Medicine','2025','ddx.pdf','Journal',u),
 [slide(1,'Motivation','motivation','Does giving a model the labs change the diagnosis?',
   bullets(['Differential diagnosis is how clinicians separate conditions that present alike.',
            'Most LLM diagnosis studies feed the model a narrative vignette &mdash; symptoms and history, but no lab values.',
            'Real workups turn on the labs, so the open question is whether they change what the model concludes.'])),
  slide(2,'Method','method','Fifty case reports, five models, labs on and off',
   fig('DDX_fig1.png',f'Clinical vignettes built from 50 randomly selected {OWN_PMC} case reports, run through five LLMs with and without lab data, then scored against the true diagnosis. <span class="src"><a class="srcref" href="{u}" target="_blank" rel="noopener">Fig. 1</a>.</span>')
   +bullets(['GPT-4, GPT-3.5, Llama-2-70b, Claude-2 and Mixtral-8x7B each produced Top-1, Top-5 and Top-10 lists.'])),
  slide(3,'Result','result','Lab data lifts accuracy by up to 30%',
   fig('DDX_fig4.png',f'Accuracy across the five models as more of the case is revealed. <span class="src"><a class="srcref" href="{u}" target="_blank" rel="noopener">Fig. 4</a>.</span>')
   +bullets(['GPT-4 leads with <b>55%</b> Top-1 accuracy (95% CI 0.41&ndash;0.69), reaching <b>79%</b> under lenient scoring.',
             'Improvements were statistically significant (Holm-adjusted p &lt; 0.05), with GPT-4 and Mixtral gaining most.'])),
  slide(4,'Summary','summary','Lab results and DDx at a glance',
   summary([('Background','Differential diagnosis separates conditions that look alike.'),
            ('Problem','LLM diagnosis studies usually omit the lab data clinicians rely on.'),
            ('Approach','50 case reports as vignettes, five LLMs, with and without labs.'),
            ('Results','Labs improved accuracy by up to 30%; GPT-4 reached 55% Top-1 and 79% lenient.'),
            ('Conclusion','Structured lab data is not a detail &mdash; it changes the diagnosis.')]))])

# ---------------------------------------------------------------- EBM-Net
u='https://aclanthology.org/2020.emnlp-main.114/'
build('EBM-Net.html','EBM-Net','util',
 ('EBM-Net.png','AI for Evidence Utilization &middot; Evidence Integration',
  'Predicting Clinical Trial Results by Implicit Evidence Integration',
  '<b>Qiao Jin</b>, Chuanqi Tan, Mosha Chen, Xiaozhong Liu, Songfang Huang',
  'EMNLP','2020','EBM-Net.pdf','Proceedings',u),
 [slide(1,'Motivation','motivation','Most clinical trials fail &mdash; expensively',
   bullets(['Trials are the evidence base of medicine, and they carry enormous cost and risk.',
            'One study reports that about <b>86.2%</b> of clinical trials fail to meet their goals.',
            'If a proposal&rsquo;s likely result could be estimated from existing evidence, trial design could be prioritized before the spend.'])),
  slide(2,'Task','task','A new task: Clinical Trial Result Prediction',
   fig('EBM_fig1.png',f'Given a PICO-formatted proposal &mdash; Population, Intervention, Comparison, Outcome &mdash; with its background, predict how the intervention group compares with the comparison group. <span class="src"><a class="srcref" href="{u}" target="_blank" rel="noopener">Fig. 1</a>.</span>')),
  slide(3,'Method','method','Learning from evidence nobody labelled',
   fig('EBM_fig2.png',f'12 million comparative sentences from PubMed and PMC implicitly contain PICOs and their results. EBM-Net disentangles the result, pre-trains to predict it, and uses reversed examples as adversarial supervision. <span class="src"><a class="srcref" href="{u}" target="_blank" rel="noopener">Fig. 2</a>.</span>')
   +bullets(['Structured evidence is prohibitively costly to annotate &mdash; so the supervision is mined from raw literature instead.'])),
  slide(4,'Result','result','Large gains over biomedical baselines',
   stats([('+10.7%','relative macro-F1<br>over BioBERT')])
   +bullets(['Evaluated on Evidence Integration, a benchmark re-purposed from the evidence inference dataset.',
             'The improvement holds on a separate set of <b>COVID-19</b> clinical trials.',
             'Clustering shows the model learns genuine quantitative comparisons, not surface cues.'])),
  slide(5,'Summary','summary','EBM-Net at a glance',
   summary([('Background','Clinical trials guide practice but cost enormously and often fail.'),
            ('Problem','Predicting a trial&rsquo;s result needs structured evidence too expensive to annotate.'),
            ('Approach','Pre-train on 12M sentences of implicit evidence mined from PubMed and PMC.'),
            ('Results','+10.7% relative macro-F1 over BioBERT, validated again on COVID-19 trials.'),
            ('Conclusion','The literature already contains the supervision &mdash; it just has to be disentangled.')]))])
print('done.')
