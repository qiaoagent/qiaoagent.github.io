/* Reuse the iceberg contour for the second-click MCQ explanation. */
(function () {
  var root=document.getElementById('evaluation-limits');
  var ring=(window.DirectionFigures||{}).RING;
  if (!root || !ring) return;
  var host=root.querySelector('.mcq-limit-berg');
  var outline='M'+ring.map(function(p){return p.join(',');}).join('L')+'Z';
  host.innerHTML='<svg viewBox="0 -12 400 536" role="img" aria-labelledby="mcq-limit-title mcq-limit-desc">'+
    '<title id="mcq-limit-title">Multiple-choice accuracy is the tip of the evaluation iceberg</title>'+
    '<desc id="mcq-limit-desc">The MCQ layer is highlighted in red. Realistic and verifiable outcomes, trustworthy process, and safety remain below it in muted blue.</desc>'+
    '<defs><clipPath id="mcq-limit-contour"><path d="'+outline+'"/></clipPath>'+
    '<linearGradient id="mcq-limit-water" x1="0" x2="0" y1="0" y2="1"><stop stop-color="#e9f1f7"/><stop offset="1" stop-color="#fff"/></linearGradient>'+
    '<linearGradient id="mcq-limit-tip-fill" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#ca6861"/><stop offset="1" stop-color="#ac4244"/></linearGradient></defs>'+
    '<rect x="-12" y="180" width="424" height="344" fill="url(#mcq-limit-water)"/>'+
    '<path d="'+outline+'" fill="#edf2f6" stroke="#b9cad8" stroke-width="1.4"/>'+
    '<g clip-path="url(#mcq-limit-contour)">'+
      '<rect x="0" y="81" width="400" height="98" fill="#e3ecf3"/>'+
      '<rect x="0" y="181" width="400" height="94" fill="#d5e2ec"/>'+
      '<rect x="0" y="277" width="400" height="250" fill="#c6d8e6"/>'+
      '<path d="M192,4 L150,512 L0,512 L0,4Z" fill="#fff" opacity=".22"/>'+
      '<rect x="0" y="-12" width="400" height="92" fill="url(#mcq-limit-tip-fill)"/>'+
      '<path d="M0 80H400 M0 180H400 M0 276H400" stroke="#fff" stroke-width="3"/>'+
    '</g>'+
    '<path d="M134.8 77.3L178.4 16.2L186.4 16L247.8 78.3" fill="none" stroke="#a63f40" stroke-width="2" stroke-linejoin="round"/>'+
    '<text id="mcq-limit-tip" x="189" y="61" text-anchor="middle" fill="#fff" font-size="19" font-weight="700">MCQ</text>'+
    '<g fill="#7b94a8" text-anchor="middle" font-family="DM Sans,sans-serif" font-size="14" font-weight="500">'+
      '<text x="208" y="130">Realistic &amp; verifiable outcomes</text>'+
      '<text x="200" y="231">Trustworthy process</text>'+
      '<text x="210" y="343">Safety</text>'+
    '</g><path d="M-12 180H412" stroke="#aac3d6" stroke-width="1.5"/>'+
    '</svg>';

  function connect() {
    var stage=root.querySelector('.mcq-limit-stage'), overlay=root.querySelector('.mcq-limit-links');
    var box=stage.getBoundingClientRect(), tip=root.querySelector('#mcq-limit-tip').getBoundingClientRect();
    if (!box.width || !tip.width) return;
    overlay.setAttribute('viewBox','0 0 '+box.width+' '+box.height);
    var y=tip.top+tip.height/2-box.top, cx=tip.left+tip.width/2-box.left;
    var out='';
    root.querySelectorAll('.mcq-limit-card').forEach(function(card,i){
      var edge=card.getBoundingClientRect(), head=card.querySelector('.mcq-limit-head').getBoundingClientRect();
      var endX=(i?edge.left:edge.right)-box.left, endY=head.top+head.height/2-box.top;
      var startX=cx+(i?43:-43), elbow=(startX+endX)/2;
      out+='<path d="M'+startX+' '+y+' C'+elbow+' '+y+' '+elbow+' '+endY+' '+endX+' '+endY+'"/>'+
        '<circle cx="'+startX+'" cy="'+y+'" r="3"/>';
    });
    overlay.innerHTML=out;
  }
  var section=document.getElementById('evaluation');
  var overview=[].slice.call(section.children).filter(function(el){return el!==root;});
  var back=document.getElementById('mcq-limit-back');
  var exportButton=document.getElementById('mcq-limit-export');
  var exportStatus=document.getElementById('mcq-limit-export-status');
  var exporting=false;
  var expandedControls=section.querySelectorAll('[aria-controls="evaluation-limits"]');
  function open(options){
    if(!root.hidden) return;
    section.dispatchEvent(new Event('evaluation:mcq-issues'));
    overview.forEach(function(el){el.hidden=true;});
    root.hidden=false;
    exportStatus.textContent='';
    section.classList.add('ib-show-limits');
    expandedControls.forEach(function(el){el.setAttribute('aria-expanded','true');});
    requestAnimationFrame(connect);
    if(!options || options.focus!==false) back.focus({preventScroll:true});
  }
  function close(options){
    if(root.hidden || exporting) return;
    root.hidden=true;
    overview.forEach(function(el){el.hidden=false;});
    section.classList.remove('ib-show-limits');
    expandedControls.forEach(function(el){el.setAttribute('aria-expanded','false');});
    section.dispatchEvent(new Event('evaluation:restore'));
    if(location.hash==='#evaluation-limits') history.replaceState(null,'',location.pathname+location.search+'#evaluation');
    if(!options || options.focus!==false) expandedControls[0].focus({preventScroll:true});
  }
  window.EvaluationLimits={open:open,close:close};
  exportButton.addEventListener('click',async function(){
    if(exporting || root.hidden) return;
    exporting=true;
    exportButton.disabled=true;
    back.disabled=true;
    root.setAttribute('aria-busy','true');
    exportButton.querySelector('span:last-child').textContent='Exporting…';
    exportStatus.textContent='';
    try {
      if(document.fonts) await document.fonts.ready;
      connect();
      await window.exportEvaluationLimitsPng(root,'medical-ai-evaluation-mcq-gaps.png');
      exportStatus.textContent='PNG downloaded.';
    } catch(error) {
      exportStatus.textContent='Could not export the PNG. Please try again.';
      console.error('MCQ evaluation gaps PNG export failed:',error);
    } finally {
      exporting=false;
      exportButton.disabled=false;
      back.disabled=false;
      root.removeAttribute('aria-busy');
      exportButton.querySelector('span:last-child').textContent='Export PNG';
    }
  });
  back.addEventListener('click',function(){close();});
  root.addEventListener('keydown',function(event){
    if(event.key==='Escape'){event.stopPropagation();close();}
    else if(event.key===' ' && event.target.closest('button')) event.stopPropagation();
  });
  function syncHash(){
    if(location.hash==='#evaluation-limits') open({focus:false});
    else close({focus:false});
  }
  window.addEventListener('hashchange',syncHash);
  syncHash();
  if(document.fonts) document.fonts.ready.then(connect);
  window.addEventListener('resize',connect);
  window.addEventListener('load',connect);
})();
