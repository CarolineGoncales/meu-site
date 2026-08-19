const CPG_API_URL = "https://cpg-estude-backend.onrender.com";

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

    projetos: 6,

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


async function obterProgresso(trilha) {

    const email = obterEmailSessao();

    if (!email) {

        throw new Error(
            "Sessão não encontrada."
        );

    }


    const resposta = await fetch(

        `${CPG_API_URL}/progresso?email=${encodeURIComponent(email)}&trilha=${encodeURIComponent(trilha)}`

    );


    const dados = await respostaJson(resposta);


    return Array.isArray(dados.apostilas)
        ? dados.apostilas
        : [];

}


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


async function renderizarProgressoTrilha(trilha) {

    const apostilas =
        await obterProgresso(trilha);


    const total =
        CPG_TOTAL_APOSTILAS[trilha];


    if (!total) {

        throw new Error(
            `Trilha "${trilha}" não está cadastrada no progresso.`
        );

    }


    const percentual = Math.round(

        (apostilas.length /
        total) * 100

    );


    const barra = document.querySelector(

        ".trilha-info .barra span"

    );


    const texto = document.querySelector(

        ".trilha-info .progresso p"

    );


    if (barra) {

        barra.style.width =
            `${percentual}%`;

    }


    if (texto) {

        texto.textContent =

            `${percentual}% concluído ` +
            `(${apostilas.length}/${total} apostilas)`;

    }


    return apostilas;

}


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

    progressoGeral,

    renderizarProgressoTrilha

};