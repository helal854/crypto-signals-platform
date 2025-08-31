import React, { useState, useEffect } from 'react';
import { Layout } from '../components/layout/Layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { LoadingCard } from '../components/ui/loading';
import { StatusBadge } from '../components/ui/status-badge';
import { dashboardAPI } from '../lib/api';
import { formatNumber, formatCurrency, formatDateShort } from '../lib/utils';
import { 
  Users, 
  TrendingUp, 
  DollarSign, 
  Radio,
  ArrowUpRight,
  ArrowDownRight,
  Activity,
  Shield,
  AlertTriangle
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

export const Dashboard = () => {
  const [overview, setOverview] = useState(null);
  const [activity, setActivity] = useState(null);
  const [usersChart, setUsersChart] = useState(null);
  const [signalsChart, setSignalsChart] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        const [overviewRes, activityRes, usersChartRes, signalsChartRes, systemStatusRes] = await Promise.all([
          dashboardAPI.getOverview(),
          dashboardAPI.getActivity(),
          dashboardAPI.getUsersChart(30),
          dashboardAPI.getSignalsChart(7),
          dashboardAPI.getSystemStatus()
        ]);

        setOverview(overviewRes.data);
        setActivity(activityRes.data);
        setUsersChart(usersChartRes.data);
        setSignalsChart(signalsChartRes.data);
        setSystemStatus(systemStatusRes.data);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <Layout title="لوحة المعلومات" subtitle="نظرة عامة على النظام والإحصائيات">
        <LoadingCard message="جاري تحميل بيانات لوحة المعلومات..." />
      </Layout>
    );
  }

  return (
    <Layout title="لوحة المعلومات" subtitle="نظرة عامة على النظام والإحصائيات">
      <div className="space-y-6">
        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Users Card */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">المستخدمون النشطون</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatNumber(overview?.users?.total_active || 0, 0)}</div>
              <p className="text-xs text-muted-foreground">
                +{overview?.users?.new_today || 0} اليوم
              </p>
            </CardContent>
          </Card>

          {/* Signals Card */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">إشارات اليوم</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{overview?.signals?.total_today || 0}</div>
              <p className="text-xs text-muted-foreground">
                Spot: {overview?.signals?.spot_today || 0} | Futures: {overview?.signals?.futures_today || 0}
              </p>
            </CardContent>
          </Card>

          {/* Revenue Card */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">الإيرادات (30 يوم)</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatCurrency(overview?.payments?.revenue_30d || 0)}
              </div>
              <p className="text-xs text-muted-foreground">
                {overview?.payments?.pending_count || 0} مدفوعات معلقة
              </p>
            </CardContent>
          </Card>

          {/* System Health Card */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">حالة النظام</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-2 space-x-reverse">
                <StatusBadge status={overview?.system?.system_health || 'unknown'} />
                {overview?.system?.system_health === 'healthy' ? (
                  <Activity className="h-4 w-4 text-green-500" />
                ) : (
                  <AlertTriangle className="h-4 w-4 text-yellow-500" />
                )}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {overview?.system?.integrations_active || 0}/{overview?.system?.integrations_total || 0} تكاملات نشطة
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Users Growth Chart */}
          <Card>
            <CardHeader>
              <CardTitle>نمو المستخدمين (30 يوم)</CardTitle>
              <CardDescription>إجمالي المستخدمين النشطين والمستخدمين الجدد</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={usersChart?.chart_data || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line 
                    type="monotone" 
                    dataKey="total_users" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    name="إجمالي المستخدمين"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="new_users" 
                    stroke="#10b981" 
                    strokeWidth={2}
                    name="مستخدمين جدد"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Signals Chart */}
          <Card>
            <CardHeader>
              <CardTitle>الإشارات (7 أيام)</CardTitle>
              <CardDescription>إشارات Spot و Futures المرسلة</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={signalsChart?.chart_data || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="spot_signals" fill="#3b82f6" name="Spot" />
                  <Bar dataKey="futures_signals" fill="#8b5cf6" name="Futures" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Market Data & Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Market Overview */}
          <Card>
            <CardHeader>
              <CardTitle>نظرة على السوق</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {overview?.market && (
                <>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">نظام السوق</span>
                    <span className="font-medium">{overview.market.regime}</span>
                  </div>
                  
                  {overview.market.btc_price && (
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">سعر BTC</span>
                      <div className="text-right">
                        <div className="font-medium">${formatNumber(overview.market.btc_price)}</div>
                        <div className={`text-xs flex items-center ${
                          overview.market.btc_change_24h >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {overview.market.btc_change_24h >= 0 ? (
                            <ArrowUpRight className="w-3 h-3 ml-1" />
                          ) : (
                            <ArrowDownRight className="w-3 h-3 ml-1" />
                          )}
                          {Math.abs(overview.market.btc_change_24h).toFixed(2)}%
                        </div>
                      </div>
                    </div>
                  )}

                  {overview.market.fear_greed && (
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">مؤشر الخوف والطمع</span>
                      <span className="font-medium">{overview.market.fear_greed.value}</span>
                    </div>
                  )}
                </>
              )}
            </CardContent>
          </Card>

          {/* Recent Signals */}
          <Card>
            <CardHeader>
              <CardTitle>أحدث الإشارات</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {activity?.recent_spot_signals?.slice(0, 3).map((signal) => (
                  <div key={signal.id} className="flex justify-between items-center">
                    <div>
                      <div className="font-medium text-sm">{signal.symbol}</div>
                      <div className="text-xs text-gray-500">{formatDateShort(signal.created_at)}</div>
                    </div>
                    <StatusBadge status={signal.status} />
                  </div>
                ))}
                
                {activity?.recent_futures_signals?.slice(0, 2).map((signal) => (
                  <div key={signal.id} className="flex justify-between items-center">
                    <div>
                      <div className="font-medium text-sm">{signal.symbol} (Futures)</div>
                      <div className="text-xs text-gray-500">{formatDateShort(signal.created_at)}</div>
                    </div>
                    <StatusBadge status={signal.status} />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle>النشاط الأخير</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {activity?.recent_broadcasts?.slice(0, 2).map((broadcast) => (
                  <div key={broadcast.id} className="flex justify-between items-center">
                    <div>
                      <div className="font-medium text-sm">رسالة عامة</div>
                      <div className="text-xs text-gray-500">{broadcast.title}</div>
                    </div>
                    <StatusBadge status={broadcast.status} />
                  </div>
                ))}
                
                {activity?.recent_users?.slice(0, 3).map((user) => (
                  <div key={user.user_id} className="flex justify-between items-center">
                    <div>
                      <div className="font-medium text-sm">مستخدم جديد</div>
                      <div className="text-xs text-gray-500">{formatDateShort(user.joined_at)}</div>
                    </div>
                    <span className="text-xs text-green-600">انضم</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* System Status Details */}
        {systemStatus && (
          <Card>
            <CardHeader>
              <CardTitle>تفاصيل حالة النظام</CardTitle>
              <CardDescription>آخر فحص: {formatDateShort(systemStatus.last_checked)}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium">قاعدة البيانات</span>
                  <StatusBadge status={systemStatus.components.database} />
                </div>
                
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium">Binance API</span>
                  <StatusBadge status={systemStatus.components.binance_api} />
                </div>
                
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium">التكاملات</span>
                  <span className="text-sm text-gray-600">
                    {systemStatus.components.integrations.filter(i => i.is_active).length}/
                    {systemStatus.components.integrations.length} نشط
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </Layout>
  );
};

