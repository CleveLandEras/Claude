
(function(){
  var sec=document.querySelector('section#p4'); var o=[];
  var sels=['.win','.win-in','.fig','.side','.menu','.main','.top','.steps','.sec','.mini','table','.card','.f','.bar','.dlg','.pop','.dd','.ddf','[id]'];
  sels.forEach(function(sel){
    sec.querySelectorAll(sel).forEach(function(e,i){
      var r=e.getBoundingClientRect(); if(r.width<4||r.height<4) return;
      o.push({sel:sel,i:i,x:Math.round(r.left),y:Math.round(r.top+scrollY),w:Math.round(r.width),h:Math.round(r.height),
              t:(e.innerText||'').replace(/\s+/g,' ').slice(0,40)});
    });
  });
  return JSON.stringify(o);
})()
