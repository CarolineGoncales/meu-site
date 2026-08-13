(function () {
    const correspondencia = window.location.pathname.match(/material-(python|ia|cloud|projetos)-(\d+)\.html$/);
    const projeto = window.location.pathname.endsWith("material-gestao-projetos.html");
    const trilha = projeto ? "projetos" : correspondencia && correspondencia[1];
    const apostila = projeto ? 1 : correspondencia && Number(correspondencia[2]);

    if (!trilha || !apostila) return;

    function criarArea() {
        let area = document.getElementById("conclusao");
        if (area) {
            const antigo = area.querySelector("#btnConclusao");
            if (antigo && !antigo.dataset.cpgControlado) {
                const novo = antigo.cloneNode(true);
                novo.dataset.cpgControlado = "true";
                antigo.replaceWith(novo);
            }
            if (!area.querySelector("#erroConclusao")) {
                area.insertAdjacentHTML("beforeend", '<p id="erroConclusao" role="alert" style="color:#b91c1c;"></p>');
            }
            return area;
        }

        area = document.createElement("div");
        area.id = "conclusao";
        area.style.cssText = "display:none; text-align:center; margin:20px 0;";
        area.innerHTML = '<button id="btnConclusao" data-cpg-controlado="true" type="button" style="padding:12px 22px; border:0; border-radius:8px; cursor:pointer; font-weight:700;">✔ Concluir Apostila</button><p id="erroConclusao" role="alert" style="color:#b91c1c;"></p>';
        const controles = document.querySelector(".pdf-controls");
        controles.insertAdjacentElement("afterend", area);
        return area;
    }

    async function atualizar() {
        const area = criarArea();
        const botao = document.getElementById("btnConclusao");
        const erro = document.getElementById("erroConclusao");
        erro.textContent = "";
        botao.disabled = true;
        botao.textContent = "Consultando progresso...";

        try {
            const apostilas = await CPG.obterProgresso(trilha);
            const concluida = apostilas.includes(apostila);
            botao.textContent = concluida ? "✔ Apostila concluída" : "✔ Concluir Apostila";
            botao.disabled = concluida;
            botao.onclick = async () => {
                botao.disabled = true;
                botao.textContent = "Registrando conclusão...";
                try {
                    await CPG.concluirApostila(trilha, apostila);
                    botao.textContent = "✔ Apostila concluída";
                } catch (e) {
                    botao.disabled = false;
                    botao.textContent = "✔ Concluir Apostila";
                    erro.textContent = e.message || "Erro ao registrar a conclusão.";
                }
            };
        } catch (e) {
            botao.disabled = false;
            botao.textContent = "Tentar novamente";
            botao.onclick = atualizar;
            erro.textContent = e.message || "Não foi possível consultar seu progresso.";
        }
        return area;
    }

    const observador = new MutationObserver(() => {
        const pagina = document.getElementById("pagina-atual");
        const ultimaPagina = pagina && /Página\s+\d+\s+de\s+(\d+)/.exec(pagina.textContent);
        const atual = pagina && /Página\s+(\d+)/.exec(pagina.textContent);
        if (!ultimaPagina || !atual) return;
        const area = criarArea();
        if (Number(atual[1]) === Number(ultimaPagina[1])) {
            area.style.display = "block";
            atualizar();
        } else {
            area.style.display = "none";
        }
    });

    document.addEventListener("DOMContentLoaded", () => {
        if (!CPG.exigirSessao()) return;
        observador.observe(document.getElementById("pagina-atual"), { childList: true, characterData: true, subtree: true });
    });
}());
