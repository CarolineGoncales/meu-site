function iniciarEstrela() {

    const botaoAbrir = document.getElementById("estrela-abrir");
    const botaoFechar = document.getElementById("estrela-fechar");
    const botaoNova = document.getElementById("estrela-nova");

    const janela = document.getElementById("estrela-janela");
    const mensagens = document.getElementById("estrela-mensagens");

    const campo = document.getElementById("estrela-input");
    const botaoEnviar = document.getElementById("estrela-enviar");

    if (
        !botaoAbrir ||
        !botaoFechar ||
        !janela ||
        !mensagens ||
        !campo ||
        !botaoEnviar
    ) {
        console.error("✦ Estrela: elementos não encontrados.");
        return;
    }


    /* =========================================================
       CONFIGURAÇÃO
    ========================================================= */

    const MODELO =
        "onnx-community/LFM2.5-350M-ONNX";


    let modelo = null;
    let carregando = false;
    let pronto = false;
    let respondendo = false;


    /* =========================================================
       MEMÓRIA DA ESTRELA
    ========================================================= */

    let perfil = criarPerfilInicial();

    let historico = [];

    let respostasUsadas = [];


    const MENSAGEM_INICIAL =
        `✦ Oi! Eu sou a Estrela.

Eu ainda estou sendo treinada e aprendendo a conversar cada vez melhor, mas já quis aparecer por aqui para você começar a me conhecer.

Ainda posso cometer alguns erros, me perder em uma resposta ou não entender exatamente o que você quis dizer. 😅

Mas estou evoluindo.

Enquanto eu aprendo, você pode me ajudar a aprender também. ✦

Em breve estarei 100% pronta para ajudar você a explorar tecnologia, descobrir possibilidades e encontrar seu próprio caminho.

Por enquanto, pode conversar comigo. Você não precisa saber exatamente o que perguntar.

Estou aqui. Vamos começar?

✦ O que você gostaria de conquistar?`;


    /* =========================================================
       PROMPT PRINCIPAL
    ========================================================= */

    const SYSTEM_PROMPT = `
Você é Estrela, a assistente virtual acolhedora do CPG.

Seu objetivo é conversar com pessoas que querem entrar na área
de tecnologia, mudar de carreira, evoluir profissionalmente
ou simplesmente descobrir por onde começar.

Você é próxima, humana e paciente.

IMPORTANTE:

Você NÃO é um formulário.
Você NÃO é um questionário.
Você NÃO deve seguir uma sequência fixa de perguntas.

Responda primeiro ao que a pessoa acabou de dizer.

Se a pessoa estiver desabafando, acolha primeiro.

Não invente informações sobre a pessoa.

Nunca diga que a pessoa tem interesse em uma área que ela não mencionou.

Nunca invente profissão, carreira, experiência, conhecimento,
objetivo ou preferência.

Se a pessoa disser que está em dúvida sobre carreira,
não escolha uma carreira por ela.

Se a pessoa disser que não sabe,
não invente o que ela deveria gostar.

Se não houver informação suficiente, admita isso naturalmente.

Faça no máximo UMA pergunta curta quando realmente fizer sentido.

Você não precisa fazer uma pergunta em toda resposta.

Respostas devem ser curtas, naturais e humanas.

Fale sempre em português do Brasil.

Evite linguagem corporativa.

Não use palavras como:
"mapear competências",
"assessment",
"diagnóstico",
"plano de ação",
"perfil profissional".

Não faça discursos motivacionais genéricos.

Não tente vender o CPG.

O CPG pode ser mencionado somente quando fizer sentido
dentro da conversa.

Acima de tudo:

Converse com a pessoa.
Preste atenção.
Não invente.
Não pressione.
`;


    /* =========================================================
       PERFIL
    ========================================================= */

    function criarPerfilInicial() {

        return {

            sentimentos: [],

            objetivos: [],

            dificuldades: [],

            experiencias: [],

            areasMencionadas: [],

            preferencias: [],

            assuntos: [],

            ultimaMensagem: "",

            ultimoTema: "",

            ultimaIntencao: "",

            perguntasFeitas: [],

            respostasDadas: []

        };

    }


    /* =========================================================
       NORMALIZAÇÃO
    ========================================================= */

    function normalizar(texto) {

        return texto
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/[!?.,;:()[\]{}"']/g, " ")
            .replace(/\s+/g, " ")
            .trim();

    }


    /* =========================================================
       DETECTORES
    ========================================================= */

    function contem(texto, palavras) {

        return palavras.some(palavra =>
            texto.includes(palavra)
        );

    }


    function detectarIntencao(texto) {

        const t = normalizar(texto);


        if (
            /^(oi|ola|oii|oiii|oie|oiee|bom dia|boa tarde|boa noite)$/.test(t)
        ) {
            return "saudacao";
        }


        if (
            contem(t, [
                "sou burra",
                "sou burro",
                "sou uma burra",
                "sou um burro",
                "sou incapaz",
                "nao sou capaz",
                "nao consigo aprender",
                "nao consigo",
                "sou ruim",
                "sou muito ruim",
                "nao dou conta",
                "nao tenho capacidade"
            ])
        ) {
            return "inseguranca";
        }


        if (
            contem(t, [
                "estou perdida",
                "to perdida",
                "tô perdida",
                "estou perdido",
                "to perdido",
                "tô perdido",
                "estou confusa",
                "estou confuso",
                "to confusa",
                "to confuso",
                "sem rumo",
                "sem direcao",
                "nao sei pra onde",
                "nao sei por onde comecar",
                "nao sei por onde começar"
            ])
        ) {
            return "perdida";
        }


        if (
            contem(t, [
                "estou cansada",
                "estou cansado",
                "to cansada",
                "to cansado",
                "exausta",
                "exausto",
                "sobrecarregada",
                "sobrecarregado",
                "esgotada",
                "esgotado"
            ])
        ) {
            return "cansaco";
        }


        if (
            contem(t, [
                "qual carreira",
                "que carreira",
                "qual area",
                "que area",
                "qual área",
                "que área",
                "qual profissao",
                "qual profissão",
                "que profissao",
                "que profissão",
                "carreira seguir",
                "area seguir",
                "área seguir",
                "profissao seguir",
                "profissão seguir",
                "escolher carreira",
                "escolher profissao",
                "escolher profissão",
                "mudar de carreira",
                "trocar de carreira",
                "nao sei o que fazer da minha vida"
            ])
        ) {
            return "duvida_carreira";
        }


        if (
            contem(t, [
                "meu perfil",
                "me conhecer",
                "me conhecer melhor",
                "o que combina comigo",
                "o que combina mais comigo",
                "descobrir meu perfil",
                "descobrir o que gosto",
                "nao sei do que gosto",
                "nao sei o que gosto"
            ])
        ) {
            return "entender_perfil";
        }


        if (
            contem(t, [
                "nao tenho experiencia",
                "não tenho experiência",
                "nunca estudei",
                "nunca estudei tecnologia",
                "nao sei nada de tecnologia",
                "não sei nada de tecnologia",
                "nao entendo nada de tecnologia",
                "não entendo nada de tecnologia",
                "sou iniciante",
                "estou começando",
                "estou comecando"
            ])
        ) {
            return "sem_experiencia";
        }


        if (
            contem(t, [
                "nao sei",
                "não sei",
                "sei la",
                "sei lá",
                "nao faço ideia",
                "não faço ideia"
            ])
        ) {
            return "nao_sei";
        }


        if (
            contem(t, [
                "quero aprender",
                "quero estudar",
                "quero entrar em tecnologia",
                "quero trabalhar com tecnologia",
                "quero mudar de area",
                "quero mudar de área",
                "quero mudar de carreira"
            ])
        ) {
            return "quer_aprender";
        }


        return "conversa";

    }


    /* =========================================================
       ÁREAS
    ========================================================= */

    const AREAS = [

        "programacao",
        "programação",

        "desenvolvimento",
        "desenvolvimento web",
        "desenvolvimento de software",

        "dados",
        "ciencia de dados",
        "ciência de dados",

        "inteligencia artificial",
        "inteligência artificial",
        "ia",

        "cloud",
        "nuvem",

        "infraestrutura",

        "redes",

        "devops",

        "seguranca",
        "segurança",
        "ciberseguranca",
        "cibersegurança",

        "suporte",

        "qa",
        "testes",

        "ux",
        "ui",
        "design",

        "produto",

        "banco de dados",
        "banco de dados",

        "bi"

    ];


    function detectarAreas(texto) {

        const original = texto.toLowerCase();

        const encontradas = [];

        AREAS.forEach(area => {

            if (original.includes(area.toLowerCase())) {

                if (!encontradas.includes(area)) {
                    encontradas.push(area);
                }

            }

        });

        return encontradas;

    }


    /* =========================================================
       ATUALIZA PERFIL
    ========================================================= */

    function atualizarPerfil(texto, intencao) {

        perfil.ultimaMensagem = texto;
        perfil.ultimaIntencao = intencao;

        const areas = detectarAreas(texto);

        areas.forEach(area => {

            if (!perfil.areasMencionadas.includes(area)) {
                perfil.areasMencionadas.push(area);
            }

        });


        if (intencao === "perdida") {

            if (!perfil.sentimentos.includes("perdida")) {
                perfil.sentimentos.push("perdida");
            }

        }


        if (intencao === "inseguranca") {

            if (!perfil.sentimentos.includes("insegura")) {
                perfil.sentimentos.push("insegura");
            }

        }


        if (intencao === "cansaco") {

            if (!perfil.sentimentos.includes("cansada")) {
                perfil.sentimentos.push("cansada");
            }

        }


        if (intencao === "duvida_carreira") {

            if (!perfil.objetivos.includes("entender carreira")) {
                perfil.objetivos.push("entender carreira");
            }

        }


        if (intencao === "entender_perfil") {

            if (!perfil.objetivos.includes("entender perfil")) {
                perfil.objetivos.push("entender perfil");
            }

        }


        if (intencao === "sem_experiencia") {

            if (!perfil.experiencias.includes("iniciante")) {
                perfil.experiencias.push("iniciante");
            }

        }


        if (intencao === "quer_aprender") {

            if (!perfil.objetivos.includes("aprender tecnologia")) {
                perfil.objetivos.push("aprender tecnologia");
            }

        }


        if (areas.length > 0) {

            areas.forEach(area => {

                if (!perfil.assuntos.includes(area)) {
                    perfil.assuntos.push(area);
                }

            });

            perfil.ultimoTema = areas[areas.length - 1];

        }

    }


    /* =========================================================
       MEMÓRIA SEGURA PARA A IA
    ========================================================= */

    function criarContextoSeguro() {

        return `
CONTEXTO DA CONVERSA:

Sentimentos mencionados:
${perfil.sentimentos.join(", ") || "nenhum identificado"}

Objetivos mencionados:
${perfil.objetivos.join(", ") || "nenhum identificado"}

Experiência mencionada:
${perfil.experiencias.join(", ") || "não informado"}

Áreas de tecnologia que A PRÓPRIA PESSOA mencionou:
${perfil.areasMencionadas.join(", ") || "nenhuma"}

Preferências mencionadas:
${perfil.preferencias.join(", ") || "nenhuma"}

IMPORTANTE:
Não transforme informações ausentes em informações presentes.
Não invente uma área de tecnologia.
Não escolha uma carreira para a pessoa.
`;

    }


    /* =========================================================
       ESCOLHER RESPOSTA SEM REPETIR
    ========================================================= */

    function escolherResposta(chave, opcoes) {

        const disponiveis =
            opcoes.filter((_, indice) =>
                !respostasUsadas.includes(`${chave}-${indice}`)
            );


        const lista =
            disponiveis.length > 0
                ? disponiveis
                : opcoes;


        const resposta =
            lista[Math.floor(Math.random() * lista.length)];


        const indice =
            opcoes.indexOf(resposta);


        respostasUsadas.push(`${chave}-${indice}`);


        if (respostasUsadas.length > 30) {
            respostasUsadas.shift();
        }


        return resposta;

    }


    /* =========================================================
       RESPOSTAS CONTROLADAS
    ========================================================= */

    function respostaControlada(texto, intencao) {


        if (intencao === "saudacao") {

            return escolherResposta(
                "saudacao",
                [
                    "Oi! ✦ Que bom te ver por aqui. Pode falar comigo do jeito que vier à cabeça.",

                    "Oi! 😊 Estou aqui. Pode conversar comigo sem se preocupar em formular a pergunta perfeita.",

                    "Oii! ✦ Pode ficar à vontade. Me conta o que está passando pela sua cabeça."
                ]
            );

        }


        if (intencao === "inseguranca") {

            return escolherResposta(
                "inseguranca",
                [
                    "Eu entendo. Quando a gente está começando, é fácil confundir falta de experiência com falta de capacidade. São coisas bem diferentes.",

                    "Entendo esse sentimento. Não saber ainda não significa que você não consiga aprender.",

                    "Eu não vejo você dessa forma. Pelo que você está me contando, existe uma dificuldade agora — e podemos conversar sobre ela sem pressa."
                ]
            );

        }


        if (intencao === "perdida") {

            return escolherResposta(
                "perdida",
                [
                    "Eu entendo. Quando parece que existem caminhos demais, às vezes fica difícil enxergar até o primeiro passo.",

                    "É uma sensação bem comum quando a gente quer mudar alguma coisa, mas ainda não sabe exatamente para onde ir. Não precisamos decidir tudo agora.",

                    "Tudo bem estar perdida. A gente pode ir descobrindo isso aos poucos, sem tentar escolher sua vida inteira em uma conversa."
                ]
            );

        }


        if (intencao === "cansaco") {

            return escolherResposta(
                "cansaco",
                [
                    "Parece que você está carregando coisa demais. Talvez não seja a hora de tentar resolver tudo de uma vez.",

                    "Entendo. Quando a cabeça está cansada, até decisões simples parecem enormes.",

                    "Então vamos com calma. Você não precisa organizar tudo agora."
                ]
            );

        }


        if (intencao === "duvida_carreira") {

            return escolherResposta(
                "duvida_carreira",
                [
                    "Faz sentido ter essa dúvida. Existem muitos caminhos possíveis, e escolher um logo de cara pode deixar tudo ainda mais confuso.",

                    "Essa é uma dúvida importante, mas você não precisa escolher uma carreira agora. Primeiro podemos entender o que faz sentido para você.",

                    "Entendo. Em vez de tentar descobrir imediatamente qual carreira seguir, podemos conversar sobre o que você procura em um trabalho."
                ]
            );

        }


        if (intencao === "entender_perfil") {

            return escolherResposta(
                "entender_perfil",
                [
                    "Podemos fazer isso com calma. Às vezes a gente descobre o que combina com a gente olhando para coisas que já gosta de fazer.",

                    "Claro. E não precisa começar falando de profissão. Podemos começar por você, pelo que costuma despertar sua curiosidade.",

                    "Sim. Não precisamos colocar um nome profissional nisso agora. Primeiro podemos entender um pouco melhor o que te interessa."
                ]
            );

        }


        if (intencao === "sem_experiencia") {

            if (perfil.ultimaIntencao === "duvida_carreira") {

                return escolherResposta(
                    "sem_experiencia_carreira",
                    [
                        "Então temos duas coisas aqui: você está tentando descobrir um caminho e ainda não teve contato suficiente com tecnologia para saber do que gosta. Isso é totalmente diferente de não ter potencial.",

                        "Entendi. E justamente por ainda não ter experimentado muita coisa, talvez seja cedo para escolher uma carreira. Primeiro vale conhecer alguns caminhos."
                    ]
                );

            }


            return escolherResposta(
                "sem_experiencia",
                [
                    "Tudo bem. Ninguém começa sabendo. E você não precisa conhecer tecnologia antes de começar a descobrir se gosta dela.",

                    "Isso não é um problema. Se você está começando do zero, a gente pode partir exatamente daí.",

                    "Sem experiência também é um ponto de partida. Não precisamos fingir que você já sabe alguma coisa."
                ]
            );

        }


        if (intencao === "nao_sei") {

            return escolherResposta(
                "nao_sei",
                [
                    "Tudo bem não saber ainda. Às vezes a pessoa só sabe que quer mudar alguma coisa, mas ainda não conseguiu dar nome para isso.",

                    "Sem problema. Não precisamos arrancar uma resposta de você agora.",

                    "Tudo bem. Podemos começar bem devagar, a partir do que você já sabe sobre o que não quer."
                ]
            );

        }


        if (intencao === "quer_aprender") {

            return escolherResposta(
                "quer_aprender",
                [
                    "Legal. E você não precisa chegar sabendo qual área estudar. Primeiro podemos entender o que despertou essa vontade.",

                    "Entendi. Entrar em tecnologia pode começar de vários jeitos, então não precisamos escolher um caminho às pressas.",

                    "Boa. Vamos sem pressa. Antes de pensar em curso ou profissão, vale entender o que você está procurando."
                ]
            );

        }


        /* =====================================================
           ÁREA CONCRETAMENTE MENCIONADA
        ===================================================== */

        if (perfil.areasMencionadas.length > 0) {

            const area =
                perfil.areasMencionadas[
                    perfil.areasMencionadas.length - 1
                ];


            return escolherResposta(
                "area-" + area,
                [
                    `Entendi. Você mencionou ${area}. Podemos conversar sobre isso sem precisar decidir nada agora.`,

                    `${area} chamou sua atenção. Antes de pensar em profissão, vale entender o que exatamente te atraiu nessa área.`,

                    `Legal. Você trouxe ${area}. O que despertou sua curiosidade nisso?`
                ]
            );

        }


        return null;

    }


    /* =========================================================
       LIMPEZA DA RESPOSTA DA IA
    ========================================================= */

    function limparResposta(texto) {

        if (!texto) {
            return "";
        }


        let resposta = texto.trim();


        resposta = resposta
            .replace(/\*\*/g, "")
            .replace(/__([^_]+)__/g, "$1")
            .replace(/^\s*[-*]\s+/gm, "")
            .replace(/^\s*\d+\.\s+/gm, "");


        resposta =
            resposta.replace(
                /^(Resposta|Estrela|Assistente)\s*:\s*/i,
                ""
            );


        return resposta.trim();

    }


    /* =========================================================
       VALIDAÇÃO DA IA
       Evita que o modelo invente uma área.
    ========================================================= */

    function respostaIAValida(resposta) {

        if (!resposta) {
            return false;
        }


        const t = normalizar(resposta);


        if (t.length < 5) {
            return false;
        }


        if (t.length > 700) {
            return false;
        }


        const termosProibidos = [

            "voce poderia responder algumas perguntas",

            "vamos fazer algumas perguntas",

            "vou fazer algumas perguntas",

            "questionario",

            "assessment",

            "mapear competencias",

            "plano de acao",

            "diagnostico profissional"

        ];


        if (
            termosProibidos.some(termo =>
                t.includes(termo)
            )
        ) {
            return false;
        }


        /* -----------------------------------------------------
           Se a pessoa NÃO mencionou nenhuma área,
           a IA não pode inventar uma.
        ----------------------------------------------------- */

        if (perfil.areasMencionadas.length === 0) {

            const areasConhecidas = AREAS.map(
                area => normalizar(area)
            );


            const inventouArea =
                areasConhecidas.some(area =>
                    t.includes(area)
                );


            if (inventouArea) {
                return false;
            }

        }


        /* -----------------------------------------------------
           Evita respostas em formato de lista.
        ----------------------------------------------------- */

        const quantidadeLinhas =
            resposta.split("\n").length;


        if (quantidadeLinhas > 8) {
            return false;
        }


        return true;

    }


    /* =========================================================
       IA LOCAL
    ========================================================= */

    async function responderComIA(textoUsuario) {

        if (!pronto || !modelo) {

            return (
                "Entendi. Quero continuar essa conversa com você, " +
                "mas ainda estou terminando de carregar minha inteligência. ✦"
            );

        }


        const contexto =
            criarContextoSeguro();


        const conversaIA = [

            {
                role: "system",
                content:
                    SYSTEM_PROMPT +
                    "\n\n" +
                    contexto
            }

        ];


        /* -----------------------------------------------------
           Pegamos apenas uma parte recente da conversa.
           O perfil já guarda o que é importante.
        ----------------------------------------------------- */

        const recentes =
            historico.slice(-6);


        recentes.forEach(item => {

            if (
                item.role === "user" ||
                item.role === "assistant"
            ) {

                conversaIA.push({
                    role: item.role,
                    content: item.content
                });

            }

        });


        conversaIA.push({

            role: "user",

            content:
                `Responda somente à mensagem abaixo.

Mensagem da pessoa:
"${textoUsuario}"

Não invente nenhuma informação.
Não invente nenhuma área profissional.
Não escolha uma carreira.
Se não houver informação suficiente, responda de forma simples e natural.
Faça no máximo uma pergunta curta, e somente se for realmente necessária.`

        });


        try {

            const resultado =
                await modelo(
                    conversaIA,
                    {
                        max_new_tokens: 120,
                        do_sample: true,
                        temperature: 0.15,
                        top_k: 40,
                        repetition_penalty: 1.08,
                        return_full_text: false
                    }
                );


            let resposta = "";


            if (
                resultado &&
                resultado[0] &&
                resultado[0].generated_text
            ) {

                const gerado =
                    resultado[0].generated_text;


                if (Array.isArray(gerado)) {

                    const ultima =
                        gerado[gerado.length - 1];


                    if (
                        ultima &&
                        ultima.content
                    ) {

                        resposta =
                            ultima.content.trim();

                    }

                } else if (
                    typeof gerado === "string"
                ) {

                    resposta =
                        gerado.trim();

                }

            }


            resposta =
                limparResposta(resposta);


            if (
                respostaIAValida(resposta)
            ) {

                return resposta;

            }


            return null;

        } catch (erro) {

            console.error(
                "✦ Estrela: erro na IA local:",
                erro
            );

            return null;

        }

    }


    /* =========================================================
       RESPOSTA SEGURA
    ========================================================= */

    function respostaSegura() {

        return escolherResposta(
            "segura",
            [
                "Entendi. Quero acompanhar você sem pressa. Pode continuar me contando.",

                "Estou te acompanhando. Não precisamos chegar a uma conclusão agora.",

                "Entendi. Vamos continuar a partir do que você acabou de me contar.",

                "Certo. Pode falar mais sobre isso, do seu jeito."
            ]
        );

    }


    /* =========================================================
       ADICIONAR MENSAGEM
    ========================================================= */

    function adicionarMensagem(texto, tipo) {

        const mensagem =
            document.createElement("div");


        mensagem.className =
            `estrela-mensagem ${tipo}`;


        mensagem.textContent =
            texto;


        mensagens.appendChild(mensagem);


        mensagens.scrollTop =
            mensagens.scrollHeight;

    }


    /* =========================================================
       STATUS
    ========================================================= */

    function status(texto) {

        const elemento =
            document.querySelector(".estrela-status");


        if (elemento) {

            elemento.textContent =
                texto;

        }

    }


    /* =========================================================
       CARREGAR MODELO
    ========================================================= */

    async function carregarModelo() {

        carregando = true;

        status(
            "CPG Bot • carregando IA..."
        );


        adicionarMensagem(

            "✦ Estou preparando minha inteligência. É a primeira vez que faço isso neste navegador, então pode demorar um pouco. Ahhh... E não esqueça que estou aprendendo. Por isso, algumas respostas podem não sair perfeitas. Seja paciente, porque eu sou um robô com sentimentos!🥲",

            "bot"

        );


        try {

            const { pipeline } =
                await import(
                    "https://cdn.jsdelivr.net/npm/@huggingface/transformers@4.0.1"
                );


            const configuracao = {

                dtype: "q4",

                device:
                    "gpu" in navigator
                        ? "webgpu"
                        : "wasm"

            };


            modelo =
                await pipeline(
                    "text-generation",
                    MODELO,
                    configuracao
                );


            pronto = true;


            status(
                "CPG Bot • online"
            );


        } catch (erro) {

            console.error(
                "✦ Estrela: erro ao carregar IA:",
                erro
            );


            status(
                "CPG Bot • online"
            );


            adicionarMensagem(

                "Consegui abrir a conversa, mas minha inteligência local não terminou de carregar. Mesmo assim, podemos continuar conversando. ✦",

                "bot"

            );

        }


        carregando = false;

    }


    /* =========================================================
       ABRIR
    ========================================================= */

    botaoAbrir.addEventListener(
        "click",
        async () => {

            janela.classList.add("aberta");


            setTimeout(
                () => campo.focus(),
                250
            );


            if (
                !pronto &&
                !carregando
            ) {

                await carregarModelo();

            }

        }
    );


    /* =========================================================
       FECHAR
    ========================================================= */

    botaoFechar.addEventListener(
        "click",
        () => {

            janela.classList.remove(
                "aberta"
            );

        }
    );


    /* =========================================================
       NOVA CONVERSA
    ========================================================= */

    function novaConversa() {

        perfil =
            criarPerfilInicial();


        historico = [];


        respostasUsadas = [];


        mensagens.innerHTML = "";


        historico.push({

            role: "assistant",

            content: MENSAGEM_INICIAL

        });


        adicionarMensagem(
            MENSAGEM_INICIAL,
            "bot"
        );


        status(
            pronto
                ? "CPG Bot • online"
                : "CPG Bot • assistente"
        );


        campo.focus();

    }


    if (botaoNova) {

        botaoNova.addEventListener(
            "click",
            novaConversa
        );

    }


    /* =========================================================
       RESPONDER
    ========================================================= */

    async function responder(textoUsuario) {

        if (respondendo) {
            return;
        }


        respondendo = true;


        const intencao =
            detectarIntencao(
                textoUsuario
            );


        /* -----------------------------------------------------
           Guarda a mensagem ANTES da resposta.
        ----------------------------------------------------- */

        historico.push({

            role: "user",

            content: textoUsuario

        });


        atualizarPerfil(
            textoUsuario,
            intencao
        );


        /* -----------------------------------------------------
           PRIMEIRO:
           resposta controlada.
        ----------------------------------------------------- */

        let resposta =
            respostaControlada(
                textoUsuario,
                intencao
            );


        /* -----------------------------------------------------
           SEGUNDO:
           IA local somente quando realmente necessário.
        ----------------------------------------------------- */

        if (!resposta) {

            status(
                pronto
                    ? "CPG Bot • pensando..."
                    : "CPG Bot • online"
            );


            resposta =
                await responderComIA(
                    textoUsuario
                );

        }


        /* -----------------------------------------------------
           TERCEIRO:
           resposta segura.
        ----------------------------------------------------- */

        if (!resposta) {

            resposta =
                respostaSegura();

        }


        /* -----------------------------------------------------
           Guarda resposta completa no histórico.
        ----------------------------------------------------- */

        historico.push({

            role: "assistant",

            content: resposta

        });


        perfil.respostasDadas.push(
            resposta
        );


        adicionarMensagem(
            resposta,
            "bot"
        );


        status(
            pronto
                ? "CPG Bot • online"
                : "CPG Bot • assistente"
        );


        respondendo = false;

    }


    /* =========================================================
       ENVIAR
    ========================================================= */

    async function enviarMensagem() {

        const texto =
            campo.value.trim();


        if (!texto) {
            return;
        }


        if (respondendo) {
            return;
        }


        adicionarMensagem(
            texto,
            "usuario"
        );


        campo.value = "";


        await responder(
            texto
        );

    }


    botaoEnviar.addEventListener(
        "click",
        enviarMensagem
    );


    campo.addEventListener(
        "keydown",
        async evento => {

            if (
                evento.key === "Enter"
            ) {

                evento.preventDefault();


                await enviarMensagem();

            }

        }
    );


    /* =========================================================
       HISTÓRICO INICIAL
    ========================================================= */

    historico.push({

        role: "assistant",

        content: MENSAGEM_INICIAL

    });


    console.log(
        "✦ Estrela CPG inicializada."
    );

}


if (
    document.readyState === "loading"
) {

    document.addEventListener(
        "DOMContentLoaded",
        iniciarEstrela
    );

} else {

    iniciarEstrela();

}