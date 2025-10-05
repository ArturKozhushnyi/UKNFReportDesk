/**
 * Login Page
 * User authentication interface
 */

import React, { useState } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { LogIn, AlertCircle, CheckCircle, User, Plus, Minus } from 'lucide-react';
import { useAuthStore } from '../stores/authStore';

// Demo accounts for quick testing
const DEMO_ACCOUNTS = [
  {
    email: 'admin_uknf@example.com',
    password: 'password123',
    label: 'UKNF Administrator',
    description: 'Urząd Komisji Nadzoru Finansowego',
  },
  {
    email: 'admin_pekao@example.com',
    password: 'password456',
    label: 'Bank Pekao Admin',
    description: 'Bank Polska Kasa Opieki SA',
  },
  {
    email: 'admin@example.com',
    password: 'admin',
    label: 'System Administrator',
    description: 'Default admin account',
  },
];

// FAQ data
const FAQ_ITEMS = [
  {
    question: 'What is UKNF Report Desk?',
    answer: 'It is a dedicated platform for managing and submitting financial reports to the Polish Financial Supervision Authority (UKNF), facilitating secure communication and report tracking.'
  },
  {
    question: 'How do I get an account?',
    answer: 'Click the \'Don\'t have an account? Register\' link. During registration, a new, isolated organization (Subject) will be created, and you will become its administrator.'
  },
  {
    question: 'Who should I contact for support?',
    answer: 'For technical support or questions about reports, please use the internal chat system after logging in. Alternatively, contact the primary administrator for your organization.'
  },
  {
    question: 'Is my data secure?',
    answer: 'Yes. The platform is built with a multi-tenant architecture, ensuring that your organization\'s data is completely isolated and secure from other entities.'
  }
];

export const LoginPage: React.FC = () => {
  const location = useLocation();
  const registrationMessage = (location.state as any)?.message;
  const registrationEmail = (location.state as any)?.email;
  
  const [email, setEmail] = useState(registrationEmail || '');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [openFAQ, setOpenFAQ] = useState<number | null>(null);
  
  const login = useAuthStore((state) => state.login);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const fillDemoCredentials = (demoEmail: string, demoPassword: string) => {
    setEmail(demoEmail);
    setPassword(demoPassword);
    setError('');
  };

  const toggleFAQ = (index: number) => {
    setOpenFAQ(openFAQ === index ? null : index);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-blue-900 flex flex-col items-center justify-center p-4 space-y-6">
      {/* Login Form Card */}
      <div className="bg-white rounded-lg shadow-2xl p-8 w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full mb-4">
            <LogIn className="text-white" size={32} />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">UKNF Report Desk</h1>
          <p className="text-gray-600 mt-2">Polish Financial Supervision Authority</p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {registrationMessage && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start">
              <CheckCircle className="text-green-600 mr-2 flex-shrink-0" size={20} />
              <p className="text-sm text-green-800">{registrationMessage}</p>
            </div>
          )}
          
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start">
              <AlertCircle className="text-red-600 mr-2 flex-shrink-0" size={20} />
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
              Email Address
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors"
              placeholder="your.email@example.com"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors disabled:bg-blue-300 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Logging in...
              </>
            ) : (
              <>
                <LogIn size={20} className="mr-2" />
                Login
              </>
            )}
          </button>
        </form>

        {/* Demo Credentials */}
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm font-semibold text-blue-900 mb-3 flex items-center">
            <User size={16} className="mr-2" />
            Demo Accounts (Click to auto-fill):
          </p>
          <div className="space-y-2">
            {DEMO_ACCOUNTS.map((account, index) => (
              <button
                key={index}
                type="button"
                onClick={() => fillDemoCredentials(account.email, account.password)}
                className="w-full text-left p-3 bg-white hover:bg-blue-100 border border-blue-200 rounded-lg transition-colors group"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900 group-hover:text-blue-700">
                      {account.label}
                    </p>
                    <p className="text-xs text-gray-600 mt-0.5">
                      {account.description}
                    </p>
                    <p className="text-xs text-gray-500 mt-1 font-mono">
                      {account.email}
                    </p>
                  </div>
                  <LogIn size={16} className="text-blue-400 group-hover:text-blue-600 flex-shrink-0 ml-2" />
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Registration Link */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Don't have an account?{' '}
            <Link
              to="/register"
              className="text-blue-600 hover:text-blue-700 font-medium transition-colors"
            >
              Register here
            </Link>
          </p>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-xs text-gray-500">
          <p>&copy; 2025 UKNF Report Desk. All rights reserved.</p>
          <p className="mt-1">GNU General Public License v2.0</p>
        </div>
      </div>

      {/* FAQ Section */}
      <div className="bg-white rounded-lg shadow-2xl p-6 w-full max-w-md">
        <h2 className="text-xl font-bold text-gray-900 mb-4 text-center">Frequently Asked Questions</h2>
        <div className="space-y-3">
          {FAQ_ITEMS.map((item, index) => (
            <div key={index} className="border border-gray-200 rounded-lg overflow-hidden">
              <button
                onClick={() => toggleFAQ(index)}
                className="w-full px-4 py-3 text-left bg-gray-50 hover:bg-gray-100 transition-colors flex items-center justify-between focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-inset"
              >
                <span className="text-sm font-medium text-gray-900 pr-2">{item.question}</span>
                {openFAQ === index ? (
                  <Minus className="text-gray-500 flex-shrink-0" size={16} />
                ) : (
                  <Plus className="text-gray-500 flex-shrink-0" size={16} />
                )}
              </button>
              {openFAQ === index && (
                <div className="px-4 py-3 bg-white border-t border-gray-200">
                  <p className="text-sm text-gray-700 leading-relaxed">{item.answer}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

