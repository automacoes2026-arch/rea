"""Testes com dados sintéticos: nenhum CNPJ real é usado."""

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import contagens_base as cb  # noqa: E402


def gerar_cnpj(base12: str) -> str:
    """Completa 12 dígitos sintéticos com dígitos verificadores válidos."""
    for d1 in "0123456789":
        for d2 in "0123456789":
            if cb.cnpj_valido(base12 + d1 + d2):
                return base12 + d1 + d2
    raise AssertionError("sem DV")


MATRIZ = gerar_cnpj("111111110001")
FILIAL = gerar_cnpj("111111110002")  # mesma raiz da matriz
OUTRA = gerar_cnpj("222222220001")

CONFIG = {
    "cnpj": "CNPJ",
    "colunas": {"no_segmento": "Seg", "abordada": "Abordada"},
}


def linhas():
    return [
        {"CNPJ": MATRIZ, "Seg": "sim", "Abordada": ""},
        {"CNPJ": FILIAL, "Seg": "", "Abordada": "x"},
        {"CNPJ": MATRIZ, "Seg": "", "Abordada": ""},  # duplicata exata
        {"CNPJ": OUTRA, "Seg": "nao", "Abordada": "nao"},
        {"CNPJ": "123", "Seg": "sim", "Abordada": "sim"},  # inválido
        {"CNPJ": "11111111111111", "Seg": "", "Abordada": ""},  # dígitos repetidos
    ]


class ValidacaoCNPJ(unittest.TestCase):
    def test_aceita_dv_correto_e_formatado(self):
        formatado = f"{OUTRA[:2]}.{OUTRA[2:5]}.{OUTRA[5:8]}/{OUTRA[8:12]}-{OUTRA[12:]}"
        self.assertTrue(cb.cnpj_valido(cb.cnpj_digitos(formatado)))

    def test_rejeita_dv_errado(self):
        errado = OUTRA[:13] + str((int(OUTRA[13]) + 1) % 10)
        self.assertFalse(cb.cnpj_valido(errado))


class Contagens(unittest.TestCase):
    def test_chave_raiz(self):
        r = cb.contar(linhas(), CONFIG)
        self.assertEqual(r["registros_totais"], 6)
        self.assertEqual(r["registros_cnpj_invalido"], 2)
        self.assertEqual(r["cadastros_validos"], 4)
        self.assertEqual(r["cnpjs_unicos"], 3)
        self.assertEqual(r["entidades_unicas"], 2)
        self.assertEqual(r["registros_duplicados"], 2)
        self.assertEqual(r["no_segmento"], 1)
        self.assertEqual(r["abordada"], 1)  # filial marca a raiz; "nao" não conta
        self.assertIsNone(r["priorizada"])

    def test_chave_completo(self):
        r = cb.contar(linhas(), {**CONFIG, "chave": "completo"})
        self.assertEqual(r["entidades_unicas"], 3)
        self.assertEqual(r["registros_duplicados"], 1)

    def test_coluna_ausente_falha(self):
        with self.assertRaises(ValueError):
            cb.contar(linhas(), {"cnpj": "CNPJ", "colunas": {"abordada": "Inexistente"}})

    def test_flag_desconhecida_falha(self):
        with self.assertRaises(ValueError):
            cb.contar(linhas(), {"cnpj": "CNPJ", "colunas": {"faturamento": "Seg"}})


class Saida(unittest.TestCase):
    def test_csv_ponto_e_virgula_e_saida_sem_cnpj(self):
        with tempfile.TemporaryDirectory() as d:
            base, cfg, saida = Path(d, "base.csv"), Path(d, "cfg.json"), Path(d, "out.json")
            with base.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=["CNPJ", "Seg", "Abordada"], delimiter=";")
                w.writeheader()
                w.writerows(linhas())
            cfg.write_text(json.dumps(CONFIG), encoding="utf-8")
            self.assertEqual(cb.main([str(base), "--config", str(cfg), "--saida", str(saida)]), 0)
            texto = saida.read_text(encoding="utf-8")
            for cnpj in (MATRIZ, FILIAL, OUTRA, MATRIZ[:8], OUTRA[:8]):
                self.assertNotIn(cnpj, texto)
            primeiro = json.loads(texto)
            self.assertEqual(primeiro["contagens"]["entidades_unicas"], 2)
            cb.main([str(base), "--config", str(cfg), "--saida", str(saida)])
            self.assertEqual(json.loads(saida.read_text(encoding="utf-8")), primeiro)

    def test_xlsx(self):
        try:
            from openpyxl import Workbook
        except ImportError:
            self.skipTest("openpyxl ausente")
        with tempfile.TemporaryDirectory() as d:
            base = Path(d, "base.xlsx")
            wb = Workbook()
            ws = wb.active
            ws.append(["CNPJ", "Seg", "Abordada"])
            for linha in linhas():
                ws.append([linha["CNPJ"], linha["Seg"], linha["Abordada"]])
            ws.append([None, None, None])  # linha vazia ignorada
            wb.save(base)
            r = cb.contar(cb.ler_linhas(base), CONFIG)
            self.assertEqual(r["registros_totais"], 6)
            self.assertEqual(r["entidades_unicas"], 2)


if __name__ == "__main__":
    unittest.main()
