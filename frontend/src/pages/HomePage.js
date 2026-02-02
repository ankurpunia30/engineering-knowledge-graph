import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Database, ArrowRight, Check, Zap, Shield, Clock, TrendingUp, Users, AlertCircle, BarChart3, GitBranch, Server } from 'lucide-react';

const HomePage = () => {
  const navigate = useNavigate();
  const [scrolled, setScrolled] = useState(false);
  const [activeTab, setActiveTab] = useState('incident');
  const [typedText, setTypedText] = useState('');

  const queryExamples = {
    incident: "Which services will break if auth-service goes down?",
    deploy: "What's the blast radius of updating user-database schema?",
    onboard: "Show me the complete payment flow architecture"
  };

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    const text = queryExamples[activeTab];
    let index = 0;
    setTypedText('');
    
    const interval = setInterval(() => {
      if (index <= text.length) {
        setTypedText(text.slice(0, index));
        index++;
      } else {
        clearInterval(interval);
      }
    }, 50);

    return () => clearInterval(interval);
  }, [activeTab]);

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className={`fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-md transition-all duration-200 ${
        scrolled ? 'shadow-sm' : ''
      }`}>
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-8">
              <div className="flex items-center gap-2.5 cursor-pointer" onClick={() => navigate('/')}>
                <div className="w-8 h-8 bg-black">
                  <Database className="w-8 h-8 p-1.5 text-white" />
                </div>
                <span className="text-lg font-bold text-gray-900">EKG</span>
              </div>
              <nav className="hidden md:flex items-center gap-1">
                <a href="#product" className="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors">Product</a>
                <a href="#solutions" className="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors">Solutions</a>
                <a href="#pricing" className="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors">Pricing</a>
                <a href="#docs" className="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors">Docs</a>
              </nav>
            </div>
            <div className="flex items-center gap-3">
              <button onClick={() => navigate('/login')} className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900">Sign in</button>
              <button onClick={() => navigate('/register')} className="px-4 py-2 bg-black text-white text-sm font-semibold rounded-lg hover:bg-gray-800 transition-all shadow-sm hover:shadow-md">
                Start free trial
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="h-16"></div>

      {/* Hero with Live Demo */}
      <section id="product" className="pt-16 pb-20 px-6 lg:px-8 bg-gradient-to-b from-gray-50 to-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-4xl mx-auto mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-50 text-emerald-700 text-sm font-medium rounded-full mb-6 border border-emerald-200">
              <Zap className="w-4 h-4" />
              Save 20+ hours per week on incident response
            </div>
            
            <h1 className="text-5xl lg:text-6xl font-bold text-gray-900 leading-tight mb-6">
              Stop guessing.
              <br />
              <span className="text-gray-600">
                Know your infrastructure.
              </span>
            </h1>

            <p className="text-xl text-gray-600 leading-relaxed mb-8 max-w-3xl mx-auto">
              Ask any question about your infrastructure in plain English. Get instant answers with 
              AI-powered dependency analysis. Never waste time tracing dependencies manually again.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-6">
              <button onClick={() => navigate('/register')} className="px-8 py-4 bg-black text-white text-base font-semibold rounded-lg hover:bg-gray-800 transition-all shadow-lg hover:shadow-xl inline-flex items-center justify-center gap-2 group">
                Start free trial <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>
              <button onClick={() => navigate('/dashboard')} className="px-8 py-4 bg-white border-2 border-gray-300 text-gray-900 text-base font-semibold rounded-lg hover:border-gray-400 hover:bg-gray-50 transition-all">
                Try live demo
              </button>
            </div>

            <div className="flex items-center justify-center gap-6 text-sm text-gray-600">
              <span className="flex items-center gap-2"><Check className="w-4 h-4 text-green-600" /> Free 14-day trial</span>
              <span className="flex items-center gap-2"><Check className="w-4 h-4 text-green-600" /> No credit card</span>
              <span className="flex items-center gap-2"><Check className="w-4 h-4 text-green-600" /> Cancel anytime</span>
            </div>
          </div>

          {/* Interactive Query Demo */}
          <div className="max-w-5xl mx-auto">
            <div className="bg-white rounded-xl shadow-2xl border border-gray-200 overflow-hidden">
              {/* Tabs */}
              <div className="flex border-b border-gray-200 bg-gray-50">
                <button
                  onClick={() => setActiveTab('incident')}
                  className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${
                    activeTab === 'incident' 
                      ? 'bg-white text-gray-900 border-b-2 border-gray-900' 
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <AlertCircle className="w-4 h-4 inline mr-2" />
                  Incident Response
                </button>
                <button
                  onClick={() => setActiveTab('deploy')}
                  className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${
                    activeTab === 'deploy' 
                      ? 'bg-white text-gray-900 border-b-2 border-gray-900' 
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <GitBranch className="w-4 h-4 inline mr-2" />
                  Safe Deployments
                </button>
                <button
                  onClick={() => setActiveTab('onboard')}
                  className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${
                    activeTab === 'onboard' 
                      ? 'bg-white text-gray-900 border-b-2 border-gray-900' 
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Users className="w-4 h-4 inline mr-2" />
                  Team Onboarding
                </button>
              </div>

              {/* Query Interface */}
              <div className="p-8">
                <div className="mb-6">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center">
                      <span className="text-white text-sm font-bold">Q</span>
                    </div>
                    <span className="text-sm font-semibold text-gray-500">YOUR QUESTION</span>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 font-mono text-base text-gray-900 min-h-[60px] flex items-center">
                    {typedText}<span className="inline-block w-0.5 h-5 bg-gray-900 ml-1 animate-pulse"></span>
                  </div>
                </div>

                <div>
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-8 h-8 bg-emerald-600 rounded-lg flex items-center justify-center">
                      <span className="text-white text-sm font-bold">A</span>
                    </div>
                    <span className="text-sm font-semibold text-gray-500">INSTANT ANSWER</span>
                  </div>
                  
                  {activeTab === 'incident' && (
                    <div className="space-y-4">
                      <div className="bg-gradient-to-r from-red-50 to-orange-50 rounded-lg p-6 border-l-4 border-red-500">
                        <div className="flex items-start justify-between mb-4">
                          <div>
                            <h4 className="font-bold text-gray-900 text-lg mb-1">Critical Impact: 12 services affected</h4>
                            <p className="text-sm text-gray-700">Auth-service is a core dependency for payment and user flows</p>
                          </div>
                          <span className="px-3 py-1 bg-red-600 text-white text-xs font-bold rounded-full">HIGH RISK</span>
                        </div>
                        <div className="grid md:grid-cols-2 gap-3 text-sm">
                          <div className="bg-white rounded-lg p-3 border border-red-200">
                            <div className="font-semibold text-red-700 mb-2">Immediate Impact (4)</div>
                            <div className="space-y-1 text-gray-700">
                              <div>• payment-gateway</div>
                              <div>• user-profile-api</div>
                              <div>• checkout-service</div>
                              <div>• session-manager</div>
                            </div>
                          </div>
                          <div className="bg-white rounded-lg p-3 border border-orange-200">
                            <div className="font-semibold text-orange-700 mb-2">Secondary Impact (8)</div>
                            <div className="space-y-1 text-gray-700">
                              <div>• notification-service</div>
                              <div>• analytics-processor</div>
                              <div>• recommendation-engine</div>
                              <div>• and 5 more services...</div>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="bg-emerald-50 rounded-lg p-4 border-l-4 border-emerald-500">
                        <div className="font-semibold text-emerald-900 mb-2 flex items-center gap-2">
                          <Zap className="w-4 h-4" />
                          Recommended Action
                        </div>
                        <p className="text-sm text-emerald-800">Implement circuit breakers on payment-gateway and checkout-service. Alert Platform and Payments teams immediately.</p>
                      </div>
                    </div>
                  )}

                  {activeTab === 'deploy' && (
                    <div className="space-y-4">
                      <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg p-6 border-l-4 border-yellow-500">
                        <div className="flex items-start justify-between mb-4">
                          <div>
                            <h4 className="font-bold text-gray-900 text-lg mb-1">Schema change affects 8 services</h4>
                            <p className="text-sm text-gray-700">Breaking changes detected in user-database schema</p>
                          </div>
                          <span className="px-3 py-1 bg-yellow-600 text-white text-xs font-bold rounded-full">REVIEW NEEDED</span>
                        </div>
                        <div className="bg-white rounded-lg p-4 border border-yellow-200 mb-3">
                          <div className="font-semibold text-gray-900 mb-3">Affected Services</div>
                          <div className="space-y-2">
                            <div className="flex items-center justify-between text-sm">
                              <span className="text-gray-700">user-profile-api <span className="text-gray-500">(direct)</span></span>
                              <span className="px-2 py-1 bg-red-100 text-red-700 text-xs font-semibold rounded">Breaking</span>
                            </div>
                            <div className="flex items-center justify-between text-sm">
                              <span className="text-gray-700">auth-service <span className="text-gray-500">(direct)</span></span>
                              <span className="px-2 py-1 bg-red-100 text-red-700 text-xs font-semibold rounded">Breaking</span>
                            </div>
                            <div className="flex items-center justify-between text-sm">
                              <span className="text-gray-700">notification-service <span className="text-gray-500">(indirect)</span></span>
                              <span className="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs font-semibold rounded">Warning</span>
                            </div>
                            <div className="text-sm text-gray-500">+ 5 more services with indirect dependencies</div>
                          </div>
                        </div>
                      </div>
                      <div className="bg-emerald-50 rounded-lg p-4 border-l-4 border-emerald-500">
                        <div className="font-semibold text-emerald-900 mb-2 flex items-center gap-2">
                          <Shield className="w-4 h-4" />
                          Deployment Plan
                        </div>
                        <p className="text-sm text-emerald-800">Deploy during maintenance window (Sat 2 AM UTC). Update user-profile-api and auth-service first, then dependent services. Estimated downtime: 15 minutes.</p>
                      </div>
                    </div>
                  )}

                  {activeTab === 'onboard' && (
                    <div className="space-y-4">
                      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 border-l-4 border-blue-500">
                        <h4 className="font-bold text-gray-900 text-lg mb-4">Payment Flow Architecture</h4>
                        <div className="space-y-3">
                          <div className="bg-white rounded-lg p-4 border border-blue-200">
                            <div className="font-mono text-sm space-y-2">
                              <div className="flex items-center gap-3 text-gray-800">
                                <div className="w-6 h-6 bg-blue-100 rounded flex items-center justify-center text-xs font-bold">1</div>
                                <span><strong>checkout-service</strong> receives payment request</span>
                              </div>
                              <div className="flex items-center gap-3 text-gray-800 ml-6">
                                <div className="w-6 h-6 bg-blue-100 rounded flex items-center justify-center text-xs font-bold">2</div>
                                <span>validates with <strong>auth-service</strong></span>
                              </div>
                              <div className="flex items-center gap-3 text-gray-800 ml-12">
                                <div className="w-6 h-6 bg-blue-100 rounded flex items-center justify-center text-xs font-bold">3</div>
                                <span>calls <strong>payment-gateway</strong> (Stripe API)</span>
                              </div>
                              <div className="flex items-center gap-3 text-gray-800 ml-6">
                                <div className="w-6 h-6 bg-blue-100 rounded flex items-center justify-center text-xs font-bold">4</div>
                                <span>updates <strong>order-database</strong></span>
                              </div>
                              <div className="flex items-center gap-3 text-gray-800 ml-12">
                                <div className="w-6 h-6 bg-blue-100 rounded flex items-center justify-center text-xs font-bold">5</div>
                                <span>triggers <strong>notification-service</strong></span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="bg-purple-50 rounded-lg p-4 border-l-4 border-purple-500">
                        <div className="font-semibold text-purple-900 mb-2 flex items-center gap-2">
                          <BarChart3 className="w-4 h-4" />
                          Key Metrics
                        </div>
                        <p className="text-sm text-purple-800">Average response time: 340ms • Success rate: 99.7% • Dependencies: 5 services, 2 databases</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Real Impact Stats */}
      <section className="py-16 px-6 lg:px-8 bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-3">Real impact from real engineering teams</h2>
            <p className="text-gray-400 text-lg">Measurable results, not vanity metrics</p>
          </div>
          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="text-5xl font-bold text-white mb-2">85%</div>
              <div className="text-gray-400 text-sm">Faster incident resolution</div>
              <div className="text-gray-500 text-xs mt-1">vs manual dependency tracing</div>
            </div>
            <div className="text-center">
              <div className="text-5xl font-bold text-white mb-2">73%</div>
              <div className="text-gray-400 text-sm">Fewer production incidents</div>
              <div className="text-gray-500 text-xs mt-1">from unknown dependencies</div>
            </div>
            <div className="text-center">
              <div className="text-5xl font-bold text-white mb-2">2-3x</div>
              <div className="text-gray-400 text-sm">Faster developer onboarding</div>
              <div className="text-gray-500 text-xs mt-1">from weeks to days</div>
            </div>
            <div className="text-center">
              <div className="text-5xl font-bold text-white mb-2">$180K</div>
              <div className="text-gray-400 text-sm">Average annual savings</div>
              <div className="text-gray-500 text-xs mt-1">in reduced downtime costs</div>
            </div>
          </div>
        </div>
      </section>

      {/* Problem-Solution */}
      <section id="solutions" className="py-20 px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-2 gap-16">
            {/* Problem */}
            <div>
              <div className="text-sm font-bold text-red-600 mb-3">THE PROBLEM</div>
              <h2 className="text-3xl font-bold text-gray-900 mb-6">Your infrastructure is invisible</h2>
              <div className="space-y-4">
                <div className="flex gap-4">
                  <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Clock className="w-6 h-6 text-red-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-1">Hours wasted during incidents</h4>
                    <p className="text-gray-600 text-sm">Engineers spend 40% of incident time just figuring out what depends on what</p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <AlertCircle className="w-6 h-6 text-orange-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-1">Unexpected production failures</h4>
                    <p className="text-gray-600 text-sm">"We had no idea that service depended on this database"</p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Users className="w-6 h-6 text-yellow-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-1">Tribal knowledge bottlenecks</h4>
                    <p className="text-gray-600 text-sm">Only senior engineers know how the system actually works</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Solution */}
            <div>
              <div className="text-sm font-bold text-emerald-600 mb-3">THE SOLUTION</div>
              <h2 className="text-3xl font-bold text-gray-900 mb-6">Automated dependency intelligence</h2>
              <div className="space-y-4">
                <div className="flex gap-4">
                  <div className="w-12 h-12 bg-black rounded-lg flex items-center justify-center flex-shrink-0">
                    <Zap className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-1">Instant dependency mapping</h4>
                    <p className="text-gray-600 text-sm">Automatically discovers and maps every service, database, and dependency from your infrastructure code</p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="w-12 h-12 bg-emerald-600 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Shield className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-1">Real-time impact analysis</h4>
                    <p className="text-gray-600 text-sm">See exactly what breaks before you deploy. No surprises, no guesswork</p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="w-12 h-12 bg-gray-700 rounded-lg flex items-center justify-center flex-shrink-0">
                    <TrendingUp className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-1">Self-service knowledge</h4>
                    <p className="text-gray-600 text-sm">Every engineer can answer their own questions. No more waiting for senior engineers</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Integration */}
      <section className="py-20 px-6 lg:px-8 bg-gradient-to-b from-gray-50 to-white">
        <div className="max-w-7xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Works with your existing stack</h2>
          <p className="text-lg text-gray-600 mb-12">No migration required. Connects to your infrastructure in minutes.</p>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
            <div className="bg-white rounded-xl p-6 border border-gray-200 hover:border-gray-400 hover:shadow-lg transition-all">
              <Server className="w-10 h-10 text-gray-700 mx-auto mb-3" />
              <div className="font-semibold text-gray-900">Kubernetes</div>
              <div className="text-xs text-gray-500 mt-1">Auto-discovery</div>
            </div>
            <div className="bg-white rounded-xl p-6 border border-gray-200 hover:border-gray-400 hover:shadow-lg transition-all">
              <Database className="w-10 h-10 text-gray-700 mx-auto mb-3" />
              <div className="font-semibold text-gray-900">Docker Compose</div>
              <div className="text-xs text-gray-500 mt-1">Full support</div>
            </div>
            <div className="bg-white rounded-xl p-6 border border-gray-200 hover:border-gray-400 hover:shadow-lg transition-all">
              <GitBranch className="w-10 h-10 text-gray-700 mx-auto mb-3" />
              <div className="font-semibold text-gray-900">Terraform</div>
              <div className="text-xs text-gray-500 mt-1">IaC parsing</div>
            </div>
            <div className="bg-white rounded-xl p-6 border border-gray-200 hover:border-gray-400 hover:shadow-lg transition-all">
              <BarChart3 className="w-10 h-10 text-gray-700 mx-auto mb-3" />
              <div className="font-semibold text-gray-900">AWS/GCP/Azure</div>
              <div className="text-xs text-gray-500 mt-1">Cloud native</div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-20 px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Start free. Scale when ready.</h2>
            <p className="text-lg text-gray-600">All plans include 14-day free trial. No credit card required.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {/* Starter */}
            <div className="bg-white rounded-2xl border-2 border-gray-200 p-8 hover:border-gray-400 hover:shadow-xl transition-all">
              <div className="text-sm font-bold text-gray-600 mb-2">STARTER</div>
              <div className="flex items-baseline gap-2 mb-6">
                <span className="text-5xl font-bold text-gray-900">$0</span>
                <span className="text-gray-600">/month</span>
              </div>
              <p className="text-gray-600 mb-6">Perfect for small teams exploring dependency management</p>
              <button onClick={() => navigate('/register')} className="w-full py-3 bg-gray-900 text-white font-semibold rounded-lg hover:bg-gray-800 transition-colors mb-8">
                Start free trial
              </button>
              <ul className="space-y-3 text-sm">
                <li className="flex items-start gap-3"><Check className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" /><span className="text-gray-700">Up to 25 services</span></li>
                <li className="flex items-start gap-3"><Check className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" /><span className="text-gray-700">Automated dependency discovery</span></li>
                <li className="flex items-start gap-3"><Check className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" /><span className="text-gray-700">Natural language queries</span></li>
                <li className="flex items-start gap-3"><Check className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" /><span className="text-gray-700">Basic visualizations</span></li>
                <li className="flex items-start gap-3"><Check className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" /><span className="text-gray-700">Community support</span></li>
              </ul>
            </div>

            {/* Professional - Most Popular */}
            <div className="bg-black rounded-2xl p-8 relative transform scale-105 shadow-2xl text-white">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-emerald-500 text-white px-4 py-1 rounded-full text-xs font-bold">
                MOST POPULAR
              </div>
              <div className="text-sm font-bold text-gray-300 mb-2">PROFESSIONAL</div>
              <div className="flex items-baseline gap-2 mb-6">
                <span className="text-5xl font-bold">$299</span>
                <span className="text-gray-300">/month</span>
              </div>
              <p className="text-gray-300 mb-6">For growing teams with complex infrastructure</p>
              <button onClick={() => navigate('/register')} className="w-full py-3 bg-white text-black font-semibold rounded-lg hover:bg-gray-100 transition-colors mb-8">
                Start free trial
              </button>
              <ul className="space-y-3 text-sm">
                <li className="flex items-start gap-3"><Check className="w-5 h-5 flex-shrink-0" /><span>Up to 250 services</span></li>
                <li className="flex items-start gap-3"><Check className="w-5 h-5 flex-shrink-0" /><span>Everything in Starter</span></li>
                <li className="flex items-start gap-3"><Check className="w-5 h-5 flex-shrink-0" /><span>Real-time impact analysis</span></li>
                <li className="flex items-start gap-3"><Check className="w-5 h-5 flex-shrink-0" /><span>Advanced visualizations</span></li>
                <li className="flex items-start gap-3"><Check className="w-5 h-5 flex-shrink-0" /><span>Priority support</span></li>
                <li className="flex items-start gap-3"><Check className="w-5 h-5 flex-shrink-0" /><span>SSO & team management</span></li>
                <li className="flex items-start gap-3"><Check className="w-5 h-5 flex-shrink-0" /><span>API access</span></li>
              </ul>
            </div>

            {/* Enterprise */}
            <div className="bg-white rounded-2xl border-2 border-gray-200 p-8 hover:border-gray-400 hover:shadow-xl transition-all">
              <div className="text-sm font-bold text-gray-600 mb-2">ENTERPRISE</div>
              <div className="flex items-baseline gap-2 mb-6">
                <span className="text-5xl font-bold text-gray-900">Custom</span>
              </div>
              <p className="text-gray-600 mb-6">For organizations with mission-critical infrastructure</p>
              <button onClick={() => navigate('/contact')} className="w-full py-3 bg-black text-white font-semibold rounded-lg hover:bg-gray-800 transition-all mb-8">
                Contact sales
              </button>
              <ul className="space-y-3 text-sm">
                <li className="flex items-start gap-3"><Check className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" /><span className="text-gray-700">Unlimited services</span></li>
                <li className="flex items-start gap-3"><Check className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" /><span className="text-gray-700">Everything in Professional</span></li>
                <li className="flex items-start gap-3"><Check className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" /><span className="text-gray-700">On-premise deployment</span></li>
                <li className="flex items-start gap-3"><Check className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" /><span className="text-gray-700">Custom SLA (99.99%)</span></li>
                <li className="flex items-start gap-3"><Check className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" /><span className="text-gray-700">Dedicated support engineer</span></li>
                <li className="flex items-start gap-3"><Check className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" /><span className="text-gray-700">Custom integrations</span></li>
                <li className="flex items-start gap-3"><Check className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" /><span className="text-gray-700">Training & onboarding</span></li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-24 px-6 lg:px-8 bg-gray-900 text-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl lg:text-5xl font-bold mb-6">
            Stop wasting time. Start shipping faster.
          </h2>
          <p className="text-xl text-gray-300 mb-10">
            Join engineering teams who've eliminated dependency confusion and reduced incident response time by 85%.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
            <button onClick={() => navigate('/register')} className="px-10 py-5 bg-white text-black text-lg font-bold rounded-xl hover:bg-gray-100 transition-all shadow-2xl inline-flex items-center justify-center gap-3 group">
              Start your free trial <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
            </button>
            <button onClick={() => navigate('/dashboard')} className="px-10 py-5 border-2 border-white text-white text-lg font-bold rounded-xl hover:bg-white hover:text-black transition-all">
              Try live demo
            </button>
          </div>
          <p className="text-gray-400 text-sm">14-day free trial • No credit card required • Setup in 5 minutes</p>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12 px-6 lg:px-8 border-t border-gray-800">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-8 mb-12">
            <div className="col-span-2">
              <div className="flex items-center gap-2.5 mb-4">
                <div className="w-8 h-8 bg-white">
                  <Database className="w-8 h-8 p-1.5 text-gray-900" />
                </div>
                <span className="text-lg font-bold text-white">EKG</span>
              </div>
              <p className="text-sm max-w-xs mb-4">
                Infrastructure dependency intelligence that helps engineering teams ship faster and break less.
              </p>
            </div>

            <div>
              <div className="text-sm font-semibold text-white mb-3">Product</div>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Security</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Integrations</a></li>
              </ul>
            </div>

            <div>
              <div className="text-sm font-semibold text-white mb-3">Company</div>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
              </ul>
            </div>

            <div>
              <div className="text-sm font-semibold text-white mb-3">Resources</div>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white transition-colors">Documentation</a></li>
                <li><a href="#" className="hover:text-white transition-colors">API Docs</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Support</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Status</a></li>
              </ul>
            </div>
          </div>

          <div className="pt-8 border-t border-gray-800 flex flex-col md:flex-row justify-between items-center gap-4 text-sm">
            <p>© 2026 EKG. All rights reserved.</p>
            <div className="flex gap-6">
              <a href="#" className="hover:text-white transition-colors">Privacy</a>
              <a href="#" className="hover:text-white transition-colors">Terms</a>
              <a href="#" className="hover:text-white transition-colors">Security</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
