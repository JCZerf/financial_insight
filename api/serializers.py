from rest_framework import serializers


class ScoreFactorsSerializer(serializers.Serializer):
    dividend_yield = serializers.FloatField()
    price_to_book = serializers.FloatField()
    liquidity = serializers.FloatField()


class FundCardSerializer(serializers.Serializer):
    rank = serializers.IntegerField(required=False)
    ticker = serializers.CharField()
    name = serializers.CharField(allow_null=True)
    segment = serializers.CharField(allow_null=True)
    price = serializers.FloatField(allow_null=True)
    ffo_yield = serializers.FloatField(allow_null=True)
    dividend_yield = serializers.FloatField(allow_null=True)
    price_to_book = serializers.FloatField(allow_null=True)
    liquidity = serializers.FloatField(allow_null=True)
    market_value = serializers.FloatField(allow_null=True)
    property_count = serializers.IntegerField(allow_null=True)
    price_per_sqm = serializers.FloatField(allow_null=True)
    rent_per_sqm = serializers.FloatField(allow_null=True)
    cap_rate = serializers.FloatField(allow_null=True)
    avg_vacancy = serializers.FloatField(allow_null=True)
    detail_available = serializers.BooleanField()
    collected_at_utc = serializers.DateTimeField(allow_null=True)
    score = serializers.FloatField(required=False)
    score_factors = ScoreFactorsSerializer(required=False)
    flags = serializers.ListField(child=serializers.CharField(), required=False)


class ScoringMetadataSerializer(serializers.Serializer):
    dividend_yield_weight = serializers.FloatField()
    price_to_book_weight = serializers.FloatField()
    liquidity_weight = serializers.FloatField()
    note = serializers.CharField()


class DashboardMetadataSerializer(serializers.Serializer):
    asset_class = serializers.CharField()
    total_funds = serializers.IntegerField()
    ranked_funds = serializers.IntegerField()
    latest_collected_at_utc = serializers.DateTimeField(allow_null=True)
    scoring = ScoringMetadataSerializer()


class DashboardSummarySerializer(serializers.Serializer):
    best_opportunity = FundCardSerializer(allow_null=True)
    average_dividend_yield = serializers.FloatField(allow_null=True)
    median_price_to_book = serializers.FloatField(allow_null=True)
    average_liquidity = serializers.FloatField(allow_null=True)
    discounted_funds_count = serializers.IntegerField()
    funds_with_details_count = serializers.IntegerField()


class SegmentSummarySerializer(serializers.Serializer):
    segment = serializers.CharField()
    funds_count = serializers.IntegerField()
    average_dividend_yield = serializers.FloatField(allow_null=True)
    average_price_to_book = serializers.FloatField(allow_null=True)
    max_liquidity = serializers.FloatField(allow_null=True)


class AppliedFiltersSerializer(serializers.Serializer):
    segment = serializers.CharField(allow_null=True)
    min_dividend_yield = serializers.FloatField(allow_null=True)
    max_price_to_book = serializers.FloatField(allow_null=True)
    min_liquidity = serializers.FloatField(allow_null=True)
    limit = serializers.IntegerField()


class DashboardResponseSerializer(serializers.Serializer):
    metadata = DashboardMetadataSerializer()
    summary = DashboardSummarySerializer()
    opportunities = FundCardSerializer(many=True)
    high_dividend = FundCardSerializer(many=True)
    discounted = FundCardSerializer(many=True)
    most_liquid = FundCardSerializer(many=True)
    segments = SegmentSummarySerializer(many=True)
    applied_filters = AppliedFiltersSerializer()


class FundListResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    results = FundCardSerializer(many=True)


class FundDetailResponseSerializer(FundCardSerializer):
    detail = serializers.DictField(allow_null=True)
