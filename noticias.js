document.addEventListener("DOMContentLoaded", () => {

    const container = document.getElementById("painel-noticias");

    if (!container) {
        return;
    }

    function tempoRelativo(dataTexto) {

        if (!dataTexto) {
            return "data não informada";
        }

        const data = new Date(dataTexto);
        const agora = new Date();

        if (isNaN(data.getTime())) {
            return "data não informada";
        }

        const diferenca =
            Math.floor((agora - data) / 1000);

        if (diferenca < 60) {
            return "agora";
        }

        const minutos =
            Math.floor(diferenca / 60);

        if (minutos < 60) {
            return `há ${minutos} ${
                minutos === 1 ? "minuto" : "minutos"
            }`;
        }

        const horas =
            Math.floor(minutos / 60);

        if (horas < 24) {
            return `há ${horas} ${
                horas === 1 ? "hora" : "horas"
            }`;
        }

        const dias =
            Math.floor(horas / 24);

        if (dias === 1) {
            return "ontem";
        }

        if (dias < 7) {
            return `há ${dias} dias`;
        }

        return data.toLocaleDateString(
            "pt-BR",
            {
                day: "2-digit",
                month: "2-digit",
                year: "numeric"
            }
        );
    }


    function escaparHTML(texto) {

        const elemento =
            document.createElement("div");

        elemento.textContent = texto || "";

        return elemento.innerHTML;
    }


    function criarNoticia(noticia) {

        const item =
            document.createElement("a");

        item.className =
            "noticia-item";

        item.href =
            noticia.link;

        item.target =
            "_blank";

        item.rel =
            "noopener noreferrer";


        const titulo =
            escaparHTML(noticia.titulo);


        const fonte =
            escaparHTML(noticia.fonte);


        const tempo =
            tempoRelativo(noticia.data);


        item.innerHTML = `
            <div class="noticia-conteudo">

                <h3>${titulo}</h3>

                <div class="noticia-meta">
                    <span class="noticia-fonte">
                        ${fonte}
                    </span>

                    <span class="noticia-separador">
                        •
                    </span>

                    <span class="noticia-tempo">
                        ${tempo}
                    </span>
                </div>

            </div>

            <span class="noticia-seta">
                →
            </span>
        `;


        return item;
    }


    function mostrarNoticias(noticias) {

        container.innerHTML = "";


        if (
            !Array.isArray(noticias) ||
            noticias.length === 0
        ) {

            container.innerHTML = `
                <div class="noticias-vazio">
                    Nenhuma notícia disponível no momento.
                </div>
            `;

            return;
        }


        noticias.forEach((noticia) => {

            const elemento =
                criarNoticia(noticia);

            container.appendChild(elemento);

        });
    }


    async function carregarNoticias() {

        try {

            container.innerHTML = `
                <div class="noticias-carregando">
                    Carregando notícias...
                </div>
            `;


            const resposta =
                await fetch(
                    "noticias.json?v=" +
                    Date.now(),
                    {
                        cache: "no-store"
                    }
                );


            if (!resposta.ok) {
                throw new Error(
                    "Não foi possível carregar noticias.json"
                );
            }


            const dados =
                await resposta.json();


            mostrarNoticias(
                dados.noticias
            );


        } catch (erro) {

            console.error(
                "Erro ao carregar notícias:",
                erro
            );


            container.innerHTML = `
                <div class="noticias-erro">
                    Não foi possível carregar as notícias agora.
                </div>
            `;
        }
    }


    carregarNoticias();

});