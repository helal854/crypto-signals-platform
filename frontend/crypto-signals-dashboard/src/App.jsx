import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';

// Simple Login Component
const Login = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50" dir="rtl">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900">
            لوحة التحكم الإدارية
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            منصة إدارة إشارات التداول
          </p>
        </div>
        
        <div className="bg-white p-8 rounded-lg shadow">
          <form className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                اسم المستخدم
              </label>
              <input
                type="text"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="أدخل اسم المستخدم"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">
                كلمة المرور
              </label>
              <input
                type="password"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="أدخل كلمة المرور"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">
                الدور
              </label>
              <select className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                <option value="admin">مدير</option>
                <option value="moderator">مشرف</option>
                <option value="support">دعم فني</option>
              </select>
            </div>
            
            <button
              type="submit"
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              تسجيل الدخول
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

// Simple Dashboard Component
const Dashboard = () => {
  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <h1 className="text-3xl font-bold text-gray-900">لوحة المعلومات</h1>
            <div className="text-sm text-gray-500">مرحباً بك في النظام</div>
          </div>
        </div>
      </div>
      
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Stats Cards */}
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm">👥</span>
                  </div>
                </div>
                <div className="mr-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      المستخدمون النشطون
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      1,234
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
          
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm">📈</span>
                  </div>
                </div>
                <div className="mr-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      إشارات اليوم
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      42
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
          
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm">💰</span>
                  </div>
                </div>
                <div className="mr-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      الإيرادات الشهرية
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      $12,345
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
          
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm">⚡</span>
                  </div>
                </div>
                <div className="mr-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      حالة النظام
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      نشط
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Recent Activity */}
        <div className="mt-8">
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900">
                النشاط الأخير
              </h3>
              <div className="mt-5">
                <div className="flow-root">
                  <ul className="-mb-8">
                    <li>
                      <div className="relative pb-8">
                        <div className="relative flex space-x-3 space-x-reverse">
                          <div>
                            <span className="h-8 w-8 rounded-full bg-green-500 flex items-center justify-center ring-8 ring-white">
                              <span className="text-white text-xs">✓</span>
                            </span>
                          </div>
                          <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4 space-x-reverse">
                            <div>
                              <p className="text-sm text-gray-500">
                                تم إرسال إشارة جديدة لـ <span className="font-medium text-gray-900">BTC/USDT</span>
                              </p>
                            </div>
                            <div className="text-right text-sm whitespace-nowrap text-gray-500">
                              منذ دقيقتين
                            </div>
                          </div>
                        </div>
                      </div>
                    </li>
                    
                    <li>
                      <div className="relative pb-8">
                        <div className="relative flex space-x-3 space-x-reverse">
                          <div>
                            <span className="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center ring-8 ring-white">
                              <span className="text-white text-xs">👤</span>
                            </span>
                          </div>
                          <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4 space-x-reverse">
                            <div>
                              <p className="text-sm text-gray-500">
                                انضم مستخدم جديد إلى البوت
                              </p>
                            </div>
                            <div className="text-right text-sm whitespace-nowrap text-gray-500">
                              منذ 5 دقائق
                            </div>
                          </div>
                        </div>
                      </div>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Dashboard />} />
          <Route path="*" element={<Dashboard />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

