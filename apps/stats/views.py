"""
仪表盘统计 API（管理员 / 养殖户首页图表）
========================================

使用 Pandas 做按日重采样与补零，返回结构便于前端 ECharts 直接使用。
路径由 ``apps.stats.urls`` 映射到 ``/api/stats/admin/dashboard/`` 与 ``farmer/dashboard/``。
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
import pandas as pd
from rest_framework.request import Request

from apps.livestock.models import LivestockBatch
from apps.production.models import DiseaseReport, FeedInfo, VaccinationRecord, FeedingRecord
from apps.users.models import FarmerProfile
from apps.users.permissions import IsAdminUser, IsFarmerUser

class AdminDashboardStatsView(APIView):
    """
    管理员首页统计数据接口
    """
    permission_classes = [IsAdminUser]

    def get(self, _request: Request) -> Response:
        active_batch_count = LivestockBatch.objects.filter(status='active').count()
        vaccinated_active_batch_count = VaccinationRecord.objects.filter(
            batch__status='active'
        ).values('batch').distinct().count()
        vaccination_coverage_rate = (
            round((vaccinated_active_batch_count / active_batch_count * 100), 1)
            if active_batch_count > 0
            else 0
        )

        base_stats = {
            'farmer_count': FarmerProfile.objects.filter(user__is_staff=False).count(),
            'active_batch_count': active_batch_count,
            'pending_disease_count': DiseaseReport.objects.filter(status='pending').count(),
            'vaccination_coverage_rate': vaccination_coverage_rate,
        }

        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=29)
        all_dates = pd.date_range(start=start_date, end=end_date)
        disease_rows = list(
            DiseaseReport.objects.filter(report_date__range=[start_date, end_date]).values('report_date')
        )

        if disease_rows:
            df_disease = pd.DataFrame(disease_rows)
            df_disease['report_date'] = pd.to_datetime(df_disease['report_date'])
            df_daily = df_disease.groupby('report_date').size().reindex(all_dates, fill_value=0).reset_index()
            df_daily.columns = ['index', 'report_count']
            disease_trend = {
                'dates': df_daily['index'].dt.strftime('%m-%d').tolist(),
                'counts': df_daily['report_count'].tolist(),
            }
        else:
            disease_trend = {
                'dates': [d.strftime('%m-%d') for d in all_dates],
                'counts': [0] * len(all_dates),
            }

        return Response({'base_stats': base_stats, 'disease_trend': disease_trend})

class FarmerDashboardStatsView(APIView):
    """
    养殖户首页统计数据接口
    """
    permission_classes = [IsFarmerUser]

    def get(self, request: Request) -> Response:
        farmer_profile = getattr(request.user, 'farmer_profile', None)
        
        # 如果没有档案且不是管理员，则尝试创建（针对刚注册的普通养殖户）
        if not farmer_profile and not request.user.is_staff:
            farmer_profile, _created = FarmerProfile.objects.get_or_create(
                user=request.user,
                defaults={'farmer_name': request.user.username, 'is_verified': False},
            )

        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=29)
        all_dates = pd.date_range(start=start_date, end=end_date)

        if not farmer_profile or not farmer_profile.is_verified:
            disease_trend = {
                'dates': [d.strftime('%m-%d') for d in all_dates],
                'counts': [0] * len(all_dates),
            }
            return Response({
                'is_verified': False,
                'message': '您的账户尚未通过实名认证，请先完成认证以查看统计数据。',
                'base_stats': {},
                'avg_eco_score': 0,
                'disease_trend': disease_trend,
            })

        active_batch_qs = LivestockBatch.objects.filter(farmer=farmer_profile, status='active').prefetch_related(
            'vaccinations',
            'diseases',
        )
        active_batches = list(active_batch_qs)
        my_active_batch_count = len(active_batches)

        if my_active_batch_count > 0:
            eco_scores = [float(batch.eco_score) for batch in active_batches]
            avg_eco_score = round(sum(eco_scores) / my_active_batch_count, 1)
        else:
            avg_eco_score = 0
        vaccinated_active_batch_count = VaccinationRecord.objects.filter(
            batch__farmer=farmer_profile,
            batch__status='active',
        ).values('batch').distinct().count()
        pending_vaccination_batch_count = max(my_active_batch_count - vaccinated_active_batch_count, 0)
        low_stock_feed_count = FeedInfo.objects.filter(farmer=farmer_profile, stock_quantity__lte=50).count()

        base_stats = {
            'my_active_batch_count': my_active_batch_count,
            'pending_vaccination_batch_count': pending_vaccination_batch_count,
            'low_stock_feed_count': low_stock_feed_count,
        }

        feeding_rows = list(
            FeedingRecord.objects.filter(
                batch__farmer=farmer_profile,
                feeding_time__date__range=[start_date, end_date],
            ).values('feeding_time__date').annotate(total_weight=Sum('feed_weight'))
        )

        if feeding_rows:
            df_feeding = pd.DataFrame(feeding_rows)
            df_feeding['feeding_time__date'] = pd.to_datetime(df_feeding['feeding_time__date'])
            df_daily = df_feeding.set_index('feeding_time__date').reindex(all_dates, fill_value=0).reset_index()
            feeding_trend = {
                'dates': df_daily['index'].dt.strftime('%m-%d').tolist(),
                'counts': df_daily['total_weight'].astype(float).round(2).tolist(),
            }
        else:
            feeding_trend = {
                'dates': [d.strftime('%m-%d') for d in all_dates],
                'counts': [0] * len(all_dates),
            }

        feed_qs = FeedInfo.objects.filter(farmer=farmer_profile).order_by('-stock_quantity')[:5]
        feed_stock_dist = [{'name': f.feed_name, 'value': float(f.stock_quantity)} for f in feed_qs]

        disease_rows = list(
            DiseaseReport.objects.filter(
                batch__farmer=farmer_profile,
                report_date__range=[start_date, end_date],
            ).values('report_date')
        )

        if disease_rows:
            df_disease = pd.DataFrame(disease_rows)
            df_disease['report_date'] = pd.to_datetime(df_disease['report_date'])
            df_daily = df_disease.groupby('report_date').size().reindex(all_dates, fill_value=0).reset_index()
            df_daily.columns = ['index', 'report_count']
            disease_trend = {
                'dates': df_daily['index'].dt.strftime('%m-%d').tolist(),
                'counts': df_daily['report_count'].tolist(),
            }
        else:
            disease_trend = {
                'dates': [d.strftime('%m-%d') for d in all_dates],
                'counts': [0] * len(all_dates),
            }

        return Response({
            'is_verified': True,
            'base_stats': base_stats,
            'avg_eco_score': avg_eco_score,
            'disease_trend': disease_trend,
            'feeding_trend': feeding_trend,
            'feed_stock_dist': feed_stock_dist,
        })