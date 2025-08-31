import React, { useState, useEffect } from 'react';
import { Layout } from '../components/layout/Layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { LoadingCard, LoadingSpinner } from '../components/ui/loading';
import { StatusBadge } from '../components/ui/status-badge';
import { RoleBadge } from '../components/ui/role-badge';
import { usersAPI } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import { formatDateShort, getSubscriptionText, getSubscriptionColor } from '../lib/utils';
import { 
  Users, 
  UserPlus, 
  Search, 
  Filter,
  MoreHorizontal,
  Edit,
  Trash2,
  Shield,
  UserCheck,
  UserX
} from 'lucide-react';
import { toast } from 'react-hot-toast';

export const Users = () => {
  const { hasPermission } = useAuth();
  const [activeTab, setActiveTab] = useState('admin');
  
  // Admin Users State
  const [adminUsers, setAdminUsers] = useState([]);
  const [adminLoading, setAdminLoading] = useState(true);
  
  // Telegram Users State
  const [telegramUsers, setTelegramUsers] = useState([]);
  const [telegramLoading, setTelegramLoading] = useState(true);
  const [telegramFilters, setTelegramFilters] = useState({
    subscription_type: '',
    is_active: '',
    limit: 50,
    offset: 0
  });
  
  // Dialog States
  const [createAdminDialog, setCreateAdminDialog] = useState(false);
  const [editUserDialog, setEditUserDialog] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  
  // Form State
  const [adminForm, setAdminForm] = useState({
    username: '',
    email: '',
    password: '',
    role: 'moderator'
  });

  // Fetch Admin Users
  const fetchAdminUsers = async () => {
    try {
      setAdminLoading(true);
      const response = await usersAPI.getAdminUsers();
      setAdminUsers(response.data.users);
    } catch (error) {
      toast.error('فشل في تحميل المستخدمين الإداريين');
    } finally {
      setAdminLoading(false);
    }
  };

  // Fetch Telegram Users
  const fetchTelegramUsers = async () => {
    try {
      setTelegramLoading(true);
      const response = await usersAPI.getTelegramUsers(telegramFilters);
      setTelegramUsers(response.data.users);
    } catch (error) {
      toast.error('فشل في تحميل مستخدمي تليجرام');
    } finally {
      setTelegramLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'admin' && hasPermission('manage_users')) {
      fetchAdminUsers();
    } else if (activeTab === 'telegram') {
      fetchTelegramUsers();
    }
  }, [activeTab, telegramFilters]);

  // Create Admin User
  const handleCreateAdmin = async (e) => {
    e.preventDefault();
    
    if (!adminForm.username || !adminForm.email || !adminForm.password) {
      toast.error('يرجى ملء جميع الحقول المطلوبة');
      return;
    }

    try {
      await usersAPI.createAdminUser(adminForm);
      toast.success('تم إنشاء المستخدم الإداري بنجاح');
      setCreateAdminDialog(false);
      setAdminForm({ username: '', email: '', password: '', role: 'moderator' });
      fetchAdminUsers();
    } catch (error) {
      toast.error(error.response?.data?.error || 'فشل في إنشاء المستخدم');
    }
  };

  // Toggle Telegram User Active Status
  const handleToggleTelegramUser = async (userId) => {
    try {
      await usersAPI.toggleTelegramUserActive(userId);
      toast.success('تم تحديث حالة المستخدم بنجاح');
      fetchTelegramUsers();
    } catch (error) {
      toast.error('فشل في تحديث حالة المستخدم');
    }
  };

  // Update Telegram User Subscription
  const handleUpdateSubscription = async (userId, subscriptionType) => {
    try {
      await usersAPI.updateTelegramUserSubscription(userId, { subscription_type: subscriptionType });
      toast.success('تم تحديث الاشتراك بنجاح');
      fetchTelegramUsers();
    } catch (error) {
      toast.error('فشل في تحديث الاشتراك');
    }
  };

  return (
    <Layout title="إدارة المستخدمين" subtitle="إدارة المستخدمين الإداريين ومستخدمي تليجرام">
      <div className="space-y-6">
        {/* Header Actions */}
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-4 space-x-reverse">
            <div className="relative">
              <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="البحث عن المستخدمين..."
                className="pr-10 w-64"
              />
            </div>
            <Button variant="outline" size="sm">
              <Filter className="w-4 h-4 ml-2" />
              تصفية
            </Button>
          </div>
          
          {hasPermission('manage_users') && (
            <Dialog open={createAdminDialog} onOpenChange={setCreateAdminDialog}>
              <DialogTrigger asChild>
                <Button>
                  <UserPlus className="w-4 h-4 ml-2" />
                  إضافة مستخدم إداري
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>إنشاء مستخدم إداري جديد</DialogTitle>
                  <DialogDescription>
                    أدخل بيانات المستخدم الإداري الجديد
                  </DialogDescription>
                </DialogHeader>
                <form onSubmit={handleCreateAdmin} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="username">اسم المستخدم</Label>
                    <Input
                      id="username"
                      value={adminForm.username}
                      onChange={(e) => setAdminForm(prev => ({ ...prev, username: e.target.value }))}
                      placeholder="أدخل اسم المستخدم"
                      required
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="email">البريد الإلكتروني</Label>
                    <Input
                      id="email"
                      type="email"
                      value={adminForm.email}
                      onChange={(e) => setAdminForm(prev => ({ ...prev, email: e.target.value }))}
                      placeholder="أدخل البريد الإلكتروني"
                      required
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="password">كلمة المرور</Label>
                    <Input
                      id="password"
                      type="password"
                      value={adminForm.password}
                      onChange={(e) => setAdminForm(prev => ({ ...prev, password: e.target.value }))}
                      placeholder="أدخل كلمة المرور"
                      required
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="role">الدور</Label>
                    <select
                      id="role"
                      value={adminForm.role}
                      onChange={(e) => setAdminForm(prev => ({ ...prev, role: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    >
                      <option value="moderator">مشرف</option>
                      <option value="support">دعم فني</option>
                      <option value="admin">مدير</option>
                    </select>
                  </div>
                  
                  <div className="flex justify-end space-x-2 space-x-reverse">
                    <Button type="button" variant="outline" onClick={() => setCreateAdminDialog(false)}>
                      إلغاء
                    </Button>
                    <Button type="submit">
                      إنشاء المستخدم
                    </Button>
                  </div>
                </form>
              </DialogContent>
            </Dialog>
          )}
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            {hasPermission('manage_users') && (
              <TabsTrigger value="admin">
                <Shield className="w-4 h-4 ml-2" />
                المستخدمون الإداريون
              </TabsTrigger>
            )}
            <TabsTrigger value="telegram">
              <Users className="w-4 h-4 ml-2" />
              مستخدمو تليجرام
            </TabsTrigger>
          </TabsList>

          {/* Admin Users Tab */}
          {hasPermission('manage_users') && (
            <TabsContent value="admin">
              <Card>
                <CardHeader>
                  <CardTitle>المستخدمون الإداريون</CardTitle>
                  <CardDescription>
                    إدارة المستخدمين الذين لديهم صلاحيات الوصول إلى لوحة التحكم
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {adminLoading ? (
                    <LoadingCard />
                  ) : (
                    <div className="space-y-4">
                      {adminUsers.map((user) => (
                        <div key={user.id} className="flex items-center justify-between p-4 border rounded-lg">
                          <div className="flex items-center space-x-4 space-x-reverse">
                            <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                              <span className="text-white font-medium">
                                {user.username.charAt(0).toUpperCase()}
                              </span>
                            </div>
                            <div>
                              <h3 className="font-medium">{user.username}</h3>
                              <p className="text-sm text-gray-500">{user.email}</p>
                              <div className="flex items-center space-x-2 space-x-reverse mt-1">
                                <RoleBadge role={user.role} />
                                <StatusBadge status={user.is_active ? 'active' : 'inactive'} />
                              </div>
                            </div>
                          </div>
                          
                          <div className="flex items-center space-x-2 space-x-reverse">
                            <span className="text-sm text-gray-500">
                              {formatDateShort(user.created_at)}
                            </span>
                            <Button variant="ghost" size="sm">
                              <MoreHorizontal className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          )}

          {/* Telegram Users Tab */}
          <TabsContent value="telegram">
            <Card>
              <CardHeader>
                <CardTitle>مستخدمو تليجرام</CardTitle>
                <CardDescription>
                  إدارة المستخدمين المشتركين في بوت تليجرام
                </CardDescription>
              </CardHeader>
              <CardContent>
                {/* Filters */}
                <div className="flex items-center space-x-4 space-x-reverse mb-6">
                  <select
                    value={telegramFilters.subscription_type}
                    onChange={(e) => setTelegramFilters(prev => ({ ...prev, subscription_type: e.target.value }))}
                    className="px-3 py-2 border border-gray-300 rounded-md"
                  >
                    <option value="">جميع الاشتراكات</option>
                    <option value="free">مجاني</option>
                    <option value="pro">احترافي</option>
                    <option value="elite">نخبة</option>
                  </select>
                  
                  <select
                    value={telegramFilters.is_active}
                    onChange={(e) => setTelegramFilters(prev => ({ ...prev, is_active: e.target.value }))}
                    className="px-3 py-2 border border-gray-300 rounded-md"
                  >
                    <option value="">جميع الحالات</option>
                    <option value="true">نشط</option>
                    <option value="false">غير نشط</option>
                  </select>
                </div>

                {telegramLoading ? (
                  <LoadingCard />
                ) : (
                  <div className="space-y-4">
                    {telegramUsers.map((user) => (
                      <div key={user.user_id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center space-x-4 space-x-reverse">
                          <div className="w-10 h-10 bg-green-600 rounded-full flex items-center justify-center">
                            <span className="text-white font-medium">
                              {user.first_name?.charAt(0) || 'U'}
                            </span>
                          </div>
                          <div>
                            <h3 className="font-medium">
                              {user.first_name} {user.last_name}
                            </h3>
                            <p className="text-sm text-gray-500">@{user.username || 'لا يوجد'}</p>
                            <div className="flex items-center space-x-2 space-x-reverse mt-1">
                              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSubscriptionColor(user.subscription_type)}`}>
                                {getSubscriptionText(user.subscription_type)}
                              </span>
                              <StatusBadge status={user.is_active ? 'active' : 'inactive'} />
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-2 space-x-reverse">
                          <span className="text-sm text-gray-500">
                            {formatDateShort(user.joined_at)}
                          </span>
                          
                          {hasPermission('manage_users_basic') && (
                            <>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleToggleTelegramUser(user.user_id)}
                              >
                                {user.is_active ? (
                                  <UserX className="w-4 h-4" />
                                ) : (
                                  <UserCheck className="w-4 h-4" />
                                )}
                              </Button>
                              
                              <select
                                value={user.subscription_type}
                                onChange={(e) => handleUpdateSubscription(user.user_id, e.target.value)}
                                className="px-2 py-1 border border-gray-300 rounded text-sm"
                              >
                                <option value="free">مجاني</option>
                                <option value="pro">احترافي</option>
                                <option value="elite">نخبة</option>
                              </select>
                            </>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  );
};

