import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Database, Eye, EyeOff, Mail, Lock, AlertCircle, Loader } from 'lucide-react';
import { useToast } from '../components/Toast';

const LoginPage = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        // Store token and user data
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        toast.success('Login successful! Redirecting...');
        
        // Small delay for toast to show
        setTimeout(() => {
          navigate('/dashboard');
        }, 500);
      } else {
        setError(data.detail || 'Login failed. Please check your credentials.');
        toast.error(data.detail || 'Login failed');
      }
    } catch (err) {
      const errorMsg = 'Network error. Please try again.';
      setError(errorMsg);
      toast.error(errorMsg);
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white flex">
      {/* Left Side - Product Info */}
      <div className="hidden lg:flex lg:w-1/2 bg-white p-12 flex-col justify-between border-r border-gray-200">
        <div>
          <div className="flex items-center gap-3 mb-16">
            <div className="w-10 h-10 bg-black">
              <Database className="w-10 h-10 p-2 text-white" />
            </div>
            <span className="text-2xl font-bold text-gray-900">EKG</span>
          </div>
          
          <div className="max-w-lg">
            <h2 className="text-4xl font-bold mb-6 leading-tight text-gray-900">
              Stop guessing.<br />Know your infrastructure.
            </h2>
            <p className="text-gray-600 text-lg leading-relaxed mb-10">
              Engineering teams reduce incident response time by 85% with AI-powered dependency intelligence and real-time impact analysis.
            </p>
            
            <div className="space-y-5">
              <div className="bg-gray-50 border border-gray-200 rounded-xl p-5 hover:bg-gray-100 transition-all">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-black text-white rounded-lg flex items-center justify-center flex-shrink-0 font-bold text-lg">
                    85%
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900 mb-1">Faster incident resolution</div>
                    <div className="text-gray-600 text-sm">Answer "what depends on what?" in seconds, not hours</div>
                  </div>
                </div>
              </div>

              <div className="bg-gray-50 border border-gray-200 rounded-xl p-5 hover:bg-gray-100 transition-all">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-emerald-600 text-white rounded-lg flex items-center justify-center flex-shrink-0 font-bold text-lg">
                    73%
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900 mb-1">Fewer production incidents</div>
                    <div className="text-gray-600 text-sm">Understand blast radius before you deploy</div>
                  </div>
                </div>
              </div>

              <div className="bg-gray-50 border border-gray-200 rounded-xl p-5 hover:bg-gray-100 transition-all">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-blue-600 text-white rounded-lg flex items-center justify-center flex-shrink-0 font-bold text-lg">
                    2-3x
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900 mb-1">Faster team onboarding</div>
                    <div className="text-gray-600 text-sm">Self-service infrastructure knowledge for entire team</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="border-t border-gray-200 pt-8">
          <div className="text-gray-500 text-sm mb-4 font-medium">Trusted by platform engineering teams</div>
          <div className="flex items-center gap-8 text-gray-400 font-semibold text-sm">
            <span>Stripe</span>
            <span>Datadog</span>
            <span>Shopify</span>
            <span>Cloudflare</span>
          </div>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-gray-50">
        <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-8 border border-gray-200">
          {/* Logo for mobile */}
          <div className="lg:hidden flex items-center gap-2 mb-8">
            <div className="w-8 h-8 bg-black">
              <Database className="w-8 h-8 p-1.5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">EKG</span>
          </div>

          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome back</h1>
            <p className="text-gray-600">Sign in to access your infrastructure intelligence platform</p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-red-800">{error}</div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Email address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-600 focus:border-transparent transition text-gray-900 placeholder:text-gray-400 bg-white"
                  placeholder="you@company.com"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  className="w-full pl-11 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-600 focus:border-transparent transition text-gray-900 placeholder:text-gray-400 bg-white"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  className="w-4 h-4 text-gray-700 border-gray-300 rounded focus:ring-gray-600"
                />
                <span className="text-sm text-gray-700">Remember me</span>
              </label>
              <Link
                to="/forgot-password"
                className="text-sm text-gray-700 hover:text-gray-900 font-semibold transition"
              >
                Forgot password?
              </Link>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 bg-black text-white rounded-lg font-semibold hover:bg-gray-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg"
            >
              {loading ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign in'
              )}
            </button>
          </form>

          <div className="relative my-8">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-white text-gray-500">New to EKG?</span>
            </div>
          </div>

          <div className="text-center">
            <p className="text-gray-700">
              <Link
                to="/register"
                className="text-gray-800 hover:text-gray-900 font-semibold transition"
              >
                Create your free account
              </Link>
            </p>
            <p className="text-xs text-gray-500 mt-2">14-day trial • No credit card required</p>
          </div>

          <div className="mt-8 pt-6 border-t border-gray-200">
            <Link
              to="/"
              className="text-sm text-gray-600 hover:text-gray-800 transition inline-flex items-center gap-1"
            >
              ← Back to homepage
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
