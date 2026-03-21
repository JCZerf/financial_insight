import unittest

from fundamentus_fii_ingestor.normalizers import normalize_fii_detail, normalize_fii_row, parse_br_number, parse_br_percent


class NormalizersTests(unittest.TestCase):
    def test_parse_br_number_and_percent(self) -> None:
        self.assertEqual(parse_br_number("1.234,56"), 1234.56)
        self.assertEqual(parse_br_number("-"), None)
        self.assertEqual(parse_br_percent("39,56%"), 39.56)
        self.assertEqual(parse_br_percent("-"), None)

    def test_normalize_fii_row_maps_expected_fields(self) -> None:
        raw = {
            "Papel": "AAZQ11",
            "Segmento": "Outros",
            "Cotação": "7,97",
            "FFO Yield": "13,15%",
            "Dividend Yield": "7,04%",
            "P/VP": "0,92",
            "Valor de Mercado": "191.577.000",
            "Liquidez": "655.342",
            "Qtd de imóveis": "0",
            "Preço do m2": "0",
            "Aluguel por m2": "0",
            "Cap Rate": "0,0%",
            "Vacância Média": "0,0%",
        }
        normalized = normalize_fii_row(raw)
        self.assertEqual(normalized["ticker"], "AAZQ11")
        self.assertEqual(normalized["price"], 7.97)
        self.assertEqual(normalized["ffo_yield"], 13.15)

    def test_normalize_fii_detail_includes_oscillations(self) -> None:
        raw_detail = {
            "ticker": "AAZQ11",
            "detail_url": "https://www.fundamentus.com.br/detalhes.php?papel=AAZQ11",
            "collection_status": "success",
            "raw_labels": {
                "Dia": ["-1,73%"],
                "Mês": ["-3,91%"],
                "30 dias": ["-3,69%"],
                "12 meses": ["39,56%"],
                "2026": ["-5,06%"],
                "2025": ["51,95%"],
                "FFO Yield": ["13,15%"],
            },
        }
        normalized = normalize_fii_detail(raw_detail)
        self.assertIn("oscillations", normalized)
        self.assertEqual(normalized["oscillations"]["day"], -1.73)
        self.assertEqual(normalized["oscillations"]["year_to_date"], -5.06)
        self.assertEqual(normalized["oscillations"]["yearly"]["2025"], 51.95)


if __name__ == "__main__":
    unittest.main()
