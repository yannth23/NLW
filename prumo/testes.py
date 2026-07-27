"""Testes do verificador. Rodam sem rede.

    python3 -m unittest prumo.testes -v

A rede entra apenas na função `_abrir`, e é ela que os testes substituem. Todo
o resto — reconhecer a citação no texto, montar a URL da fonte oficial, achar o
artigo dentro do corpo da norma, detectar que o artigo foi alterado — é lógica
pura e é onde os erros aparecem.
"""

from __future__ import annotations

import unittest
from unittest import mock

from . import citacoes
from .fonte_simulada import L9784, abrir


def verificar(texto):
    with mock.patch.object(citacoes, "_abrir", side_effect=abrir):
        return citacoes.verificar(citacoes.extrair(texto))


class Extracao(unittest.TestCase):

    def test_formatos_de_lei(self):
        for texto in ("Lei nº 9.784, de 1999",
                      "Lei 9784/1999",
                      "Lei nº 9.784, de 29 de janeiro de 1999",
                      "lei 9.784/99"):
            with self.subTest(texto=texto):
                (c,) = citacoes.extrair(texto)
                self.assertEqual((c.tipo, c.numero, c.ano), ("lei", "9784", "1999"))

    def test_ano_de_dois_digitos(self):
        self.assertEqual(citacoes.extrair("Lei 8.666/93")[0].ano, "1993")
        self.assertEqual(citacoes.extrair("Lei Complementar 123/06")[0].ano, "2006")

    def test_lei_complementar_nao_vira_lei_ordinaria(self):
        (c,) = citacoes.extrair("Lei Complementar nº 87, de 1996")
        self.assertEqual(c.tipo, "lei-complementar")

    def test_decreto_e_decreto_lei(self):
        (a,) = citacoes.extrair("Decreto nº 70.235/1972")
        (b,) = citacoes.extrair("Decreto-Lei nº 1.598, de 1977")
        self.assertEqual(a.tipo, "decreto")
        self.assertEqual(b.tipo, "decreto-lei")

    def test_artigo_antes_e_depois_da_norma(self):
        (a,) = citacoes.extrair("o art. 26 da Lei nº 9.784, de 1999 dispõe")
        (b,) = citacoes.extrair("Lei nº 9.784, de 1999, art. 26")
        self.assertEqual(a.artigo, "26")
        self.assertEqual(b.artigo, "26")

    def test_artigo_de_outra_frase_nao_gruda(self):
        # O ponto final entre o artigo e a norma corta o vínculo.
        (c,) = citacoes.extrair("Cita-se o art. 99. Adiante, a Lei nº 9.784, de 1999.")
        self.assertIsNone(c.artigo)

    def test_ctn_e_constituicao(self):
        achados = citacoes.extrair("art. 173 do CTN e art. 5º da Constituição Federal")
        tipos = {c.tipo: c.artigo for c in achados}
        self.assertEqual(tipos, {"ctn": "173", "cf": "5"})

    def test_sumulas(self):
        achados = citacoes.extrair("A Súmula CARF nº 11 e a Súmula STJ nº 555.")
        self.assertEqual([c.numero for c in achados],
                         ["CARF nº 11", "STJ nº 555"])

    def test_mesma_norma_artigos_diferentes_sao_duas(self):
        achados = citacoes.extrair(
            "art. 26 da Lei nº 9.784, de 1999 e art. 50 da Lei nº 9.784, de 1999")
        self.assertEqual(len(achados), 2)

    def test_repeticao_identica_colapsa(self):
        achados = citacoes.extrair("Lei 9.784/1999. Depois, Lei nº 9.784, de 1999.")
        self.assertEqual(len(achados), 1)

    def test_texto_sem_citacao(self):
        self.assertEqual(citacoes.extrair("O auto não indica a data do fato."), [])


class Urls(unittest.TestCase):

    def primeira(self, texto):
        return citacoes.urls(citacoes.extrair(texto)[0])

    def test_lei_antiga_fica_na_raiz(self):
        self.assertIn("https://www.planalto.gov.br/ccivil_03/leis/L9784.htm",
                      self.primeira("Lei nº 9.784, de 1999"))

    def test_lei_recente_vai_para_o_bloco_do_ano(self):
        self.assertEqual(
            self.primeira("Lei nº 13.988, de 2020")[0],
            "https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2020/lei/L13988.htm")

    def test_lei_complementar_tem_caminho_proprio(self):
        self.assertTrue(all("/lcp/" in u
                            for u in self.primeira("Lei Complementar nº 87, de 1996")))

    def test_ctn_aponta_para_a_versao_compilada(self):
        self.assertIn("compilado", self.primeira("art. 173 do CTN")[0])


class BlocoDoArtigo(unittest.TestCase):

    def setUp(self):
        self.texto = citacoes._limpa(L9784)

    def test_recorta_ate_o_artigo_seguinte(self):
        bloco = citacoes._bloco_do_artigo(self.texto, "26")
        self.assertIn("intimação do interessado", bloco)
        self.assertIn("§ 3º", bloco)
        self.assertNotIn("deverão ser motivados", bloco)

    def test_artigo_inexistente(self):
        self.assertIsNone(citacoes._bloco_do_artigo(self.texto, "87"))

    def test_nao_confunde_prefixo(self):
        # "Art. 5" não pode casar dentro de "Art. 50".
        self.assertIsNone(citacoes._bloco_do_artigo(self.texto, "5"))


class Verificacao(unittest.TestCase):

    def um(self, texto):
        (r,) = verificar(texto)
        return r

    def test_norma_e_artigo_existentes_conferem(self):
        r = self.um("o art. 26 da Lei nº 9.784, de 1999")
        self.assertEqual(r.status, "CONFERE")
        self.assertTrue(r.url.endswith("L9784.htm"))
        self.assertTrue(r.consultado_em)

    def test_norma_existe_artigo_nao(self):
        r = self.um("o art. 87 da Lei nº 9.784, de 1999")
        self.assertEqual(r.status, "ARTIGO_AUSENTE")
        self.assertFalse(r.passa)

    def test_norma_inexistente(self):
        r = self.um("a Lei nº 14.999, de 2023")
        self.assertEqual(r.status, "NAO_ENCONTRADA")

    def test_artigo_alterado_e_sinalizado(self):
        r = self.um("art. 10 da Lei nº 13.988, de 2020")
        self.assertEqual(r.status, "CONFERE")
        self.assertTrue(r.alteracoes)
        self.assertIn("data do fato gerador", r.nota)

    def test_sumula_nao_passa_sozinha(self):
        r = self.um("Súmula CARF nº 11")
        self.assertEqual(r.status, "SEM_FONTE")
        self.assertFalse(r.passa)

    def test_fonte_fora_do_ar_nao_aprova(self):
        with mock.patch.object(citacoes, "_abrir",
                               return_value=(0, None, "TimeoutError: timed out")):
            (r,) = citacoes.verificar(citacoes.extrair("art. 26 da Lei nº 9.784, de 1999"))
        self.assertEqual(r.status, "INDISPONIVEL")
        self.assertFalse(r.passa)

    def test_uma_url_por_norma(self):
        # Duas citações da mesma lei abrem a fonte uma vez só.
        with mock.patch.object(citacoes, "_abrir", side_effect=abrir) as m:
            citacoes.verificar(citacoes.extrair(
                "art. 26 da Lei nº 9.784, de 1999 e art. 50 da Lei nº 9.784, de 1999"))
        self.assertEqual(m.call_count, 1)


class Relatorio(unittest.TestCase):

    def test_lista_o_que_nao_entrega(self):
        saida = citacoes.relatorio(verificar(
            "art. 26 da Lei nº 9.784, de 1999; art. 87 da Lei nº 9.784, de 1999"))
        self.assertIn("Não entregar ao usuário", saida)
        self.assertIn("art. 87", saida)

    def test_texto_limpo_nao_gera_secao_de_falha(self):
        saida = citacoes.relatorio(verificar("art. 26 da Lei nº 9.784, de 1999"))
        self.assertNotIn("Não entregar", saida)

    def test_sem_citacao(self):
        self.assertIn("Nenhuma citação", citacoes.relatorio([]))


class Prompts(unittest.TestCase):

    def test_biblioteca_completa(self):
        from . import prompts
        self.assertEqual(len(prompts.BIBLIOTECA), 8)
        self.assertEqual(sorted(prompts.BIBLIOTECA), [f"0{i}" for i in range(1, 9)])

    def test_auto_entra_delimitado(self):
        from . import prompts
        (msg,) = prompts.BIBLIOTECA["02"].montar("TEXTO DO AUTO")
        self.assertIn("<auto>\nTEXTO DO AUTO\n</auto>", msg["content"])

    def test_preambulo_e_cacheado(self):
        from . import prompts
        (bloco,) = prompts.sistema()
        self.assertEqual(bloco["cache_control"], {"type": "ephemeral"})

    def test_laudo_exige_nao_verificado(self):
        from .laudo import LAUDO
        self.assertIn("nao_verificado", LAUDO["required"])


if __name__ == "__main__":
    unittest.main()
