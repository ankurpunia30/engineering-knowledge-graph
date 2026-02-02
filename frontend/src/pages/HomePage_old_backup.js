import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Database, ArrowRight, Menu, X, CheckCircle, AlertTriangle, Zap, Shield, GitBranch, Users, Code } from 'lucide-react';

const HomePage = () => {
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeTestimonial, setActiveTestimonial] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => setActiveTestimonial((prev) => (prev + 1) % 3), 5000);
    return () => clearInterval(interval);
  }, []);

  const keyMetrics = [
    { value: "10x", label: "Faster Resolution", sublabel: "vs manual dependency tracking" },
    { value: "60%", label: "Cost Reduction", sublabel: "through intelligent caching" },
    { value: "<30s", label: "Query Response", sublabel: "for complex infrastructure" },
    { value: "100%", label: "Auto-Discovery", sublabel: "from existing configs" }
  ];

  const coreCapabilities = [
    { icon: <Zap className="w-6 h-6" />, title: "Natural Language Queries", description: "Ask questions in plain English. Your team doesn't need to learn Cypher, GraphQL, or specialized query languages." },
    { icon: <AlertTriangle className="w-6 h-6" />, title: "Real-Time Blast Radius", description: "During incidents, instantly understand impact scope. Know exactly what breaks when a service fails." },
    { icon: <GitBranch className="w-6 h-6" />, title: "Dependency Intelligence", description: "Automatically map service dependencies from Docker Compose, Kubernetes manifests, and team configurations." },
    { icon: <Shield className="w-6 h-6" />, title: "Enterprise Security", description: "PostgreSQL-backed auth, JWT sessions, role-based access control, and audit logging built-in." }
  ];

  const problemSolutions = [
    { problem: "Incident at 3 AM: Which services are affected?", before: "30 minutes of manual digging through docs and configs", after: "Ask: 'What depends on Redis?' - 10 second answer", savings: "95% time saved" },
    { problem: "New engineer needs to understand the system", before: "Days of documentation reading and tribal knowledge", after: "Interactive queries reveal architecture in minutes", savings: "80% faster onboarding" },
    { problem: "Planning to deprecate a legacy service", before: "Hours analyzing code, hoping you found everything", after: "Complete impact analysis with dependency chains", savings: "90% risk reduction" }
  ];

  const enterpriseFeatures = ["Multi-tenancy with organization isolation", "PostgreSQL for production-grade data persistence", "Intelligent caching layer (60% LLM cost savings)", "JWT-based authentication with refresh tokens", "Role-based access control (RBAC)", "Audit logs for compliance", "RESTful API for integrations", "On-premise deployment options", "SSO/SAML integration (Enterprise)", "99.9% uptime SLA (Enterprise)"];

  const testimonials = [
    { quote: "Cut our incident resolution time from 45 minutes to under 5 minutes. The blast radius analysis is a game-changer.", author: "Sarah Chen", role: "VP Engineering", company: "TechCorp" },
    { quote: "We saved $18,000/year in LLM costs with the intelligent caching layer. ROI in the first quarter.", author: "Michael Rodriguez", role: "CTO", company: "DataFlow Inc" },
    { quote: "New engineers are productive on day one. They can query the infrastructure instead of reading outdated docs.", author: "Emily Watson", role: "Engineering Manager", company: "CloudScale" }
  ];

  return (
    <div className="min-h-screen bg-white">
      <nav className="border-b border-gray-200 bg-white sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/')}>
              <div className="w-9 h-9 bg-blue-600 rounded flex items-center justify-center">
                <Database className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-gray-900">EKG</h1>
                <p className="text-[10px] text-gray-500 -mt-0.5">Engineering Knowledge Graph</p>
              </div>
            </div>
            <div className="hidden md:flex items-center gap-8">
              <a href="#capabilities" className="text-sm text-gray-600 hover:text-gray-900">Capabilities</a>
              <a href="#enterprise" className="text-sm text-gray-600 hover:text-gray-900">Enterprise</a>
              <a href="#pricing" className="text-sm text-gray-600 hover:text-gray-900">Pricing</a>
              <button onClick={() => navigate('/login')} className="text-sm text-gray-600 hover:text-gray-900">Sign In</button>
              <button onClick={() => navigate('/register')} className="px-5 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition">Start Free Trial</button>
            </div>
            <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="md:hidden p-2 text-gray-600">
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
          {mobileMenuOpen && (
            <div className="md:hidden py-4 space-y-2 border-t border-gray-200">
              <a href="#capabilities" className="block px-4 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded">Capabilities</a>
              <a href="#enterprise" className="block px-4 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded">Enterprise</a>
              <a href="#pricing" className="block px-4 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded">Pricing</a>
              <button onClick={() => navigate('/login')} className="block w-full text-left px-4 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded">Sign In</button>
              <button onClick={() => navigate('/register')} className="block w-full px-4 py-2 bg-blue-600 text-white text-sm rounded">Start Free Trial</button>
            </div>
          )}
        </div>
      </nav>

      <section className="py-20 bg-gradient-to-b from-gray-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-50 rounded-full mb-6">
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium text-blue-900">Production-Ready Infrastructure Intelligence</span>
            </div>
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
              Understand Your Infrastructure
              <span className="block text-blue-600">Without the Learning Curve</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 leading-relaxed">
              Ask questions in plain English. Get instant answers about dependencies, blast radius, and service ownership. Built for engineering teams who value their time.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 mb-12">
              <button onClick={() => navigate('/register')} className="px-8 py-4 bg-blue-600 text-white rounded font-medium hover:bg-blue-700 transition flex items-center justify-center gap-2 group">
                Start Free Trial
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition" />
              </button>
              <button className="px-8 py-4 bg-white text-gray-900 rounded font-medium border-2 border-gray-200 hover:border-gray-300 transition">Schedule Demo</button>
            </div>
            <p className="text-sm text-gray-500">No credit card required • Free tier includes 1,000 nodes • Enterprise plans available</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-16 pt-16 border-t border-gray-200">
            {keyMetrics.map((metric, index) => (
              <div key={index}>
                <div className="text-4xl font-bold text-gray-900 mb-1">{metric.value}</div>
                <div className="text-sm font-medium text-gray-900">{metric.label}</div>
                <div className="text-xs text-gray-500 mt-1">{metric.sublabel}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="capabilities" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-2xl mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Core Capabilities</h2>
            <p className="text-lg text-gray-600">Everything you need to understand, monitor, and manage complex microservice architectures.</p>
          </div>
          <div className="grid md:grid-cols-2 gap-12">
            {coreCapabilities.map((capability, index) => (
              <div key={index} className="flex gap-4">
                <div className="flex-shrink-0 w-12 h-12 bg-blue-50 rounded flex items-center justify-center text-blue-600">{capability.icon}</div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{capability.title}</h3>
                  <p className="text-gray-600">{capability.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-2xl mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Real Problems. Real Solutions.</h2>
            <p className="text-lg text-gray-600">See the measurable impact on common engineering scenarios.</p>
          </div>
          <div className="space-y-8">
            {problemSolutions.map((item, index) => (
              <div key={index} className="bg-white rounded-lg border border-gray-200 p-8">
                <h3 className="text-xl font-semibold text-gray-900 mb-6">{item.problem}</h3>
                <div className="grid md:grid-cols-2 gap-8">
                  <div>
                    <div className="text-sm font-medium text-red-600 mb-2">Before EKG</div>
                    <p className="text-gray-700">{item.before}</p>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-green-600 mb-2">With EKG</div>
                    <p className="text-gray-700 mb-3">{item.after}</p>
                    <div className="inline-flex items-center gap-2 px-3 py-1 bg-green-50 rounded-full">
                      <CheckCircle className="w-4 h-4 text-green-600" />
                      <span className="text-sm font-medium text-green-900">{item.savings}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 bg-blue-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-white mb-2">Trusted by Engineering Teams</h2>
            <p className="text-blue-100">Hear from teams who transformed their infrastructure management</p>
          </div>
          <div className="bg-white rounded-lg p-8 md:p-12">
            <div className="mb-6">
              <p className="text-xl text-gray-900 leading-relaxed mb-6">"{testimonials[activeTestimonial].quote}"</p>
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                  <Users className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <div className="font-semibold text-gray-900">{testimonials[activeTestimonial].author}</div>
                  <div className="text-sm text-gray-600">{testimonials[activeTestimonial].role}, {testimonials[activeTestimonial].company}</div>
                </div>
              </div>
            </div>
            <div className="flex justify-center gap-2 mt-8">
              {testimonials.map((_, index) => (
                <button key={index} onClick={() => setActiveTestimonial(index)} className={`w-2 h-2 rounded-full transition ${index === activeTestimonial ? 'bg-blue-600 w-8' : 'bg-gray-300'}`} />
              ))}
            </div>
          </div>
        </div>
      </section>

      <section id="enterprise" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Enterprise-Grade Platform</h2>
              <p className="text-lg text-gray-600 mb-8">Built for security, scalability, and compliance from day one. Not a prototype—a production-ready system.</p>
              <div className="space-y-3">
                {enterpriseFeatures.map((feature, index) => (
                  <div key={index} className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-700">{feature}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-8">
              <h3 className="text-xl font-semibold text-gray-900 mb-6">Technical Architecture</h3>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <Code className="w-5 h-5 text-blue-600 mt-0.5" />
                  <div>
                    <div className="font-medium text-gray-900">LLM-Powered Query Layer</div>
                    <div className="text-sm text-gray-600">Groq/Llama 3 with intelligent intent classification</div>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Database className="w-5 h-5 text-blue-600 mt-0.5" />
                  <div>
                    <div className="font-medium text-gray-900">Hybrid Graph Storage</div>
                    <div className="text-sm text-gray-600">NetworkX (dev) → Neo4j (production scale)</div>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Shield className="w-5 h-5 text-blue-600 mt-0.5" />
                  <div>
                    <div className="font-medium text-gray-900">PostgreSQL Backend</div>
                    <div className="text-sm text-gray-600">User auth, multi-tenancy, audit logs</div>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Zap className="w-5 h-5 text-blue-600 mt-0.5" />
                  <div>
                    <div className="font-medium text-gray-900">Intelligent Cache Layer</div>
                    <div className="text-sm text-gray-600">60% LLM cost reduction, sub-second responses</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="pricing" className="py-20 bg-gray-50">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Transparent Pricing</h2>
            <p className="text-lg text-gray-600">Start free, scale with your team. No surprises.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white rounded-lg border-2 border-gray-200 p-8">
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Free</h3>
              <div className="text-3xl font-bold text-gray-900 mb-4">$0</div>
              <p className="text-gray-600 mb-6">For individuals & small teams</p>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center gap-2 text-sm"><CheckCircle className="w-4 h-4 text-green-600" />1,000 nodes</li>
                <li className="flex items-center gap-2 text-sm"><CheckCircle className="w-4 h-4 text-green-600" />Natural language queries</li>
                <li className="flex items-center gap-2 text-sm"><CheckCircle className="w-4 h-4 text-green-600" />Community support</li>
              </ul>
              <button onClick={() => navigate('/register')} className="w-full py-3 border-2 border-gray-900 text-gray-900 rounded font-medium hover:bg-gray-900 hover:text-white transition">Get Started</button>
            </div>
            <div className="bg-blue-600 rounded-lg p-8 relative">
              <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-3 py-1 bg-yellow-400 text-gray-900 text-xs font-semibold rounded-full">MOST POPULAR</div>
              <h3 className="text-xl font-semibold text-white mb-2">Professional</h3>
              <div className="text-3xl font-bold text-white mb-4">$49</div>
              <p className="text-blue-100 mb-6">For growing teams</p>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center gap-2 text-sm text-white"><CheckCircle className="w-4 h-4" />25,000 nodes</li>
                <li className="flex items-center gap-2 text-sm text-white"><CheckCircle className="w-4 h-4" />Advanced analytics</li>
                <li className="flex items-center gap-2 text-sm text-white"><CheckCircle className="w-4 h-4" />Priority support</li>
                <li className="flex items-center gap-2 text-sm text-white"><CheckCircle className="w-4 h-4" />Team collaboration</li>
              </ul>
              <button onClick={() => navigate('/register')} className="w-full py-3 bg-white text-blue-600 rounded font-medium hover:bg-gray-50 transition">Start Trial</button>
            </div>
            <div className="bg-white rounded-lg border-2 border-gray-200 p-8">
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Enterprise</h3>
              <div className="text-3xl font-bold text-gray-900 mb-4">Custom</div>
              <p className="text-gray-600 mb-6">For large organizations</p>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center gap-2 text-sm"><CheckCircle className="w-4 h-4 text-green-600" />Unlimited nodes</li>
                <li className="flex items-center gap-2 text-sm"><CheckCircle className="w-4 h-4 text-green-600" />SSO/SAML</li>
                <li className="flex items-center gap-2 text-sm"><CheckCircle className="w-4 h-4 text-green-600" />On-premise deployment</li>
                <li className="flex items-center gap-2 text-sm"><CheckCircle className="w-4 h-4 text-green-600" />99.9% SLA</li>
              </ul>
              <button className="w-full py-3 border-2 border-gray-900 text-gray-900 rounded font-medium hover:bg-gray-900 hover:text-white transition">Contact Sales</button>
            </div>
          </div>
        </div>
      </section>

      <section className="py-20 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Ready to Stop Wrestling with Infrastructure Complexity?</h2>
          <p className="text-xl text-gray-600 mb-8">Join engineering teams who value their time. Start free, no credit card required.</p>
          <button onClick={() => navigate('/register')} className="px-8 py-4 bg-blue-600 text-white rounded font-medium hover:bg-blue-700 transition text-lg">Start Free Trial</button>
          <p className="text-sm text-gray-500 mt-4">Setup takes 3 minutes • Cancel anytime</p>
        </div>
      </section>

      <footer className="bg-gray-900 text-gray-400 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-7 h-7 bg-blue-600 rounded flex items-center justify-center">
                  <Database className="w-4 h-4 text-white" />
                </div>
                <span className="text-white font-semibold">EKG</span>
              </div>
              <p className="text-sm">Infrastructure intelligence for engineering teams</p>
            </div>
            <div>
              <h4 className="text-white font-medium mb-4 text-sm">Product</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#capabilities" className="hover:text-white">Capabilities</a></li>
                <li><a href="#pricing" className="hover:text-white">Pricing</a></li>
                <li><a href="/docs" className="hover:text-white">Documentation</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-medium mb-4 text-sm">Company</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="/about" className="hover:text-white">About</a></li>
                <li><a href="/blog" className="hover:text-white">Blog</a></li>
                <li><a href="/security" className="hover:text-white">Security</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-medium mb-4 text-sm">Legal</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="/privacy" className="hover:text-white">Privacy</a></li>
                <li><a href="/terms" className="hover:text-white">Terms</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 text-center text-sm">
            <p>© 2026 Engineering Knowledge Graph. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
