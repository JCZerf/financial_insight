from django.db import models
import uuid


class RealEstateFund(models.Model):
    """Dados gerais extraídos de fii_resultado.php (snapshot geral)."""

    run_id = models.UUIDField(default=uuid.uuid4, db_index=True)
    source = models.CharField(max_length=120)
    url = models.URLField(max_length=500)
    collected_at_utc = models.DateTimeField(db_index=True)

    papel = models.CharField(max_length=20, db_index=True, unique=True)
    segmento = models.CharField(max_length=120, blank=True, null=True)

    cotacao = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True)
    ffo_yield = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    dividend_yield = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    p_vp = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)

    valor_mercado = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)
    liquidez = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)

    qtd_imoveis = models.PositiveIntegerField(blank=True, null=True)
    preco_m2 = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True)
    aluguel_m2 = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True)
    cap_rate = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    vacancia_media = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "real_estate_fund"
        indexes = [
            models.Index(fields=["papel", "collected_at_utc"], name="idx_ref_papel_collected"),
        ]

    def __str__(self) -> str:
        return f"{self.papel} ({self.run_id})"


class RealEstateFundDetail(models.Model):
    """Dados detalhados extraídos de detalhes.php?papel=... (snapshot detalhado)."""

    fund = models.OneToOneField(
        RealEstateFund,
        on_delete=models.CASCADE,
        related_name="detail",
    )

    run_id = models.UUIDField(db_index=True)
    source = models.CharField(max_length=120)
    url = models.URLField(max_length=500)
    detalhe_url = models.URLField(max_length=500, blank=True, null=True)
    collected_at_utc = models.DateTimeField(db_index=True)
    status_coleta = models.CharField(max_length=32, blank=True, null=True)

    # identificacao
    identificacao_nome = models.TextField(blank=True, null=True)
    identificacao_segmento = models.CharField(max_length=120, blank=True, null=True)
    identificacao_mandato = models.CharField(max_length=120, blank=True, null=True)
    identificacao_gestao = models.CharField(max_length=120, blank=True, null=True)

    # mercado
    mercado_cotacao = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True)
    mercado_data_ult_cot = models.CharField(max_length=32, blank=True, null=True)
    mercado_min_52_sem = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True)
    mercado_max_52_sem = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True)
    mercado_vol_medio_2m = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)
    mercado_valor_mercado = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)
    mercado_numero_cotas = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)
    mercado_data_relatorio = models.CharField(max_length=32, blank=True, null=True)
    mercado_ult_info_trimestral = models.CharField(max_length=32, blank=True, null=True)

    # indicadores
    indicadores_ffo_yield = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    indicadores_ffo_cota = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True)
    indicadores_dividend_yield = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    indicadores_dividendo_cota = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True)
    indicadores_p_vp = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    indicadores_vp_cota = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True)

    # resultado
    resultado_ult_12m_receita = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)
    resultado_ult_3m_receita = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)
    resultado_ult_12m_venda_ativos = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)
    resultado_ult_3m_venda_ativos = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)
    resultado_ult_12m_ffo = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)
    resultado_ult_3m_ffo = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)
    resultado_ult_12m_rend_distribuido = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)
    resultado_ult_3m_rend_distribuido = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)

    # balanco
    balanco_ativos = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)
    balanco_patrimonio_liquido = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)

    # imoveis
    imoveis_qtd_imoveis = models.PositiveIntegerField(blank=True, null=True)
    imoveis_qtd_unidades = models.PositiveIntegerField(blank=True, null=True)
    imoveis_area_m2 = models.DecimalField(max_digits=24, decimal_places=4, blank=True, null=True)
    imoveis_preco_m2 = models.DecimalField(max_digits=24, decimal_places=4, blank=True, null=True)
    imoveis_aluguel_m2 = models.DecimalField(max_digits=24, decimal_places=4, blank=True, null=True)
    imoveis_cap_rate = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    imoveis_vacancia_media = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    imoveis_imoveis_pl_percent = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "real_estate_fund_detail"
        indexes = [
            models.Index(fields=["run_id", "status_coleta"], name="idx_ref_detail_run_status"),
        ]

    def __str__(self) -> str:
        return f"Detail {self.fund.papel} ({self.run_id})"
