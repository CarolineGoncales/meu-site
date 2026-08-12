

// =======================================
// PROGRESSO
// =======================================

function registrarConclusao(trilha, apostila){

    const chave = `progresso_${trilha}`;

    let progresso = JSON.parse(localStorage.getItem(chave)) || [];

    if(!progresso.includes(apostila)){

        progresso.push(apostila);

        progresso.sort((a,b)=>a-b);

        localStorage.setItem(chave, JSON.stringify(progresso));

    }

}

function obterProgresso(trilha){

    const chave = `progresso_${trilha}`;

    return JSON.parse(localStorage.getItem(chave)) || [];

}

function calcularProgresso(trilha,total){

    return Math.round((obterProgresso(trilha).length/total)*100);

}

function trilhaConcluida(trilha,total){

    return obterProgresso(trilha).length>=total;

}

function apostilaConcluida(trilha, apostila){

    return obterProgresso(trilha).includes(apostila);

}

function progressoGeral(){

    let concluidas = 0;

    if(trilhaConcluida("python",6)) concluidas++;

    if(trilhaConcluida("ia",6)) concluidas++;

    if(trilhaConcluida("projetos",6)) concluidas++;

    if(trilhaConcluida("cloud",6)) concluidas++;

    return{

        concluidas: concluidas,

        porcentagem: Math.round((concluidas/4)*100)

    };

}

const CERTIFICADOS = {

    python:{
        nome:"TRILHA PYTHON",
        horas:60,
        codigo:"PY"
    },

    projetos:{
        nome:"TRILHA ANALISTA DE PROJETOS",
        horas:80,
        codigo:"GP"
    },

    ia:{
        nome:"TRILHA INTELIGÊNCIA ARTIFICIAL",
        horas:70,
        codigo:"IA"
    },

    cloud:{
        nome:"TRILHA CLOUD & DEVOPS",
        horas:80,
        codigo:"CL"
    }

};

function gerarCodigo(prefixo){

    return "CPG-" +
           prefixo + "-" +
           Date.now().toString().slice(-8);

}