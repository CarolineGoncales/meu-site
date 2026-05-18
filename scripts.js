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

// =========================================
// ACESSIBILIDADE GLOBAL CPG
// =========================================

const audio =
document.getElementById(
"apresentacaoAudio"
);

const voiceButton =
document.getElementById(
"voiceButton"
);




// =========================================
// INICIAR ÁUDIO
// =========================================

window.addEventListener("load", () => {

setTimeout(() => {

if(audio){

audio.play()

.then(() => {

if(voiceButton){

voiceButton.style.display =
"none";

}

})

.catch(() => {

if(voiceButton){

voiceButton.style.display =
"flex";

}

});

}

}, 2000);

});


// =========================================
// ÁUDIO FINALIZOU
// =========================================

if(audio){

audio.addEventListener("ended", () => {

const isMobile =
/Android|iPhone|iPad|iPod/i
.test(navigator.userAgent);


// MOBILE

if(isMobile){

setTimeout(() => {

    iniciarReconhecimento();

}, 3500);

}


// DESKTOP

else{

setTimeout(() => {

    iniciarReconhecimento();

}, 2000);

}

});

}




if(voiceButton){

voiceButton.addEventListener(
"click",

() => {

const isMobile =
/Android|iPhone|iPad|iPod/i
.test(navigator.userAgent);


// =========================================
// MOBILE
// =========================================

if(isMobile){

voiceButton.style.display =
"none";

iniciarReconhecimento();

setTimeout(() => {

audio.play();

}, 500);

}


// =========================================
// DESKTOP
// =========================================

else{

audio.play();

voiceButton.style.display =
"none";

setTimeout(() => {

iniciarReconhecimento();

}, 1000);

}

}

);

}

// =========================================
// LEITURA DA PÁGINA
// =========================================

function lerPagina(){

const descricaoPagina =
document.body.dataset.voice;

if(!descricaoPagina){

return;

}

const fala =
new SpeechSynthesisUtterance(
descricaoPagina
);

fala.lang = "pt-BR";

fala.onend = () => {

setTimeout(() => {

    iniciarReconhecimento();

}, 4000);

};

speechSynthesis.speak(fala);

}




// =========================================
// RECONHECIMENTO
// =========================================

function iniciarReconhecimento(){

const SpeechRecognition =
window.SpeechRecognition ||
window.webkitSpeechRecognition;

if(!SpeechRecognition){

return;

}

const recognition =
new SpeechRecognition();

recognition.lang = "pt-BR";

recognition.continuous = false;

recognition.start();

recognition.onresult = (event) => {

const texto =
event.results[
event.results.length -1
][0]
.transcript
.toLowerCase();

console.log(texto);

// =========================================
// ATIVAR LEITURA
// =========================================



if(
texto.includes("ativar leitura")
)
{

lerPagina();

}




// =========================================
// NAVEGAÇÃO PRINCIPAL
// =========================================

if(
texto.includes("home") ||
texto.includes("início")
){

window.location.href =
"index.html?voice=true";

}



if(texto.includes("sobre")){

window.location.href =
"sobre.html?voice=true";

}



if(
texto.includes("curso") ||
texto.includes("cursos")
){

window.location.href =
"cursos.html?voice=true";

}



if(
texto.includes("certificação") ||
texto.includes("certificações")
){

window.location.href =
"certificacao.html?voice=true";

}



if(texto.includes("contato")){

window.location.href =
"contato.html?voice=true";

}


if(
texto.includes("play") ||
texto.includes("c p g play")
){

abrirPlayPopup();

setTimeout(() => {

const fala =
new SpeechSynthesisUtterance(

"Você está prestes a entrar no CPG Play. Um ambiente interativo criado para explorar tecnologia, desafios, inteligência artificial e inovação. O CPG Play ainda está em evolução e algumas áreas podem não possuir suporte completo de acessibilidade por voz neste momento. Você deseja entrar ou cancelar?"

);

fala.lang = "pt-BR";

speechSynthesis.speak(fala);

fala.onend = () => {

setTimeout(() => {

    iniciarReconhecimentoPlay();

}, 2000);

};

}, 1000);

}




// =========================================
// CPG PLAY
// =========================================

if(
texto.includes("terminal") ||
texto.includes("terminal hacker")
){

window.location.href =
"games/terminal.html";

}



if(
texto.includes("code") ||
texto.includes("código") ||
texto.includes("c p g code")
){

window.location.href =
"games/code.html";

}



if(
texto.includes("laboratório") ||
texto.includes("labs") ||
texto.includes("logic cloud labs")
){

window.location.href =
"games/logic-cloud-labs.html";

}



}}

// =========================================
// LEITURA AUTOMÁTICA ENTRE PÁGINAS
// =========================================

window.addEventListener("load", () => {

const params =
new URLSearchParams(
window.location.search
);

const voiceMode =
params.get("voice");

if(voiceMode === "true"){

setTimeout(() => {

    lerPagina();

}, 3000);

}

});

// =========================================
// RECONHECIMENTO POPUP PLAY
// =========================================

function iniciarReconhecimentoPlay(){

const SpeechRecognition =
window.SpeechRecognition ||
window.webkitSpeechRecognition;

if(!SpeechRecognition){

return;

}

const recognition =
new SpeechRecognition();

recognition.lang = "pt-BR";

recognition.continuous = false;

recognition.start();

recognition.onresult = (event) => {

const texto =
event.results[0][0]
.transcript
.toLowerCase();

console.log(texto);



// =========================================
// ENTRAR
// =========================================

if(
texto.includes("entrar")
){

window.location.href =
"play.html?voice=true";

}



// =========================================
// CANCELAR
// =========================================

if(
texto.includes("cancelar")
){

fecharPlayPopup();

}

};

}