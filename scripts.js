// ===== PROJETOS =====

function abrirExplicacao(){
  document.getElementById("popupExplicacao").style.display="flex";
}

function fecharPopupExplicacao(){
  document.getElementById("popupExplicacao").style.display="none";
}

function abrirCurso(){
  document.getElementById("popupExplicacao").style.display="none";
  document.getElementById("popupCurso").style.display="flex";
}

function fecharCurso(){
  let popup = document.getElementById("popupCurso");
  popup.style.display="none";

  let iframe = popup.querySelector("iframe");
  if(iframe) iframe.src = iframe.src;
}


// ===== PYTHON =====

function abrirExplicacaoPython(){
  document.getElementById("popupExplicacaoPython").style.display="flex";
}

function fecharPopupPython(){
  document.getElementById("popupExplicacaoPython").style.display="none";
}

function abrirCursoPython(){
  document.getElementById("popupExplicacaoPython").style.display="none";
  document.getElementById("popupCursoPython").style.display="flex";
}

function fecharCursoPython(){
  let popup = document.getElementById("popupCursoPython");
  popup.style.display="none";

  let iframe = popup.querySelector("iframe");
  if(iframe) iframe.src = iframe.src;
}


// ===== POPUP GENÉRICO =====

function abrirPopup(){
  document.getElementById("popup").style.display="flex";
}

function fecharPopup(){
  document.getElementById("popup").style.display="none";
}


// ===== CURSO PAGO =====

function abrirOpcoesCurso(){
  document.getElementById("popupOpcoes").style.display="flex";
}

function fecharOpcoes(){
  document.getElementById("popupOpcoes").style.display="none";
}


// ===== UDEMY =====

function abrirCursoUdemy(){
  document.getElementById("popupUdemy").style.display = "flex";
}

function fecharCursoUdemy(){
  document.getElementById("popupUdemy").style.display = "none";
}