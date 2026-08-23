// No desenvolvimento local, o frontend usa o backend local. No site publicado,
// usa o serviço da Render; assim o progresso não fica preso ao computador local.
const CPG_API_URL = ["localhost", "127.0.0.1"].includes(window.location.hostname)
    ? "http://127.0.0.1:8000"
    : "https://cpg-estude-backend.onrender.com";


const CPG_TRILHAS = [
    "python",
    "ia",
    "cloud",
    "projetos",
    "banco-de-dados",
    "dados-bi",
    "desenvolvimento-web",
    "redes-computadores",
    "seguranca-informacao"
];


const CPG_TOTAL_APOSTILAS = {

    python: 6,

    ia: 6,

    cloud: 8,

    projetos: 24,

    "banco-de-dados": 6,

    "dados-bi": 6,

    "desenvolvimento-web": 6,

    "redes-computadores": 6,

    "seguranca-informacao": 6

};


function obterEmailSessao() {

    return localStorage.getItem("email");

}


function encerrarSessao() {

    [
        "usuario",
        "email",
        "status",
        "status_pagamento",
        "plano"
    ].forEach((chave) =>
        localStorage.removeItem(chave)
    );

}


function exigirSessao() {

    if (
        !obterEmailSessao() ||
        localStorage.getItem("status") !== "ativo"
    ) {

        window.location.replace("login.html");

        return false;

    }

    return true;

}


async function respostaJson(resposta) {

    let dados;

    try {

        dados = await resposta.json();

    } catch (_) {

        throw new Error(
            "A API retornou uma resposta inválida."
        );

    }


    if (!resposta.ok || dados.erro) {

        throw new Error(
            dados.erro ||
            "Não foi possível consultar a API."
        );

    }


    return dados;

}


/* =========================================================
   PROGRESSO NORMAL DAS TRILHAS
========================================================= */

async function obterProgresso(trilha) {

    const email = obterEmailSessao();

    if (!email) {

        throw new Error(
            "Sessão não encontrada."
        );

    }


    /*
     * A trilha PROJETOS possui:
     *
     * 1 apostila
     * 23 vídeos
     *
     * Total = 24 conteúdos
     */

    if (trilha === "projetos") {

        const respostaApostilas = await fetch(

            `${CPG_API_URL}/progresso?email=${encodeURIComponent(email)}&trilha=${encodeURIComponent(trilha)}`

        );


        const dadosApostilas =
            await respostaJson(respostaApostilas);


        const respostaVideos = await fetch(

            `${CPG_API_URL}/progresso-projetos?email=${encodeURIComponent(email)}`

        );


        const dadosVideos =
            await respostaJson(respostaVideos);


        const apostilas =
            Array.isArray(dadosApostilas.apostilas)
                ? dadosApostilas.apostilas
                : [];


        const videos =
            Array.isArray(dadosVideos.conteudos)
                ? dadosVideos.conteudos
                : [];


        const resultado = [];


        /*
         * A apostila representa o primeiro conteúdo.
         */

        if (apostilas.length > 0) {

            resultado.push(1);

        }


        /*
         * Cada vídeo representa um conteúdo.
         */

        videos.forEach((video) => {

            const numeroVideo = Number(video);

            if (
                Number.isInteger(numeroVideo) &&
                numeroVideo >= 101 &&
                numeroVideo <= 123 &&
                !resultado.includes(numeroVideo)
            ) {

                resultado.push(numeroVideo);

            }

        });


        return resultado;

    }


    /*
     * Todas as outras trilhas continuam
     * funcionando como antes.
     */

    const resposta = await fetch(

        `${CPG_API_URL}/progresso?email=${encodeURIComponent(email)}&trilha=${encodeURIComponent(trilha)}`

    );


    const dados =
        await respostaJson(resposta);


    return Array.isArray(dados.apostilas)
        ? dados.apostilas
        : [];

}


/* =========================================================
   CONCLUIR APOSTILA
========================================================= */

async function concluirApostila(trilha, apostila) {

    const email = obterEmailSessao();

    if (!email) {

        throw new Error(
            "Sessão não encontrada."
        );

    }


    const corpo = new URLSearchParams({

        email,

        trilha,

        apostila: String(apostila)

    });


    const resposta = await fetch(

        `${CPG_API_URL}/concluir-apostila`,

        {

            method: "POST",

            headers: {

                "Content-Type":
                    "application/x-www-form-urlencoded"

            },

            body: corpo.toString()

        }

    );


    return respostaJson(resposta);

}


/* =========================================================
   CONCLUIR VÍDEO — SOMENTE TRILHA PROJETOS
========================================================= */

async function concluirVideoProjetos(conteudo) {

    const email = obterEmailSessao();

    if (!email) {

        throw new Error(
            "Sessão não encontrada."
        );

    }


    const numero =
        Number(conteudo);


    if (
        !Number.isInteger(numero) ||
        numero < 101 ||
        numero > 123
    ) {

        throw new Error(
            "Conteúdo de vídeo inválido."
        );

    }


    const corpo = new URLSearchParams({

        email,

        conteudo: String(numero)

    });


    const resposta = await fetch(

        `${CPG_API_URL}/concluir-conteudo-projetos`,

        {

            method: "POST",

            headers: {

                "Content-Type":
                    "application/x-www-form-urlencoded"

            },

            body: corpo.toString()

        }

    );


    return respostaJson(resposta);

}


/* =========================================================
   PROGRESSO GERAL
========================================================= */

async function progressoGeral() {

    const progressos = await Promise.all(

        CPG_TRILHAS.map(
            async (trilha) => ({

                trilha,

                apostilas:
                    await obterProgresso(trilha)

            })
        )

    );


    const concluidas = progressos.filter(

        ({ trilha, apostilas }) =>

            apostilas.length >=
            CPG_TOTAL_APOSTILAS[trilha]

    ).length;


    return {

        concluidas,

        porcentagem:

            Math.round(

                (concluidas /
                CPG_TRILHAS.length) * 100

            )

    };

}


/* =========================================================
   MARCAR CONTEÚDOS CONCLUÍDOS — PROJETOS
========================================================= */

function marcarConteudosConcluidosProjetos(conteudos) {

    /*
     * APOSTILA
     */

    const linkApostila =
        document.querySelector(
            '.btn-material[href="material-gestao-projetos.html"]'
        );


    if (linkApostila) {

        const material =
            linkApostila.closest(".material") ||
            linkApostila.parentElement;


        if (material) {

            const nomeApostila =
                material.querySelector("strong");


            if (
                nomeApostila &&
                conteudos.includes(1)
            ) {

                adicionarStatusConcluido(
                    nomeApostila
                );

            }

        }

    }


    /*
     * VÍDEOS
     */

    const botoes =
        document.querySelectorAll(
            ".btn-video"
        );


    botoes.forEach((botao) => {

        const onclick =
            botao.getAttribute("onclick") || "";


        const correspondencia =
            onclick.match(
                /abrirVideoProjetos\s*\(\s*[^,]+,\s*(\d+)/
            );


        if (!correspondencia) {

            return;

        }


        const numero =
            Number(correspondencia[1]);


        const aula =
            botao.closest(".aula-item");


        if (!aula) {

            return;

        }


        const nomeAula =
            aula.querySelector("strong");


        if (!nomeAula) {

            return;

        }


        if (conteudos.includes(numero)) {

            adicionarStatusConcluido(
                nomeAula
            );

            botao.textContent =
                "✓ Concluído";

            botao.disabled = true;

            botao.style.background =
                "#6b7280";

            botao.style.cursor =
                "default";

        }

    });

}


/* =========================================================
   ADICIONAR STATUS CONCLUÍDO
========================================================= */

function adicionarStatusConcluido(elemento) {

    if (!elemento) {

        return;

    }


    if (
        elemento.querySelector(
            ".status-concluido"
        )
    ) {

        return;

    }


    const status =
        document.createElement("span");


    status.className =
        "status-concluido";


    status.textContent =
        " ✓ Concluído";


    status.style.color =
        "#16a34a";


    status.style.fontWeight =
        "bold";


    status.style.marginLeft =
        "6px";


    elemento.appendChild(status);

}


/* =========================================================
   RENDERIZAR PROGRESSO DA TRILHA
========================================================= */

async function renderizarProgressoTrilha(trilha) {

    const conteudos =
        await obterProgresso(trilha);


    const total =
        CPG_TOTAL_APOSTILAS[trilha];


    if (!total) {

        throw new Error(
            `Trilha "${trilha}" não está cadastrada no progresso.`
        );

    }


    const percentual = Math.round(

        (conteudos.length /
        total) * 100

    );


    const barra =
        document.querySelector(
            ".trilha-info .barra span"
        );


    const texto =
        document.querySelector(
            ".trilha-info .progresso p"
        );


    if (barra) {

        barra.style.width =
            `${percentual}%`;

    }


    if (texto) {

        texto.textContent =

            `${percentual}% concluído ` +
            `(${conteudos.length}/${total} conteúdos)`;

    }


    /*
     * Marca visualmente os conteúdos
     * concluídos da trilha Projetos.
     */

    if (trilha === "projetos") {

        marcarConteudosConcluidosProjetos(
            conteudos
        );

    }


    return conteudos;

}


/* =========================================================
   DISPONIBILIZAR API PARA O SITE
========================================================= */

window.CPG = {

    apiUrl:
        CPG_API_URL,

    trilhas:
        CPG_TRILHAS,

    totalApostilas:
        CPG_TOTAL_APOSTILAS,

    obterEmailSessao,

    encerrarSessao,

    exigirSessao,

    respostaJson,

    obterProgresso,

    concluirApostila,

    concluirVideoProjetos,

    progressoGeral,

    renderizarProgressoTrilha

};
